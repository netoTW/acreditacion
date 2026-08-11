"""
Desafío aplicado — la exigencia extra de la dimensión crítica.

No pregunta qué es algo: sienta a la persona en una silla («integras el comité de
autoevaluación…»), le da una situación con datos y le pide **decidir** entre
opciones definidas. Es aplicar, no recordar.

Tres cosas que lo mantienen honesto:

1. **Lo corrige el servidor.** El cliente recibe las opciones, nunca la clave. Si
   la pantalla mintiera sobre el resultado, no cambiaría nada de lo que queda
   registrado.
2. **No otorga completitud.** Da XP lúdico y abre la puerta de la evaluación
   reforzada; ni medalla ni XP acreditable. Usa `origen_tipo='juego'`, que el
   CHECK de la migración 001 ya obliga a ser lúdico: la regla vive en la base.
3. **Resolverlo es el requisito, no aprobarlo.** Equivocarse deja pasar a la
   evaluación —donde el 85% sí es un gate de verdad—, pero paga menos XP. Un
   requisito que se puede reprobar sin consecuencia sería teatro; uno que
   bloquea sin gate sería un segundo umbral escondido. Esto es lo que hay en el
   medio: cuesta tiempo y atención, y no regala nada.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from uuid import UUID

from .eventos import registrar_evento

PUNTOS_POR_DECISION = 60
BONO_DESAFIO_PERFECTO = 120


@dataclass(frozen=True)
class ResultadoDesafio:
    total: int
    aciertos: int
    perfecto: bool
    xp_otorgado: int
    ya_resuelto: bool
    revelacion: list[dict]


class NoCritica(Exception):
    """El desafío existe solo donde el rol tiene una dimensión crítica."""


def ver_desafio(conn, *, colaborador_id: UUID, bloque_ruta_id: UUID) -> dict:
    """
    El caso, **sin las respuestas correctas**.

    Se comprueba acá que el bloque sea de la ruta propia y que sea crítico: si el
    desafío se pudiera abrir en cualquier bloque, sería una vía para ver el caso
    de una ruta ajena.
    """
    fila = conn.execute(
        """
        SELECT d.id, d.titulo, d.rol_ficticio, d.situacion, d.datos,
               br.es_critica, dim.nombre_oficial, bc.nivel_estandar
          FROM bloque_ruta br
          JOIN ruta r              ON r.id  = br.ruta_id
          JOIN bloque_contenido bc ON bc.id = br.bloque_contenido_id
          JOIN dimension dim       ON dim.id = bc.dimension_id
          JOIN desafio_aplicado d  ON d.bloque_contenido_id = bc.id
         WHERE br.id = %s AND r.colaborador_id = %s
        """,
        (bloque_ruta_id, colaborador_id),
    ).fetchone()
    if fila is None:
        raise LookupError("no hay desafío para este bloque")

    desafio_id, titulo, rol, situacion, datos, es_critica, dimension, nivel = fila
    if not es_critica:
        raise NoCritica("esta dimensión no es crítica para tu rol")

    decisiones = conn.execute(
        """SELECT id, orden, tipo, enunciado, opciones, grupos
             FROM decision_desafio WHERE desafio_id = %s ORDER BY orden""",
        (desafio_id,),
    ).fetchall()

    resuelto = conn.execute(
        """SELECT aciertos, total FROM resolucion_desafio
            WHERE colaborador_id = %s AND bloque_ruta_id = %s""",
        (colaborador_id, bloque_ruta_id),
    ).fetchone()

    return {
        "desafio_id": desafio_id,
        "titulo": titulo,
        "dimension": dimension,
        "nivel_estandar": nivel,
        "rol_ficticio": rol,
        "situacion": situacion,
        "datos": datos,
        "ya_resuelto": resuelto is not None,
        "aciertos_previos": resuelto[0] if resuelto else None,
        "decisiones": [
            {
                "decision_id": d[0], "orden": d[1], "tipo": d[2],
                "enunciado": d[3], "opciones": d[4], "grupos": d[5],
            }
            for d in decisiones
        ],
    }


def resolver_desafio(conn, *, colaborador_id: UUID, bloque_ruta_id: UUID,
                     respuestas: list[dict]) -> ResultadoDesafio:
    """Corrige en el servidor, registra la resolución y paga XP lúdico."""
    caso = ver_desafio(conn, colaborador_id=colaborador_id, bloque_ruta_id=bloque_ruta_id)
    desafio_id = caso["desafio_id"]

    claves = {
        f[0]: {"tipo": f[1], "correcta": f[2], "explicacion": f[3]}
        for f in conn.execute(
            """SELECT id, tipo, clave_correcta, explicacion
                 FROM decision_desafio WHERE desafio_id = %s""",
            (desafio_id,),
        ).fetchall()
    }

    dadas = {str(r["decision_id"]): r.get("respuesta") for r in respuestas}
    aciertos, revelacion = 0, []

    for d in caso["decisiones"]:
        real = claves.get(d["decision_id"])
        if real is None:
            continue
        dada = dadas.get(str(d["decision_id"]))
        acerto = _acerto(real["tipo"], dada, real["correcta"])
        aciertos += acerto
        revelacion.append({
            "decision_id": d["decision_id"],
            "orden": d["orden"],
            "acerto": acerto,
            "respuesta_dada": dada,
            "clave_correcta": real["correcta"],
            "explicacion": real["explicacion"],
        })

    total = len(revelacion)
    if total == 0:
        raise LookupError("el desafío llegó sin decisiones")

    perfecto = aciertos == total
    puntos = aciertos * PUNTOS_POR_DECISION + (BONO_DESAFIO_PERFECTO if perfecto else 0)

    # La resolución se guarda una sola vez: es la que abre la evaluación reforzada.
    # Volver a mandar el mismo desafío no la reescribe ni vuelve a pagar.
    guardada = conn.execute(
        """INSERT INTO resolucion_desafio (colaborador_id, bloque_ruta_id, desafio_id,
                                           respuestas, aciertos, total)
           VALUES (%s,%s,%s,%s::jsonb,%s,%s)
           ON CONFLICT (colaborador_id, bloque_ruta_id) DO NOTHING
           RETURNING id""",
        (colaborador_id, bloque_ruta_id, desafio_id,
         json.dumps(respuestas, ensure_ascii=False, default=str), aciertos, total),
    ).fetchone()

    evento = None
    if guardada:
        evento = registrar_evento(
            conn,
            colaborador_id=colaborador_id,
            tipo="desafio_aplicado_resuelto",
            origen_tipo="juego",            # obliga a que el XP sea lúdico (001)
            origen_id=desafio_id,
            xp=puntos,
            clase_xp="ludico",
            clave_idempotencia=f"desafio:{colaborador_id}:{bloque_ruta_id}",
        )

    return ResultadoDesafio(
        total=total,
        aciertos=aciertos,
        perfecto=perfecto,
        xp_otorgado=puntos if evento else 0,
        ya_resuelto=guardada is None,
        revelacion=revelacion,
    )


def _acerto(tipo: str, dada, correcta) -> bool:
    """
    Compara según el tipo de decisión.

    Todo o nada por decisión, a propósito: en una selección múltiple, acertar dos
    de tres y marcar además una que no correspondía no es «casi bien» — es haber
    comprometido a la institución con una acción que no sostiene la dimensión.
    """
    if dada is None:
        return False
    if tipo == "eleccion_unica":
        return dada == correcta
    if tipo == "seleccion_multiple":
        return isinstance(dada, list) and set(dada) == set(correcta)
    if tipo == "clasificacion":
        return isinstance(dada, dict) and dada == correcta
    return False
