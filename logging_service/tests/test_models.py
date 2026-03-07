"""
Tests para los modelos Pydantic del sistema de logging.

Verifica validación estricta de LogEntry: tipos de evento,
enums, auto-generación de UUIDs, y rechazo de datos inválidos.
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID

from models.log_entry import (
    LogEntry,
    LogLayer,
    ActorRole,
    RetentionPolicy,
    VALID_EVENT_TYPES,
    TECHNICAL_EVENTS,
    METHODOLOGICAL_EVENTS,
    AI_DECISION_EVENTS,
    LAYER_EVENT_MAP,
)


# ─── Test 1: Creación exitosa con campos mínimos ─────────────────────────────


class TestLogEntryCreation:
    """Verifica que LogEntry se crea correctamente con datos válidos."""

    def test_creates_with_required_fields_only(self):
        """Los campos opcionales deben tener valores por defecto."""
        entry = LogEntry(
            study_id="study-001",
            layer=LogLayer.TECHNICAL,
            event_type="STUDY_CREATED",
            actor_id="user-123",
            actor_role=ActorRole.RESEARCHER,
        )

        assert entry.study_id == "study-001"
        assert entry.layer == LogLayer.TECHNICAL
        assert entry.event_type == "STUDY_CREATED"
        assert entry.actor_id == "user-123"
        assert entry.actor_role == ActorRole.RESEARCHER

    def test_auto_generates_log_id_as_uuid(self):
        """log_id debe generarse automáticamente como UUID v4."""
        entry = LogEntry(
            study_id="study-001",
            layer=LogLayer.TECHNICAL,
            event_type="STUDY_CREATED",
            actor_id="system",
            actor_role=ActorRole.SYSTEM,
        )

        # Verificar que es un UUID válido
        parsed = UUID(entry.log_id, version=4)
        assert str(parsed) == entry.log_id

    def test_auto_generates_trace_id_as_uuid(self):
        """trace_id debe generarse automáticamente como UUID v4."""
        entry = LogEntry(
            study_id="study-001",
            layer=LogLayer.TECHNICAL,
            event_type="STUDY_CREATED",
            actor_id="system",
            actor_role=ActorRole.SYSTEM,
        )

        parsed = UUID(entry.trace_id, version=4)
        assert str(parsed) == entry.trace_id

    def test_auto_generates_timestamp_utc(self):
        """timestamp debe generarse automáticamente en UTC."""
        before = datetime.now(timezone.utc)
        entry = LogEntry(
            study_id="study-001",
            layer=LogLayer.TECHNICAL,
            event_type="STUDY_CREATED",
            actor_id="system",
            actor_role=ActorRole.SYSTEM,
        )
        after = datetime.now(timezone.utc)

        assert before <= entry.timestamp <= after

    def test_creates_with_all_optional_fields(self):
        """Debe aceptar todos los campos opcionales."""
        entry = LogEntry(
            study_id="study-001",
            session_id="session-abc",
            layer=LogLayer.METHODOLOGICAL,
            event_type="TASK_PRESENTED",
            actor_id="participant-456",
            actor_role=ActorRole.PARTICIPANT,
            payload={"task_index": 3, "task_title": "Login flow"},
            parent_log_id="parent-log-789",
            metadata={"platform_version": "2.1.0", "env": "production"},
            is_anonymized=True,
            retention_policy=RetentionPolicy.YEAR_1,
        )

        assert entry.session_id == "session-abc"
        assert entry.payload["task_index"] == 3
        assert entry.parent_log_id == "parent-log-789"
        assert entry.is_anonymized is True
        assert entry.retention_policy == RetentionPolicy.YEAR_1


# ─── Test 2: Validación de event_type ────────────────────────────────────────


class TestEventTypeValidation:
    """Verifica que event_type solo acepta valores del registro."""

    def test_rejects_unknown_event_type(self):
        """Debe rechazar tipos de evento no registrados."""
        with pytest.raises(ValueError, match="Unknown event_type"):
            LogEntry(
                study_id="study-001",
                layer=LogLayer.TECHNICAL,
                event_type="INVALID_EVENT",
                actor_id="system",
                actor_role=ActorRole.SYSTEM,
            )

    def test_accepts_all_technical_events(self):
        """Debe aceptar todos los eventos técnicos registrados."""
        for event_type in TECHNICAL_EVENTS:
            entry = LogEntry(
                study_id="study-001",
                layer=LogLayer.TECHNICAL,
                event_type=event_type,
                actor_id="system",
                actor_role=ActorRole.SYSTEM,
            )
            assert entry.event_type == event_type

    def test_accepts_all_methodological_events(self):
        """Debe aceptar todos los eventos metodológicos registrados."""
        for event_type in METHODOLOGICAL_EVENTS:
            entry = LogEntry(
                study_id="study-001",
                layer=LogLayer.METHODOLOGICAL,
                event_type=event_type,
                actor_id="system",
                actor_role=ActorRole.SYSTEM,
            )
            assert entry.event_type == event_type

    def test_accepts_all_ai_decision_events(self):
        """Debe aceptar todos los eventos de decisión IA registrados."""
        for event_type in AI_DECISION_EVENTS:
            entry = LogEntry(
                study_id="study-001",
                layer=LogLayer.AI_DECISION,
                event_type=event_type,
                actor_id="system",
                actor_role=ActorRole.SYSTEM,
            )
            assert entry.event_type == event_type

    def test_error_message_contains_event_name(self):
        """El mensaje de error debe incluir el nombre del evento inválido."""
        with pytest.raises(ValueError, match="FAKE_EVENT"):
            LogEntry(
                study_id="study-001",
                layer=LogLayer.TECHNICAL,
                event_type="FAKE_EVENT",
                actor_id="system",
                actor_role=ActorRole.SYSTEM,
            )


# ─── Test 3: Validación de campos requeridos ─────────────────────────────────


class TestRequiredFieldValidation:
    """Verifica que los campos requeridos no pueden omitirse."""

    def test_missing_study_id_raises_error(self):
        """study_id es requerido."""
        with pytest.raises(Exception):
            LogEntry(
                layer=LogLayer.TECHNICAL,
                event_type="STUDY_CREATED",
                actor_id="system",
                actor_role=ActorRole.SYSTEM,
            )

    def test_missing_layer_raises_error(self):
        """layer es requerido."""
        with pytest.raises(Exception):
            LogEntry(
                study_id="study-001",
                event_type="STUDY_CREATED",
                actor_id="system",
                actor_role=ActorRole.SYSTEM,
            )

    def test_missing_actor_id_raises_error(self):
        """actor_id es requerido."""
        with pytest.raises(Exception):
            LogEntry(
                study_id="study-001",
                layer=LogLayer.TECHNICAL,
                event_type="STUDY_CREATED",
                actor_role=ActorRole.SYSTEM,
            )

    def test_empty_study_id_raises_error(self):
        """study_id no puede ser cadena vacía."""
        with pytest.raises(Exception):
            LogEntry(
                study_id="",
                layer=LogLayer.TECHNICAL,
                event_type="STUDY_CREATED",
                actor_id="system",
                actor_role=ActorRole.SYSTEM,
            )


# ─── Test 4: Enums ──────────────────────────────────────────────────────────


class TestEnumValidation:
    """Verifica que los enums rechazan valores inválidos."""

    def test_invalid_layer_raises_error(self):
        """layer debe ser uno de los valores del enum."""
        with pytest.raises(Exception):
            LogEntry(
                study_id="study-001",
                layer="invalid_layer",
                event_type="STUDY_CREATED",
                actor_id="system",
                actor_role=ActorRole.SYSTEM,
            )

    def test_invalid_actor_role_raises_error(self):
        """actor_role debe ser uno de los valores del enum."""
        with pytest.raises(Exception):
            LogEntry(
                study_id="study-001",
                layer=LogLayer.TECHNICAL,
                event_type="STUDY_CREATED",
                actor_id="system",
                actor_role="invalid_role",
            )

    def test_invalid_retention_policy_raises_error(self):
        """retention_policy debe ser uno de los valores del enum."""
        with pytest.raises(Exception):
            LogEntry(
                study_id="study-001",
                layer=LogLayer.TECHNICAL,
                event_type="STUDY_CREATED",
                actor_id="system",
                actor_role=ActorRole.SYSTEM,
                retention_policy="invalid_policy",
            )


# ─── Test 5: Serialización a Firestore ───────────────────────────────────────


class TestFirestoreSerialization:
    """Verifica la conversión a formato compatible con Firestore."""

    def test_to_firestore_dict_returns_all_fields(self):
        """to_firestore_dict debe incluir todos los campos del modelo."""
        entry = LogEntry(
            study_id="study-001",
            layer=LogLayer.TECHNICAL,
            event_type="STUDY_CREATED",
            actor_id="system",
            actor_role=ActorRole.SYSTEM,
        )

        result = entry.to_firestore_dict()

        assert "log_id" in result
        assert "study_id" in result
        assert "layer" in result
        assert "event_type" in result
        assert "timestamp" in result
        assert "actor_id" in result
        assert "actor_role" in result
        assert "trace_id" in result
        assert isinstance(result["timestamp"], datetime)

    def test_to_firestore_dict_preserves_payload(self):
        """El payload debe preservarse en la serialización."""
        entry = LogEntry(
            study_id="study-001",
            layer=LogLayer.AI_DECISION,
            event_type="AI_WEIGHT_COMPUTED",
            actor_id="system",
            actor_role=ActorRole.SYSTEM,
            payload={"weights": [0.3, 0.5, 0.2], "consistency_ratio": 0.04},
        )

        result = entry.to_firestore_dict()

        assert result["payload"]["weights"] == [0.3, 0.5, 0.2]
        assert result["payload"]["consistency_ratio"] == 0.04


# ─── Test 6: Registro de eventos ─────────────────────────────────────────────


class TestEventRegistry:
    """Verifica la integridad del registro de tipos de eventos."""

    def test_valid_event_types_is_union_of_all_layers(self):
        """VALID_EVENT_TYPES debe ser la unión de los tres conjuntos."""
        expected = TECHNICAL_EVENTS | METHODOLOGICAL_EVENTS | AI_DECISION_EVENTS
        assert VALID_EVENT_TYPES == expected

    def test_no_duplicate_events_across_layers(self):
        """No debe haber eventos duplicados entre capas."""
        tech_method = TECHNICAL_EVENTS & METHODOLOGICAL_EVENTS
        tech_ai = TECHNICAL_EVENTS & AI_DECISION_EVENTS
        method_ai = METHODOLOGICAL_EVENTS & AI_DECISION_EVENTS

        assert len(tech_method) == 0, f"Duplicados tech/method: {tech_method}"
        assert len(tech_ai) == 0, f"Duplicados tech/ai: {tech_ai}"
        assert len(method_ai) == 0, f"Duplicados method/ai: {method_ai}"

    def test_layer_event_map_covers_all_layers(self):
        """LAYER_EVENT_MAP debe tener una entrada por cada capa."""
        assert set(LAYER_EVENT_MAP.keys()) == {
            LogLayer.TECHNICAL,
            LogLayer.METHODOLOGICAL,
            LogLayer.AI_DECISION,
        }

    def test_total_event_count(self):
        """Verificar el conteo total de eventos registrados."""
        assert len(VALID_EVENT_TYPES) == 28
