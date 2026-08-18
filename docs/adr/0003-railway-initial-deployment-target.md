# ADR 0003: Use Railway as the Initial Deployment Target

## Status

Accepted

## Context

The project needs a simple initial production target without introducing
infrastructure-heavy tooling.

## Decision

Use Railway as the initial deployment target.

## Consequences

The project can deploy without adding Kubernetes, Terraform, or custom
infrastructure automation. Deployment details will be handled separately when the
application is ready for that step.
