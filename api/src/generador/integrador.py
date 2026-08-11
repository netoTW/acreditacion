"""
Integrador: contenido validado → base de datos.

Dos reglas que no se negocian:

1. **Lo que no pasa el validador no entra.** Ni siquiera parcialmente
   (CLAUDE.md §9.3).
2. **No se reemplaza contenido que ya tiene intentos rindiéndose encima.** Cambiar
   los ítems bajo un intento en curso rompería la trazabilidad entre la insignia y
   la evaluación que la respalda, que es justo lo que ADR-005 protege.
"""
from __future__ import annotations

import hashlib
import json

from .validador import normalizar, validar


def _hash(enunciado: str) -> str:
    return hashlib.sha1(normalizar(enunciado).encode("utf-8")).hexdigest()


def integrar(conn, bloques: list[dict]) -> dict:
    """Integra los bloques válidos. Devuelve un resumen de lo hecho y lo omitido."""
    resumen = {"integrados": [], "rechazados": [], "omitidos": [], "items": 0, "modulos": 0}

    for bloque in bloques:
        r = validar(bloque)
        etiqueta = f"{bloque.get('dimension')} N{bloque.get('nivel_estandar')}"

        if not r.valido:
            resumen["rechazados"].append({"bloque": etiqueta, "errores": r.errores})
            continue

        dimension_id = conn.execute(
            "SELECT id FROM dimension WHERE codigo = %s", (bloque["dimension"],)
        ).fetchone()
        if dimension_id is None:
            resumen["rechazados"].append(
                {"bloque": etiqueta, "errores": ["la dimensión no existe en el catálogo"]}
            )
            continue
        dimension_id = dimension_id[0]

        bc_id = conn.execute(
            """INSERT INTO bloque_contenido
                   (dimension_id, nivel_estandar, titulo, es_contenido_prueba, estado)
               VALUES (%s, %s, %s, %s, 'validado')
               ON CONFLICT (dimension_id, nivel_estandar)
               DO UPDATE SET titulo = EXCLUDED.titulo, estado = 'validado'
               RETURNING id""",
            (dimension_id, bloque["nivel_estandar"], bloque["titulo"],
             bloque["es_contenido_prueba"]),
        ).fetchone()[0]

        # Regla 2: si hay intentos apoyados en este bloque, no se toca el contenido.
        con_intentos = conn.execute(
            """SELECT count(*) FROM intento_evaluacion ie
                 JOIN bloque_ruta br ON br.id = ie.bloque_ruta_id
                WHERE br.bloque_contenido_id = %s""",
            (bc_id,),
        ).fetchone()[0]
        if con_intentos:
            resumen["omitidos"].append(
                {"bloque": etiqueta,
                 "razon": f"tiene {con_intentos} intento(s): no se reemplaza contenido "
                          "bajo evaluaciones ya rendidas"}
            )
            continue

        n_mod, n_items = _reemplazar_contenido(conn, bc_id, bloque)
        resumen["integrados"].append(etiqueta)
        resumen["modulos"] += n_mod
        resumen["items"] += n_items

    return resumen


def _reemplazar_contenido(conn, bc_id, bloque: dict) -> tuple[int, int]:
    # Sin intentos de por medio, el borrado es seguro.
    conn.execute(
        """DELETE FROM item_evaluacion
            WHERE evaluacion_id IN (SELECT id FROM evaluacion WHERE bloque_contenido_id = %s)""",
        (bc_id,),
    )
    # Los ítems de quiz caen con su módulo por ON DELETE CASCADE.
    conn.execute("DELETE FROM modulo WHERE bloque_contenido_id = %s", (bc_id,))

    for m in bloque["modulos"]:
        modulo_id = conn.execute(
            """INSERT INTO modulo (bloque_contenido_id, orden, titulo, cuerpo,
                                   duracion_min, xp, nivel_estandar_origen)
               VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
            (bc_id, m["orden"], m["titulo"], m["cuerpo"], m["duracion_min"],
             m["xp"], m["nivel_estandar_origen"]),
        ).fetchone()[0]

        # El quiz formativo va en su propia tabla: entrega la respuesta correcta
        # al cliente para el feedback inmediato, y el banco de la evaluación no
        # la entrega nunca.
        for orden, item in enumerate(m["quiz_formativo"], start=1):
            conn.execute(
                """INSERT INTO item_quiz_formativo
                       (modulo_id, orden, enunciado, alternativas, indice_correcta,
                        explicaciones, hash_enunciado, dificultad)
                   VALUES (%s,%s,%s,%s::jsonb,%s,%s::jsonb,%s,%s)
                   ON CONFLICT (modulo_id, hash_enunciado) DO NOTHING""",
                (modulo_id, orden, item["enunciado"],
                 json.dumps(item["alternativas"], ensure_ascii=False),
                 item["indice_correcta"],
                 json.dumps(item["explicaciones"], ensure_ascii=False),
                 _hash(item["enunciado"]), item.get("dificultad")),
            )

    ev = bloque["evaluacion"]
    ev_id = conn.execute(
        """INSERT INTO evaluacion (bloque_contenido_id, umbral_aprobacion,
                                   n_items_por_intento, max_reintentos, minutos_expiracion)
           VALUES (%s,%s,%s,%s,%s)
           ON CONFLICT (bloque_contenido_id) DO UPDATE
             SET umbral_aprobacion   = EXCLUDED.umbral_aprobacion,
                 n_items_por_intento = EXCLUDED.n_items_por_intento,
                 max_reintentos      = EXCLUDED.max_reintentos,
                 minutos_expiracion  = EXCLUDED.minutos_expiracion
           RETURNING id""",
        (bc_id, ev["umbral_aprobacion"], ev["n_items_por_intento"],
         ev["max_reintentos"], ev["minutos_expiracion"]),
    ).fetchone()[0]

    for item in ev["banco_items"]:
        conn.execute(
            """INSERT INTO item_evaluacion (evaluacion_id, enunciado, alternativas,
                                            indice_correcta, explicaciones, hash_enunciado,
                                            dificultad)
               VALUES (%s,%s,%s::jsonb,%s,%s::jsonb,%s,%s)
               ON CONFLICT (evaluacion_id, hash_enunciado) DO NOTHING""",
            (ev_id, item["enunciado"], json.dumps(item["alternativas"], ensure_ascii=False),
             item["indice_correcta"], json.dumps(item["explicaciones"], ensure_ascii=False),
             _hash(item["enunciado"]), item.get("dificultad")),
        )

    # Los dos rangos. Cuál se otorga lo decide la criticidad de la ruta, no esto.
    for med in bloque["medallas"]:
        conn.execute(
            """INSERT INTO definicion_medalla (bloque_contenido_id, tipo, nombre, xp)
               VALUES (%s,%s,%s,%s)
               ON CONFLICT (bloque_contenido_id, tipo) DO UPDATE
                 SET nombre = EXCLUDED.nombre, xp = EXCLUDED.xp""",
            (bc_id, med["tipo"], med["nombre"], med["xp"]),
        )

    _reemplazar_desafio(conn, bc_id, bloque["desafio"])

    return len(bloque["modulos"]), len(ev["banco_items"])


def _reemplazar_desafio(conn, bc_id, desafio: dict) -> None:
    """
    El desafío del bloque. Se rehace entero: sus decisiones no se referencian desde
    ninguna insignia, así que no arrastra el problema de trazabilidad del banco.
    """
    desafio_id = conn.execute(
        """INSERT INTO desafio_aplicado (bloque_contenido_id, titulo, rol_ficticio,
                                         situacion, datos, es_contenido_prueba)
           VALUES (%s,%s,%s,%s,%s::jsonb,%s)
           ON CONFLICT (bloque_contenido_id) DO UPDATE
             SET titulo = EXCLUDED.titulo, rol_ficticio = EXCLUDED.rol_ficticio,
                 situacion = EXCLUDED.situacion, datos = EXCLUDED.datos
           RETURNING id""",
        (bc_id, desafio["titulo"], desafio["rol_ficticio"], desafio["situacion"],
         json.dumps(desafio["datos"], ensure_ascii=False), desafio["es_contenido_prueba"]),
    ).fetchone()[0]

    conn.execute("DELETE FROM decision_desafio WHERE desafio_id = %s", (desafio_id,))
    for d in desafio["decisiones"]:
        conn.execute(
            """INSERT INTO decision_desafio (desafio_id, orden, tipo, enunciado,
                                             opciones, grupos, clave_correcta, explicacion)
               VALUES (%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,%s)""",
            (desafio_id, d["orden"], d["tipo"], d["enunciado"],
             json.dumps(d["opciones"], ensure_ascii=False),
             json.dumps(d["grupos"], ensure_ascii=False),
             json.dumps(d["clave_correcta"], ensure_ascii=False),
             d["explicacion"]),
        )
