from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.learning.models import LearningResource
from app.main import app


@pytest.fixture
def engine() -> Iterator[Engine]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection: object, _: object) -> None:
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(engine: Engine) -> Iterator[TestClient]:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db() -> Iterator[Session]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_create_topic(client: TestClient) -> None:
    response = client.post(
        "/learning/topics",
        json={
            "title": "SQL fundamentals",
            "area": "Data Engineering",
            "description": "Practice querying relational data.",
            "status": "learning",
            "difficulty": "easy",
            "progress": 25,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "SQL fundamentals"
    assert data["notes"] is None
    assert data["status"] == "learning"
    assert data["progress"] == 25


def test_list_topics(client: TestClient) -> None:
    client.post(
        "/learning/topics",
        json={
            "title": "SQL fundamentals",
            "area": "Data Engineering",
            "difficulty": "easy",
        },
    )
    client.post(
        "/learning/topics",
        json={
            "title": "Embeddings",
            "area": "GenAI",
            "difficulty": "medium",
            "status": "reviewing",
            "progress": 40,
        },
    )

    response = client.get("/learning/topics")

    assert response.status_code == 200
    assert [topic["title"] for topic in response.json()] == [
        "SQL fundamentals",
        "Embeddings",
    ]


def test_update_status_and_progress(client: TestClient) -> None:
    created = client.post(
        "/learning/topics",
        json={
            "title": "Docker fundamentals",
            "area": "Cloud",
            "difficulty": "medium",
        },
    ).json()

    response = client.patch(
        f"/learning/topics/{created['id']}",
        json={"status": "reviewing", "progress": 75},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "reviewing"
    assert data["progress"] == 75


def test_save_read_and_clear_notes(client: TestClient) -> None:
    created = client.post(
        "/learning/topics",
        json={
            "title": "Embeddings",
            "area": "GenAI",
            "difficulty": "medium",
        },
    ).json()

    saved = client.patch(
        f"/learning/topics/{created['id']}",
        json={"notes": "Remember to compare cosine similarity and dot product."},
    )

    assert saved.status_code == 200
    assert saved.json()["notes"] == (
        "Remember to compare cosine similarity and dot product."
    )

    retrieved = client.get(f"/learning/topics/{created['id']}")

    assert retrieved.status_code == 200
    assert retrieved.json()["notes"] == (
        "Remember to compare cosine similarity and dot product."
    )

    cleared = client.patch(
        f"/learning/topics/{created['id']}",
        json={"notes": None},
    )

    assert cleared.status_code == 200
    assert cleared.json()["notes"] is None

    retrieved_after_clear = client.get(f"/learning/topics/{created['id']}")

    assert retrieved_after_clear.status_code == 200
    assert retrieved_after_clear.json()["notes"] is None


def test_create_and_list_resources_for_topic(client: TestClient) -> None:
    topic = client.post(
        "/learning/topics",
        json={
            "title": "Spark fundamentals",
            "area": "Data Engineering",
            "difficulty": "hard",
        },
    ).json()

    created = client.post(
        f"/learning/topics/{topic['id']}/resources",
        json={
            "title": "Spark SQL documentation",
            "url": "https://spark.apache.org/docs/latest/sql-programming-guide.html",
            "resource_type": "documentation",
            "description": "Official Spark SQL guide.",
        },
    )

    assert created.status_code == 201
    resource = created.json()
    assert resource["topic_id"] == topic["id"]
    assert resource["title"] == "Spark SQL documentation"
    assert resource["resource_type"] == "documentation"

    listed = client.get(f"/learning/topics/{topic['id']}/resources")

    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [resource["id"]]


def test_resource_is_attached_to_correct_topic(client: TestClient) -> None:
    first_topic = client.post(
        "/learning/topics",
        json={
            "title": "SQL fundamentals",
            "area": "Data Engineering",
            "difficulty": "easy",
        },
    ).json()
    second_topic = client.post(
        "/learning/topics",
        json={
            "title": "Embeddings",
            "area": "GenAI",
            "difficulty": "medium",
        },
    ).json()

    client.post(
        f"/learning/topics/{first_topic['id']}/resources",
        json={
            "title": "SQL tutorial",
            "url": "https://www.postgresql.org/docs/current/tutorial.html",
            "resource_type": "documentation",
        },
    )

    listed = client.get(f"/learning/topics/{second_topic['id']}/resources")

    assert listed.status_code == 200
    assert listed.json() == []


def test_resource_missing_topic_returns_404(client: TestClient) -> None:
    listed = client.get("/learning/topics/999/resources")
    created = client.post(
        "/learning/topics/999/resources",
        json={
            "title": "Missing parent",
            "url": "https://example.com/resource",
            "resource_type": "other",
        },
    )

    assert listed.status_code == 404
    assert listed.json()["detail"] == "Learning topic not found"
    assert created.status_code == 404
    assert created.json()["detail"] == "Learning topic not found"


def test_delete_resource(client: TestClient) -> None:
    topic = client.post(
        "/learning/topics",
        json={
            "title": "Python for data",
            "area": "Analytics",
            "difficulty": "easy",
        },
    ).json()
    resource = client.post(
        f"/learning/topics/{topic['id']}/resources",
        json={
            "title": "Python docs",
            "url": "https://docs.python.org/3/",
            "resource_type": "documentation",
        },
    ).json()

    deleted = client.delete(
        f"/learning/topics/{topic['id']}/resources/{resource['id']}"
    )
    listed = client.get(f"/learning/topics/{topic['id']}/resources")

    assert deleted.status_code == 204
    assert listed.status_code == 200
    assert listed.json() == []


def test_topic_delete_cascades_resources(client: TestClient, engine: Engine) -> None:
    topic = client.post(
        "/learning/topics",
        json={
            "title": "Docker fundamentals",
            "area": "Cloud",
            "difficulty": "medium",
        },
    ).json()
    client.post(
        f"/learning/topics/{topic['id']}/resources",
        json={
            "title": "Docker docs",
            "url": "https://docs.docker.com/",
            "resource_type": "documentation",
        },
    )

    response = client.delete(f"/learning/topics/{topic['id']}")

    with Session(engine) as db:
        remaining_resources = db.scalars(select(LearningResource)).all()

    assert response.status_code == 204
    assert remaining_resources == []


def test_rejects_invalid_progress(client: TestClient) -> None:
    response = client.post(
        "/learning/topics",
        json={
            "title": "Impossible progress",
            "area": "Analytics",
            "difficulty": "easy",
            "progress": 101,
        },
    )

    assert response.status_code == 422


def test_get_missing_topic_returns_404(client: TestClient) -> None:
    response = client.get("/learning/topics/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Learning topic not found"
