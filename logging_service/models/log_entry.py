"""
Modelos Pydantic para las entradas de log del sistema de trazabilidad.

Define el esquema completo de LogEntry, enums para capas y roles,
y el registro de tipos de eventos válidos por capa.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


# ─── Enums ───────────────────────────────────────────────────────────────────


class LogLayer(str, Enum):
    """Las tres capas de logging definidas en SPEC.md."""
    TECHNICAL = "technical"
    METHODOLOGICAL = "methodological"
    AI_DECISION = "ai_decision"


class ActorRole(str, Enum):
    """Roles de actores que generan eventos."""
    RESEARCHER = "researcher"
    EVALUATOR = "evaluator"
    PARTICIPANT = "participant"
    SYSTEM = "system"


class RetentionPolicy(str, Enum):
    """Políticas de retención para logs según GDPR."""
    DAYS_30 = "30d"
    DAYS_90 = "90d"
    YEAR_1 = "1y"
    PERMANENT = "permanent"


# ─── Tipos de eventos válidos por capa ───────────────────────────────────────

# Eventos técnicos: operaciones del sistema
TECHNICAL_EVENTS = {
    "STUDY_CREATED",
    "STUDY_UPDATED",
    "STUDY_DELETED",
    "USER_SIGNED_IN",
    "USER_SIGNED_OUT",
    "SESSION_STARTED",
    "SESSION_ENDED",
    "API_CALLED",
    "API_ERROR",
    "FUNCTION_TRIGGERED",
    "SESSIONS_CLEANED",
    "FILE_UPLOADED",
    "TEMPLATE_CREATED",
    "TEMPLATE_UPDATED",
    "TEMPLATE_DELETED",
}

# Eventos metodológicos: ciclo de vida del estudio
METHODOLOGICAL_EVENTS = {
    "TASK_PRESENTED",
    "TASK_COMPLETED",
    "HEURISTIC_SCORED",
    "CARD_SORTED",
    "CALIBRATION_STARTED",
    "CALIBRATION_COMPLETED",
    "ANSWER_SUBMITTED",
    "ACCESSIBILITY_EVALUATED",
}

# Eventos de decisión IA: computaciones y análisis automatizados
AI_DECISION_EVENTS = {
    "AI_WEIGHT_COMPUTED",
    "AI_CONSISTENCY_CHECK",
    "SENTIMENT_ANALYZED",
    "FACIAL_SENTIMENT_ANALYZED",
    "EYE_TRACKING_PROCESSED",
}

# Registro unificado de todos los tipos de eventos válidos
VALID_EVENT_TYPES = TECHNICAL_EVENTS | METHODOLOGICAL_EVENTS | AI_DECISION_EVENTS

# Mapeo de capa → eventos válidos para validación cruzada
LAYER_EVENT_MAP = {
    LogLayer.TECHNICAL: TECHNICAL_EVENTS,
    LogLayer.METHODOLOGICAL: METHODOLOGICAL_EVENTS,
    LogLayer.AI_DECISION: AI_DECISION_EVENTS,
}


# ─── Modelo principal ───────────────────────────────────────────────────────


class LogEntry(BaseModel):
    """
    Entrada de log estructurada para el sistema de trazabilidad unificado.

    Cada instancia representa un evento capturado en una de las tres capas
    (técnica, metodológica, decisión IA) con metadatos completos para
    trazabilidad y cumplimiento GDPR.
    """

    log_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Identificador único del log (UUID v4)",
    )
    study_id: str = Field(
        ...,
        min_length=1,
        description="ID del estudio asociado",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="ID de la sesión del participante (si aplica)",
    )
    layer: LogLayer = Field(
        ...,
        description="Capa del log: technical, methodological, ai_decision",
    )
    event_type: str = Field(
        ...,
        description="Tipo de evento (debe estar en VALID_EVENT_TYPES)",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Marca temporal UTC del evento",
    )
    actor_id: str = Field(
        ...,
        description="ID del actor (anonimizado para participantes)",
    )
    actor_role: ActorRole = Field(
        ...,
        description="Rol del actor que generó el evento",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Datos adicionales del evento (sin PII)",
    )
    trace_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="ID de traza para correlacionar eventos relacionados",
    )
    parent_log_id: Optional[str] = Field(
        default=None,
        description="ID del log padre (para relaciones jerárquicas)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadatos del contexto: platform_version, env, etc.",
    )
    is_anonymized: bool = Field(
        default=False,
        description="Indica si los datos del actor ya fueron anonimizados",
    )
    retention_policy: RetentionPolicy = Field(
        default=RetentionPolicy.DAYS_90,
        description="Política de retención del log",
    )

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value: str) -> str:
        """Valida que el tipo de evento esté en el registro de eventos válidos."""
        if value not in VALID_EVENT_TYPES:
            raise ValueError(
                f"Unknown event_type '{value}'. "
                f"Valid types: {sorted(VALID_EVENT_TYPES)}"
            )
        return value

    def to_firestore_dict(self) -> dict[str, Any]:
        """Convierte el modelo a un diccionario compatible con Firestore."""
        data = self.model_dump()
        # Firestore maneja datetime nativamente
        data["timestamp"] = self.timestamp
        return data
