"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type TopicStatus = "not_started" | "learning" | "reviewing" | "mastered";
type TopicDifficulty = "easy" | "medium" | "hard";

type LearningTopic = {
  id: number;
  title: string;
  area: string;
  description: string | null;
  notes: string | null;
  status: TopicStatus;
  difficulty: TopicDifficulty;
  progress: number;
  created_at: string;
  updated_at: string;
};

const statusLabels: Record<TopicStatus, string> = {
  not_started: "Not started",
  learning: "Learning",
  reviewing: "Reviewing",
  mastered: "Mastered"
};

const difficultyLabels: Record<TopicDifficulty, string> = {
  easy: "Easy",
  medium: "Medium",
  hard: "Hard"
};

export default function LearningTopicPage() {
  const params = useParams<{ id: string }>();
  const topicId = useMemo(() => Number(params.id), [params.id]);
  const [topic, setTopic] = useState<LearningTopic | null>(null);
  const [notesDraft, setNotesDraft] = useState("");
  const [statusDraft, setStatusDraft] = useState<TopicStatus>("not_started");
  const [progressDraft, setProgressDraft] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadTopic() {
      if (!Number.isInteger(topicId) || topicId <= 0) {
        setError("Topic not found.");
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch(`${apiBaseUrl}/learning/topics/${topicId}`);
        if (response.status === 404) {
          throw new Error("Topic not found.");
        }
        if (!response.ok) {
          throw new Error("Could not load topic.");
        }

        const data = (await response.json()) as LearningTopic;
        setTopic(data);
        setNotesDraft(data.notes ?? "");
        setStatusDraft(data.status);
        setProgressDraft(data.progress);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Load failed.");
      } finally {
        setIsLoading(false);
      }
    }

    loadTopic();
  }, [topicId]);

  async function saveTopic() {
    if (topic === null) {
      return;
    }

    setIsSaving(true);
    setError(null);
    setMessage(null);

    try {
      const response = await fetch(`${apiBaseUrl}/learning/topics/${topic.id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          notes: notesDraft.length > 0 ? notesDraft : null,
          status: statusDraft,
          progress: progressDraft
        })
      });

      if (!response.ok) {
        throw new Error("Could not save topic.");
      }

      const updatedTopic = (await response.json()) as LearningTopic;
      setTopic(updatedTopic);
      setNotesDraft(updatedTopic.notes ?? "");
      setStatusDraft(updatedTopic.status);
      setProgressDraft(updatedTopic.progress);
      setMessage("Saved.");
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Save failed.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="learningShell">
      <section className="learningHeader">
        <div>
          <p className="eyebrow">Learning Core</p>
          <h1>{topic ? topic.title : "Topic detail"}</h1>
        </div>
        <Link className="secondaryLink" href="/learning">
          All topics
        </Link>
      </section>

      {isLoading ? <p className="statusMessage">Loading topic...</p> : null}
      {error ? <p className="statusMessage error">{error}</p> : null}
      {message ? <p className="statusMessage success">{message}</p> : null}

      {!isLoading && topic ? (
        <section className="topicDetail topicDetailPage" aria-label="Topic detail">
          <div>
            <p className="eyebrow">{topic.area}</p>
            <h2>{topic.title}</h2>
            {topic.description ? <p>{topic.description}</p> : null}
          </div>

          <dl className="topicMeta">
            <div>
              <dt>Difficulty</dt>
              <dd>{difficultyLabels[topic.difficulty]}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{statusLabels[topic.status]}</dd>
            </div>
            <div>
              <dt>Progress</dt>
              <dd>{topic.progress}%</dd>
            </div>
          </dl>

          <div className="editPanel">
            <label>
              Status
              <select
                value={statusDraft}
                onChange={(event) =>
                  setStatusDraft(event.target.value as TopicStatus)
                }
              >
                {Object.entries(statusLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Progress
              <input
                max={100}
                min={0}
                onChange={(event) => setProgressDraft(Number(event.target.value))}
                type="number"
                value={progressDraft}
              />
            </label>
          </div>

          <label className="notesPanel">
            Personal notes
            <textarea
              onChange={(event) => {
                setNotesDraft(event.target.value);
                setMessage(null);
              }}
              placeholder="Write study notes, reminders, or questions for this topic."
              value={notesDraft}
            />
          </label>

          <button
            className="saveButton"
            disabled={isSaving}
            onClick={saveTopic}
            type="button"
          >
            {isSaving ? "Saving..." : "Save"}
          </button>
        </section>
      ) : null}
    </main>
  );
}
