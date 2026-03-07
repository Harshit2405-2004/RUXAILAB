"""
Tests de API (Tier 1) - Con Firestore mockeado.
Se ejecutan rápido y no requieren emulador.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from main import app
from models.log_entry import LogLayer, ActorRole


client = TestClient(app)


def test_health_check():
    """El endpoint /health debe devolver 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("services.log_writer.write", new_callable=AsyncMock)
def test_create_log_success(mock_write):
    """POST /log exitoso devuelve 201 y log_id."""
    mock_write.return_value = "mocked-log-id"

    payload = {
        "study_id": "study-001",
        "layer": "technical",
        "event_type": "STUDY_CREATED",
        "actor_id": "system",
        "actor_role": "system"
    }

    response = client.post("/log", json=payload)
    
    assert response.status_code == 201
    assert response.json()["log_id"] == "mocked-log-id"
    mock_write.assert_called_once()


@patch("services.log_writer.write", new_callable=AsyncMock)
def test_create_log_invalid_payload(mock_write):
    """POST /log rechaza payload inválido con 422."""
    payload = {
        "study_id": "study-001",
        "layer": "technical",
        "event_type": "INVALID_EVENT", # Evento no registrado
        "actor_id": "system",
        "actor_role": "system"
    }

    response = client.post("/log", json=payload)
    
    assert response.status_code == 422
    mock_write.assert_not_called()


@patch("services.log_writer.write_batch", new_callable=AsyncMock)
def test_create_log_batch_success(mock_write_batch):
    """POST /log/batch exitoso devuelve 201 y log_ids."""
    mock_write_batch.return_value = ["id-1", "id-2"]

    payload = [
        {
            "study_id": "study-001",
            "layer": "technical",
            "event_type": "STUDY_CREATED",
            "actor_id": "system",
            "actor_role": "system"
        },
        {
            "study_id": "study-001",
            "layer": "technical",
            "event_type": "STUDY_UPDATED",
            "actor_id": "system",
            "actor_role": "system"
        }
    ]

    response = client.post("/log/batch", json=payload)
    
    assert response.status_code == 201
    assert response.json()["count"] == 2
    assert response.json()["log_ids"] == ["id-1", "id-2"]
    mock_write_batch.assert_called_once()


@patch("services.log_reader.query", new_callable=AsyncMock)
def test_get_logs_success(mock_query):
    """GET /logs retorna lista de logs."""
    mock_query.return_value = [{"log_id": "1"}, {"log_id": "2"}]

    response = client.get("/logs?study_id=test-001")
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    mock_query.assert_called_once_with(study_id="test-001", layer=None, limit=100)


def test_get_logs_missing_study_id():
    """GET /logs sin study_id retorna 422."""
    response = client.get("/logs")
    assert response.status_code == 422
