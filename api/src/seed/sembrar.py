"""
Siembra el catálogo institucional y las rutas de los 3 colaboradores del slice.

Es idempotente: correrlo dos veces no duplica nada. Corre en cada arranque, así
que si el seed se rompe, el sistema no levanta — y eso es lo correcto (ADR-001).
"""
from __future__ import annotations

from generador import generar_todo, integrar

from .datos import (
    CARGOS, COLABORADORES, COMITES_FIJOS, DIMENSIONES, DISTRIBUCION, HITOS,
    HITOS_POR_POSICION, UMBRAL_CRITICO, UNIDADES, matriz_de,
)


def _retirar_roles_obsoletos(conn) -> list[str]:
    """
    Saca de la base los cargos de la taxonomía anterior.

    Solo retira los que no tienen a nadie encima: un colaborador con historial no
    se borra —sus eventos e insignias son evidencia y la base prohíbe borrarlos—.
    Si queda alguno, se informa y se sigue; la instrucción para el director es
    levantar con volumen nuevo.
    """
    vigentes = [c[0] for c in CARGOS]
    obsoletos = [
        r[0] for r in conn.execute(
            "SELECT codigo FROM cargo WHERE codigo <> ALL(%s)", (vigentes,)
        ).fetchall()
    ]
    if not obsoletos:
        return []

    conn.execute(
        """DELETE FROM exigencia_cargo_dimension
            WHERE cargo_id IN (SELECT id FROM cargo WHERE codigo = ANY(%s))""",
        (obsoletos,),
    )
    conn.execute(
        """DELETE FROM cargo
            WHERE codigo = ANY(%s)
              AND id NOT IN (SELECT cargo_id FROM colaborador)
              AND id NOT IN (SELECT cargo_id FROM ruta)""",
        (obsoletos,),
    )
    return [
        r[0] for r in conn.execute(
            "SELECT codigo FROM cargo WHERE codigo <> ALL(%s)", (vigentes,)
        ).fetchall()
    ]


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

    quedaron = _retirar_roles_obsoletos(conn)
    if quedaron:
        print(
            "  aviso · quedan cargos de la taxonomía anterior con gente encima: "
            f"{', '.join(quedaron)}. Para verlos desaparecer, levanta con volumen "
            "nuevo (docker compose down -v).",
            flush=True,
        )

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
    # El único dato escrito a mano es el % del Excel. El nivel de exigencia y la
    # criticidad se DERIVAN de él (`matriz_de`), igual que el escalón se deriva
    # del XP: lo derivable no se transcribe, para que no se desincronice.
    for codigo_rol in DISTRIBUCION:
        matriz = matriz_de(codigo_rol)
        # La ruta se ordena por peso descendente: primero donde más impacta el rol.
        orden_dims = sorted(
            matriz.items(),
            key=lambda kv: (-kv[1]["pct"], [d[0] for d in DIMENSIONES].index(kv[0])),
        )
        # Las 5 dimensiones del rol entran en UNA sentencia, no de a una. El
        # candado que verifica que la distribución sume 1 es diferido, y en
        # autocommit "diferido" significa "al terminar la sentencia": fila por
        # fila, la primera ya fallaría con una suma de 0,30 que todavía no está
        # completa. La matriz de un rol es un todo y se escribe como un todo.
        plantilla, valores = [], []
        for posicion, (codigo_dim, e) in enumerate(orden_dims, start=1):
            plantilla.append("(%s,%s,%s,%s,%s,%s,%s)")
            valores += [cargo[codigo_rol], dim[codigo_dim], e["nivel"], posicion,
                        hito[HITOS_POR_POSICION[posicion - 1]], e["pct"], e["critica"]]

        conn.execute(
            """INSERT INTO exigencia_cargo_dimension
                   (cargo_id, dimension_id, nivel_estandar, orden_en_ruta, hito_id,
                    distribucion_pct, es_critica)
               VALUES """ + ",".join(plantilla) + """
               ON CONFLICT (cargo_id, dimension_id) DO UPDATE
                 SET nivel_estandar   = EXCLUDED.nivel_estandar,
                     orden_en_ruta    = EXCLUDED.orden_en_ruta,
                     hito_id          = EXCLUDED.hito_id,
                     distribucion_pct = EXCLUDED.distribucion_pct,
                     es_critica       = EXCLUDED.es_critica""",
            valores,
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
        """SELECT ecd.dimension_id, ecd.nivel_estandar, ecd.orden_en_ruta, ecd.hito_id,
                  ecd.distribucion_pct, ecd.es_critica
             FROM exigencia_cargo_dimension ecd
            WHERE ecd.cargo_id = %s
            ORDER BY ecd.orden_en_ruta""",
        (cargo_id,),
    ).fetchall()

    for dimension_id, nivel, orden, hito_id, pct, critica in filas:
        bc = conn.execute(
            "SELECT id FROM bloque_contenido WHERE dimension_id = %s AND nivel_estandar = %s",
            (dimension_id, nivel),
        ).fetchone()[0]
        # El umbral reforzado viaja con la ruta, no con el contenido: el mismo
        # bloque es crítico para un rol y estándar para otro.
        umbral = UMBRAL_CRITICO if critica else None
        conn.execute(
            """INSERT INTO bloque_ruta (ruta_id, bloque_contenido_id, orden, hito_id, estado,
                                        es_critica, peso_ranking, umbral_aprobacion)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (ruta_id, orden) DO UPDATE
                 SET bloque_contenido_id = EXCLUDED.bloque_contenido_id,
                     hito_id             = EXCLUDED.hito_id,
                     es_critica          = EXCLUDED.es_critica,
                     peso_ranking        = EXCLUDED.peso_ranking,
                     umbral_aprobacion   = EXCLUDED.umbral_aprobacion""",
            (ruta_id, bc, orden, hito_id, "disponible" if orden == 1 else "bloqueado",
             critica, pct, umbral),
        )
