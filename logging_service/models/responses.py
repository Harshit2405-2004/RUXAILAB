"""
Esquemas de respuesta para los endpoints de la API de logging.
"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Respuesta del endpoint de salud."""
    status: str = "ok"


class LogCreatedResponse(BaseModel):
    """Respuesta tras crear un log individual."""
    log_id: str
    message: str = "Log created successfully"


class BatchLogResponse(BaseModel):
    """Respuesta tras crear logs en lote."""
    log_ids: list[str]
    count: int
    message: str = "Batch logs created successfully"


class ErrorResponse(BaseModel):
    """Respuesta de error estructurada."""
    error: str
    detail: str | None = None
