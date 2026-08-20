from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

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
        Base.metadata.drop_all(bind=engine)


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
