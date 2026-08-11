"""
Juego de D3 Aseguramiento — «Línea de tiempo del proceso».

No se responde nada: se **acomoda una secuencia**. Seis hitos del proceso real de
AIEP, desordenados, y hay que dejarlos en el orden en que ocurren.

Tres decisiones que hacen que esto sea un juego y no una pregunta larga:

1. **Se reparten 6 de los 13.** El proceso tiene una sola secuencia auténtica —esa
   fue la objeción honesta al diseñar B1—, así que la rejugabilidad no puede venir
   de cambiar el orden: viene de cambiar QUÉ tramo te toca ordenar. Con 6 de 13 hay
   1.716 tableros distintos sobre la misma verdad.
2. **Se puntúa por PARES, no por casillas.** Si un hito queda una posición corrida,
   con puntaje por casilla se pierde todo aunque hayas entendido la secuencia
   completa. Contando pares en orden correcto, el puntaje mide lo que de verdad
   importa: si sabes qué va antes que qué.
3. **Durante el juego solo se ve el título.** El período y el año llegan recién en la
   revelación; si viajaran antes, ordenar sería leer fechas.

El contenido no cuesta nada: los 13 hitos ya están en la base con su `orden`, desde
la ruta oficial de AIEP.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from .eventos import registrar_evento

HITOS_POR_LINEA = 6
PUNTOS_POR_PAR = 18
BONO_LINEA_PERFECTA = 90

CLAVE = "linea_tiempo"


@dataclass(frozen=True)
class ResultadoLinea:
    total: int
    en_su_lugar: int
    pares_correctos: int
    pares_totales: int
    linea_perfecta: bool
    puntos: int
    xp_otorgado: int
    ya_jugado_hoy: bool
    revelacion: list[dict]


def repartir(conn, *, colaborador_id: UUID, bloque_ruta_id: UUID) -> dict:
    """
    Arma un tablero: 6 hitos barajados, **sin su período ni su año**.

    El bloque tiene que ser de la ruta propia (I-10 también rige para los juegos).
    """
    fila = conn.execute(
        """
        SELECT d.codigo, bc.nivel_estandar
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

    from .juegos import exigir
    exigir(fila[0], CLAVE)

    hitos = conn.execute(
        """
        SELECT id, codigo, titulo FROM hito ORDER BY random() LIMIT %s
        """,
        (HITOS_POR_LINEA,),
    ).fetchall()
    if len(hitos) < 2:
        raise LookupError("no hay hitos suficientes para armar la línea")

    return {
        "juego": CLAVE,
        "dimension": fila[0],
        "cartas": [{"hito_id": h[0], "codigo": h[1], "titulo": h[2]} for h in hitos],
    }


def cerrar_linea(conn, *, colaborador_id: UUID, bloque_ruta_id: UUID,
                 orden_propuesto: list[str]) -> ResultadoLinea:
    """
    Corrige la secuencia. El cliente manda **en qué orden dejó las cartas**; cuál era
    el orden real y cuántos puntos vale sigue siendo del servidor.
    """
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

    from .juegos import exigir
    exigir(fila[0], CLAVE)

    if len(set(orden_propuesto)) != len(orden_propuesto):
        raise ValueError("la línea llegó con hitos repetidos")
    if not 2 <= len(orden_propuesto) <= HITOS_POR_LINEA:
        raise ValueError(f"la línea lleva entre 2 y {HITOS_POR_LINEA} hitos")

    # Las claves van como TEXTO: psycopg devuelve UUID y el cliente manda strings.
    # Mezclarlos daba un KeyError que el `except LookupError` del endpoint disfrazaba
    # de 404 —KeyError hereda de LookupError—, o sea un bug con cara de dato ajeno.
    verdad = {
        str(f[0]): {"orden": f[1], "codigo": f[2], "titulo": f[3], "ruta": f[4],
                    "anio": f[5], "periodo_texto": f[6]}
        for f in conn.execute(
            """SELECT id, orden, codigo, titulo, ruta, anio, periodo_texto
                 FROM hito WHERE id = ANY(%s::uuid[])""",
            (orden_propuesto,),
        ).fetchall()
    }
    if len(verdad) != len(orden_propuesto):
        raise LookupError("la línea cita hitos que no existen")

    # La secuencia real de los hitos que tocaron, para poder decir en qué posición
    # iba cada uno DENTRO de este tablero y no dentro de los 13.
    real = sorted(orden_propuesto, key=lambda h: verdad[h]["orden"])
    posicion_real = {h: i for i, h in enumerate(real)}

    # Puntaje por pares: cada par que quedó en el orden correcto entre sí.
    pares_correctos = 0
    n = len(orden_propuesto)
    for i in range(n):
        for j in range(i + 1, n):
            if posicion_real[orden_propuesto[i]] < posicion_real[orden_propuesto[j]]:
                pares_correctos += 1
    pares_totales = n * (n - 1) // 2

    en_su_lugar = sum(1 for i, h in enumerate(orden_propuesto) if posicion_real[h] == i)
    perfecta = pares_correctos == pares_totales
    puntos = pares_correctos * PUNTOS_POR_PAR + (BONO_LINEA_PERFECTA if perfecta else 0)

    revelacion = [
        {
            "hito_id": h,
            "codigo": verdad[h]["codigo"],
            "titulo": verdad[h]["titulo"],
            "ruta": verdad[h]["ruta"],
            "anio": verdad[h]["anio"],
            "periodo_texto": verdad[h]["periodo_texto"],
            "puesto_en": orden_propuesto.index(h) + 1,
            "posicion_real": i + 1,
            "acerto": posicion_real[h] == orden_propuesto.index(h),
        }
        for i, h in enumerate(real)
    ]

    evento = registrar_evento(
        conn,
        colaborador_id=colaborador_id,
        tipo="linea_de_tiempo_jugada",
        origen_tipo="juego",               # obliga a que el XP sea lúdico (001)
        origen_id=bloque_ruta_id,          # el juego es del bloque: cupo diario propio
        xp=puntos,
        clase_xp="ludico",
        clave_idempotencia=f"linea:{colaborador_id}:{bloque_ruta_id}:{date.today().isoformat()}",
    )

    return ResultadoLinea(
        total=n,
        en_su_lugar=en_su_lugar,
        pares_correctos=pares_correctos,
        pares_totales=pares_totales,
        linea_perfecta=perfecta,
        puntos=puntos,
        xp_otorgado=puntos if evento else 0,
        ya_jugado_hoy=evento is None,
        revelacion=revelacion,
    )
