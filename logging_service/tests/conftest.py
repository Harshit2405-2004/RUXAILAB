"""
Configuración de pytest para el servicio de logging.
"""

import os
import pytest
from db.firestore_client import reset_client

@pytest.fixture(autouse=True)
def setup_env():
    """Configura variables de entorno para tests antes de cada prueba."""
    # Apuntar al emulador por defecto para los tests
    os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8081"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
    # Reiniciar cliente para asegurar conexión limpia
    reset_client()
    yield
    reset_client()
