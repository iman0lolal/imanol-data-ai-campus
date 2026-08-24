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


def test_progress_with_zero_attempts(client: TestClient) -> None:
    response = client.get("/interview/progress")

    assert response.status_code == 200
    data = response.json()
    assert data["overall"] == {
        "total_questions": 4,
        "attempted_questions": 0,
        "unattempted_questions": 4,
        "coverage_percentage": 0.0,
        "total_attempts": 0,
    }
    assert data["revisit_questions"] == []


def test_progress_counts_one_attempted_question(client: TestClient) -> None:
    question = client.get("/interview/questions", params={"category": "SQL"}).json()[0]
    client.post(
        f"/interview/questions/{question['id']}/attempts",
        json={"answer": "Group by email.", "confidence": "medium"},
    )

    response = client.get("/interview/progress")

    assert response.status_code == 200
    overall = response.json()["overall"]
    assert overall["attempted_questions"] == 1
    assert overall["unattempted_questions"] == 3
    assert overall["coverage_percentage"] == 25.0


def test_progress_counts_multiple_attempts_once_for_coverage(
    client: TestClient,
) -> None:
    question = client.get("/interview/questions", params={"category": "Python"}).json()[
        0
    ]
    client.post(
        f"/interview/questions/{question['id']}/attempts",
        json={"answer": "First answer."},
    )
    client.post(
        f"/interview/questions/{question['id']}/attempts",
        json={"answer": "Second answer.", "result": "acceptable"},
    )

    response = client.get("/interview/progress")

    assert response.status_code == 200
    overall = response.json()["overall"]
    assert overall["attempted_questions"] == 1
    assert overall["coverage_percentage"] == 25.0
    assert overall["total_attempts"] == 2


def test_progress_groups_by_category(client: TestClient) -> None:
    sql_question = client.get(
        "/interview/questions", params={"category": "SQL"}
    ).json()[0]
    spark_question = client.get(
        "/interview/questions", params={"category": "Spark"}
    ).json()[0]
    client.post(
        f"/interview/questions/{sql_question['id']}/attempts",
        json={"answer": "SQL answer."},
    )
    client.post(
        f"/interview/questions/{spark_question['id']}/attempts",
        json={"answer": "Spark answer."},
    )

    response = client.get("/interview/progress")

    categories = {item["name"]: item for item in response.json()["by_category"]}
    assert categories["SQL"]["attempted_questions"] == 1
    assert categories["SQL"]["coverage_percentage"] == 100.0
    assert categories["Spark"]["attempted_questions"] == 1
    assert categories["Behavioral"]["attempted_questions"] == 0


def test_progress_groups_by_difficulty(client: TestClient) -> None:
    medium_question = client.get(
        "/interview/questions", params={"category": "Spark"}
    ).json()[0]
    client.post(
        f"/interview/questions/{medium_question['id']}/attempts",
        json={"answer": "Spark answer."},
    )

    response = client.get("/interview/progress")

    difficulties = {item["name"]: item for item in response.json()["by_difficulty"]}
    assert difficulties["medium"]["total_questions"] == 2
    assert difficulties["medium"]["attempted_questions"] == 1
    assert difficulties["medium"]["coverage_percentage"] == 50.0
    assert difficulties["easy"]["attempted_questions"] == 0


def test_progress_revisit_uses_latest_attempt(client: TestClient) -> None:
    question = client.get("/interview/questions", params={"category": "SQL"}).json()[0]
    client.post(
        f"/interview/questions/{question['id']}/attempts",
        json={
            "answer": "Needs more work.",
            "confidence": "low",
            "result": "needs_work",
        },
    )
    client.post(
        f"/interview/questions/{question['id']}/attempts",
        json={
            "answer": "Improved answer.",
            "confidence": "high",
            "result": "strong",
        },
    )

    response = client.get("/interview/progress")

    assert response.status_code == 200
    assert response.json()["revisit_questions"] == []


def test_progress_revisit_includes_latest_low_or_needs_work(
    client: TestClient,
) -> None:
    question = client.get("/interview/questions", params={"category": "Python"}).json()[
        0
    ]
    client.post(
        f"/interview/questions/{question['id']}/attempts",
        json={
            "answer": "Still shaky.",
            "confidence": "low",
            "result": "acceptable",
        },
    )

    response = client.get("/interview/progress")

    revisit_questions = response.json()["revisit_questions"]
    assert len(revisit_questions) == 1
    assert revisit_questions[0]["id"] == question["id"]
    assert revisit_questions[0]["latest_confidence"] == "low"
    assert revisit_questions[0]["latest_result"] == "acceptable"


def test_filter_questions_by_attempted_state(client: TestClient) -> None:
    question = client.get("/interview/questions", params={"category": "SQL"}).json()[0]
    client.post(
        f"/interview/questions/{question['id']}/attempts",
        json={"answer": "SQL answer."},
    )

    attempted = client.get("/interview/questions", params={"attempted": "true"})
    unattempted = client.get("/interview/questions", params={"attempted": "false"})

    assert attempted.status_code == 200
    assert [item["id"] for item in attempted.json()] == [question["id"]]
    assert unattempted.status_code == 200
    assert question["id"] not in {item["id"] for item in unattempted.json()}
    assert len(unattempted.json()) == 3


def test_filter_questions_by_latest_self_assessment(client: TestClient) -> None:
    question = client.get("/interview/questions", params={"category": "Spark"}).json()[
        0
    ]
    client.post(
        f"/interview/questions/{question['id']}/attempts",
        json={"answer": "First answer.", "confidence": "low", "result": "needs_work"},
    )
    client.post(
        f"/interview/questions/{question['id']}/attempts",
        json={"answer": "Second answer.", "confidence": "high", "result": "strong"},
    )

    low_confidence = client.get("/interview/questions", params={"confidence": "low"})
    strong_result = client.get("/interview/questions", params={"result": "strong"})

    assert low_confidence.status_code == 200
    assert low_confidence.json() == []
    assert strong_result.status_code == 200
    assert [item["id"] for item in strong_result.json()] == [question["id"]]


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
