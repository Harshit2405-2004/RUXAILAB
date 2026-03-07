"""
Logging microservice para el sistema de trazabilidad unificado de RUXAILAB.

Proporciona endpoints para escritura y lectura de logs estructurados
en Firestore, organizados en tres capas: técnica, metodológica y decisiones IA.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.log_entry import LogEntry
from models.responses import (
    HealthResponse,
    LogCreatedResponse,
    BatchLogResponse,
    ErrorResponse,
)
from services import log_writer, log_reader


app = FastAPI(
    title="RUXAILAB Logging Service",
    description="Unified Logging & Traceability System for Usability Studies",
    version="0.1.0",
)

# Configuración CORS para permitir peticiones desde el frontend Vue.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Se restringe en producción via env var
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de salud para verificar que el servicio está activo."""
    return HealthResponse()


@app.post("/log", status_code=201, response_model=LogCreatedResponse)
async def create_log(entry: LogEntry):
    """
    Crea una entrada de log individual en Firestore.

    La escritura es no-bloqueante: se ejecuta en un thread pool
    para no afectar el event loop de FastAPI.
    """
    try:
        log_id = await log_writer.write(entry)
        return LogCreatedResponse(log_id=log_id)
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to write log: {str(err)}",
        )


@app.post("/log/batch", status_code=201, response_model=BatchLogResponse)
async def create_log_batch(entries: list[LogEntry]):
    """
    Crea múltiples entradas de log en un batch atómico de Firestore.

    Usa db.batch() (escritura atómica, no transacción).
    Límite: 500 entradas por batch.
    """
    try:
        log_ids = await log_writer.write_batch(entries)
        return BatchLogResponse(
            log_ids=log_ids,
            count=len(log_ids),
        )
    except ValueError as err:
        # Error de validación (batch size excedido)
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to write batch: {str(err)}",
        )


@app.get("/logs")
async def get_logs(study_id: str, layer: str | None = None, limit: int = 100):
    """
    Consulta logs por study_id. Filtro opcional por layer.
    """
    if limit > 1000:
        limit = 1000
    try:
        logs = await log_reader.query(study_id=study_id, layer=layer, limit=limit)
        return logs
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query logs: {str(err)}",
        )
