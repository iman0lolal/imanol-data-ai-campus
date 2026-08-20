"use client";

import Link from "next/link";
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

export default function LearningPage() {
  const [topics, setTopics] = useState<LearningTopic[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [statusDraft, setStatusDraft] = useState<TopicStatus>("not_started");
  const [progressDraft, setProgressDraft] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadTopics() {
      try {
        const response = await fetch(`${apiBaseUrl}/learning/topics`);
        if (!response.ok) {
          throw new Error("Could not load learning topics.");
        }
        const data = (await response.json()) as LearningTopic[];
        setTopics(data);
        if (data.length > 0) {
          setSelectedId(data[0].id);
          setStatusDraft(data[0].status);
          setProgressDraft(data[0].progress);
        }
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Load failed.");
      } finally {
        setIsLoading(false);
      }
    }

    loadTopics();
  }, []);

  const selectedTopic = topics.find((topic) => topic.id === selectedId) ?? null;
  const groupedTopics = useMemo(() => {
    return topics.reduce<Record<string, LearningTopic[]>>((groups, topic) => {
      groups[topic.area] = [...(groups[topic.area] ?? []), topic];
      return groups;
    }, {});
  }, [topics]);

  function selectTopic(topic: LearningTopic) {
    setSelectedId(topic.id);
    setStatusDraft(topic.status);
    setProgressDraft(topic.progress);
    setError(null);
  }

  async function saveProgress() {
    if (selectedTopic === null) {
      return;
    }

    setIsSaving(true);
    setError(null);
    try {
      const response = await fetch(
        `${apiBaseUrl}/learning/topics/${selectedTopic.id}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            status: statusDraft,
            progress: progressDraft
          })
        }
      );
      if (!response.ok) {
        throw new Error("Could not save topic progress.");
      }

      const updatedTopic = (await response.json()) as LearningTopic;
      setTopics((currentTopics) =>
        currentTopics.map((topic) =>
          topic.id === updatedTopic.id ? updatedTopic : topic
        )
      );
      setSelectedId(updatedTopic.id);
      setStatusDraft(updatedTopic.status);
      setProgressDraft(updatedTopic.progress);
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
          <h1>Campus topics</h1>
        </div>
        <Link className="secondaryLink" href="/">
          Foundation
        </Link>
      </section>

      {error ? <p className="statusMessage error">{error}</p> : null}
      {isLoading ? <p className="statusMessage">Loading topics...</p> : null}

      {!isLoading && topics.length > 0 ? (
        <section className="learningLayout">
          <div className="topicList" aria-label="Learning topics by area">
            {Object.entries(groupedTopics).map(([area, areaTopics]) => (
              <section className="areaGroup" key={area}>
                <h2>{area}</h2>
                <div className="topicButtons">
                  {areaTopics.map((topic) => (
                    <div className="topicActionRow" key={topic.id}>
                      <button
                        className={
                          topic.id === selectedId
                            ? "topicButton selected"
                            : "topicButton"
                        }
                        onClick={() => selectTopic(topic)}
                        type="button"
                      >
                        <span>{topic.title}</span>
                        <span>{topic.progress}%</span>
                      </button>
                      <Link
                        className="topicOpenLink"
                        href={`/learning/${topic.id}`}
                      >
                        Open
                      </Link>
                    </div>
                  ))}
                </div>
              </section>
            ))}
          </div>

          {selectedTopic ? (
            <section className="topicDetail" aria-label="Selected topic">
              <div>
                <p className="eyebrow">{selectedTopic.area}</p>
                <h2>{selectedTopic.title}</h2>
                {selectedTopic.description ? (
                  <p>{selectedTopic.description}</p>
                ) : null}
              </div>

              <dl className="topicMeta">
                <div>
                  <dt>Difficulty</dt>
                  <dd>{difficultyLabels[selectedTopic.difficulty]}</dd>
                </div>
                <div>
                  <dt>Status</dt>
                  <dd>{statusLabels[selectedTopic.status]}</dd>
                </div>
                <div>
                  <dt>Progress</dt>
                  <dd>{selectedTopic.progress}%</dd>
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
                    onChange={(event) =>
                      setProgressDraft(Number(event.target.value))
                    }
                    type="number"
                    value={progressDraft}
                  />
                </label>

                <button
                  className="saveButton"
                  disabled={isSaving}
                  onClick={saveProgress}
                  type="button"
                >
                  {isSaving ? "Saving..." : "Save"}
                </button>
              </div>

              <Link
                className="secondaryLink detailLink"
                href={`/learning/${selectedTopic.id}`}
              >
                Open topic detail
              </Link>
            </section>
          ) : null}
        </section>
      ) : null}
    </main>
  );
}
