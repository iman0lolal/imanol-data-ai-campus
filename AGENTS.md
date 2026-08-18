# Agent Guidance

This repository is a personal learning platform and a software engineering
learning project. Keep changes small, clear, and easy to reverse.

## Working Rules

- Inspect existing code before modifying it.
- Keep PRs focused on the requested task.
- Prefer simple, explicit solutions.
- Do not introduce major dependencies without clear justification.
- Do not change architecture silently.
- Write or update tests when behavior changes.
- Update relevant documentation when structure, commands, or decisions change.
- Run applicable checks before declaring work complete.
- Never commit secrets.
- Do not implement unrelated improvements.
- Flag architectural uncertainty instead of guessing.

## Architecture Boundaries

- Treat the application as a modular monolith.
- FastAPI owns application and domain logic.
- Next.js owns UI and presentation.
- Do not add microservices, message brokers, standalone vector databases,
  complex agent frameworks, authentication, or multi-user features unless a
  future task explicitly approves them.

## Required Completion Summary

Every completed task or PR summary must include these sections:

### What changed

A concise description of the implementation.

### Why

Why the chosen implementation was used.

### Validation

Commands and tests executed.

### What Imanol should learn from this change

Explain 2-5 technical lessons from the implementation in clear language.
