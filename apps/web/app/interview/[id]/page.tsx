"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type QuestionType = "coding" | "conceptual" | "scenario" | "behavioral";
type Difficulty = "easy" | "medium" | "hard";
type AnswerFormat = "sql" | "python" | "free_text" | "star";

type InterviewQuestion = {
  id: number;
  question: string;
  category: string;
  topic: string;
  subtopic: string | null;
  question_type: QuestionType;
  difficulty: Difficulty;
  answer_format: AnswerFormat;
  expected_concepts: string | null;
  reference_answer: string | null;
  source: string | null;
  source_context: string | null;
  created_at: string;
};

const questionTypeLabels: Record<QuestionType, string> = {
  coding: "Coding",
  conceptual: "Conceptual",
  scenario: "Scenario",
  behavioral: "Behavioral"
};

const difficultyLabels: Record<Difficulty, string> = {
  easy: "Easy",
  medium: "Medium",
  hard: "Hard"
};

const answerFormatLabels: Record<AnswerFormat, string> = {
  sql: "SQL",
  python: "Python",
  free_text: "Free text",
  star: "STAR"
};

export default function InterviewQuestionPage() {
  const params = useParams<{ id: string }>();
  const questionId = useMemo(() => Number(params.id), [params.id]);
  const [question, setQuestion] = useState<InterviewQuestion | null>(null);
  const [answerDraft, setAnswerDraft] = useState("");
  const [isReferenceVisible, setIsReferenceVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadQuestion() {
      if (!Number.isInteger(questionId) || questionId <= 0) {
        setError("Interview question not found.");
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch(
          `${apiBaseUrl}/interview/questions/${questionId}`
        );
        if (response.status === 404) {
          throw new Error("Interview question not found.");
        }
        if (!response.ok) {
          throw new Error("Could not load interview question.");
        }

        setQuestion((await response.json()) as InterviewQuestion);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Load failed.");
      } finally {
        setIsLoading(false);
      }
    }

    loadQuestion();
  }, [questionId]);

  return (
    <main className="learningShell">
      <section className="learningHeader">
        <div>
          <p className="eyebrow">Interview Lab</p>
          <h1>{question ? question.category : "Question detail"}</h1>
        </div>
        <Link className="secondaryLink" href="/interview">
          Question bank
        </Link>
      </section>

      {isLoading ? <p className="statusMessage">Loading question...</p> : null}
      {error ? <p className="statusMessage error">{error}</p> : null}

      {!isLoading && question ? (
        <section className="interviewDetail" aria-label="Interview question">
          <div>
            <p className="eyebrow">
              {question.topic}
              {question.subtopic ? ` / ${question.subtopic}` : ""}
            </p>
            <h2>{question.question}</h2>
          </div>

          <dl className="topicMeta">
            <div>
              <dt>Difficulty</dt>
              <dd>{difficultyLabels[question.difficulty]}</dd>
            </div>
            <div>
              <dt>Type</dt>
              <dd>{questionTypeLabels[question.question_type]}</dd>
            </div>
            <div>
              <dt>Answer</dt>
              <dd>{answerFormatLabels[question.answer_format]}</dd>
            </div>
          </dl>

          {question.answer_format === "star" ? (
            <div className="starHint" aria-label="STAR answer hint">
              <span>Situation</span>
              <span>Task</span>
              <span>Action</span>
              <span>Result</span>
            </div>
          ) : null}

          <label className="answerPanel">
            Your answer
            <textarea
              onChange={(event) => setAnswerDraft(event.target.value)}
              placeholder="Draft your answer locally. Attempts are saved in the next slice."
              value={answerDraft}
            />
          </label>

          <button
            className="saveButton"
            onClick={() => setIsReferenceVisible((isVisible) => !isVisible)}
            type="button"
          >
            {isReferenceVisible ? "Hide reference" : "Reveal reference answer"}
          </button>

          {isReferenceVisible ? (
            <section className="referencePanel">
              {question.expected_concepts ? (
                <div>
                  <h2>Expected concepts</h2>
                  <p>{question.expected_concepts}</p>
                </div>
              ) : null}
              {question.reference_answer ? (
                <div>
                  <h2>Reference answer</h2>
                  <p>{question.reference_answer}</p>
                </div>
              ) : null}
            </section>
          ) : null}
        </section>
      ) : null}
    </main>
  );
}
