# ADR 0001: Use a Monorepo

## Status

Accepted

## Context

The project includes a web app, an API, documentation, local development
tooling, and CI. It is a personal learning project where keeping related code
together should make changes easier to understand.

## Decision

Use a monorepo with `apps/web` for Next.js and `apps/api` for FastAPI.

## Consequences

Cross-application changes can be reviewed together. Tooling must stay simple so
the monorepo does not become harder to maintain than separate repositories.
