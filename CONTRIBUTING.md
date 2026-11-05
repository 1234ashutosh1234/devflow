# Contributing to DevFlow

Thank you for your interest in contributing to DevFlow! Contributions from developers of all experience levels are welcome. This guide explains how to report problems, propose improvements, set up the project locally, and submit changes.

## Ways to contribute

You can help by:

- Reporting reproducible bugs.
- Suggesting features or improvements.
- Improving documentation and setup instructions.
- Adding or improving automated tests.
- Fixing bugs or implementing accepted features.
- Reviewing open pull requests and giving constructive feedback.

For larger changes, please open an issue first so we can discuss the approach before you spend time implementing it.

## Before you start

1. Read the project [README](README.md) and check the existing issues and pull requests.
2. For a bug, check whether it has already been reported. If not, open a bug report with reproduction steps.
3. For a feature, open a feature request describing the problem, the proposed behaviour, and any alternatives you considered.
4. Do not include passwords, API keys, access tokens, webhook secrets, private user data, or production configuration in issues, pull requests, logs, screenshots, or commits.
5. For a suspected security vulnerability, **do not open a public issue** or include exploit details in a pull request. Use GitHub's private vulnerability reporting feature if it is enabled for the repository; otherwise, contact the maintainer privately to request a secure reporting channel.

## Development environment

DevFlow uses a Python/FastAPI backend, a React/Vite frontend, and PostgreSQL for local development. The current GitHub Actions workflow uses Python 3.13 and Node.js 24, so use those versions when possible. You will also need Git and Docker with Docker Compose. The commands below are written for Windows PowerShell first; equivalent macOS/Linux commands are included where they differ.

### 1. Fork and clone the repository

Fork the repository on GitHub, then clone your fork:

```bash
git clone https://github.com/<your-github-username>/devflow.git
cd devflow
```

Add the upstream repository so you can sync your fork:

```bash
git remote add upstream https://github.com/1234ashutosh1234/devflow.git
git remote -v
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

If PowerShell blocks virtual-environment activation, use the Python executable directly from `.venv\Scripts\python.exe` or follow Microsoft's guidance for your local execution policy. Do not change a machine-wide security policy just to run this project.

### 3. Install backend dependencies

From the repository root:

```bash
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file by copying `.env.example`:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Review the variables in `.env` and the configuration described in the README. Use local development values and your own test credentials. Never commit `.env` or real secrets. The repository's `.gitignore` excludes local environment files; keep it that way.

### 5. Start PostgreSQL

Make sure Docker Desktop (or another Docker Compose-compatible environment) is running, then run this from the repository root:

```bash
docker compose up -d
```

To stop the database container when you are finished:

```bash
docker compose down
```

Do not use `docker compose down -v` unless you intentionally want to delete the local database volume and its data.

### 6. Start the backend

Open a terminal, activate the virtual environment, and run:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. FastAPI's interactive API documentation is normally available at `http://127.0.0.1:8000/docs` while the local server is running.

### 7. Start the frontend

Open a second terminal at the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Use the local URL printed by Vite in the terminal. Keep the backend and PostgreSQL services running while testing features that depend on them.

## Run checks before submitting

Run the same core checks used by the repository's GitHub Actions workflow.

### Backend tests

From the repository root, with the virtual environment active:

```powershell
cd backend
python -m pytest -q
```

### Frontend lint and production build

Open another terminal:

```powershell
cd frontend
npm ci
npm run lint
npm run build
```

If a check fails, investigate and fix the failure before opening a pull request. Include relevant test coverage for bug fixes and new behaviour. Do not claim a test passed unless you ran it successfully.

## Branch and commit conventions

Create a focused branch from the latest `main` branch. Suggested prefixes:

- `fix/` for bug fixes.
- `feat/` for new features.
- `docs/` for documentation changes.
- `test/` for test-only changes.
- `refactor/` for code restructuring without intended behaviour changes.

Example:

```bash
git fetch upstream
git switch main
git pull upstream main
git switch -c docs/improve-contribution-guide
```

Keep commits small and describe what changed. Suggested commit-message format:

```text
<type>: <short description>
```

Examples:

```text
docs: add contributor setup instructions
fix: reject invalid webhook signatures
test: cover missing webhook signature
```

## Pull request guidelines

When your change is ready:

1. Run the relevant backend tests and frontend checks.
2. Review your own diff with `git diff` and remove unrelated changes, debug output, generated files, and secrets.
3. Push your branch to your fork.
4. Open a pull request against the `main` branch of `1234ashutosh1234/devflow`.
5. Complete the pull request template and explain the problem, the solution, and how you tested it.
6. Link the related issue, if one exists.
7. Respond respectfully to review feedback and make requested changes in follow-up commits.

A pull request should ideally address one concern at a time. Large changes should be discussed in an issue first.

## Pull request checklist

Before submitting, check that:

- [ ] The change has a clear purpose and is related to an issue or agreed improvement.
- [ ] Backend tests pass when backend code is changed.
- [ ] Frontend lint and build pass when frontend code is changed.
- [ ] Tests have been added or updated where appropriate.
- [ ] Documentation has been updated where needed.
- [ ] No secrets, tokens, passwords, or personal data are included.
- [ ] No unrelated files or generated build artifacts are included.
- [ ] The pull request description explains the change and testing performed.

## Coding and review expectations

- Prefer clear, readable code over clever or unnecessarily complex code.
- Keep changes focused and consistent with the existing project structure.
- Validate external input and handle errors deliberately.
- Do not weaken authentication, authorization, webhook verification, or secret-handling controls to make a test pass.
- Avoid adding dependencies unless they are needed; explain significant new dependencies in the pull request.
- Be respectful and constructive in code reviews and discussions.

## Community expectations

Please be welcoming and respectful. Critique code and ideas, not people. Assume good intent, explain disagreements clearly, and help keep discussions useful for everyone.

Thank you for helping improve DevFlow!
