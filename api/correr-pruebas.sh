#!/usr/bin/env bash
# Levanta PostgreSQL en Docker y corre la regresión de integridad.
# Contra PostgreSQL REAL, nunca SQLite: los CHECK y triggers de ADR-005 no existen ahí.
set -euo pipefail

cd "$(dirname "$0")"

CONTENEDOR=somoscalidad-pg-test
PUERTO=5433
export DATABASE_URL="postgresql://somoscalidad:somoscalidad@localhost:${PUERTO}/somoscalidad_test"

if ! docker inspect "$CONTENEDOR" >/dev/null 2>&1; then
  echo "  levantando PostgreSQL de pruebas…"
  docker run -d --name "$CONTENEDOR" \
    -e POSTGRES_USER=somoscalidad \
    -e POSTGRES_PASSWORD=somoscalidad \
    -e POSTGRES_DB=somoscalidad_test \
    -p "${PUERTO}:5432" \
    --health-cmd="pg_isready -U somoscalidad" \
    --health-interval=2s --health-timeout=3s --health-retries=15 \
    postgres:16 >/dev/null
elif [ "$(docker inspect -f '{{.State.Running}}' "$CONTENEDOR")" != "true" ]; then
  docker start "$CONTENEDOR" >/dev/null
fi

printf "  esperando a la base"
for _ in $(seq 1 45); do
  if [ "$(docker inspect -f '{{.State.Health.Status}}' "$CONTENEDOR" 2>/dev/null)" = "healthy" ]; then
    echo " · lista"; break
  fi
  printf "."; sleep 1
done

if [ ! -d .venv ]; then
  echo "  creando entorno de Python…"
  python3 -m venv .venv
  ./.venv/bin/pip install --quiet --disable-pip-version-check -r requirements.txt
fi

exec ./.venv/bin/python -m pytest "$@"
