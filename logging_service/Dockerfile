# Base Python 3.11 slim image optimizada para Cloud Run
FROM python:3.11-slim

# Evitar escritura de .pyc y forzar stdout/stderr unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias primero para cachear esta capa
COPY requirements.txt .

# Limpiar cache de pip inmediatamente para mantener imagen pequeña
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Exponer el puerto 8080 (requerido por Cloud Run)
EXPOSE 8080

# Crear un usuario no root para seguridad
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
