"""
Juego de D2 Docencia — «El caso del estudiante que se pierde».

No se ordena ni se clasifica: se **lee una cohorte y se señala dónde se rompe**.

Cada caso pide dos cosas distintas, y por eso se cobran por separado:

1. **El tramo.** Cuántos estudiantes quedan en cada etapa, y cuánto se conservaría
   normalmente en cada paso. El quiebre es el que más cae bajo SU referencia, no
   el que pierde más gente — perder el 35% entre egreso y titulación oportuna es
   lo normal del sistema; perderlo entre primero y segundo año es una hemorragia.
   Esa distinción es todo el juego.
2. **El indicador.** Cuatro indicadores, los cuatro desviados. El correcto no es
   el más desviado: es el que **ocurre en la etapa donde se rompió**. Encontrar el
   quiebre es leer datos; explicarlo es entender el proceso formativo.

El servidor nunca manda `tramo_quiebre` ni `indicador_correcto` antes de que la
persona responda. Como en el resto del sistema, lo que corrige no viaja.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from .eventos import registrar_evento

CASOS_POR_PARTIDA = 3
PUNTOS_TRAMO = 45
PUNTOS_INDICADOR = 45
BONO_LECTURA_LIMPIA = 90

CLAVE = "cohorte"


@dataclass(frozen=True)
class ResultadoCohorte:
    total_casos: int
    tramos_correctos: int
    indicadores_correctos: int
    lectura_limpia: bool
    puntos: int
    xp_otorgado: int
    ya_jugado_hoy: bool
    revelacion: list[dict]


def _dimension_del_bloque(conn, colaborador_id: UUID, bloque_ruta_id: UUID) -> str:
    fila = conn.execute(
        """
        SELECT d.codigo
          FROM bloque_ruta br
          JOIN ruta r              ON r.id  = br.ruta_id
          JOIN bloque_contenido bc ON bc.id = br.bloque_contenido_id
          JOIN dimension d         ON d.id  = bc.dimension_id
         WHERE br.id = %s AND r.colaborador_id = %s
        """,
        (bloque_ruta_id, colaborador_id),
    ).fetchone()
    if fila is None:
        raise LookupError("ese bloque no está en tu ruta")
    return fila[0]


def repartir(conn, *, colaborador_id: UUID, bloque_ruta_id: UUID) -> dict:
    """Tres casos al azar, **sin el tramo de quiebre ni el indicador correcto**."""
    from .juegos import exigir
    exigir(_dimension_del_bloque(conn, colaborador_id, bloque_ruta_id), CLAVE)

    casos = conn.execute(
        """SELECT id, codigo, titulo, contexto, etapas, tramos, indicadores
             FROM caso_cohorte ORDER BY random() LIMIT %s""",
        (CASOS_POR_PARTIDA,),
    ).fetchall()
    if not casos:
        raise LookupError("todavía no hay casos de cohorte cargados")

    return {
        "juego": CLAVE,
        "casos": [
            {
                "caso_id": c[0], "codigo": c[1], "titulo": c[2], "contexto": c[3],
                "etapas": c[4], "tramos": c[5], "indicadores": c[6],
            }
            for c in casos
        ],
    }


def cerrar_cohorte(conn, *, colaborador_id: UUID, bloque_ruta_id: UUID,
                   respuestas: list[dict]) -> ResultadoCohorte:
    """Corrige los tres casos en el servidor y paga XP lúdico."""
    from .juegos import exigir
    exigir(_dimension_del_bloque(conn, colaborador_id, bloque_ruta_id), CLAVE)

    ids = [str(r["caso_id"]) for r in respuestas]
    if not ids:
        raise ValueError("la partida llegó vacía")
    if len(set(ids)) != len(ids):
        raise ValueError("la partida llegó con casos repetidos")

    verdad = {
        str(f[0]): {
            "codigo": f[1], "titulo": f[2], "tramo_quiebre": f[3],
            "explicacion_quiebre": f[4], "indicador_correcto": f[5],
            "explicacion_indicador": f[6], "tramos": f[7], "indicadores": f[8],
        }
        for f in conn.execute(
            """SELECT id, codigo, titulo, tramo_quiebre, explicacion_quiebre,
                      indicador_correcto, explicacion_indicador, tramos, indicadores
                 FROM caso_cohorte WHERE id = ANY(%s::uuid[])""",
            (ids,),
        ).fetchall()
    }
    if len(verdad) != len(ids):
        raise LookupError("la partida cita casos que no existen")

    tramos_ok = indicadores_ok = 0
    revelacion = []

    for r in respuestas:
        real = verdad[str(r["caso_id"])]
        acerto_tramo = r.get("tramo") == real["tramo_quiebre"]
        acerto_indicador = r.get("indicador") == real["indicador_correcto"]
        tramos_ok += acerto_tramo
        indicadores_ok += acerto_indicador

        nombre_indicador = next(
            (i["nombre"] for i in real["indicadores"]
             if i["clave"] == real["indicador_correcto"]),
            real["indicador_correcto"],
        )
        tramo = real["tramos"][real["tramo_quiebre"]]

        revelacion.append({
            "caso_id": str(r["caso_id"]),
            "codigo": real["codigo"],
            "titulo": real["titulo"],
            "acerto_tramo": acerto_tramo,
            "acerto_indicador": acerto_indicador,
            "tramo_correcto": real["tramo_quiebre"],
            "tramo_nombre": f"{tramo['desde']} → {tramo['hasta']}",
            "explicacion_quiebre": real["explicacion_quiebre"],
            "indicador_correcto": real["indicador_correcto"],
            "indicador_nombre": nombre_indicador,
            "explicacion_indicador": real["explicacion_indicador"],
        })

    total = len(revelacion)
    limpia = total > 0 and tramos_ok == total and indicadores_ok == total
    puntos = (tramos_ok * PUNTOS_TRAMO + indicadores_ok * PUNTOS_INDICADOR
              + (BONO_LECTURA_LIMPIA if limpia else 0))

    evento = registrar_evento(
        conn,
        colaborador_id=colaborador_id,
        tipo="cohorte_diagnosticada",
        origen_tipo="juego",              # obliga a que el XP sea lúdico (001)
        origen_id=bloque_ruta_id,
        xp=puntos,
        clase_xp="ludico",
        clave_idempotencia=f"cohorte:{colaborador_id}:{bloque_ruta_id}:{date.today().isoformat()}",
    )

    return ResultadoCohorte(
        total_casos=total,
        tramos_correctos=tramos_ok,
        indicadores_correctos=indicadores_ok,
        lectura_limpia=limpia,
        puntos=puntos,
        xp_otorgado=puntos if evento else 0,
        ya_jugado_hoy=evento is None,
        revelacion=revelacion,
    )
