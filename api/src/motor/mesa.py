"""
B2 «Mesa de comité» — clasificar afirmaciones por dimensión.

No se responde una pregunta: se **acomoda un tablero**. Seis afirmaciones sueltas,
cinco bandejas —una por dimensión— y libertad para moverlas entre bandejas hasta
decidir cerrar. Se juega comparando unas con otras: «si esta es Aseguramiento,
entonces esta otra no puede serlo».

De dónde sale el contenido, y por qué de ahí:

- Las afirmaciones son las **alternativas correctas de los ítems de definición del
  quiz formativo**. Son verdaderas, se entienden solas y vienen ya etiquetadas con
  su dimensión: cero contenido nuevo.
- **Solo quiz formativo, nunca el banco de la evaluación.** La mesa revela a qué
  dimensión pertenece cada afirmación; el banco no sale del servidor con su
  respuesta, ni acá ni en Calibre.
- Solo afirmaciones de **los bloques de la propia ruta**: el aislamiento por cargo
  (I-10) también rige para los juegos.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from .eventos import registrar_evento

CARTAS_POR_MESA = 6
PUNTOS_POR_ACIERTO = 40
BONO_MESA_PERFECTA = 80


@dataclass(frozen=True)
class ResultadoMesa:
    total: int
    aciertos: int
    puntos: int
    mesa_perfecta: bool
    xp_otorgado: int
    ya_jugado_hoy: bool
    revelacion: list[dict]


def repartir(conn, *, colaborador_id: UUID) -> dict:
    """
    Arma una mesa. Devuelve las bandejas y las cartas **sin decir a cuál va cada una**.

    Se busca variedad de dimensiones: primero una afirmación de cada dimensión que el
    colaborador tenga en su ruta, y el resto al azar. Una mesa donde casi todo es de la
    misma dimensión se resuelve por descarte y deja de ser interesante.
    """
    candidatas = conn.execute(
        """
        SELECT q.id, q.alternativas->>q.indice_correcta AS texto, d.codigo, q.enunciado
          FROM item_quiz_formativo q
          JOIN modulo m            ON m.id  = q.modulo_id
          JOIN bloque_contenido bc ON bc.id = m.bloque_contenido_id
          JOIN dimension d         ON d.id  = bc.dimension_id
          JOIN bloque_ruta br      ON br.bloque_contenido_id = bc.id
          JOIN ruta r              ON r.id  = br.ruta_id
         WHERE r.colaborador_id = %s
           AND q.dificultad = 1          -- solo definiciones: se entienden solas
         ORDER BY random()
        """,
        (colaborador_id,),
    ).fetchall()
    if not candidatas:
        raise LookupError("todavía no hay afirmaciones para armar la mesa")

    elegidas, dimensiones_usadas = [], set()
    for fila in candidatas:                       # una de cada dimensión primero
        if fila[2] not in dimensiones_usadas:
            elegidas.append(fila)
            dimensiones_usadas.add(fila[2])
    for fila in candidatas:                       # y se completa al azar
        if len(elegidas) >= CARTAS_POR_MESA:
            break
        if fila not in elegidas:
            elegidas.append(fila)
    elegidas = elegidas[:CARTAS_POR_MESA]

    bandejas = [
        {"codigo": f[0], "nombre": f[1]}
        for f in conn.execute(
            "SELECT codigo, nombre_oficial FROM dimension ORDER BY orden"
        ).fetchall()
    ]

    return {
        "bandejas": bandejas,
        "cartas": [{"item_id": f[0], "texto": f[1]} for f in elegidas],
    }


def cerrar_mesa(conn, *, colaborador_id: UUID, colocaciones: list[dict]) -> ResultadoMesa:
    """
    Corrige el tablero. El cliente manda **dónde puso cada carta**; el resto lo pone
    el servidor: qué era correcto, cuántos puntos y si la mesa quedó perfecta.
    """
    ids = [c["item_id"] for c in colocaciones]
    if not ids:
        raise LookupError("la mesa llegó vacía")

    verdad = {
        f[0]: {"dimension": f[1], "dimension_nombre": f[2], "enunciado": f[3]}
        for f in conn.execute(
            """
            SELECT q.id, d.codigo, d.nombre_oficial, q.enunciado
              FROM item_quiz_formativo q
              JOIN modulo m            ON m.id  = q.modulo_id
              JOIN bloque_contenido bc ON bc.id = m.bloque_contenido_id
              JOIN dimension d         ON d.id  = bc.dimension_id
              JOIN bloque_ruta br      ON br.bloque_contenido_id = bc.id
              JOIN ruta r              ON r.id  = br.ruta_id
             WHERE r.colaborador_id = %s AND q.id = ANY(%s::uuid[])
            """,
            (colaborador_id, ids),
        ).fetchall()
    }

    aciertos = 0
    revelacion = []
    for c in colocaciones:
        real = verdad.get(c["item_id"])
        if real is None:
            continue                      # carta que no es de su ruta: se ignora
        acerto = c["dimension"] == real["dimension"]
        aciertos += acerto
        revelacion.append({
            "item_id": c["item_id"],
            "acerto": acerto,
            "puesta_en": c["dimension"],
            "dimension_correcta": real["dimension"],
            "dimension_nombre": real["dimension_nombre"],
            "enunciado": real["enunciado"],
        })

    total = len(revelacion)
    perfecta = total > 0 and aciertos == total
    puntos = aciertos * PUNTOS_POR_ACIERTO + (BONO_MESA_PERFECTA if perfecta else 0)

    # El origen es la ruta: la mesa es un juego del recorrido completo, no de un
    # módulo, así que tiene su propio cupo diario.
    ruta_id = conn.execute(
        "SELECT id FROM ruta WHERE colaborador_id = %s", (colaborador_id,)
    ).fetchone()[0]

    evento = registrar_evento(
        conn,
        colaborador_id=colaborador_id,
        tipo="mesa_de_comite_jugada",
        origen_tipo="juego",
        origen_id=ruta_id,
        xp=puntos,
        clase_xp="ludico",
        clave_idempotencia=f"mesa:{colaborador_id}:{date.today().isoformat()}",
    )

    return ResultadoMesa(
        total=total,
        aciertos=aciertos,
        puntos=puntos,
        mesa_perfecta=perfecta,
        xp_otorgado=puntos if evento else 0,
        ya_jugado_hoy=evento is None,
        revelacion=revelacion,
    )
