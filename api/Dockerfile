# El contexto de build es la RAÍZ del repo, no api/: el Validador necesita
# docs/contenido/schema-bloque-contenido.json, que es el contrato entre el
# Generador y el Integrador y debe tener una sola fuente de verdad.
FROM python:3.12-slim

WORKDIR /app

# El intérprete va DENTRO del contenedor: la máquina del director tiene Python 3.9
# y la API pide 3.12 (DECISIONES-AUTONOMAS.md).
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/migraciones ./migraciones
COPY api/src ./src
COPY api/entrypoint.sh .
COPY docs/contenido ./docs/contenido
RUN chmod +x entrypoint.sh

EXPOSE 8000
CMD ["./entrypoint.sh"]
