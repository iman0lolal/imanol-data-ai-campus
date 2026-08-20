"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import type { FormEvent } from "react";
import { useEffect, useMemo, useState } from "react";

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type TopicStatus = "not_started" | "learning" | "reviewing" | "mastered";
type TopicDifficulty = "easy" | "medium" | "hard";
type ResourceType =
  | "documentation"
  | "article"
  | "video"
  | "course"
  | "repository"
  | "exercise"
  | "other";

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

type LearningResource = {
  id: number;
  topic_id: number;
  title: string;
  url: string;
  resource_type: ResourceType;
  description: string | null;
  created_at: string;
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

const resourceTypeLabels: Record<ResourceType, string> = {
  documentation: "Documentation",
  article: "Article",
  video: "Video",
  course: "Course",
  repository: "Repository",
  exercise: "Exercise",
  other: "Other"
};

const resourceTypes = Object.keys(resourceTypeLabels) as ResourceType[];

export default function LearningTopicPage() {
  const params = useParams<{ id: string }>();
  const topicId = useMemo(() => Number(params.id), [params.id]);
  const [topic, setTopic] = useState<LearningTopic | null>(null);
  const [resources, setResources] = useState<LearningResource[]>([]);
  const [notesDraft, setNotesDraft] = useState("");
  const [statusDraft, setStatusDraft] = useState<TopicStatus>("not_started");
  const [progressDraft, setProgressDraft] = useState(0);
  const [resourceTitle, setResourceTitle] = useState("");
  const [resourceUrl, setResourceUrl] = useState("");
  const [resourceType, setResourceType] = useState<ResourceType>("documentation");
  const [resourceDescription, setResourceDescription] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isAddingResource, setIsAddingResource] = useState(false);
  const [deletingResourceId, setDeletingResourceId] = useState<number | null>(
    null
  );
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
        const [topicResponse, resourcesResponse] = await Promise.all([
          fetch(`${apiBaseUrl}/learning/topics/${topicId}`),
          fetch(`${apiBaseUrl}/learning/topics/${topicId}/resources`)
        ]);

        if (topicResponse.status === 404) {
          throw new Error("Topic not found.");
        }
        if (!topicResponse.ok || !resourcesResponse.ok) {
          throw new Error("Could not load topic.");
        }

        const topicData = (await topicResponse.json()) as LearningTopic;
        const resourceData =
          (await resourcesResponse.json()) as LearningResource[];
        setTopic(topicData);
        setResources(resourceData);
        setNotesDraft(topicData.notes ?? "");
        setStatusDraft(topicData.status);
        setProgressDraft(topicData.progress);
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

  async function addResource(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (topic === null) {
      return;
    }

    setIsAddingResource(true);
    setError(null);
    setMessage(null);

    try {
      const response = await fetch(
        `${apiBaseUrl}/learning/topics/${topic.id}/resources`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            title: resourceTitle,
            url: resourceUrl,
            resource_type: resourceType,
            description:
              resourceDescription.length > 0 ? resourceDescription : null
          })
        }
      );

      if (!response.ok) {
        throw new Error("Could not add resource.");
      }

      const createdResource = (await response.json()) as LearningResource;
      setResources((currentResources) => [
        ...currentResources,
        createdResource
      ]);
      setResourceTitle("");
      setResourceUrl("");
      setResourceType("documentation");
      setResourceDescription("");
      setMessage("Resource added.");
    } catch (saveError) {
      setError(
        saveError instanceof Error ? saveError.message : "Resource save failed."
      );
    } finally {
      setIsAddingResource(false);
    }
  }

  async function deleteResource(resourceId: number) {
    if (topic === null) {
      return;
    }

    setDeletingResourceId(resourceId);
    setError(null);
    setMessage(null);

    try {
      const response = await fetch(
        `${apiBaseUrl}/learning/topics/${topic.id}/resources/${resourceId}`,
        {
          method: "DELETE"
        }
      );

      if (!response.ok) {
        throw new Error("Could not delete resource.");
      }

      setResources((currentResources) =>
        currentResources.filter((resource) => resource.id !== resourceId)
      );
      setMessage("Resource deleted.");
    } catch (deleteError) {
      setError(
        deleteError instanceof Error ? deleteError.message : "Delete failed."
      );
    } finally {
      setDeletingResourceId(null);
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

          <section className="resourcePanel" aria-label="Learning resources">
            <div>
              <h2>Resources</h2>
              <p>
                Keep useful docs, courses, videos, repositories, and exercises
                close to this topic.
              </p>
            </div>

            {resources.length > 0 ? (
              <ul className="resourceList">
                {resources.map((resource) => (
                  <li className="resourceItem" key={resource.id}>
                    <div>
                      <a href={resource.url} rel="noreferrer" target="_blank">
                        {resource.title}
                      </a>
                      <span>{resourceTypeLabels[resource.resource_type]}</span>
                      {resource.description ? (
                        <p>{resource.description}</p>
                      ) : null}
                    </div>
                    <button
                      className="secondaryButton"
                      disabled={deletingResourceId === resource.id}
                      onClick={() => deleteResource(resource.id)}
                      type="button"
                    >
                      {deletingResourceId === resource.id
                        ? "Deleting..."
                        : "Delete"}
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="emptyMessage">No resources yet.</p>
            )}

            <form className="resourceForm" onSubmit={addResource}>
              <label>
                Title
                <input
                  maxLength={160}
                  onChange={(event) => setResourceTitle(event.target.value)}
                  required
                  type="text"
                  value={resourceTitle}
                />
              </label>

              <label>
                URL
                <input
                  onChange={(event) => setResourceUrl(event.target.value)}
                  required
                  type="url"
                  value={resourceUrl}
                />
              </label>

              <label>
                Type
                <select
                  onChange={(event) =>
                    setResourceType(event.target.value as ResourceType)
                  }
                  value={resourceType}
                >
                  {resourceTypes.map((type) => (
                    <option key={type} value={type}>
                      {resourceTypeLabels[type]}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Description
                <textarea
                  onChange={(event) => setResourceDescription(event.target.value)}
                  value={resourceDescription}
                />
              </label>

              <button
                className="saveButton"
                disabled={isAddingResource}
                type="submit"
              >
                {isAddingResource ? "Adding..." : "Add resource"}
              </button>
            </form>
          </section>
        </section>
      ) : null}
    </main>
  );
}
