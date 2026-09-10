# DevFlow — AI-Powered Developer Collaboration & Code Review Platform

> Automated GitHub Pull Request analysis that detects security, maintainability, and performance issues, persists structured findings, and publishes actionable inline comments directly to GitHub.

---

## 🚀 Overview

DevFlow is a full-stack developer collaboration and AI-assisted code review platform built around a real GitHub Pull Request workflow.

When a developer pushes a new commit to a Pull Request, GitHub sends a webhook to DevFlow. The backend validates the webhook, retrieves the Pull Request and unified diff, parses changed files, runs automated code analysis, stores the review in PostgreSQL, and publishes the findings back to GitHub as inline review comments.

### End-to-End Flow

```text
Developer Push
      ↓
GitHub Pull Request
      ↓
pull_request Webhook
      ↓
Public Tunnel / Webhook Endpoint
      ↓
FastAPI Backend
      ↓
Webhook Signature Validation
      ↓
GitHub API
      ↓
Pull Request + Unified Diff
      ↓
Multi-file Diff Parser
      ↓
AI / Automated Review Engine
      ↓
Structured Findings + Score
      ↓
PostgreSQL
      ↓
GitHub Review Publisher
      ↓
Inline Comments on Changed Lines
```

---

# ✨ Features

- Automated GitHub Pull Request code review
- Real GitHub `pull_request` webhook integration
- Automatic review on `opened`, `reopened`, and `synchronize`
- HMAC-SHA256 webhook signature verification
- GitHub Pull Request metadata retrieval
- Unified diff retrieval and parsing
- Multi-file Pull Request analysis
- Reviewable-line detection
- Security issue detection
- Maintainability checks
- Performance-oriented checks
- Severity classification
- Confidence scoring
- Review score calculation
- PostgreSQL review persistence
- Structured review finding persistence
- JWT authentication
- Password hashing
- GitHub review publication
- GitHub inline review comments
- FastAPI REST API
- SQLAlchemy ORM
- Alembic migrations
- Docker/PostgreSQL development environment
- Pluggable review-provider architecture

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │      Developer       │
                         │                      │
                         │     Pushes Code      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       GitHub         │
                         │   Pull Request       │
                         └──────────┬───────────┘
                                    │
                           pull_request event
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Public Webhook URL  │
                         │   ngrok / Tunnel     │
                         └──────────┬───────────┘
                                    │
                                    ▼
               ┌────────────────────────────────────────┐
               │             DevFlow Backend            │
               │                                        │
               │              FastAPI API               │
               └───────────────────┬────────────────────┘
                                   │
                                   ▼
                       ┌──────────────────────┐
                       │ Webhook Validation   │
                       │                      │
                       │ X-Hub-Signature-256  │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │   GitHub Client      │
                       │                      │
                       │ PR Metadata          │
                       │ Unified Diff         │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │    Diff Parser       │
                       │                      │
                       │ Multi-file parsing   │
                       │ Reviewable lines     │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │   Review Engine      │
                       │                      │
                       │ Security             │
                       │ Maintainability      │
                       │ Performance          │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │    Review Service    │
                       │                      │
                       │ Findings             │
                       │ Score                │
                       │ Status               │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │      PostgreSQL      │
                       │                      │
                       │ Users                │
                       │ Projects             │
                       │ Repositories         │
                       │ Pull Requests        │
                       │ Reviews              │
                       │ Findings             │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │ GitHub Review API    │
                       │                      │
                       │ Summary              │
                       │ Inline comments      │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │ GitHub Pull Request  │
                       │                      │
                       │ Review + Comments    │
                       └──────────────────────┘
```

---

# 🔄 Event-Driven Review Workflow

```text
1. Developer pushes a commit
                ↓
2. GitHub updates the Pull Request
                ↓
3. GitHub sends a pull_request webhook
                ↓
4. DevFlow reads the raw request body
                ↓
5. HMAC-SHA256 signature is verified
                ↓
6. Repository and Pull Request are identified
                ↓
7. Pull Request metadata is fetched
                ↓
8. Unified diff is fetched
                ↓
9. Changed files and reviewable lines are parsed
                ↓
10. Review engine analyzes the code
                ↓
11. Findings are generated
                ↓
12. Overall review score is calculated
                ↓
13. Review + findings are stored in PostgreSQL
                ↓
14. GitHub Review API publishes the results
                ↓
15. Developers see inline comments on changed lines
```

---

# 🧠 Automated Code Review

The current local review provider performs deterministic analysis over changed code.

### Detection Rules

| Category | Detection |
|---|---|
| Security | Hardcoded credentials |
| Security | `eval()` |
| Security | `exec()` |
| Security | Shell command execution |
| Maintainability | Bare `except` |
| Maintainability | TODO/FIXME markers |
| Performance | `range(len(...))` |

### Finding Structure

Every finding contains structured information:

```text
Filename
Line Number
Category
Severity
Title
Description
Suggestion
Confidence
```

Example:

```text
HIGH: Possible hardcoded secret

A credential-like value appears to be hardcoded directly
in source code.

Suggestion:
Move the secret to an environment variable or a managed
secret store.

Confidence: 97%
```

---

# 📊 Review Scoring

Each review receives an overall score.

A real webhook-triggered test produced:

```text
Review ID: 11
Files analyzed: 3
Findings: 12
Score: 40/100
Status: completed_with_findings
```

The findings covered:

```text
Security
Maintainability
Performance
```

---

# 🗄️ Database Architecture

DevFlow uses PostgreSQL for persistent application data.

```text
Organization
     │
     ├── Users / Memberships
     │
     └── Projects
           │
           └── Repository
                 │
                 └── Pull Request
                        │
                        └── Code Review
                               │
                               └── Review Findings
```

### Core Entities

- Organizations
- Users
- Memberships
- Projects
- Repositories
- Pull Requests
- Code Reviews
- Review Findings
- Tasks

SQLAlchemy is used as the ORM/data-access layer and Alembic manages schema migrations.

---

# 🔐 Authentication

DevFlow uses JWT-based authentication for protected API endpoints.

```text
User
  │
  ▼
POST /api/v1/auth/login
  │
  ▼
Credential Verification
  │
  ▼
JWT Access Token
  │
  ▼
Authorization: Bearer <token>
  │
  ▼
Protected API
```

Passwords are hashed using bcrypt through Passlib.

---

# 🔒 Webhook Security

DevFlow validates GitHub webhooks using:

```text
X-Hub-Signature-256
```

The validation process is:

```text
Raw Request Body
       +
GITHUB_WEBHOOK_SECRET
       ↓
HMAC-SHA256
       ↓
Compare Against GitHub Signature
```

Invalid or unsigned requests are rejected before review processing.

Example:

```text
Unsigned Request
      ↓
403 Forbidden
```

Valid GitHub webhook:

```text
GitHub Request
      ↓
Signature Verified
      ↓
Review Processing
      ↓
200 OK
```

---

# 🌐 API

### Authentication

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### Pull Requests

```text
Pull Request management
Review history
```

### Code Reviews

```text
Review creation
Review retrieval
Review findings
```

### GitHub

```text
GitHub integration
Pull Request retrieval
Review publishing
```

### Webhook

```text
POST /api/v1/github/webhook
```

---

# 📚 API Documentation

When the backend is running:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### OpenAPI

```text
http://127.0.0.1:8000/openapi.json
```

---

# 🛠️ Technology Stack

## Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- Pydantic Settings
- Alembic
- PostgreSQL
- HTTPX

## Authentication

- JWT
- Python-JOSE
- Passlib
- bcrypt

## AI / Code Review

- Python-based review engine
- Pluggable provider architecture
- Deterministic local review provider
- Structured findings
- Severity classification
- Confidence scoring

## GitHub Integration

- GitHub REST API
- GitHub Pull Request Webhooks
- GitHub Pull Request Reviews
- GitHub inline review comments
- HMAC-SHA256 webhook verification

## Infrastructure

- Docker
- Docker Compose
- PostgreSQL
- ngrok for local webhook development

---

# 📁 Project Structure

```text
devflow/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │
│   │   ├── core/
│   │   │
│   │   ├── integrations/
│   │   │
│   │   ├── models/
│   │   │
│   │   ├── repositories/
│   │   │
│   │   ├── schemas/
│   │   │
│   │   ├── services/
│   │   │
│   │   └── workers/
│   │
│   └── alembic/
│
├── ai-reviewer/
│
├── frontend/
│
├── github-review-demo/
│
├── docs/
│
├── infrastructure/
│
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

# ⚙️ Local Setup

## 1. Clone the Repository

```bash
git clone https://github.com/1234ashutosh1234/devflow.git
cd devflow
```

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create `.env` from `.env.example`.

Configure:

```text
DATABASE_URL
JWT_SECRET
JWT_ALGORITHM
GITHUB_TOKEN
GITHUB_API_URL
GITHUB_WEBHOOK_SECRET
```

Never commit real credentials.

## 5. Start PostgreSQL

```bash
docker compose up -d
```

## 6. Start the Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

The backend runs at:

```text
http://127.0.0.1:8000
```

---

# 🔗 GitHub Webhook Setup

For local development, expose FastAPI through a public tunnel.

Example:

```bash
ngrok http 8000
```

ngrok provides a public URL similar to:

```text
https://YOUR-NGROK-DOMAIN.ngrok-free.dev
```

Configure your GitHub webhook as:

```text
https://YOUR-NGROK-DOMAIN.ngrok-free.dev/api/v1/github/webhook
```

Use:

```text
Content-Type: application/json
```

Select the:

```text
Pull requests
```

event.

The GitHub webhook secret must match:

```text
GITHUB_WEBHOOK_SECRET
```

---

# 🧪 End-to-End Verification

DevFlow has been tested against a real GitHub Pull Request.

### Verified Sequence

```text
Git Push
    ↓
GitHub Pull Request Updated
    ↓
pull_request synchronize
    ↓
GitHub Webhook
    ↓
ngrok
    ↓
FastAPI
    ↓
Webhook Signature Validation
    ↓
GitHub PR + Diff Retrieval
    ↓
Multi-file Diff Parsing
    ↓
Automated Review
    ↓
12 Findings
    ↓
PostgreSQL Persistence
    ↓
GitHub Review Publication
    ↓
Inline Comments
```

### Verified Result

```text
Review ID: 11
Files: 3
Findings: 12
Score: 40/100
Status: completed_with_findings
```

The review findings were successfully displayed as inline comments in the GitHub Pull Request.

---

# 📸 Demo

Recommended screenshots for the project:

### GitHub Pull Request

Show:

- Pull Request
- Changed files
- DevFlow review
- Inline review comments

### Swagger

Show:

```text
http://127.0.0.1:8000/docs
```

### Review Results

Show:

- Review score
- Finding count
- Severity
- Filename
- Line number
- Suggestion
- Confidence

---

# ✅ Successfully Demonstrated

The project has successfully demonstrated:

- Real GitHub webhook delivery
- HMAC webhook validation
- Automatic `synchronize` review triggering
- GitHub Pull Request retrieval
- Unified diff retrieval
- Multi-file diff parsing
- Automated code analysis
- Review generation
- PostgreSQL persistence
- Review finding persistence
- GitHub review publication
- GitHub inline comments

---

# 🧱 Engineering Concepts

## Backend

- REST API development
- Service-layer architecture
- Repository pattern
- Dependency injection
- Schema validation
- Error handling

## Database

- Relational data modeling
- SQLAlchemy ORM
- Repository-based data access
- Foreign-key relationships
- Database migrations

## Security

- JWT authentication
- Password hashing
- Environment-based secrets
- HMAC-SHA256 webhook verification
- API authorization

## Integration

- GitHub REST API
- GitHub Webhooks
- Pull Request diff retrieval
- GitHub Review API
- Inline review comments

## Event-Driven Processing

```text
GitHub Event
     ↓
Webhook
     ↓
Validation
     ↓
Processing
     ↓
Review
     ↓
Persistence
     ↓
GitHub Publication
```

---

# 🚧 Current Limitations

- Webhook idempotency is currently process-memory based
- Local webhook development requires a public tunnel
- The local provider uses deterministic review rules
- Background review processing can be expanded
- Production deployment configuration is still evolving

---

# 🔮 Future Improvements

## AI

- Context-aware LLM reasoning
- Repository-aware analysis
- Architecture-aware code review
- Better false-positive reduction
- Natural-language review summaries

## GitHub

- GitHub Checks integration
- Commit status reporting
- Review dismissal handling
- Review approval workflows
- Repository-specific review rules

## Backend

- Background job queue
- Persistent webhook idempotency
- Distributed workers
- Caching
- GitHub rate-limit handling

## Frontend

- Review dashboard
- Review history
- Repository health metrics
- Team analytics
- Finding trends
- Developer productivity metrics

## Developer Experience

- Custom review rules
- Configurable severity thresholds
- `.devflow.yml`
- Finding suppression
- Finding acknowledgment
- Notifications

---

# 🔒 Security Notes

Never commit:

```text
.env
GitHub tokens
API keys
JWT secrets
Webhook secrets
Database passwords
```

Use `.env.example` with placeholder values.

If credentials are accidentally exposed:

```text
Revoke Credential
       ↓
Generate Replacement
       ↓
Update Environment
       ↓
Restart Application
```

---

# 💼 Recruiter Highlights

DevFlow demonstrates practical experience with:

- Python backend development
- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT authentication
- REST API design
- GitHub API integration
- GitHub Webhooks
- HMAC-SHA256 security
- Event-driven processing
- Unified diff parsing
- Multi-file analysis
- Automated code review
- AI-assisted developer tooling
- Docker
- API documentation
- Service/repository architecture

---

# 🎯 Project Objective

DevFlow combines backend engineering, database design, authentication, third-party API integration, webhook security, automated code analysis, and AI-assisted developer tooling into a single developer productivity platform.

The goal is to shorten the feedback loop between:

```text
Code Change
    ↓
Automated Analysis
    ↓
Actionable Findings
    ↓
Developer Feedback
```

---

# 🏆 Project Achievement

A real GitHub Pull Request was used to validate the complete automated workflow:

```text
Developer
    ↓
GitHub
    ↓
Webhook
    ↓
DevFlow
    ↓
Code Analysis
    ↓
Structured Findings
    ↓
PostgreSQL
    ↓
GitHub Review
    ↓
Inline Comments
```

This confirms that the project can participate in a real GitHub-based development workflow rather than operating only as an isolated local code-analysis script.

---

# 📄 License

This project is currently provided for educational and portfolio purposes.

---

# 👨‍💻 Author

## Ashutosh Raj

GitHub:

https://github.com/1234ashutosh1234

Repository:

https://github.com/1234ashutosh1234/devflow
