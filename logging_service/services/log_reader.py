"""
Servicio de lectura de logs desde Firestore.

Permite consultar logs filtrados por estudio y capa.
"""

import asyncio
from functools import partial

from google.cloud.firestore_v1.base_query import FieldFilter
from db.firestore_client import get_firestore_client, UNIFIED_LOGS_COLLECTION


async def query(study_id: str, layer: str | None = None, limit: int = 100) -> list[dict]:
    """
    Consulta logs en Firestore filtrando por study_id y opcionalmente por layer.
    
    Se ejecuta de forma no bloqueante usando run_in_executor.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(_sync_query, study_id, layer, limit))


def _sync_query(study_id: str, layer: str | None, limit: int) -> list[dict]:
    """Consulta síncrona a Firestore."""
    db = get_firestore_client()
    logs_query = db.collection(UNIFIED_LOGS_COLLECTION).where(filter=FieldFilter("study_id", "==", study_id))
    
    if layer:
        logs_query = logs_query.where(filter=FieldFilter("layer", "==", layer))
        
    # Ordenar por timestamp descendente y aplicar límite
    # Nota: Requiere índice compuesto en Firestore si se usa layer + orderBy
    # Para el POC simplificaremos obteniendo los documentos y ordenándolos si es necesario, 
    # o asumiendo orden natural si no se provee orderBy complejo.
    logs_query = logs_query.order_by("timestamp", direction="DESCENDING").limit(limit)
    
    results = []
    for doc in logs_query.stream():
        data = doc.to_dict()
        # Firestore devuelve Datetime con TZ. Lo convertimos a ISO format para JSON.
        if "timestamp" in data and hasattr(data["timestamp"], "isoformat"):
            data["timestamp"] = data["timestamp"].isoformat()
        results.append(data)
        
    return results
