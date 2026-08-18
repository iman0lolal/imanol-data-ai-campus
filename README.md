# Imanol Data & AI Campus

Imanol Data & AI Campus is a personal learning platform for Data Engineering,
Analytics, AI/ML, GenAI, Cloud, interview preparation, certifications, notes,
and personal projects.

This repository currently contains only the foundation: a minimal Next.js web
app, a minimal FastAPI backend, PostgreSQL for local development, Alembic for
future database migrations, Docker Compose, CI, and documentation.

## Stack

- Frontend: Next.js and TypeScript
- Backend: FastAPI and Python
- Database: PostgreSQL
- Migrations: Alembic
- Local development: Docker Compose
- CI: GitHub Actions
- Initial deployment target: Railway

## Repository Structure

```text
apps/
  web/      Next.js application
  api/      FastAPI application
docs/
  adr/      Architecture decision records
```

Root-level files provide shared project documentation, Docker Compose, example
environment variables, GitHub Actions, and agent guidance.

## Environment Setup

Copy `.env.example` to `.env` at the repository root for local development and
adjust values if needed. Run backend commands from the repository root so the
FastAPI settings read this single root `.env` file. The defaults are
development-only values and must not be reused as production secrets.

Required tools for local development:

- Docker Desktop with Docker Compose
- Node.js 24 or compatible
- Python 3.12 or newer

## Run Locally

Start the full local stack:

```bash
docker compose up --build
```

Expected endpoints:

- Web: http://localhost:3000
- API: http://localhost:8000
- Health: http://localhost:8000/health

## Useful Commands

Install frontend dependencies:

```bash
npm install
```

Run frontend checks:

```bash
npm run web:lint
npm run web:type-check
npm run web:build
```

Install backend dependencies:

```bash
python -m pip install -e "apps/api[dev]"
```

Run backend checks:

```bash
ruff format --check apps/api
ruff check apps/api
pytest apps/api
```

Run Alembic migrations:

```bash
alembic -c apps/api/alembic.ini upgrade head
```

On Windows PowerShell, if script execution blocks `npm`, use `npm.cmd` instead.

## Tests

The current backend test verifies that `GET /health` returns a successful
response. More tests should be added when real behavior is introduced.
