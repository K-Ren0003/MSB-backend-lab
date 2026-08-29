from collections.abc import Iterator
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.app.db import Base, get_db
from api.app.main import app
from api.app.mongo import get_activity_collection


test_engine = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


@event.listens_for(test_engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class FakeCursor:
    def __init__(self, documents):
        self.documents = documents

    def sort(self, key, direction):
        reverse = direction == -1
        self.documents.sort(key=lambda document: document[key], reverse=reverse)
        return self

    def limit(self, count):
        self.documents = self.documents[:count]
        return self

    def __iter__(self):
        return iter(self.documents)


class FakeActivityCollection:
    def __init__(self):
        self.documents = []

    def insert_one(self, document):
        stored = deepcopy(document)
        stored["_id"] = len(self.documents) + 1
        self.documents.append(stored)

    def find(self):
        return FakeCursor(deepcopy(self.documents))


@pytest.fixture
def fake_activity_collection():
    return FakeActivityCollection()


@pytest.fixture
def client(fake_activity_collection) -> Iterator[TestClient]:
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_get_activity_collection():
        return fake_activity_collection

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[
        get_activity_collection
    ] = override_get_activity_collection

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
