# Dockerfile FINAL
FROM python:3.11-slim

# 1. Instalar solo lo esencial
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Directorio de trabajo
WORKDIR /app

# 3. Copiar SOLO archivos Python/backend
COPY requirements.txt .
COPY *.py ./
COPY config/ ./config/
COPY controllers/ ./controllers/
COPY models/ ./models/

# 4. Instalar dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Comando SIMPLE y DIRECTO
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]