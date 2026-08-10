"""
Corredor de migraciones.

Aplica los .sql de `migraciones/` en orden y registra cuáles ya corrieron.
Sin dependencias: el esquema es SQL plano y auditable, que es lo que se quiere
para un sistema donde los invariantes VIVEN en el esquema (ADR-005).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg

MIGRACIONES = Path(__file__).resolve().parents[1] / "migraciones"


def migrar(dsn: str) -> list[str]:
    aplicadas = []
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS migracion_aplicada (
                   nombre text PRIMARY KEY,
                   aplicada_en timestamptz NOT NULL DEFAULT now()
               )"""
        )
        ya = {r[0] for r in conn.execute("SELECT nombre FROM migracion_aplicada").fetchall()}

        for archivo in sorted(MIGRACIONES.glob("*.sql")):
            if archivo.name in ya:
                continue
            print(f"  migrando · {archivo.name}", flush=True)
            with conn.transaction():
                conn.execute(archivo.read_text(encoding="utf-8"))
                conn.execute(
                    "INSERT INTO migracion_aplicada (nombre) VALUES (%s)", (archivo.name,)
                )
            aplicadas.append(archivo.name)

    return aplicadas


if __name__ == "__main__":
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("  FALTA la variable DATABASE_URL. Copia .env.example a .env.", file=sys.stderr)
        sys.exit(1)
    hechas = migrar(dsn)
    print(f"  migraciones aplicadas: {len(hechas) or 'ninguna nueva'}", flush=True)
