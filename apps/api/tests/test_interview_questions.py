import importlib.util
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.interview.models import InterviewQuestion
from app.main import app


@pytest.fixture
def engine() -> Iterator[Engine]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        db.add_all(
            [
                InterviewQuestion(
                    question="Find duplicate email addresses in a Person table.",
                    category="SQL",
                    topic="Aggregation",
                    question_type="coding",
                    difficulty="easy",
                    answer_format="sql",
                    expected_concepts="GROUP BY, HAVING, COUNT",
                    reference_answer="Group by email and filter count greater than 1.",
                ),
                InterviewQuestion(
                    question="Generate an infinite Fibonacci sequence.",
                    category="Python",
                    topic="Generators",
                    question_type="coding",
                    difficulty="medium",
                    answer_format="python",
                    expected_concepts="yield, loop, state variables",
                    reference_answer="Yield values while updating two state variables.",
                ),
                InterviewQuestion(
                    question="Explain Spark lazy evaluation and the DAG.",
                    category="Spark",
                    topic="Execution model",
                    question_type="conceptual",
                    difficulty="medium",
                    answer_format="free_text",
                    expected_concepts="Transformations, actions, DAG",
                    reference_answer=(
                        "Transformations build a DAG that actions execute."
                    ),
                ),
                InterviewQuestion(
                    question="How do you handle tight client deadlines?",
                    category="Behavioral",
                    topic="Delivery",
                    question_type="behavioral",
                    difficulty="easy",
                    answer_format="star",
                    expected_concepts="Prioritization, communication, scope",
                    reference_answer=(
                        "Use STAR and explain communication and tradeoffs."
                    ),
                ),
            ]
        )
        db.commit()

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


def test_list_questions(client: TestClient) -> None:
    response = client.get("/interview/questions")

    assert response.status_code == 200
    assert len(response.json()) == 4


def test_filter_questions(client: TestClient) -> None:
    response = client.get(
        "/interview/questions",
        params={"category": "SQL", "difficulty": "easy", "question_type": "coding"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "SQL"
    assert data[0]["question_type"] == "coding"


def test_get_question_detail(client: TestClient) -> None:
    listed = client.get("/interview/questions", params={"category": "Python"}).json()

    response = client.get(f"/interview/questions/{listed[0]['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "Generate an infinite Fibonacci sequence."
    assert data["answer_format"] == "python"
    assert data["expected_concepts"] == "yield, loop, state variables"


def test_missing_question_returns_404(client: TestClient) -> None:
    response = client.get("/interview/questions/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Interview question not found"


def test_create_attempt(client: TestClient) -> None:
    question = client.get("/interview/questions", params={"category": "SQL"}).json()[0]

    response = client.post(
        f"/interview/questions/{question['id']}/attempts",
        json={
            "answer": "I would group by email and use HAVING count greater than 1.",
            "confidence": "medium",
            "result": "acceptable",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["question_id"] == question["id"]
    assert data["confidence"] == "medium"
    assert data["result"] == "acceptable"


def test_retrieve_attempts_persists_answers(client: TestClient) -> None:
    question = client.get("/interview/questions", params={"category": "Python"}).json()[
        0
    ]
    client.post(
        f"/interview/questions/{question['id']}/attempts",
        json={"answer": "Use a generator with yield.", "confidence": "high"},
    )

    response = client.get(f"/interview/questions/{question['id']}/attempts")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["answer"] == "Use a generator with yield."
    assert data[0]["confidence"] == "high"
    assert data[0]["result"] is None


def test_attempts_missing_question_returns_404(client: TestClient) -> None:
    listed = client.get("/interview/questions/999/attempts")
    created = client.post(
        "/interview/questions/999/attempts",
        json={"answer": "Missing parent answer"},
    )

    assert listed.status_code == 404
    assert listed.json()["detail"] == "Interview question not found"
    assert created.status_code == 404
    assert created.json()["detail"] == "Interview question not found"


def test_attempts_are_returned_newest_first(client: TestClient) -> None:
    question = client.get("/interview/questions", params={"category": "Spark"}).json()[
        0
    ]
    first = client.post(
        f"/interview/questions/{question['id']}/attempts",
        json={"answer": "First attempt"},
    ).json()
    second = client.post(
        f"/interview/questions/{question['id']}/attempts",
        json={"answer": "Second attempt", "result": "needs_work"},
    ).json()

    response = client.get(f"/interview/questions/{question['id']}/attempts")

    assert response.status_code == 200
    assert [attempt["id"] for attempt in response.json()] == [
        second["id"],
        first["id"],
    ]


def test_seed_data_count_and_content_sanity() -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "20260820_1135_create_interview_questions.py"
    )
    spec = importlib.util.spec_from_file_location("interview_seed", migration_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    seed_questions = module.INTERVIEW_QUESTIONS

    assert len(seed_questions) == 33
    assert {question["category"] for question in seed_questions} == {
        "SQL",
        "Python",
        "Spark",
        "Azure",
        "Behavioral",
    }
    assert any(
        question["question"] == "Find the second highest salary."
        for question in seed_questions
    )
