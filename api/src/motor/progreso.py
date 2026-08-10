"""
Progreso dentro de un bloque: módulos vistos y apertura del bloque siguiente.

Un módulo completado emite un evento de XP **acreditable** (S-04): es parte del
recorrido formativo, no un juego. Pero **no otorga insignia** — eso sigue siendo
exclusivo de la evaluación aprobada, y la base lo impone (ADR-005).

La idempotencia la da la clave del evento: marcar dos veces el mismo módulo no
suma XP dos veces.
"""
from __future__ import annotations

from uuid import UUID

from .eventos import registrar_evento


def completar_modulo(conn, *, colaborador_id: UUID, modulo_id: UUID) -> dict:
    """Marca un módulo como visto. Devuelve si sumó XP y cuánto."""
    fila = conn.execute(
        """SELECT m.xp, m.bloque_contenido_id, br.id AS bloque_ruta_id
             FROM modulo m
             JOIN bloque_ruta br ON br.bloque_contenido_id = m.bloque_contenido_id
             JOIN ruta r ON r.id = br.ruta_id
            WHERE m.id = %s AND r.colaborador_id = %s""",
        (modulo_id, colaborador_id),
    ).fetchone()
    if fila is None:
        # Igual que en el resto de la API: no se distingue "no existe" de "no es tuyo".
        raise LookupError("ese módulo no está en tu ruta")

    xp, _bloque_contenido_id, bloque_ruta_id = fila

    evento_id = registrar_evento(
        conn,
        colaborador_id=colaborador_id,
        tipo="modulo_completado",
        origen_tipo="modulo",
        origen_id=modulo_id,
        xp=xp,
        clase_xp="acreditable",
        clave_idempotencia=f"modulo:{colaborador_id}:{modulo_id}",
    )

    if evento_id:
        conn.execute(
            "UPDATE bloque_ruta SET estado = 'en_curso' WHERE id = %s AND estado = 'disponible'",
            (bloque_ruta_id,),
        )

    return {
        "modulo_id": modulo_id,
        "ya_estaba": evento_id is None,
        "xp_otorgado": 0 if evento_id is None else xp,
    }


def modulos_completos(conn, *, colaborador_id: UUID, bloque_ruta_id: UUID) -> tuple[int, int]:
    """(completos, total) de los módulos del bloque."""
    fila = conn.execute(
        """SELECT count(*) AS total,
                  count(*) FILTER (WHERE e.id IS NOT NULL) AS completos
             FROM bloque_ruta br
             JOIN modulo m ON m.bloque_contenido_id = br.bloque_contenido_id
             LEFT JOIN evento_gamificacion e
                    ON e.origen_id = m.id AND e.origen_tipo = 'modulo'
                   AND e.colaborador_id = %s
            WHERE br.id = %s""",
        (colaborador_id, bloque_ruta_id),
    ).fetchone()
    return int(fila[1]), int(fila[0])


def abrir_siguiente_bloque(conn, *, bloque_ruta_id: UUID) -> UUID | None:
    """
    Al completarse un bloque, se habilita el siguiente de la ruta.

    Sin esto la ruta queda con un solo bloque abierto para siempre y el mapa no
    avanza nunca. Se llama desde `cerrar_intento` cuando el intento aprueba.
    """
    fila = conn.execute(
        """SELECT siguiente.id
             FROM bloque_ruta actual
             JOIN bloque_ruta siguiente
               ON siguiente.ruta_id = actual.ruta_id
              AND siguiente.orden = actual.orden + 1
            WHERE actual.id = %s""",
        (bloque_ruta_id,),
    ).fetchone()
    if fila is None:
        return None            # era el último bloque de la ruta

    conn.execute(
        "UPDATE bloque_ruta SET estado = 'disponible' WHERE id = %s AND estado = 'bloqueado'",
        (fila[0],),
    )
    return fila[0]
