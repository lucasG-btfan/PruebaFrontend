# Dockerfile - Versión optimizada para Render
FROM python:3.11-slim

# 1. Instalar dependencias críticas
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 2. Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 3. Crear usuario no-root
RUN useradd -m -u 1000 appuser

# 4. Directorio de trabajo
WORKDIR /app

# 5. Copiar requirements y instalar
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 6. Copiar todo el código
COPY --chown=appuser:appuser . .

# 7. Cambiar usuario
USER appuser

# 8. Comando de inicio ÚNICO y SIMPLE
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
