"""
Juego de D5 Investigación — «El cuadrante de la producción».

La mecánica que faltaba: un **juicio de dos ejes**. Las otras cuatro piden una
sola decisión por pieza —ordenarla, señalarla, conectarla, descartarla—. Acá cada
producción exige dos preguntas independientes que se cruzan:

- **¿Es investigación, creación o innovación?**
- **¿La institución puede reclamarla?**

Se pueden acertar por separado, y el puntaje **se cobra por eje**: decir que un
artículo indexado con la afiliación de otra universidad *es* investigación es
correcto aunque uno se equivoque en de quién es. Ese medio acierto es información
real sobre lo que la persona entendió, y perderlo sería fingir que el juicio es
uno solo.

El casillero que cuenta para el informe es uno de los cuatro. Los otros tres son
donde el listado se infla sin querer: se suma lo propio que no es investigación,
y la investigación que es de otro.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from .eventos import registrar_evento

PIEZAS_POR_TABLERO = 6
PUNTOS_POR_EJE = 25
BONO_CUADRANTE_LIMPIO = 60

CLAVE = "produccion"


@dataclass(frozen=True)
class ResultadoCuadrante:
    total: int
    ejes_correctos: int
    ejes_totales: int
    piezas_perfectas: int
    cuadrante_limpio: bool
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
    Seis producciones, **sin decir en qué casillero va cada una**.

    Se toma **una de cada cuadrante** antes de completar al azar. Un tablero donde
    faltara un cuadrante enseñaría lo contrario de lo que el juego busca: que hay
    casilleros que nunca se usan.
    """
    from .juegos import exigir
    exigir(_dimension_del_bloque(conn, colaborador_id, bloque_ruta_id), CLAVE)

    una_por_cuadrante = conn.execute(
        """
        SELECT DISTINCT ON (es_ici, es_adscrita)
               id, codigo, titulo, tipo, detalle
          FROM produccion_ici
         ORDER BY es_ici, es_adscrita, random()
        """
    ).fetchall()
    if len(una_por_cuadrante) < 4:
        raise LookupError("el catálogo no cubre los cuatro cuadrantes")

    resto = conn.execute(
        """SELECT id, codigo, titulo, tipo, detalle FROM produccion_ici
            WHERE id <> ALL(%s::uuid[]) ORDER BY random() LIMIT %s""",
        ([f[0] for f in una_por_cuadrante], PIEZAS_POR_TABLERO - 4),
    ).fetchall()

    import random as _r
    piezas = list(una_por_cuadrante) + list(resto)
    _r.shuffle(piezas)

    lineas = conn.execute(
        "SELECT clave, nombre, descripcion FROM linea_ici ORDER BY nombre"
    ).fetchall()

    return {
        "juego": CLAVE,
        # Las líneas declaradas van como referencia del tablero: ayudan a decidir,
        # pero no son un tercer eje ni se responden.
        "lineas": [{"clave": l[0], "nombre": l[1], "descripcion": l[2]} for l in lineas],
        "piezas": [
            {"pieza_id": p[0], "codigo": p[1], "titulo": p[2], "tipo": p[3], "detalle": p[4]}
            for p in piezas
        ],
    }


def cerrar_cuadrante(conn, *, colaborador_id: UUID, bloque_ruta_id: UUID,
                     ubicaciones: list[dict]) -> ResultadoCuadrante:
    """Corrige los dos ejes de cada pieza en el servidor."""
    from .juegos import exigir
    exigir(_dimension_del_bloque(conn, colaborador_id, bloque_ruta_id), CLAVE)

    ids = [str(u["pieza_id"]) for u in ubicaciones]
    if not ids:
        raise ValueError("el tablero llegó vacío")
    if len(set(ids)) != len(ids):
        raise ValueError("el tablero llegó con piezas repetidas")

    verdad = {
        str(f[0]): {"titulo": f[1], "tipo": f[2], "es_ici": f[3], "es_adscrita": f[4],
                    "razon_ici": f[5], "razon_adscripcion": f[6], "linea": f[7]}
        for f in conn.execute(
            """SELECT p.id, p.titulo, p.tipo, p.es_ici, p.es_adscrita,
                      p.razon_ici, p.razon_adscripcion, l.nombre
                 FROM produccion_ici p
                 LEFT JOIN linea_ici l ON l.clave = p.linea_clave
                WHERE p.id = ANY(%s::uuid[])""",
            (ids,),
        ).fetchall()
    }
    if len(verdad) != len(ids):
        raise LookupError("el tablero cita piezas que no existen")

    ejes_ok = perfectas = 0
    revelacion = []

    for u in ubicaciones:
        real = verdad[str(u["pieza_id"])]
        acerto_ici = bool(u.get("es_ici")) == real["es_ici"]
        acerto_adscripcion = bool(u.get("es_adscrita")) == real["es_adscrita"]
        ejes_ok += acerto_ici + acerto_adscripcion
        perfectas += acerto_ici and acerto_adscripcion

        revelacion.append({
            "pieza_id": str(u["pieza_id"]),
            "titulo": real["titulo"],
            "tipo": real["tipo"],
            "acerto_ici": acerto_ici,
            "acerto_adscripcion": acerto_adscripcion,
            "es_ici": real["es_ici"],
            "es_adscrita": real["es_adscrita"],
            "cuenta_para_el_informe": real["es_ici"] and real["es_adscrita"],
            "linea": real["linea"],
            "razon_ici": real["razon_ici"],
            "razon_adscripcion": real["razon_adscripcion"],
        })

    total = len(revelacion)
    ejes_totales = total * 2
    limpio = ejes_ok == ejes_totales
    puntos = ejes_ok * PUNTOS_POR_EJE + (BONO_CUADRANTE_LIMPIO if limpio else 0)

    evento = registrar_evento(
        conn,
        colaborador_id=colaborador_id,
        tipo="cuadrante_de_produccion_resuelto",
        origen_tipo="juego",             # obliga a que el XP sea lúdico (001)
        origen_id=bloque_ruta_id,
        xp=puntos,
        clase_xp="ludico",
        clave_idempotencia=f"cuadrante:{colaborador_id}:{bloque_ruta_id}:{date.today().isoformat()}",
    )

    return ResultadoCuadrante(
        total=total,
        ejes_correctos=ejes_ok,
        ejes_totales=ejes_totales,
        piezas_perfectas=perfectas,
        cuadrante_limpio=limpio,
        puntos=puntos,
        xp_otorgado=puntos if evento else 0,
        ya_jugado_hoy=evento is None,
        revelacion=revelacion,
    )
