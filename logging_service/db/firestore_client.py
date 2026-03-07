"""
Cliente Firestore singleton para el servicio de logging.

Inicializa Firebase Admin SDK y expone el cliente de Firestore.
El SDK es síncrono — las llamadas se envuelven con run_in_executor
en los servicios que lo usan para no bloquear el event loop de FastAPI.
"""

import os

import firebase_admin
from firebase_admin import credentials, firestore


# Nombre de la colección principal de logs
UNIFIED_LOGS_COLLECTION = "unified_logs"

# Variable global para el cliente — se inicializa una sola vez
_db = None


def get_firestore_client():
    """
    Obtiene el cliente de Firestore (singleton).

    Si el emulador está configurado via FIRESTORE_EMULATOR_HOST,
    se conecta al emulador en lugar de producción.
    """
    global _db
    if _db is not None:
        return _db

    # Inicializar Firebase si no está inicializado
    if not firebase_admin._apps:
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # En emulador o Cloud Run (credenciales automáticas)
            firebase_admin.initialize_app()

    _db = firestore.client()
    return _db


def reset_client():
    """
    Reinicia el cliente — usado solo en tests para limpiar estado.
    """
    global _db
    _db = None
