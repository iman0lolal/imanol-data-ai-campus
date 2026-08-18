const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function Home() {
  return (
    <main className="shell">
      <section className="intro">
        <p className="eyebrow">Repository foundation</p>
        <h1>Imanol Data & AI Campus</h1>
        <p>
          A clean starting point for a personal Data Engineering, Analytics,
          AI/ML, GenAI, Cloud, interview preparation, certifications, notes, and
          projects platform.
        </p>
        <div className="endpoints" aria-label="Local development endpoints">
          <span>Web: http://localhost:3000</span>
          <span>API: {apiBaseUrl}</span>
        </div>
      </section>
    </main>
  );
}
