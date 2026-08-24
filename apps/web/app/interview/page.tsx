"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type QuestionType = "coding" | "conceptual" | "scenario" | "behavioral";
type Difficulty = "easy" | "medium" | "hard";
type AnswerFormat = "sql" | "python" | "free_text" | "star";
type Confidence = "low" | "medium" | "high";
type Result = "needs_work" | "acceptable" | "strong";
type AttemptFilter = "all" | "attempted" | "unattempted";

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

type ProgressOverall = {
  total_questions: number;
  attempted_questions: number;
  unattempted_questions: number;
  coverage_percentage: number;
  total_attempts: number;
};

type ProgressBreakdownItem = {
  name: string;
  total_questions: number;
  attempted_questions: number;
  coverage_percentage: number;
};

type RevisitQuestion = {
  id: number;
  question: string;
  category: string;
  topic: string;
  difficulty: Difficulty;
  latest_confidence: Confidence | null;
  latest_result: Result | null;
  latest_attempted_at: string;
};

type InterviewProgress = {
  overall: ProgressOverall;
  by_category: ProgressBreakdownItem[];
  by_difficulty: ProgressBreakdownItem[];
  revisit_questions: RevisitQuestion[];
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

const categories = ["SQL", "Python", "Spark", "Azure", "Behavioral"];
const difficulties: Difficulty[] = ["easy", "medium", "hard"];
const questionTypes: QuestionType[] = [
  "coding",
  "conceptual",
  "scenario",
  "behavioral"
];

export default function InterviewPage() {
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [progress, setProgress] = useState<InterviewProgress | null>(null);
  const [category, setCategory] = useState("");
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [questionType, setQuestionType] = useState("");
  const [attemptFilter, setAttemptFilter] = useState<AttemptFilter>("all");
  const [isLoading, setIsLoading] = useState(true);
  const [isProgressLoading, setIsProgressLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadProgress() {
      setIsProgressLoading(true);
      setError(null);

      try {
        const response = await fetch(`${apiBaseUrl}/interview/progress`);
        if (!response.ok) {
          throw new Error("Could not load interview progress.");
        }

        setProgress((await response.json()) as InterviewProgress);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Load failed.");
      } finally {
        setIsProgressLoading(false);
      }
    }

    loadProgress();
  }, []);

  useEffect(() => {
    async function loadQuestions() {
      setIsLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (category.length > 0) {
        params.set("category", category);
      }
      if (topic.length > 0) {
        params.set("topic", topic);
      }
      if (difficulty.length > 0) {
        params.set("difficulty", difficulty);
      }
      if (questionType.length > 0) {
        params.set("question_type", questionType);
      }
      if (attemptFilter === "attempted") {
        params.set("attempted", "true");
      }
      if (attemptFilter === "unattempted") {
        params.set("attempted", "false");
      }

      try {
        const queryString = params.toString();
        const response = await fetch(
          `${apiBaseUrl}/interview/questions${queryString ? `?${queryString}` : ""}`
        );
        if (!response.ok) {
          throw new Error("Could not load interview questions.");
        }

        setQuestions((await response.json()) as InterviewQuestion[]);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Load failed.");
      } finally {
        setIsLoading(false);
      }
    }

    loadQuestions();
  }, [attemptFilter, category, difficulty, questionType, topic]);

  return (
    <main className="learningShell">
      <section className="learningHeader">
        <div>
          <p className="eyebrow">Interview Lab</p>
          <h1>Question bank</h1>
        </div>
        <Link className="secondaryLink" href="/">
          Home
        </Link>
      </section>

      {error ? <p className="statusMessage error">{error}</p> : null}

      <section className="progressOverview" aria-label="Interview progress">
        {isProgressLoading ? (
          <p className="statusMessage">Loading progress...</p>
        ) : null}

        {!isProgressLoading && progress ? (
          <>
            <div className="progressSummary">
              <div>
                <p className="eyebrow">Progress</p>
                <h2>
                  {progress.overall.attempted_questions} /{" "}
                  {progress.overall.total_questions} attempted
                </h2>
                <div
                  aria-label={`${progress.overall.coverage_percentage}% coverage`}
                  className="progressBar"
                >
                  <span
                    style={{
                      width: `${progress.overall.coverage_percentage}%`
                    }}
                  />
                </div>
              </div>
              <dl className="summaryStats">
                <div>
                  <dt>Coverage</dt>
                  <dd>{progress.overall.coverage_percentage}%</dd>
                </div>
                <div>
                  <dt>Attempts</dt>
                  <dd>{progress.overall.total_attempts}</dd>
                </div>
                <div>
                  <dt>Not attempted</dt>
                  <dd>{progress.overall.unattempted_questions}</dd>
                </div>
              </dl>
            </div>

            <div className="progressBreakdowns">
              <ProgressBreakdown
                items={progress.by_category}
                title="By category"
              />
              <ProgressBreakdown
                items={progress.by_difficulty.map((item) => ({
                  ...item,
                  name:
                    difficultyLabels[item.name as Difficulty] ?? item.name
                }))}
                title="By difficulty"
              />
            </div>

            <section className="revisitPanel" aria-label="Needs review">
              <div>
                <p className="eyebrow">Practice next</p>
                <h2>Needs review</h2>
              </div>
              {progress.revisit_questions.length > 0 ? (
                <div className="revisitList">
                  {progress.revisit_questions.map((question) => (
                    <Link
                      className="revisitItem"
                      href={`/interview/${question.id}`}
                      key={question.id}
                    >
                      <span>{question.category}</span>
                      <strong>{question.question}</strong>
                      <small>
                        {question.latest_confidence
                          ? confidenceLabels[question.latest_confidence]
                          : "No confidence"}{" "}
                        /{" "}
                        {question.latest_result
                          ? resultLabels[question.latest_result]
                          : "No result"}
                      </small>
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="emptyMessage">
                  No low-confidence or needs-work questions yet.
                </p>
              )}
            </section>
          </>
        ) : null}
      </section>

      <section className="questionBank">
        <form className="filterPanel">
          <label>
            Category
            <select
              onChange={(event) => setCategory(event.target.value)}
              value={category}
            >
              <option value="">All categories</option>
              {categories.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </label>

          <label>
            Topic
            <input
              onChange={(event) => setTopic(event.target.value)}
              placeholder="Exact topic"
              type="text"
              value={topic}
            />
          </label>

          <label>
            Difficulty
            <select
              onChange={(event) => setDifficulty(event.target.value)}
              value={difficulty}
            >
              <option value="">All difficulties</option>
              {difficulties.map((value) => (
                <option key={value} value={value}>
                  {difficultyLabels[value]}
                </option>
              ))}
            </select>
          </label>

          <label>
            Type
            <select
              onChange={(event) => setQuestionType(event.target.value)}
              value={questionType}
            >
              <option value="">All types</option>
              {questionTypes.map((value) => (
                <option key={value} value={value}>
                  {questionTypeLabels[value]}
                </option>
              ))}
            </select>
          </label>

          <label>
            Attempts
            <select
              onChange={(event) =>
                setAttemptFilter(event.target.value as AttemptFilter)
              }
              value={attemptFilter}
            >
              <option value="all">All questions</option>
              <option value="attempted">Attempted</option>
              <option value="unattempted">Not attempted</option>
            </select>
          </label>
        </form>

        {isLoading ? <p className="statusMessage">Loading questions...</p> : null}

        {!isLoading ? (
          <div className="questionList" aria-label="Interview questions">
            {questions.map((question) => (
              <article className="questionItem" key={question.id}>
                <div>
                  <p className="eyebrow">{question.category}</p>
                  <h2>{question.question}</h2>
                  <p>
                    {question.topic}
                    {question.subtopic ? ` / ${question.subtopic}` : ""}
                  </p>
                  <div className="questionMeta">
                    <span>{difficultyLabels[question.difficulty]}</span>
                    <span>{questionTypeLabels[question.question_type]}</span>
                    <span>{question.answer_format}</span>
                  </div>
                </div>
                <Link className="secondaryLink" href={`/interview/${question.id}`}>
                  Open
                </Link>
              </article>
            ))}
            {questions.length === 0 ? (
              <p className="emptyMessage">No questions match these filters.</p>
            ) : null}
          </div>
        ) : null}
      </section>
    </main>
  );
}

function ProgressBreakdown({
  items,
  title
}: {
  items: ProgressBreakdownItem[];
  title: string;
}) {
  return (
    <section className="breakdownPanel" aria-label={title}>
      <h2>{title}</h2>
      <div className="breakdownList">
        {items.map((item) => (
          <div className="breakdownItem" key={item.name}>
            <div>
              <strong>{item.name}</strong>
              <span>
                {item.attempted_questions} / {item.total_questions}
              </span>
            </div>
            <div
              aria-label={`${item.coverage_percentage}% coverage`}
              className="progressBar"
            >
              <span style={{ width: `${item.coverage_percentage}%` }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
