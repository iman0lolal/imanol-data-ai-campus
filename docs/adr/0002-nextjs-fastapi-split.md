# ADR 0002: Split Next.js and FastAPI Responsibilities

## Status

Accepted

## Context

The project needs a modern frontend and a Python backend suitable for Data and
AI work.

## Decision

Use Next.js with TypeScript for UI and presentation. Use FastAPI with Python for
application logic, domain behavior, persistence, and future integrations.

## Consequences

The frontend remains focused on user experience. Backend behavior has one clear
home in FastAPI, reducing the chance of duplicated domain logic.
