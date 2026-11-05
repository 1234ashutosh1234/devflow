# DevFlow — GitHub Pull Request Review Platform

DevFlow is an early-stage, open-source developer tool that connects to GitHub pull-request workflows, analyses code changes for security, maintainability, and performance concerns, stores structured findings, and can publish review feedback to pull requests.

The project is maintained independently and is open to contributions. APIs and features may change while the project is under active development. Please test with repositories and data you are authorised to use, and review automated findings before acting on them.

<p align="left">
  <a href="https://github.com/1234ashutosh1234/devflow/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License"></a>
  <a href="https://github.com/1234ashutosh1234/devflow/actions"><img src="https://img.shields.io/github/actions/workflow/status/1234ashutosh1234/devflow/ci.yml?branch=main&label=CI" alt="CI status"></a>
  <a href="https://github.com/1234ashutosh1234/devflow/issues"><img src="https://img.shields.io/github/issues/1234ashutosh1234/devflow" alt="GitHub issues"></a>
</p>

## Project links

| Resource | Link |
| --- | --- |
| Live application | https://devflow-1-s18m.onrender.com |
| Backend API | https://devflow-11ku.onrender.com |
| API documentation | https://devflow-11ku.onrender.com/docs |
| Backend health endpoint | https://devflow-11ku.onrender.com/health |
| Source code | https://github.com/1234ashutosh1234/devflow |
| Contribution guide | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Security policy | [SECURITY.md](SECURITY.md) |
| Report a bug | [Open a bug report](https://github.com/1234ashutosh1234/devflow/issues/new?template=bug_report.yml) |
| Request a feature | [Request a feature](https://github.com/1234ashutosh1234/devflow/issues/new?template=feature_request.yml) |
| Report a vulnerability | Use [GitHub private vulnerability reporting](https://github.com/1234ashutosh1234/devflow/security/advisories/new) — do not disclose security issues in public issues. |

> **Demo availability:** The hosted services use a free Render deployment and may sleep after inactivity. The first request can take longer while a service starts. The live demo may also differ from the latest code in `main`.

## What DevFlow does

- Receives GitHub pull-request webhook events.
- Validates webhook signatures using HMAC-SHA256.
- Retrieves pull-request metadata and unified diffs through the GitHub API.
- Parses changed files and reviewable lines.
- Runs automated checks for security, maintainability, and performance patterns.
- Organises findings with severity and confidence information.
- Persists projects, repositories, pull requests, reviews, and findings in PostgreSQL.
- Exposes application functionality through a FastAPI REST API.
- Provides a React dashboard for projects, pull requests, reviews, and findings.
- Supports publishing review summaries and inline comments to GitHub.

Automated analysis is a decision-support aid, not a guarantee that code is secure or correct. Findings can be incomplete or inaccurate; developers should verify them in context.

## Technology stack

| Area | Technology |
| --- | --- |
| Backend | Python, FastAPI, Pydantic |
| Frontend | React, Vite, JavaScript |
| Database | PostgreSQL, SQLAlchemy |
| Migrations | Alembic |
| GitHub integration | GitHub REST API and webhooks |
| Authentication | JWT and password hashing |
| Testing | Pytest, Oxlint, Vite production build |
| Local database | Docker Compose |
| CI | GitHub Actions |

## How the workflow fits together

```text
Developer opens or updates a pull request
                  |
                  v
          GitHub webhook event
                  |
                  v
       HMAC-SHA256 signature check
                  |
                  v
      Fetch pull-request data and diff
                  |
                  v
       Parse changed files and lines
                  |
                  v
   Automated review and finding generation
                  |
                  v
    Persist review and findings in PostgreSQL
                  |
                  v
      Publish review feedback to GitHub
                  |
                  v
        Developer reviews the results
```

## Repository layout

```text
devflow/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   │   └── ci.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── backend/
│   ├── ai_reviewer/
│   ├── app/
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── package-lock.json
├── docs/
├── docker-compose.yml
├── .env.example
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── SECURITY.md
```

## Run DevFlow locally

### Prerequisites

- Git
- Python 3.13 (the CI workflow currently uses Python 3.13)
- Node.js 24 and npm (the CI workflow currently uses Node.js 24)
- Docker Desktop or another Docker Compose-compatible environment

### 1. Clone the repository

```bash
git clone https://github.com/1234ashutosh1234/devflow.git
cd devflow
```

### 2. Create and activate a Python virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If PowerShell prevents activation, use `.venv\Scripts\python.exe` directly rather than changing a machine-wide execution policy.

### 3. Install backend dependencies

Run this from the repository root:

```bash
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file from the example.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

At minimum, check that `DATABASE_URL` points to your local PostgreSQL database and replace the example `JWT_SECRET` with a new, private development secret. The settings are loaded by `backend/app/core/config.py`.

Optional integrations may require additional settings:

| Variable | Purpose |
| --- | --- |
| `GITHUB_TOKEN` | GitHub API access for operations that require an authenticated token |
| `GITHUB_WEBHOOK_SECRET` | Shared secret used to validate incoming GitHub webhook signatures |
| `OPENAI_API_KEY` | API access when using an OpenAI-backed review provider |
| `AI_REVIEW_PROVIDER` | Review provider selection; defaults to `local` |
| `OPENAI_MODEL` | Model name used by the configured OpenAI provider |
| `CORS_ORIGINS` | Comma-separated allowed browser origins |
| `VITE_API_URL` | Optional backend base URL for the frontend; local Vite development proxies API requests to the local backend |

Use credentials that you control and have permission to use. Never commit `.env`, personal access tokens, webhook secrets, API keys, private keys, or production credentials. `.gitignore` excludes local environment files; keep that protection in place.

### 5. Start PostgreSQL

Run this from the repository root while Docker is running:

```bash
docker compose up -d
```

The Compose file starts a local PostgreSQL 17 container. The development database credentials in `docker-compose.yml` are for local use only; do not reuse them in production.

To stop the database container:

```bash
docker compose down
```

This keeps the named database volume. Do not add `-v` unless you intentionally want to delete your local database data.

### 6. Start the backend

Open a terminal, activate the virtual environment, then run:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

The backend runs at:

- API: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

### 7. Start the frontend

Open a second terminal at the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Vite prints the local frontend URL in the terminal (the project config uses port `5173`). Its development proxy forwards `/api` and `/health` requests to `http://127.0.0.1:8000`.

Keep PostgreSQL and the backend running while testing frontend features that use the API.

## Run checks before opening a pull request

Run the same core checks used by the GitHub Actions workflow.

### Backend tests

From the repository root, with the Python virtual environment active:

```powershell
cd backend
python -m pytest -q
```

### Frontend lint and production build

In another terminal:

```powershell
cd frontend
npm ci
npm run lint
npm run build
```

Record the commands you actually ran and their results in your pull request. Do not mark a check as passing unless it completed successfully. If a check fails, include the relevant error output (with secrets and personal data removed) when asking for help.

## GitHub webhook development

To receive GitHub webhook events during local development, the backend must be reachable through a secure public tunnel. Configure the webhook URL and the same secret in GitHub and in your local environment. The backend validates the request signature before processing the event.

Do not expose a production secret in a screenshot, issue, pull request, terminal recording, or public log. Use a dedicated test repository and test credentials when experimenting with webhook delivery. See [CONTRIBUTING.md](CONTRIBUTING.md) for the contributor setup and [SECURITY.md](SECURITY.md) for vulnerability reporting.

## Contributing

Contributions are welcome, including bug reports, feature proposals, documentation improvements, tests, and code fixes.

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) before making changes.
2. Search existing [issues](https://github.com/1234ashutosh1234/devflow/issues) and pull requests first.
3. Use the issue forms for reproducible bug reports and feature requests.
4. For larger changes, open an issue to discuss the approach before coding.
5. Create a focused branch and submit a pull request using the repository template.
6. Include test results and update documentation when behaviour or setup changes.

Please keep pull requests focused and respectful. The maintainer may ask for changes, tests, or clarification before merging.

## Security and responsible disclosure

Do not post suspected vulnerabilities, exploit details, credentials, or private user data in public issues or pull requests. Use [GitHub private vulnerability reporting](https://github.com/1234ashutosh1234/devflow/security/advisories/new) to report security issues privately. Read [SECURITY.md](SECURITY.md) for supported versions and reporting guidance.

## Current project status

DevFlow is an independently maintained, early-stage project. Features, database schemas, and API behaviour may change. Contributions and careful feedback are welcome; please do not assume that the hosted demo is suitable for production workloads or sensitive repositories without carrying out your own review and testing.

## License

DevFlow is licensed under the [MIT License](LICENSE).

## Maintainer

**Ashutosh Raj** — [GitHub profile](https://github.com/1234ashutosh1234)

Project repository: https://github.com/1234ashutosh1234/devflow
