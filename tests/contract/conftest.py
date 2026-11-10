"""Implementaciones de PDFRepository sobre las que corre el contrato.

- memory:    el fake usado por el resto de la suite.
- mongomock: el adaptador real de MongoDB sobre un Mongo en memoria.
- mongodb:   el adaptador real contra un servidor MongoDB (marca
             `integration`; se omite si no hay servidor disponible).

La base de integración es `<MONGODB_DATABASE>_test` y se elimina al
terminar: los tests nunca tocan la base de datos de la aplicación.
"""

import mongomock
import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config.settings import settings
from app.infrastructure.database_setup import setup_database
from app.infrastructure.mongo_pdf_repository import MongoPDFRepository
from tests.support.fakes import InMemoryPDFRepository

TEST_DATABASE = f"{settings.mongodb_database}_test"


@pytest.fixture(scope="session")
def mongo_server():
    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=1000)
    try:
        client.admin.command("ping")
    except PyMongoError as e:
        client.close()
        pytest.skip(f"MongoDB not available: {e}")
    yield client
    client.drop_database(TEST_DATABASE)
    client.close()


def _mongo_repository(client):
    client.drop_database(TEST_DATABASE)
    return MongoPDFRepository(setup_database(client[TEST_DATABASE]))


@pytest.fixture(
    params=[
        "memory",
        "mongomock",
        pytest.param("mongodb", marks=pytest.mark.integration),
    ]
)
def repo(request):
    if request.param == "memory":
        return InMemoryPDFRepository()
    if request.param == "mongomock":
        return _mongo_repository(mongomock.MongoClient())
    return _mongo_repository(request.getfixturevalue("mongo_server"))
