"""
Tests del escritor y lector a Firestore (Tier 2).
Requiere que el Firestore Emulator esté ejecutándose.
"""

import pytest
import os
import requests
from db.firestore_client import get_firestore_client, UNIFIED_LOGS_COLLECTION
from services import log_writer, log_reader
from models.log_entry import LogEntry, LogLayer, ActorRole


# Verificar si el emulador está verdaderamente levantado para saltar los tests si no
def is_emulator_running():
    host = os.environ.get("FIRESTORE_EMULATOR_HOST", "localhost:8081")
    try:
        requests.get(f"http://{host}/", timeout=1)
        return True
    except:
        return False

# Skip mark en base al emulador
require_emulator = pytest.mark.skipif(
    not is_emulator_running(),
    reason="Firestore emulator is not running"
)


def clear_emulator_data():
    """Limpia los datos del emulador via su API REST."""
    host = os.environ.get("FIRESTORE_EMULATOR_HOST", "localhost:8081")
    # Firebase project ID usado en pruebas
    project_id = "demo-ruxailab" 
    try:
        requests.delete(f"http://{host}/emulator/v1/projects/{project_id}/databases/(default)/documents")
    except Exception:
        pass


@pytest.fixture(autouse=True)
def setup_teardown():
    """Limpiar emulador antes de cada test real."""
    if is_emulator_running():
        # Set dummy project to match clear url
        os.environ["GCLOUD_PROJECT"] = "demo-ruxailab"
        clear_emulator_data()
    yield


@require_emulator
@pytest.mark.asyncio
async def test_write_single_log():
    """Debe escribir correctamente un log a Firestore Emulado."""
    entry = LogEntry(
        study_id="test-study",
        layer=LogLayer.TECHNICAL,
        event_type="STUDY_CREATED",
        actor_id="system",
        actor_role=ActorRole.SYSTEM
    )

    log_id = await log_writer.write(entry)
    
    # Verificar leyendo directo de BD
    db = get_firestore_client()
    doc = db.collection(UNIFIED_LOGS_COLLECTION).document(log_id).get()
    
    assert doc.exists
    assert doc.to_dict()["study_id"] == "test-study"
    assert doc.to_dict()["event_type"] == "STUDY_CREATED"


@require_emulator
@pytest.mark.asyncio
async def test_write_batch_logs():
    """Debe escribir múltiples logs atómicamente a Firestore Emulado."""
    entries = [
        LogEntry(
            study_id="test-study",
            layer=LogLayer.TECHNICAL,
            event_type="STUDY_CREATED",
            actor_id="system",
            actor_role=ActorRole.SYSTEM
        ),
        LogEntry(
            study_id="test-study",
            layer=LogLayer.METHODOLOGICAL,
            event_type="TASK_PRESENTED",
            actor_id="participant-1",
            actor_role=ActorRole.PARTICIPANT
        )
    ]

    log_ids = await log_writer.write_batch(entries)
    assert len(log_ids) == 2
    
    db = get_firestore_client()
    doc1 = db.collection(UNIFIED_LOGS_COLLECTION).document(log_ids[0]).get()
    doc2 = db.collection(UNIFIED_LOGS_COLLECTION).document(log_ids[1]).get()
    
    assert doc1.exists
    assert doc2.exists


@require_emulator
@pytest.mark.asyncio
async def test_log_reader_query():
    """Debe poder consultar logs por study_id."""
    # Insertar data dummy
    entries = [
        LogEntry(study_id="test-study-A", layer=LogLayer.TECHNICAL, event_type="STUDY_CREATED", actor_id="sys", actor_role=ActorRole.SYSTEM),
        LogEntry(study_id="test-study-A", layer=LogLayer.METHODOLOGICAL, event_type="TASK_PRESENTED", actor_id="sys", actor_role=ActorRole.SYSTEM),
        LogEntry(study_id="test-study-B", layer=LogLayer.TECHNICAL, event_type="STUDY_CREATED", actor_id="sys", actor_role=ActorRole.SYSTEM),
    ]
    await log_writer.write_batch(entries)
    
    # Query por estudio A
    logs_a = await log_reader.query(study_id="test-study-A", layer=None, limit=10)
    assert len(logs_a) == 2
    
    # Query por estudio A y capa methodological
    logs_a_meth = await log_reader.query(study_id="test-study-A", layer=LogLayer.METHODOLOGICAL.value, limit=10)
    assert len(logs_a_meth) == 1
    assert logs_a_meth[0]["layer"] == "methodological"

    # Query por estudio B
    logs_b = await log_reader.query(study_id="test-study-B", layer=None, limit=10)
    assert len(logs_b) == 1
