"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

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
  const [category, setCategory] = useState("");
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [questionType, setQuestionType] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
  }, [category, difficulty, questionType, topic]);

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
