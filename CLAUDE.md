# Frontend Architecture Rules

This repository contains a Vue 3 + TypeScript application inside a lightweight pnpm monorepo.

The priority is:

- maintainability
- scalability
- testability
- explicit architecture boundaries
- long-term code health

# Mandatory Stack

- Vue 3
- TypeScript strict
- Vite
- Pinia
- Vue Router
- TanStack Query
- Zod
- Vitest
- Vue Testing Library
- Playwright

# Architecture Style

The frontend follows:

- Feature-first architecture
- Clean Architecture concepts
- SOLID principles
- Domain-oriented design

# Source Structure

src/
  app/
  shared/
  entities/
  features/
  pages/
  processes/

# Layer Responsibilities

## shared

Generic reusable technical code only.

Never contains business logic.

## entities

Core business entities:

- models
- DTOs
- mappers
- contracts

Must not depend on features/pages.

## features

Business use cases and orchestration.

Can depend on:

- shared
- entities

Must not depend on pages.

## pages

Page composition only.

Minimal logic.

# Forbidden

- Fetch calls directly in components
- DTO leakage into UI
- Giant Pinia stores
- God composables
- Circular dependencies
- Business logic in pages
- Deep relative imports
- Generic "services" dumping grounds

# Required

- Explicit typing
- Zod runtime validation
- Strong separation of concerns
- Small focused files
- Repository pattern where relevant
- Testable business logic
- Smart/Dumb component separation

# Testing

Business logic must be testable without Vue runtime.

Prefer:

- pure functions
- composables
- isolated domain logic

# Import Rules

Allowed:
shared -> none
entities -> shared
features -> entities/shared
pages -> features/entities/shared
app -> all

Forbidden:

- shared importing business layers
- entities importing features/pages
- features importing pages

# Quality Gates

After modifying any file in a service, always run that service's quality gates before reporting the task as done.

| Service modified | Command to run |
|---|---|
| `edge/orchestrator/` | `cd edge/orchestrator && make lint check tests` |
| `edge/camera/` | `cd edge/camera && make lint check unit_tests` |
| `edge/tflite_serving/` | `cd edge/tflite_serving && make lint check unit_tests` |
| `edge/cockpit/` | `cd edge/cockpit && make lint type_check unit_tests` |

Run from the repo root. If a quality gate fails, fix it before considering the task complete.

# Expectations

Whenever generating or refactoring code:

- preserve architecture integrity
- improve separation of concerns
- reduce coupling
- avoid overengineering
- keep code production-ready
