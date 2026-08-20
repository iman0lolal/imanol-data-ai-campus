"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type QuestionType = "coding" | "conceptual" | "scenario" | "behavioral";
type Difficulty = "easy" | "medium" | "hard";
type AnswerFormat = "sql" | "python" | "free_text" | "star";
type Confidence = "low" | "medium" | "high";
type Result = "needs_work" | "acceptable" | "strong";

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

type InterviewAttempt = {
  id: number;
  question_id: number;
  answer: string;
  confidence: Confidence | null;
  result: Result | null;
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

const confidenceLabels: Record<Confidence, string> = {
  low: "Low",
  medium: "Medium",
  high: "High"
};

const resultLabels: Record<Result, string> = {
  needs_work: "Needs work",
  acceptable: "Acceptable",
  strong: "Strong"
};

const confidences: Confidence[] = ["low", "medium", "high"];
const results: Result[] = ["needs_work", "acceptable", "strong"];

export default function InterviewQuestionPage() {
  const params = useParams<{ id: string }>();
  const questionId = useMemo(() => Number(params.id), [params.id]);
  const [question, setQuestion] = useState<InterviewQuestion | null>(null);
  const [attempts, setAttempts] = useState<InterviewAttempt[]>([]);
  const [answerDraft, setAnswerDraft] = useState("");
  const [confidenceDraft, setConfidenceDraft] = useState("");
  const [resultDraft, setResultDraft] = useState("");
  const [isReferenceVisible, setIsReferenceVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSavingAttempt, setIsSavingAttempt] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadQuestion() {
      if (!Number.isInteger(questionId) || questionId <= 0) {
        setError("Interview question not found.");
        setIsLoading(false);
        return;
      }

      try {
        const [questionResponse, attemptsResponse] = await Promise.all([
          fetch(`${apiBaseUrl}/interview/questions/${questionId}`),
          fetch(`${apiBaseUrl}/interview/questions/${questionId}/attempts`)
        ]);
        if (questionResponse.status === 404) {
          throw new Error("Interview question not found.");
        }
        if (!questionResponse.ok || !attemptsResponse.ok) {
          throw new Error("Could not load interview question.");
        }

        setQuestion((await questionResponse.json()) as InterviewQuestion);
        setAttempts((await attemptsResponse.json()) as InterviewAttempt[]);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Load failed.");
      } finally {
        setIsLoading(false);
      }
    }

    loadQuestion();
  }, [questionId]);

  async function saveAttempt() {
    if (question === null) {
      return;
    }

    setIsSavingAttempt(true);
    setError(null);
    setMessage(null);

    try {
      const response = await fetch(
        `${apiBaseUrl}/interview/questions/${question.id}/attempts`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            answer: answerDraft,
            confidence: confidenceDraft.length > 0 ? confidenceDraft : null,
            result: resultDraft.length > 0 ? resultDraft : null
          })
        }
      );

      if (!response.ok) {
        throw new Error("Could not save attempt.");
      }

      const createdAttempt = (await response.json()) as InterviewAttempt;
      setAttempts((currentAttempts) => [createdAttempt, ...currentAttempts]);
      setAnswerDraft("");
      setConfidenceDraft("");
      setResultDraft("");
      setMessage("Attempt saved.");
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Save failed.");
    } finally {
      setIsSavingAttempt(false);
    }
  }

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
      {message ? <p className="statusMessage success">{message}</p> : null}

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
              onChange={(event) => {
                setAnswerDraft(event.target.value);
                setMessage(null);
              }}
              placeholder="Write your practice answer."
              value={answerDraft}
            />
          </label>

          <div className="attemptControls">
            <label>
              Confidence
              <select
                onChange={(event) => setConfidenceDraft(event.target.value)}
                value={confidenceDraft}
              >
                <option value="">Not set</option>
                {confidences.map((confidence) => (
                  <option key={confidence} value={confidence}>
                    {confidenceLabels[confidence]}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Result
              <select
                onChange={(event) => setResultDraft(event.target.value)}
                value={resultDraft}
              >
                <option value="">Not set</option>
                {results.map((result) => (
                  <option key={result} value={result}>
                    {resultLabels[result]}
                  </option>
                ))}
              </select>
            </label>

            <button
              className="saveButton"
              disabled={isSavingAttempt || answerDraft.trim().length === 0}
              onClick={saveAttempt}
              type="button"
            >
              {isSavingAttempt ? "Saving..." : "Save attempt"}
            </button>
          </div>

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

          <section className="attemptHistory" aria-label="Previous attempts">
            <h2>Previous attempts</h2>
            {attempts.length > 0 ? (
              <div className="attemptList">
                {attempts.map((attempt) => (
                  <article className="attemptItem" key={attempt.id}>
                    <div className="questionMeta">
                      <span>
                        {new Date(attempt.created_at).toLocaleString(undefined, {
                          dateStyle: "medium",
                          timeStyle: "short"
                        })}
                      </span>
                      {attempt.confidence ? (
                        <span>{confidenceLabels[attempt.confidence]}</span>
                      ) : null}
                      {attempt.result ? (
                        <span>{resultLabels[attempt.result]}</span>
                      ) : null}
                    </div>
                    <p>{attempt.answer}</p>
                  </article>
                ))}
              </div>
            ) : (
              <p className="emptyMessage">No saved attempts yet.</p>
            )}
          </section>
        </section>
      ) : null}
    </main>
  );
}
