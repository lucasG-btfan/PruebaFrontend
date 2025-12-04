# Usar una imagen oficial de Python slim para reducir el tamaño
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para PostgreSQL y compilación
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requisitos e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Crear directorio para logs
RUN mkdir -p logs

# Exponer el puerto
EXPOSE 10000

# Configurar variables de entorno para producción
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app \
    UVICORN_WORKERS=4 \
    API_HOST=0.0.0.0 \
    API_PORT=10000 \
    RELOAD=false

# Comando para ejecutar la aplicación
CMD ["python", "run_production.py"]
