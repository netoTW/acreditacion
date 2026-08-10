"""
Siembra el catálogo institucional y las rutas de los 3 colaboradores del slice.

Es idempotente: correrlo dos veces no duplica nada. Corre en cada arranque, así
que si el seed se rompe, el sistema no levanta — y eso es lo correcto (ADR-001).
"""
from __future__ import annotations

from generador import generar_todo, integrar

from .datos import (
    CARGOS, COLABORADORES, COMITES_FIJOS, DIMENSIONES, HITOS, HITOS_POR_POSICION,
    MATRIZ, UNIDADES,
)


def sembrar(conn) -> dict:
    ids = {}

    # ---------------------------------------------------------- dimensiones
    dim = {}
    for codigo, nombre, obligatoria, orden in DIMENSIONES:
        dim[codigo] = conn.execute(
            """INSERT INTO dimension (codigo, nombre_oficial, obligatoria, orden)
               VALUES (%s,%s,%s,%s)
               ON CONFLICT (codigo) DO UPDATE SET nombre_oficial = EXCLUDED.nombre_oficial
               RETURNING id""",
            (codigo, nombre, obligatoria, orden),
        ).fetchone()[0]

    # ----------------------------------------------------------------- hitos
    hito = {}
    for codigo, ruta, anio, periodo, titulo, ini, fin, orden in HITOS:
        hito[codigo] = conn.execute(
            """INSERT INTO hito (codigo, ruta, anio, periodo_texto, titulo,
                                 fecha_inicio, fecha_fin, orden)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (codigo) DO UPDATE SET titulo = EXCLUDED.titulo
               RETURNING id""",
            (codigo, ruta, anio, periodo, titulo, ini, fin, orden),
        ).fetchone()[0]

    # -------------------------------------------------------------- unidades
    unidad = {}
    for tipo, nombre in UNIDADES:
        unidad[nombre] = conn.execute(
            """INSERT INTO unidad (tipo, nombre) VALUES (%s,%s)
               ON CONFLICT (nombre) DO UPDATE SET tipo = EXCLUDED.tipo RETURNING id""",
            (tipo, nombre),
        ).fetchone()[0]

    # --------------------------------------------------------------- comités
    comite = {}
    for tipo, nombre in COMITES_FIJOS:
        comite[nombre] = conn.execute(
            """INSERT INTO comite (tipo, nombre) VALUES (%s,%s)
               ON CONFLICT (nombre) DO UPDATE SET tipo = EXCLUDED.tipo RETURNING id""",
            (tipo, nombre),
        ).fetchone()[0]

    for codigo, nombre_dim, _o, _n in DIMENSIONES:
        nombre = f"Comité de Autoevaluación · {nombre_dim}"
        comite[nombre] = conn.execute(
            """INSERT INTO comite (tipo, nombre, dimension_id) VALUES ('por_dimension',%s,%s)
               ON CONFLICT (nombre) DO UPDATE SET dimension_id = EXCLUDED.dimension_id
               RETURNING id""",
            (nombre, dim[codigo]),
        ).fetchone()[0]

    for tipo, nombre_unidad in UNIDADES:
        if tipo in ("sede", "escuela"):
            etiqueta = "Comité de Sede" if tipo == "sede" else "Comité de Escuela"
            nombre = f"{etiqueta} · {nombre_unidad}"
            comite[nombre] = conn.execute(
                """INSERT INTO comite (tipo, nombre, unidad_id) VALUES (%s,%s,%s)
                   ON CONFLICT (nombre) DO UPDATE SET unidad_id = EXCLUDED.unidad_id
                   RETURNING id""",
                (tipo, nombre, unidad[nombre_unidad]),
            ).fetchone()[0]

    # ---------------------------------------------------------------- cargos
    cargo = {}
    for codigo, nombre, descripcion in CARGOS:
        cargo[codigo] = conn.execute(
            """INSERT INTO cargo (codigo, nombre, descripcion) VALUES (%s,%s,%s)
               ON CONFLICT (codigo) DO UPDATE SET nombre = EXCLUDED.nombre,
                                                 descripcion = EXCLUDED.descripcion
               RETURNING id""",
            (codigo, nombre, descripcion),
        ).fetchone()[0]

    # ------------------------------------------------------------- contenido
    # Las 15 unidades (5 dimensiones × 3 niveles, ADR-003) las produce el Generador
    # y solo entran si pasan el Validador. Los cargos que exigen el mismo par
    # comparten exactamente este contenido.
    resumen = integrar(conn, generar_todo())
    if resumen["rechazados"]:
        detalle = "; ".join(
            f"{r['bloque']}: {r['errores'][0]}" for r in resumen["rechazados"]
        )
        # Si el contenido no valida, el sistema no levanta. Es lo correcto: mejor no
        # arrancar que arrancar con un banco que se puede aprobar sin saber la materia.
        raise RuntimeError(f"contenido rechazado por el validador → {detalle}")

    # ----------------------------------------------------------- LA MATRIZ
    for codigo_cargo, exigencias in MATRIZ.items():
        # La ruta se ordena por exigencia descendente: primero donde más se le pide.
        orden_dims = sorted(
            exigencias.items(),
            key=lambda kv: (-kv[1], [d[0] for d in DIMENSIONES].index(kv[0])),
        )
        for posicion, (codigo_dim, nivel) in enumerate(orden_dims, start=1):
            conn.execute(
                """INSERT INTO exigencia_cargo_dimension
                       (cargo_id, dimension_id, nivel_estandar, orden_en_ruta, hito_id)
                   VALUES (%s,%s,%s,%s,%s)
                   ON CONFLICT (cargo_id, dimension_id) DO UPDATE
                     SET nivel_estandar = EXCLUDED.nivel_estandar,
                         orden_en_ruta  = EXCLUDED.orden_en_ruta,
                         hito_id        = EXCLUDED.hito_id""",
                (cargo[codigo_cargo], dim[codigo_dim], nivel, posicion,
                 hito[HITOS_POR_POSICION[posicion - 1]]),
            )

    # --------------------------------------------- colaboradores y sus rutas
    for email, nombre, codigo_cargo, nombre_unidad, comites in COLABORADORES:
        colaborador_id = conn.execute(
            """INSERT INTO colaborador (email, nombre, cargo_id, unidad_id)
               VALUES (%s,%s,%s,%s)
               ON CONFLICT (email) DO UPDATE SET nombre = EXCLUDED.nombre,
                                                 cargo_id = EXCLUDED.cargo_id,
                                                 unidad_id = EXCLUDED.unidad_id
               RETURNING id""",
            (email, nombre, cargo[codigo_cargo], unidad[nombre_unidad]),
        ).fetchone()[0]

        for nombre_comite in comites:
            conn.execute(
                """INSERT INTO membresia_comite (colaborador_id, comite_id)
                   VALUES (%s,%s) ON CONFLICT DO NOTHING""",
                (colaborador_id, comite[nombre_comite]),
            )

        generar_ruta(conn, colaborador_id=colaborador_id, cargo_id=cargo[codigo_cargo])
        ids[email] = colaborador_id

    return ids


def generar_ruta(conn, *, colaborador_id, cargo_id) -> None:
    """
    Materializa la ruta de un colaborador leyendo la matriz de su cargo.

    Acá es donde el modelo Cargo × Dimensión se vuelve visible: dos cargos
    distintos producen rutas distintas leyendo las mismas 15 unidades de contenido.
    """
    ruta_id = conn.execute(
        """INSERT INTO ruta (colaborador_id, cargo_id) VALUES (%s,%s)
           ON CONFLICT (colaborador_id) DO UPDATE SET cargo_id = EXCLUDED.cargo_id
           RETURNING id""",
        (colaborador_id, cargo_id),
    ).fetchone()[0]

    filas = conn.execute(
        """SELECT ecd.dimension_id, ecd.nivel_estandar, ecd.orden_en_ruta, ecd.hito_id
             FROM exigencia_cargo_dimension ecd
            WHERE ecd.cargo_id = %s
            ORDER BY ecd.orden_en_ruta""",
        (cargo_id,),
    ).fetchall()

    for dimension_id, nivel, orden, hito_id in filas:
        bc = conn.execute(
            "SELECT id FROM bloque_contenido WHERE dimension_id = %s AND nivel_estandar = %s",
            (dimension_id, nivel),
        ).fetchone()[0]
        conn.execute(
            """INSERT INTO bloque_ruta (ruta_id, bloque_contenido_id, orden, hito_id, estado)
               VALUES (%s,%s,%s,%s,%s)
               ON CONFLICT (ruta_id, orden) DO UPDATE
                 SET bloque_contenido_id = EXCLUDED.bloque_contenido_id,
                     hito_id = EXCLUDED.hito_id""",
            (ruta_id, bc, orden, hito_id, "disponible" if orden == 1 else "bloqueado"),
        )
