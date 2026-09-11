# DevFlow — AI-Powered Developer Collaboration & Code Review Platform

[![DevFlow CI](https://github.com/1234ashutosh1234/devflow/actions/workflows/ci.yml/badge.svg)](https://github.com/1234ashutosh1234/devflow/actions/workflows/ci.yml)

> A full-stack developer collaboration platform that connects GitHub Pull Requests to automated code review, structured findings, PostgreSQL persistence, and a recruiter-friendly review dashboard.

## Overview

DevFlow turns a GitHub Pull Request into a repeatable code-review workflow:

```text
Developer pushes code
        ↓
GitHub Pull Request
        ↓
GitHub webhook
        ↓
FastAPI backend
        ↓
Webhook signature validation
        ↓
GitHub PR metadata + unified diff
        ↓
Multi-file diff parsing
        ↓
Automated review engine
        ↓
Structured findings + score
        ↓
PostgreSQL persistence
        ↓
Review dashboard / GitHub review publishing
```

The project demonstrates backend API design, relational data modeling, authentication, event-driven processing, GitHub API integration, automated static-analysis style checks, React UI development, Docker-based local infrastructure, and CI validation.

## What is working

- JWT authentication with password hashing
- Organization, project, repository, Pull Request, review, and finding data models
- FastAPI REST API with protected endpoints
- PostgreSQL persistence using SQLAlchemy
- Alembic database migrations
- GitHub Pull Request integration
- GitHub `pull_request` webhook handling
- HMAC-SHA256 webhook signature verification
- Pull Request metadata and unified diff retrieval
- Multi-file diff parsing and reviewable-line detection
- Deterministic local automated review provider
- Structured findings with severity and confidence
- Review score calculation
- Review history and findings dashboard
- GitHub review publishing endpoint
- React/Vite frontend for projects, Pull Requests, reviews, findings, and GitHub review execution
- GitHub Actions CI for backend tests plus frontend lint/build

## Product flow

### Dashboard

The dashboard summarizes:

- Pull Request count
- Review count
- Finding count
- Average review score
- Recent review activity
- Review health

### Projects

The Projects view loads organization/project data and displays connected repositories, provider, and default branch.

### Pull Requests

The Pull Requests view loads repository Pull Requests and exposes review history for each Pull Request.

### Reviews

The Reviews view shows review status, score, summary, and associated Pull Request information.

### Review details

A review detail page displays each finding with:

- severity
- category
- title
- file/line information when available
- description
- remediation suggestion

### GitHub

The GitHub page can invoke the existing DevFlow GitHub review endpoint for a connected repository and Pull Request number.

## Architecture

```text
                          ┌──────────────────────────┐
                          │        Developer         │
                          │      pushes changes      │
                          └────────────┬─────────────┘
                                       │
                                       ▼
                          ┌──────────────────────────┐
                          │          GitHub          │
                          │      Pull Request       │
                          └────────────┬─────────────┘
                                       │
                                pull_request event
                                       │
                                       ▼
                          ┌──────────────────────────┐
                          │   Public webhook URL     │
                          │    during local dev      │
                          └────────────┬─────────────┘
                                       │
                                       ▼
                    ┌───────────────────────────────────┐
                    │         FastAPI backend            │
                    │                                   │
                    │ auth · projects · reviews · GitHub│
                    └───────────────┬───────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Webhook verification │
                         │    HMAC-SHA256       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    GitHub client     │
                         │  PR + unified diff   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     Diff parser      │
                         │ multi-file changes   │
                         │ reviewable lines     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Review engine     │
                         │ security             │
                         │ maintainability      │
                         │ performance          │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    PostgreSQL        │
                         │ reviews + findings   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                 ┌────────────────────────────────────────┐
                 │           React / Vite UI              │
                 │ dashboard · projects · PRs · reviews  │
                 │ findings · GitHub review execution     │
                 └────────────────────────────────────────┘
```

## Backend API surface

### Authentication

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### Organizations

```text
GET  /api/v1/organizations
POST /api/v1/organizations
GET  /api/v1/organizations/{organization_id}/members
POST /api/v1/organizations/{organization_id}/members
```

### Projects and repositories

```text
GET  /api/v1/projects/organizations/{organization_id}
POST /api/v1/projects/organizations/{organization_id}
GET  /api/v1/projects/{project_id}
GET  /api/v1/projects/{project_id}/repositories
POST /api/v1/projects/{project_id}/repositories
GET  /api/v1/repositories/{repository_id}
```

### Pull Requests and reviews

```text
GET  /api/v1/repositories/{repository_id}/pull-requests
POST /api/v1/repositories/{repository_id}/pull-requests
GET  /api/v1/pull-requests/{pull_request_id}
GET  /api/v1/pull-requests/{pull_request_id}/reviews
POST /api/v1/pull-requests/{pull_request_id}/reviews
GET  /api/v1/code-reviews/{review_id}
GET  /api/v1/code-reviews/{review_id}/findings
```

### Dashboard and automated review

```text
GET  /api/v1/dashboard/summary
POST /api/v1/pull-requests/{pull_request_id}/ai-review
```

### GitHub integration

```text
POST /api/v1/github/pull-request-review
POST /api/v1/github/webhook
POST /api/v1/github/reviews/{review_id}/publish
```

### Health

```text
GET /health
```

## Automated review engine

The current local provider is deterministic so the repository can be tested without depending on an external AI service.

The implemented rules include:

| Category | Detection |
|---|---|
| Security | hardcoded credential-like values |
| Security | `eval()` usage |
| Security | `exec()` usage |
| Security | shell execution with `shell=True` |
| Maintainability | bare `except` |
| Maintainability | `TODO` / `FIXME` markers |
| Performance | `range(len(...))` pattern |

Each finding is stored with structured metadata:

```text
filename
line_number
category
severity
title
description
suggestion
confidence
```

The provider architecture is designed so additional review providers can be added without replacing the service layer.

## Database model

```text
Organization
   │
   ├── Memberships ── Users
   │
   └── Projects
         │
         └── Repositories
               │
               └── Pull Requests
                     │
                     └── Code Reviews
                           │
                           └── Review Findings
```

Core persisted entities include:

- organizations
- organization memberships
- users
- projects
- repositories
- pull requests
- code reviews
- review findings

SQLAlchemy is used for ORM/data access and Alembic manages database migrations.

## Authentication and security

Authentication uses JWT bearer tokens for protected API routes.

```text
POST /api/v1/auth/login
        ↓
credential verification
        ↓
JWT access token
        ↓
Authorization: Bearer <token>
        ↓
protected API endpoint
```

Passwords are stored as hashes, not plaintext credentials.

GitHub webhook requests are protected using `X-Hub-Signature-256`. DevFlow validates the signature against the raw request body and configured webhook secret before processing the event.

Never commit real tokens, webhook secrets, database passwords, or `.env` files.

## Tech stack

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy 2
- Pydantic v2
- pydantic-settings
- Alembic
- PostgreSQL 17
- HTTPX

### Authentication

- JWT
- python-jose
- Passlib / bcrypt

### Review engine

- Python automated review provider
- provider factory architecture
- structured finding model
- severity classification
- confidence scoring

### GitHub

- GitHub REST API
- GitHub Pull Request webhooks
- GitHub Pull Request diff retrieval
- GitHub review publishing
- inline review comment support
- HMAC-SHA256 webhook verification

### Frontend

- React 19
- Vite 8
- React Router
- JavaScript / JSX
- Oxlint

### Infrastructure and tooling

- Docker
- Docker Compose
- PostgreSQL container
- ngrok for local webhook testing
- GitHub Actions

## Project structure

```text
devflow/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── ai_reviewer/
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── integrations/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   └── tests/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
├── .env.example
├── docker-compose.yml
├── LICENSE
├── README.md
└── requirements.txt
```

## Local setup

### Prerequisites

- Python 3.13 recommended
- Node.js 24 recommended for the current frontend toolchain
- Docker Desktop
- Git

### 1. Clone

```bash
git clone https://github.com/1234ashutosh1234/devflow.git
cd devflow
```

### 2. Start PostgreSQL

```bash
docker compose up -d
```

### 3. Configure environment

Create your local `.env` from `.env.example` and provide the required application settings.

For real GitHub webhook testing, configure the GitHub token, GitHub API URL, and webhook secret required by the backend.

### 4. Create and activate a Python environment

#### Windows CMD

```cmd
python -m venv .venv
.venv\Scripts\activate
```

#### PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 5. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 6. Start FastAPI

```bash
python -m uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

OpenAPI:

```text
http://127.0.0.1:8000/openapi.json
```

### 7. Start the frontend

Open another terminal:

```cmd
cd frontend
npm ci
npm run dev
```

Frontend:

```text
http://localhost:5173
```

The Vite development server proxies `/api` requests to the local FastAPI server.

### 8. Validate the frontend

```bash
npm run lint
npm run build
```

Both commands are also enforced by CI.

## GitHub webhook setup for local development

For local webhook testing, expose port 8000 through a public tunnel.

Example:

```bash
ngrok http 8000
```

Configure the GitHub repository webhook URL as:

```text
https://YOUR-NGROK-DOMAIN/api/v1/github/webhook
```

Use JSON content delivery and enable Pull Request events.

For the webhook secret, configure the same value in the backend environment and GitHub webhook settings.

Supported review-triggering Pull Request events include the workflow events implemented by the backend such as opened, reopened, and synchronize.

## CI/CD

GitHub Actions validates the project on pushes to `main` and feature branches and on Pull Requests targeting `main`.

The pipeline contains two jobs:

```text
Backend tests
    ├── PostgreSQL service
    ├── install backend dependencies
    ├── run pytest
    └── verify FastAPI application

Frontend lint and build
    ├── install Node dependencies
    ├── npm run lint
    └── npm run build
```

A green CI run means both the backend test suite and the frontend production build have passed.

## Testing strategy

The backend test suite covers application behavior including automated review components, webhook handling, schemas, and dashboard services.

The frontend validation currently includes:

- Oxlint with zero warnings/errors in the checked codebase
- Vite production build

The GitHub Actions workflow runs both validation layers automatically.

## Demo walkthrough

A simple recruiter/interviewer walkthrough is:

```text
1. Start PostgreSQL
2. Start FastAPI
3. Start React/Vite
4. Sign in to DevFlow
5. Open Dashboard
6. Open Projects and show connected repository
7. Open Pull Requests and select a PR
8. Open Reviews and inspect review score/status
9. Open a review and inspect findings
10. Open GitHub and run a PR review
11. Show the resulting review data in DevFlow
12. Show GitHub Actions with both CI jobs green
```

## Engineering highlights

This project demonstrates several practical engineering patterns:

- layered FastAPI architecture
- dependency injection
- repository/service separation
- Pydantic request/response validation
- SQLAlchemy relationships and persistence
- database migrations with Alembic
- JWT authentication and authorization
- GitHub API integration
- event-driven webhook processing
- HMAC request verification
- deterministic automated code review
- structured finding storage
- React dashboard state management
- frontend/backend API integration
- Dockerized local PostgreSQL
- automated CI checks

## Current limitations

- The local review provider is deterministic rather than a hosted LLM by default.
- Local GitHub webhook development requires a public tunnel such as ngrok.
- Webhook duplicate-delivery protection is currently process-memory based.
- Production deployment and horizontal-scaling configuration are not yet the focus of the project.

## Future improvements

- persistent webhook idempotency with delivery identifiers
- asynchronous background review workers
- richer LLM-assisted review explanations
- repository-aware review context
- improved GitHub comment threading and lifecycle management
- richer Pull Request comparison views
- role administration UI
- production deployment configuration
- observability, metrics, and tracing

## Why this project is recruiter-ready

DevFlow is intentionally more than a CRUD application. It demonstrates a complete workflow across external events, APIs, persistence, automated code analysis, security controls, frontend UX, and CI.

A recruiter or interviewer can inspect the repository and follow a concrete engineering path:

```text
GitHub event
   → API
   → validation
   → diff parsing
   → automated analysis
   → persistence
   → dashboard
   → CI verification
```

That makes the project useful for demonstrating backend engineering, full-stack development, integration work, and practical software-engineering discipline.

## Repository

GitHub: https://github.com/1234ashutosh1234/devflow

---

Built as a portfolio project focused on practical full-stack and developer-tooling engineering.
