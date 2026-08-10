"""
Entorno de pruebas del motor de integridad.

Corre contra PostgreSQL REAL, nunca SQLite: los CHECK, los triggers y los índices
únicos de ADR-005 no existen en SQLite, y probar contra otro motor daría una
garantía falsa (DECISIONES-AUTONOMAS.md).
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

import psycopg
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

DSN = os.environ.get(
    "DATABASE_URL", "postgresql://somoscalidad:somoscalidad@localhost:5433/somoscalidad_test"
)
MIGRACIONES = sorted((RAIZ / "migraciones").glob("*.sql"))


@pytest.fixture(scope="session")
def conexion():
    with psycopg.connect(DSN, autocommit=True) as conn:
        conn.execute("DROP SCHEMA IF EXISTS public CASCADE")
        conn.execute("CREATE SCHEMA public")
        for archivo in MIGRACIONES:
            conn.execute(archivo.read_text(encoding="utf-8"))

        # Banco de mutación: sabotea un candado a propósito para comprobar que la
        # suite lo delata. Un test de integridad que pasa igual con el candado roto
        # no está probando nada. Se usa desde prueba-mutacion.sh; en CI va vacío.
        mutacion = os.environ.get("MUTACION")
        if mutacion:
            print(f"\n  !! MUTACIÓN ACTIVA: {mutacion}\n")
            conn.execute(mutacion)

        yield conn


@dataclass
class Escenario:
    colaborador_id: UUID
    otro_colaborador_id: UUID
    bloque_ruta_id: UUID
    otro_bloque_ruta_id: UUID
    bloque_contenido_id: UUID
    otro_bloque_contenido_id: UUID
    medalla_id: UUID
    otra_medalla_id: UUID
    items: list[UUID]          # todos con indice_correcta = 0
    otros_items: list[UUID]


@pytest.fixture
def db(conexion):
    """Base limpia por prueba, con el escenario mínimo sembrado."""
    conexion.execute(
        """
        TRUNCATE insignia, evento_gamificacion, respuesta_intento, intento_evaluacion,
                 bloque_ruta, ruta, membresia_comite, colaborador, comite, unidad,
                 exigencia_cargo_dimension, hito, definicion_medalla, modulo,
                 item_evaluacion, evaluacion, bloque_contenido, dimension, cargo
        RESTART IDENTITY CASCADE
        """
    )
    return conexion


@pytest.fixture
def esc(db) -> Escenario:
    cargo_id = db.execute(
        "INSERT INTO cargo (codigo, nombre) VALUES ('DOCENTE','Docente') RETURNING id"
    ).fetchone()[0]

    colaborador_id = db.execute(
        "INSERT INTO colaborador (email, nombre, cargo_id) VALUES (%s,%s,%s) RETURNING id",
        ("pablo@aiep.cl", "Pablo", cargo_id),
    ).fetchone()[0]
    otro_colaborador_id = db.execute(
        "INSERT INTO colaborador (email, nombre, cargo_id) VALUES (%s,%s,%s) RETURNING id",
        ("otra@aiep.cl", "Otra Persona", cargo_id),
    ).fetchone()[0]

    def crear_bloque(codigo, nombre, nivel, orden, titulo, xp_medalla):
        dim = db.execute(
            "INSERT INTO dimension (codigo, nombre_oficial, orden) VALUES (%s,%s,%s) RETURNING id",
            (codigo, nombre, orden),
        ).fetchone()[0]
        bc = db.execute(
            """INSERT INTO bloque_contenido (dimension_id, nivel_estandar, titulo, estado)
               VALUES (%s,%s,%s,'validado') RETURNING id""",
            (dim, nivel, titulo),
        ).fetchone()[0]
        ev = db.execute(
            """INSERT INTO evaluacion (bloque_contenido_id, umbral_aprobacion, n_items_por_intento)
               VALUES (%s, 0.80, 5) RETURNING id""",
            (bc,),
        ).fetchone()[0]
        items = []
        for n in range(10):
            item = db.execute(
                """INSERT INTO item_evaluacion
                       (evaluacion_id, enunciado, alternativas, indice_correcta,
                        explicaciones, hash_enunciado)
                   VALUES (%s,%s,%s::jsonb,0,%s::jsonb,%s) RETURNING id""",
                (
                    ev,
                    f"{titulo} · pregunta {n}",
                    json.dumps(["correcta", "mala 1", "mala 2", "mala 3"]),
                    json.dumps(["es la correcta", "no", "tampoco", "menos"]),
                    f"{titulo}-{n}",
                ),
            ).fetchone()[0]
            items.append(item)
        medalla = db.execute(
            """INSERT INTO definicion_medalla (bloque_contenido_id, tipo, nombre, xp)
               VALUES (%s,'silver',%s,%s) RETURNING id""",
            (bc, f"Medalla {titulo}", xp_medalla),
        ).fetchone()[0]
        return bc, medalla, items

    bc1, medalla1, items1 = crear_bloque("DOCENCIA", "Docencia y Resultados", 3, 1, "Docencia N3", 400)
    bc2, medalla2, items2 = crear_bloque("VCM", "Vinculación con el Medio", 1, 2, "VcM N1", 200)

    ruta_id = db.execute(
        "INSERT INTO ruta (colaborador_id, cargo_id) VALUES (%s,%s) RETURNING id",
        (colaborador_id, cargo_id),
    ).fetchone()[0]
    br1 = db.execute(
        """INSERT INTO bloque_ruta (ruta_id, bloque_contenido_id, orden, estado)
           VALUES (%s,%s,1,'disponible') RETURNING id""",
        (ruta_id, bc1),
    ).fetchone()[0]
    br2 = db.execute(
        """INSERT INTO bloque_ruta (ruta_id, bloque_contenido_id, orden, estado)
           VALUES (%s,%s,2,'disponible') RETURNING id""",
        (ruta_id, bc2),
    ).fetchone()[0]

    return Escenario(
        colaborador_id=colaborador_id,
        otro_colaborador_id=otro_colaborador_id,
        bloque_ruta_id=br1,
        otro_bloque_ruta_id=br2,
        bloque_contenido_id=bc1,
        otro_bloque_contenido_id=bc2,
        medalla_id=medalla1,
        otra_medalla_id=medalla2,
        items=items1,
        otros_items=items2,
    )


# ------------------------------------------------------------------ utilidades
def responder_intento(db, intento_id, *, aciertos: int):
    """Responde el intento con `aciertos` respuestas correctas (la correcta es la 0)."""
    from motor.evaluacion import responder

    servidos = db.execute(
        "SELECT items_servidos FROM intento_evaluacion WHERE id = %s", (intento_id,)
    ).fetchone()[0]
    for i, item_id in enumerate(servidos):
        responder(db, intento_id=intento_id, item_id=UUID(item_id),
                  indice_elegido=0 if i < aciertos else 1)
