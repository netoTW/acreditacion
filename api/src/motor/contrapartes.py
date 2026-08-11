"""
Juego de D4 Vinculación — «El mapa de contrapartes».

No se ordena, no se clasifica en bandejas y no se lee un gráfico: se **tienden
vínculos** entre dos catálogos. Actores externos a un lado, acciones
institucionales al otro, y una línea entre los que se sostienen.

Lo que lo separa de clasificar (la Mesa de comité): en la Mesa **toda** carta
tiene bandeja y la partida termina cuando no queda ninguna suelta. Acá hay
actores que **no van a ninguna parte** —un proveedor, una agencia contratada, un
medio que publicó una nota— y dejarlos sin vínculo es la respuesta correcta. El
juego no es repartir: es decidir qué entra al listado y qué no.

Y hay **acciones señuelo**: se reparten más acciones de las que se usan, para que
el tablero no se resuelva por descarte una vez tendidos los primeros vínculos.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from .eventos import registrar_evento

ACTORES_CONTRAPARTE = 4
ACTORES_SIN_VINCULO = 2
ACCIONES_SENUELO = 2

PUNTOS_POR_VINCULO = 50
BONO_MAPA_LIMPIO = 60

CLAVE = "contrapartes"


@dataclass(frozen=True)
class ResultadoMapa:
    total: int
    aciertos: int
    descartes_correctos: int
    descartes_totales: int
    mapa_limpio: bool
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
    """
    Arma un mapa: seis actores y seis acciones, **sin decir cuál va con cuál**.

    Los cuatro actores con contraparte se eligen con **acciones distintas entre
    sí**: dos actores que compartieran acción harían que el tablero tuviera más de
    una lectura razonable y castigarían a quien entendió.
    """
    from .juegos import exigir
    exigir(_dimension_del_bloque(conn, colaborador_id, bloque_ruta_id), CLAVE)

    con_vinculo = conn.execute(
        """
        SELECT DISTINCT ON (accion_clave) id, codigo, nombre, tipo, descripcion, accion_clave
          FROM actor_externo
         WHERE accion_clave IS NOT NULL
         ORDER BY accion_clave, random()
        """
    ).fetchall()
    sin_vinculo = conn.execute(
        """SELECT id, codigo, nombre, tipo, descripcion, accion_clave
             FROM actor_externo WHERE accion_clave IS NULL
            ORDER BY random() LIMIT %s""",
        (ACTORES_SIN_VINCULO,),
    ).fetchall()

    if len(con_vinculo) < ACTORES_CONTRAPARTE or len(sin_vinculo) < ACTORES_SIN_VINCULO:
        raise LookupError("no hay actores suficientes para armar el mapa")

    # `DISTINCT ON` ya garantizó una acción distinta por fila; queda barajar cuáles.
    import random as _r
    con_vinculo = _r.sample(con_vinculo, ACTORES_CONTRAPARTE)

    usadas = {f[5] for f in con_vinculo}
    senuelos = conn.execute(
        """SELECT clave, nombre, descripcion FROM accion_institucional
            WHERE clave <> ALL(%s) ORDER BY random() LIMIT %s""",
        (list(usadas), ACCIONES_SENUELO),
    ).fetchall()

    acciones = conn.execute(
        """SELECT clave, nombre, descripcion FROM accion_institucional
            WHERE clave = ANY(%s) ORDER BY random()""",
        (list(usadas) + [s[0] for s in senuelos],),
    ).fetchall()

    actores = con_vinculo + sin_vinculo
    _r.shuffle(actores)

    return {
        "juego": CLAVE,
        "actores": [
            {"actor_id": a[0], "codigo": a[1], "nombre": a[2], "tipo": a[3],
             "descripcion": a[4]}
            for a in actores
        ],
        "acciones": [
            {"clave": a[0], "nombre": a[1], "descripcion": a[2]} for a in acciones
        ],
    }


def cerrar_mapa(conn, *, colaborador_id: UUID, bloque_ruta_id: UUID,
                vinculos: list[dict]) -> ResultadoMapa:
    """
    Corrige el mapa. El cliente manda **a qué acción ató cada actor**, o `null` si
    lo dejó fuera. Cuál era el vínculo real y cuánto vale lo pone el servidor.
    """
    from .juegos import exigir
    exigir(_dimension_del_bloque(conn, colaborador_id, bloque_ruta_id), CLAVE)

    ids = [str(v["actor_id"]) for v in vinculos]
    if not ids:
        raise ValueError("el mapa llegó vacío")
    if len(set(ids)) != len(ids):
        raise ValueError("el mapa llegó con actores repetidos")

    verdad = {
        str(f[0]): {"nombre": f[1], "accion_clave": f[2], "razon": f[3],
                    "accion_nombre": f[4]}
        for f in conn.execute(
            """SELECT a.id, a.nombre, a.accion_clave, a.razon, ai.nombre
                 FROM actor_externo a
                 LEFT JOIN accion_institucional ai ON ai.clave = a.accion_clave
                WHERE a.id = ANY(%s::uuid[])""",
            (ids,),
        ).fetchall()
    }
    if len(verdad) != len(ids):
        raise LookupError("el mapa cita actores que no existen")

    aciertos = descartes_ok = descartes_totales = 0
    revelacion = []

    for v in vinculos:
        real = verdad[str(v["actor_id"])]
        atado = v.get("accion_clave")
        acerto = atado == real["accion_clave"]
        aciertos += acerto

        # Los descartes se cuentan aparte: distinguir al proveedor del convenio es
        # la parte del juego que de verdad enseña, y conviene poder mirarla sola.
        if real["accion_clave"] is None:
            descartes_totales += 1
            descartes_ok += acerto

        revelacion.append({
            "actor_id": str(v["actor_id"]),
            "nombre": real["nombre"],
            "acerto": acerto,
            "ato_en": atado,
            "accion_correcta": real["accion_clave"],
            "accion_nombre": real["accion_nombre"],
            "es_contraparte": real["accion_clave"] is not None,
            "razon": real["razon"],
        })

    total = len(revelacion)
    limpio = aciertos == total
    puntos = aciertos * PUNTOS_POR_VINCULO + (BONO_MAPA_LIMPIO if limpio else 0)

    evento = registrar_evento(
        conn,
        colaborador_id=colaborador_id,
        tipo="mapa_de_contrapartes_trazado",
        origen_tipo="juego",             # obliga a que el XP sea lúdico (001)
        origen_id=bloque_ruta_id,
        xp=puntos,
        clase_xp="ludico",
        clave_idempotencia=f"mapa:{colaborador_id}:{bloque_ruta_id}:{date.today().isoformat()}",
    )

    return ResultadoMapa(
        total=total,
        aciertos=aciertos,
        descartes_correctos=descartes_ok,
        descartes_totales=descartes_totales,
        mapa_limpio=limpio,
        puntos=puntos,
        xp_otorgado=puntos if evento else 0,
        ya_jugado_hoy=evento is None,
        revelacion=revelacion,
    )
