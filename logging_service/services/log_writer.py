"""
Servicio de escritura de logs a Firestore.

Envuelve las operaciones síncronas del SDK de Firestore con
asyncio.run_in_executor para no bloquear el event loop de FastAPI.
"""

import asyncio
from functools import partial

from db.firestore_client import get_firestore_client, UNIFIED_LOGS_COLLECTION
from models.log_entry import LogEntry


# Límite máximo de escrituras por batch en Firestore
MAX_BATCH_SIZE = 500


async def write(entry: LogEntry) -> str:
    """
    Escribe una entrada de log individual a Firestore.

    Ejecuta la escritura síncrona en un thread pool para
    no bloquear el event loop.

    Args:
        entry: Entrada de log validada.

    Returns:
        log_id de la entrada creada.
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, partial(_sync_write, entry))
    return entry.log_id


async def write_batch(entries: list[LogEntry]) -> list[str]:
    """
    Escribe múltiples entradas de log a Firestore en un batch atómico.

    Usa db.batch() (escritura atómica) — NO transactions.
    Firestore limita los batches a 500 operaciones.

    Args:
        entries: Lista de entradas de log validadas.

    Returns:
        Lista de log_ids creados.

    Raises:
        ValueError: Si el batch excede MAX_BATCH_SIZE.
    """
    if len(entries) > MAX_BATCH_SIZE:
        raise ValueError(
            f"Batch size {len(entries)} exceeds maximum of {MAX_BATCH_SIZE}"
        )

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, partial(_sync_write_batch, entries))
    return [entry.log_id for entry in entries]


def _sync_write(entry: LogEntry) -> None:
    """Escritura síncrona de un log individual a Firestore."""
    db = get_firestore_client()
    doc_ref = db.collection(UNIFIED_LOGS_COLLECTION).document(entry.log_id)
    doc_ref.set(entry.to_firestore_dict())


def _sync_write_batch(entries: list[LogEntry]) -> None:
    """Escritura síncrona de un batch de logs a Firestore."""
    db = get_firestore_client()
    batch = db.batch()

    for entry in entries:
        doc_ref = db.collection(UNIFIED_LOGS_COLLECTION).document(entry.log_id)
        batch.set(doc_ref, entry.to_firestore_dict())

    batch.commit()
