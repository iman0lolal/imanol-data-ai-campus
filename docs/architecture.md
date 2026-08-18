# Architecture

Imanol Data & AI Campus is currently a modular monolith.

The system is intentionally small: one web application, one API application, one
PostgreSQL database, and supporting development/CI tooling. Future features
should be added as modules inside the FastAPI application unless there is a clear
reason to revisit the architecture.

## Next.js

Next.js owns the user interface and presentation layer. It should render pages,
components, and client-side interactions. It should not evolve into a second
independent backend with separate domain rules.

## FastAPI

FastAPI owns application and domain logic. Future modules for learning,
interviews, notes, projects, certifications, or AI features should begin here
when they require business rules, persistence, or integrations.

## PostgreSQL

PostgreSQL is the primary relational database. It is available locally through
Docker Compose and is accessed by the FastAPI application through environment
variables.

## Alembic

Alembic manages database migrations. No domain schema exists yet, but the
migration structure is in place so schema changes can be tracked from the start.

## Docker Compose

Docker Compose starts the local development stack: web, API, and PostgreSQL. It
is for local development convenience, not production orchestration.

## GitHub Actions

GitHub Actions runs pull request checks for frontend linting, type checking, and
builds, plus backend formatting, linting, and tests.

## Production Target

Railway is the initial production target. Deployment automation is intentionally
not included yet.
