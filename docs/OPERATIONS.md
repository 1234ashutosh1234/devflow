# DevFlow staging, monitoring, and rollback runbook

This runbook describes the operational setup for the current Render deployment:

- Production frontend: `https://devflow-1-s18m.onrender.com`
- Production API: `https://devflow-11ku.onrender.com`
- Production liveness: `/health`
- Production readiness (database check): `/health/ready`
- Production branch: `main`

Do not put production credentials, database URLs, or personal access tokens in this file, a pull request, or a screenshot.

## 1. Staging environment

Staging is deliberately a separate Render environment, not a branch switch on the production services. Do not point staging at the production PostgreSQL database.

### Cost and plan check before creating services

- Render Preview Environments require a Pro workspace or higher and are billed like their copied services. This repository does not enable them automatically.
- Render Free web services spin down after 15 minutes without inbound traffic and can take about a minute to wake up.
- Render Free PostgreSQL databases expire after 30 days. Do not use a Free Postgres database as a durable staging database.
- Check current workspace pricing and included usage in the Render Dashboard before creating any service or database. A persistent staging API, frontend, and isolated database may incur charges.

### Recommended single shared staging environment

Create staging only when there is a suitable isolated database and the expected service costs are acceptable.

1. Create a `staging` branch from the latest `main`:

   ```powershell
   git switch main
   git pull --ff-only origin main
   git switch -c staging
   git push -u origin staging
   ```

2. In Render, create a separate staging API service from this repository and connect it to the `staging` branch. Copy the production API's build/start commands and runtime settings, but not its production secrets.
3. Create a separate PostgreSQL database for staging. Set the staging API's `DATABASE_URL` to this database and run the normal Alembic migration command during deploy/build as appropriate for the service. Never reuse the production `DATABASE_URL`.
4. Configure staging-only secrets and integration values:
   - `JWT_SECRET`: a newly generated staging-only value.
   - `GITHUB_TOKEN`: preferably a fine-grained token restricted to a dedicated test repository.
   - `GITHUB_WEBHOOK_SECRET`: a staging-only webhook secret, if staging webhooks are enabled.
   - `AI_REVIEW_PROVIDER=local` unless paid model use is intentionally enabled for staging.
   - `CORS_ORIGINS`: the staging frontend origin only.
5. Create a separate staging frontend service from the same repository and `staging` branch. Copy the production frontend build settings and set `VITE_API_URL` to the staging API URL. Do not point the staging frontend to production API unless that is an intentional read-only test.
6. Set the staging API's Render Health Check Path to `/health`. Keep this check lightweight; use `/health/ready` for external checks that should verify the database too.
7. After both services deploy, verify:
   - `https://<staging-api-host>/health` returns `{"status":"ok"}`.
   - `https://<staging-api-host>/health/ready` returns HTTP 200 with `{"status":"ready","database":"ok",...}`.
   - The staging frontend loads and can sign in using a staging test account.
   - A test PR in the dedicated test repository can be reviewed without accessing production data.

8. Update the `staging` branch from `main` after each production release, then validate the change in staging before subsequent production feature work where practical. Keep staging secrets and data separate at all times.

This repository intentionally does not provision staging services automatically. Creating the services is a Render Dashboard action and can create billable infrastructure.

## 2. Production monitoring

The repository includes `.github/workflows/production-monitor.yml` and `scripts/production_monitor.py`.

- It runs once daily at 04:35 UTC (10:05 India time) and can also be started manually from GitHub Actions.
- It checks API liveness (`/health`), PostgreSQL readiness (`/health/ready`), and the frontend home page.
- It retries because the current Free Render API can be asleep when the daily check starts.
- A failed run appears as a failed GitHub Actions workflow. Enable GitHub Actions failure notifications in GitHub notification settings if email alerts are desired.

The daily cadence is intentional: frequent polling can keep a Free Render web service awake and consume more included usage. Render Free services normally sleep after 15 minutes of inactivity. If DevFlow moves to an always-on paid service and needs tighter alerting, configure an external uptime monitor with an interval appropriate to the desired response time.

### Manual monitoring run

From the repository root:

```powershell
$python = if (Test-Path ".\.venv\Scripts\python.exe") {
    (Resolve-Path ".\.venv\Scripts\python.exe").Path
} else {
    "python"
}

& $python .\scripts\production_monitor.py `
  --api-url "https://devflow-11ku.onrender.com" `
  --frontend-url "https://devflow-1-s18m.onrender.com" `
  --attempts 12 `
  --interval 15 `
  --request-timeout 12
```

A successful check prints `PRODUCTION MONITOR PASSED`. A persistent failure exits with code 1.

### Render-native health check

Set the Render backend service Health Check Path to `/health` when the
intention is to verify API process availability without making each
platform probe depend on PostgreSQL.

This is a deliberate trade-off: `/health` can pass while the database
is unavailable. The separate `/health/ready` endpoint checks database
connectivity and is used by the production smoke test and monitoring
workflow.

Use `/health/ready` as Render's Health Check Path instead if database
connectivity must be required before the instance receives traffic.

## 3. Production release procedure

1. Develop on a feature branch; do not push directly to `main`.
2. Open a pull request and wait for the required `Backend tests` and `Frontend lint and build` checks.
3. Merge only after required checks pass and the branch is up to date.
4. Render auto-deploys the production services from `main`.
5. Confirm the Render deployment is marked Live and the `DevFlow Production Smoke Test` workflow passes. That workflow checks that Render serves the exact commit that passed CI and that PostgreSQL is reachable.
6. For releases involving database changes, verify the Alembic migration completed and review application logs for migration or query errors.

## 4. Rollback procedure

### Application rollback

1. Open the Render Dashboard and select the affected production service.
2. Open **Deploys** and identify the last known-good successful deploy. Confirm its commit SHA and timestamp; do not guess from the deploy order alone.
3. Select **Rollback** on that deploy and confirm.
4. Repeat for the other application service (frontend or API) only if needed. Keep frontend and API versions compatible.
5. Open the service's **Events** and **Logs** pages. Confirm the rollback deploy is Live and review startup errors.
6. Verify the API:
   - `/health` returns HTTP 200.
   - `/health/ready` returns HTTP 200 and `database=ok`.
   - The frontend loads and the sign-in / review workflow works.
7. Render Dashboard rollbacks automatically disable auto-deploys as a safeguard. Keep them disabled while diagnosing the incident. After a corrective commit has passed PR checks and is merged, re-enable auto-deploys in the service Settings page and deploy the intended commit.

### Database and migration safety

A Render code rollback does **not** roll back PostgreSQL schema or data. Before a production migration:

- Prefer additive, backward-compatible migrations (expand/contract): add new nullable columns/tables first, deploy code that can work with both old and new schema, migrate data, then remove obsolete schema in a later release.
- Verify the backup/restore procedure and retention for the production database before destructive data or schema changes.
- Never assume a code rollback reverses a migration, restores deleted rows, or restores environment variables.
- If a migration is destructive or cannot be reversed safely, stop and use a reviewed database recovery plan or a forward-fix migration. Do not blindly run `alembic downgrade` in production.

### Incident notes

For each production incident, record the affected service, start/end time, last known-good commit, failing commit, user-visible impact, rollback or mitigation, database impact, and follow-up issue. Keep secrets and customer data out of incident notes.

## 5. Operational links

- [GitHub Actions](https://github.com/1234ashutosh1234/devflow/actions)
- [Production Render API](https://devflow-11ku.onrender.com)
- [Production frontend](https://devflow-1-s18m.onrender.com)
- [Render Deploys and Rollbacks documentation](https://render.com/docs/rollbacks)
- [Render Health Checks documentation](https://render.com/docs/health-checks)
- [Render Preview Environments documentation](https://render.com/docs/preview-environments)
