# HireStone API

FastAPI backend for a job boarding plateform named **HireStone**. Here employers post jobs, candidates upload resumes
and apply, employers track applications, admins get platform-wide stats.

Built in phases:

- **Basic** — models, JWT auth, CRUD for jobs/resumes/applications.
- **Intermediate** — search filters, resume upload validation, status-change
  notifications, role-based guards, Alembic migrations.
- **Polished** — admin panel + reporting, pytest suite (35 tests), Docker Compose
  deployment, seed script for the first admin.

## Stack

- FastAPI + SQLAlchemy 2.0 (ORM)
- PostgreSQL (Docker) / SQLite (tests)
- Alembic migrations
- JWT auth (`python-jose`) + `bcrypt` password hashing
- `uv` for dependency/project management
- Docker Compose for local + deploy prep (FastAPI Cloud takes the same image)

## Project layout

```
app/
  main.py           FastAPI app, lifespan, CORS, router registration
  config.py         pydantic-settings (.env driven)
  database.py       SQLAlchemy engine/session/Base
  security.py       JWT encode/decode, bcrypt hash/verify
  deps.py           get_current_user + require_employer/candidate/admin guards
  models/           User, Employer, Candidate, JobListing, Resume, Application
  schemas/          Pydantic request/response models
  routers/          auth, employers, candidates, jobs, resumes, applications, admin
  services/         notifications.py (email stub, swap for SES/SendGrid)
  scripts/          create_admin.py — bootstrap the first admin user
alembic/            migrations (env.py wired to app settings + models metadata)
tests/              pytest suite, isolated SQLite per test
```

## Setup

```bash
cd job-board
uv sync                  # installs runtime deps into .venv
cp .env.example .env     # edit SECRET_KEY at minimum
```

### Run with Docker Compose (recommended)

```bash
docker compose up --build
```

This starts Postgres + the API. On container start the API runs
`alembic upgrade head` before serving. API is on `http://localhost:8000`,
docs at `http://localhost:8000/docs`.

### Run locally against SQLite (quick dev loop, no Docker)

```bash
export DATABASE_URL="sqlite:///./dev.db"
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

## Migrations

Schema is Alembic-owned — no `create_all` at runtime.

```bash
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head
uv run alembic downgrade -1     # roll back one step
```

## Creating the first admin

There is no public admin-registration endpoint (by design — admins shouldn't
self-serve). Bootstrap one via the CLI script:

```bash
uv run python -m app.scripts.create_admin admin@example.com StrongPass123
```

Re-running with an existing email promotes that user to admin instead of erroring.

## Tests

```bash
uv run pytest -q
```

35 tests covering: registration/login, role guards, job CRUD + search filters (keyword, location, job type, remote, salary range, pagination, closed-job exclusion), resume upload validation + primary-resume logic, application lifecycle (apply, duplicate block, status transitions, notifications fired), and admin (user list/activate/deactivate, application stats). 

Each test runs against a throwaway SQLite DB via dependency override — no shared state, no Docker needed.

## API overview

| Area | Endpoints |
|---|---|
| Auth | `POST /auth/register/employer`<br>`POST /auth/register/candidate`<br>`POST /auth/login` |
| Employers | `GET/PATCH /employers/me`<br>`GET /employers/{id}` |
| Candidates | `GET/PATCH /candidates/me` |
| Jobs | `POST /jobs`<br>`GET /jobs/search`<br>`GET/PATCH/DELETE /jobs/{id}` |
| Resumes | `POST /resumes`<br>`GET /resumes`<br>`PATCH /resumes/{id}/primary`<br>`DELETE /resumes/{id}` |
| Applications | `POST /applications`<br>`GET /applications/mine`<br>`GET /applications/job/{job_id}`<br>`PATCH /applications/{id}/status` |
| Admin | `GET /admin/users`<br>`PATCH /admin/users/{id}/activate\|deactivate`<br>`GET /admin/stats` |



**Job search filters:**
 (`GET /jobs/search`): `q`, `location`, `job_type`, `remote`,`salary_min`, `salary_max`, `employer_id`, `page`, `page_size`. Only `open` jobs are returned.

**Auth:**
`Authorization: Bearer <token>` from `/auth/login` (OAuth2 password flow — `username` field takes the email). Roles: `employer`, `candidate`, `admin`. Cross-role and cross-owner writes return `403`.

**Notifications:** 
Employer gets notified on new application, candidate gets
notified on status change. `app/services/notifications.py` logs to console if `SMTP_HOST` isn't set — swap in SendGrid/SES for production without touching call sites.

## Future Works

- Refresh tokens (currently access-token-only, `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`)
- Resume storage is a local Docker volume — move to S3/GCS for horizontal scaling
- No rate limiting on public endpoints (`/jobs/search`, `/auth/login`)
- FastAPI Cloud: same Docker image should work directly; point its Postgres add-on at `DATABASE_URL` and run `alembic upgrade head` as a release step.
