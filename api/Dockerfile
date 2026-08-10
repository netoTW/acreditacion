FROM python:3.12-slim

WORKDIR /app

# El intérprete va DENTRO del contenedor: la máquina del director tiene Python 3.9
# y la API pide 3.12 (DECISIONES-AUTONOMAS.md).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY migraciones ./migraciones
COPY src ./src
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000
CMD ["./entrypoint.sh"]
