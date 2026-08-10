"""
Ciclo de vida del intento de evaluación.

`cerrar_intento` es la ÚNICA ruta de código del sistema que puede producir una
insignia. Aun así, no se confía en ella: la base de datos impone el invariante
por su cuenta (ADR-005). Si algún día aparece una segunda ruta —un seed, una
migración, un constructor apurado— el esquema la rechaza igual.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from .eventos import registrar_evento
from .progreso import abrir_siguiente_bloque, modulos_completos

XP_POR_NIVEL_ESTANDAR = {1: 200, 2: 300, 3: 400}   # S-37


@dataclass(frozen=True)
class ResultadoIntento:
    intento_id: UUID
    puntaje: float
    aprobado: bool
    insignia_id: UUID | None
    xp_otorgado: int
    reintentos_restantes: int


class IntentoExpirado(Exception):
    pass


class SinReintentos(Exception):
    pass


class ModulosPendientes(Exception):
    """La evaluación cierra el bloque: se rinde después de recorrerlo, no antes."""


def abrir_intento(conn, *, colaborador_id: UUID, bloque_ruta_id: UUID) -> UUID:
    """Abre un intento. Si ya hay uno abierto y vigente, lo retoma (S-14)."""
    ev = conn.execute(
        """
        SELECT e.id, e.max_reintentos, e.minutos_expiracion, e.n_items_por_intento
          FROM bloque_ruta br
          JOIN evaluacion e ON e.bloque_contenido_id = br.bloque_contenido_id
         WHERE br.id = %s
        """,
        (bloque_ruta_id,),
    ).fetchone()
    if ev is None:
        raise LookupError("el bloque de ruta no tiene evaluación asociada")
    evaluacion_id, max_reintentos, minutos_exp, n_items = ev

    # La secuencia formativa se impone en el servidor, no solo en la pantalla: si
    # solo la cuidara la UI, bastaría con llamar al endpoint para saltarse el bloque.
    completos, total = modulos_completos(
        conn, colaborador_id=colaborador_id, bloque_ruta_id=bloque_ruta_id
    )
    if total and completos < total:
        raise ModulosPendientes(
            f"faltan {total - completos} módulos por ver antes de rendir la evaluación"
        )

    abierto = conn.execute(
        """
        SELECT id, expira_en FROM intento_evaluacion
         WHERE bloque_ruta_id = %s AND estado = 'abierto'
        """,
        (bloque_ruta_id,),
    ).fetchone()
    if abierto:
        intento_id, expira_en = abierto
        if _ahora() <= expira_en:
            return intento_id
        _expirar(conn, intento_id)            # S-12: consume reintento, no otorga nada

    usados = conn.execute(
        "SELECT COALESCE(MAX(numero_intento), 0) FROM intento_evaluacion WHERE bloque_ruta_id = %s",
        (bloque_ruta_id,),
    ).fetchone()[0]

    if usados >= max_reintentos:
        # S-11: agotar reintentos NUNCA otorga la medalla. El bloque queda
        # esperando acompañamiento, no se cierra solo.
        conn.execute(
            "UPDATE bloque_ruta SET estado = 'requiere_acompanamiento' WHERE id = %s",
            (bloque_ruta_id,),
        )
        raise SinReintentos(f"se agotaron los {max_reintentos} intentos")

    items = conn.execute(
        """
        SELECT id FROM item_evaluacion
         WHERE evaluacion_id = %s
         ORDER BY random()
         LIMIT %s
        """,
        (evaluacion_id, n_items),
    ).fetchall()
    servidos = [str(i[0]) for i in items]

    import json

    intento_id = conn.execute(
        """
        INSERT INTO intento_evaluacion
              (colaborador_id, bloque_ruta_id, evaluacion_id, numero_intento,
               items_servidos, expira_en)
        VALUES (%s, %s, %s, %s, %s::jsonb, %s)
        RETURNING id
        """,
        (colaborador_id, bloque_ruta_id, evaluacion_id, usados + 1,
         json.dumps(servidos), _ahora() + timedelta(minutes=minutos_exp)),
    ).fetchone()[0]

    conn.execute(
        "UPDATE bloque_ruta SET estado = 'en_curso' WHERE id = %s AND estado <> 'completo'",
        (bloque_ruta_id,),
    )
    return intento_id


def responder(conn, *, intento_id: UUID, item_id: UUID, indice_elegido: int) -> None:
    """Autosave por respuesta (§7). Una caída al enviar no pierde nada (S-14)."""
    estado_intento = conn.execute(
        "SELECT estado, expira_en FROM intento_evaluacion WHERE id = %s", (intento_id,)
    ).fetchone()
    if estado_intento is None:
        raise LookupError("intento inexistente")
    if estado_intento[0] != "abierto":
        raise IntentoExpirado("el intento ya está cerrado")
    if _ahora() > estado_intento[1]:
        _expirar(conn, intento_id)
        raise IntentoExpirado("el intento expiró")

    conn.execute(
        """
        INSERT INTO respuesta_intento (intento_id, item_id, indice_elegido)
        VALUES (%s, %s, %s)
        ON CONFLICT (intento_id, item_id)
        DO UPDATE SET indice_elegido = EXCLUDED.indice_elegido, respondido_en = now()
        """,
        (intento_id, item_id, indice_elegido),
    )


def cerrar_intento(conn, *, intento_id: UUID) -> ResultadoIntento:
    """
    Corrige, cierra y —solo si corresponde— otorga.

    Idempotente por `intento_id` (S-13): un segundo envío devuelve el resultado
    del primero y NO crea un segundo evento de XP.
    """
    fila = conn.execute(
        """
        SELECT ie.estado, ie.colaborador_id, ie.bloque_ruta_id, ie.evaluacion_id,
               ie.items_servidos, ie.puntaje, ie.aprobado, ie.numero_intento,
               e.umbral_aprobacion, e.max_reintentos,
               br.bloque_contenido_id, bc.nivel_estandar
          FROM intento_evaluacion ie
          JOIN evaluacion e   ON e.id = ie.evaluacion_id
          JOIN bloque_ruta br ON br.id = ie.bloque_ruta_id
          JOIN bloque_contenido bc ON bc.id = br.bloque_contenido_id
         WHERE ie.id = %s
        """,
        (intento_id,),
    ).fetchone()
    if fila is None:
        raise LookupError("intento inexistente")

    (estado_i, colaborador_id, bloque_ruta_id, _evaluacion_id, items_servidos,
     puntaje_prev, aprobado_prev, numero_intento, umbral, max_reintentos,
     bloque_contenido_id, nivel_estandar) = fila

    # --- ya cerrado: se devuelve lo mismo, sin volver a otorgar nada ---
    if estado_i != "abierto":
        insignia_id = _insignia_de(conn, intento_id)
        return ResultadoIntento(
            intento_id=intento_id,
            puntaje=float(puntaje_prev or 0),
            aprobado=bool(aprobado_prev),
            insignia_id=insignia_id,
            xp_otorgado=_xp_del_intento(conn, intento_id),
            reintentos_restantes=max(0, max_reintentos - numero_intento),
        )

    # --- corrección ---
    total = len(items_servidos) or 1
    correctas = conn.execute(
        """
        SELECT count(*)
          FROM respuesta_intento r
          JOIN item_evaluacion i ON i.id = r.item_id
         WHERE r.intento_id = %s AND r.indice_elegido = i.indice_correcta
        """,
        (intento_id,),
    ).fetchone()[0]

    puntaje = round(correctas / total, 3)
    aprobado = puntaje >= float(umbral)

    conn.execute(
        """
        UPDATE intento_evaluacion
           SET estado = 'enviado', enviado_en = now(), puntaje = %s, aprobado = %s
         WHERE id = %s
        """,
        (puntaje, aprobado, intento_id),
    )

    # --- reprobado: no otorga NADA y no deja residuo (§4.5) ---
    if not aprobado:
        restantes = max(0, max_reintentos - numero_intento)
        if restantes == 0:
            conn.execute(
                "UPDATE bloque_ruta SET estado = 'requiere_acompanamiento' WHERE id = %s",
                (bloque_ruta_id,),
            )
        else:
            conn.execute(
                "UPDATE bloque_ruta SET estado = 'disponible' WHERE id = %s", (bloque_ruta_id,)
            )
        return ResultadoIntento(intento_id, puntaje, False, None, 0, restantes)

    # --- aprobado: acá, y solo acá, nace una insignia ---
    medalla = conn.execute(
        "SELECT id, xp FROM definicion_medalla WHERE bloque_contenido_id = %s",
        (bloque_contenido_id,),
    ).fetchone()

    insignia_id = None
    xp_otorgado = 0

    if medalla:
        definicion_medalla_id, xp_medalla = medalla
        insignia = conn.execute(
            """
            INSERT INTO insignia (colaborador_id, definicion_medalla_id, intento_evaluacion_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (colaborador_id, definicion_medalla_id) DO NOTHING
            RETURNING id
            """,
            (colaborador_id, definicion_medalla_id, intento_id),
        ).fetchone()
        insignia_id = insignia[0] if insignia else None

        if insignia_id:
            xp_otorgado = xp_medalla or XP_POR_NIVEL_ESTANDAR[nivel_estandar]
            registrar_evento(
                conn,
                colaborador_id=colaborador_id,
                tipo="medalla_otorgada",
                origen_tipo="medalla",
                origen_id=insignia_id,
                xp=xp_otorgado,
                clase_xp="acreditable",
                clave_idempotencia=f"insignia:{insignia_id}",
            )

    conn.execute("UPDATE bloque_ruta SET estado = 'completo' WHERE id = %s", (bloque_ruta_id,))
    abrir_siguiente_bloque(conn, bloque_ruta_id=bloque_ruta_id)

    return ResultadoIntento(
        intento_id=intento_id,
        puntaje=puntaje,
        aprobado=True,
        insignia_id=insignia_id,
        xp_otorgado=xp_otorgado,
        reintentos_restantes=max(0, max_reintentos - numero_intento),
    )


# ------------------------------------------------------------------ auxiliares
def _ahora() -> datetime:
    return datetime.now(timezone.utc)


def _expirar(conn, intento_id: UUID) -> None:
    conn.execute(
        """
        UPDATE intento_evaluacion
           SET estado = 'expirado', aprobado = false, enviado_en = COALESCE(enviado_en, now())
         WHERE id = %s AND estado = 'abierto'
        """,
        (intento_id,),
    )


def _insignia_de(conn, intento_id: UUID):
    fila = conn.execute(
        "SELECT id FROM insignia WHERE intento_evaluacion_id = %s", (intento_id,)
    ).fetchone()
    return fila[0] if fila else None


def _xp_del_intento(conn, intento_id: UUID) -> int:
    return int(
        conn.execute(
            """
            SELECT COALESCE(SUM(e.xp), 0)
              FROM evento_gamificacion e
              JOIN insignia i ON i.id = e.origen_id
             WHERE i.intento_evaluacion_id = %s
            """,
            (intento_id,),
        ).fetchone()[0]
    )
