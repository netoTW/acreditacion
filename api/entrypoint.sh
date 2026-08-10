#!/usr/bin/env sh
# Arranque autosuficiente (CLAUDE.md §11): espera dependencias → migra → siembra → sirve.
# Sin pasos manuales. Si falta una variable, corta con instrucción clara en vez de
# arrancar a medias.
set -e

if [ -z "${DATABASE_URL:-}" ]; then
  echo ""
  echo "  FALTA la variable DATABASE_URL."
  echo "  Copia .env.example a .env en la raíz del repo y vuelve a levantar:"
  echo "      cp .env.example .env && docker compose up"
  echo ""
  exit 1
fi

echo "  esperando la base de datos…"
i=0
until python -c "
import os,sys,psycopg
try:
    psycopg.connect(os.environ['DATABASE_URL'], connect_timeout=2).close()
except Exception:
    sys.exit(1)
" 2>/dev/null; do
  i=$((i + 1))
  if [ "$i" -gt 60 ]; then
    echo "  la base no respondió en 60 intentos. ¿Está sano el servicio 'db'?"
    exit 1
  fi
  sleep 1
done
echo "  base lista"

python src/migrar.py
python -c "
import os, psycopg, sys
sys.path.insert(0, 'src')
from seed.sembrar import sembrar
with psycopg.connect(os.environ['DATABASE_URL'], autocommit=True) as conn:
    ids = sembrar(conn)
    n = lambda q: conn.execute(q).fetchone()[0]
    print(f'  seed · {n(\"SELECT count(*) FROM dimension\")} dimensiones · '
          f'{n(\"SELECT count(*) FROM hito\")} hitos · '
          f'{n(\"SELECT count(*) FROM cargo\")} cargos · '
          f'{n(\"SELECT count(*) FROM exigencia_cargo_dimension\")} filas de matriz · '
          f'{n(\"SELECT count(*) FROM bloque_contenido\")} unidades de contenido · '
          f'{len(ids)} colaboradores', flush=True)
"

echo ""
echo "  API lista  →  http://localhost:${PUERTO_API:-8000}/docs"
echo ""
exec uvicorn app:app --host 0.0.0.0 --port 8000 --app-dir src
