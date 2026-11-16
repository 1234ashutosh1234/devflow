import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.ai_reviews import router as ai_review_router
from app.api.routes.auth import router as auth_router
from app.api.routes.code_reviews import router as code_review_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.memberships import router as membership_router
from app.api.routes.organizations import router as organization_router
from app.api.routes.projects import router as project_router
from app.api.routes.pull_requests import router as pull_request_router
from app.api.routes.repositories import router as repository_router
from app.api.routes.github import router as github_router
from app.api.routes.github_publish import router as github_publish_router
from app.api.routes.github_webhooks import router as github_webhooks_router
from app.core.config import get_settings
from app.core.database import engine


settings = get_settings()

cors_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]


app = FastAPI(
    title="DevFlow API",
    description="AI-powered developer collaboration and code review platform.",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(organization_router)
app.include_router(project_router)
app.include_router(membership_router)
app.include_router(repository_router)
app.include_router(pull_request_router)
app.include_router(code_review_router)
app.include_router(dashboard_router)
app.include_router(ai_review_router)
app.include_router(github_router)
app.include_router(github_webhooks_router)
app.include_router(github_publish_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Liveness probe: confirms that the API process is responding."""
    return {"status": "ok"}


@app.get("/health/ready")
def readiness_check() -> dict[str, str]:
    """Readiness probe: confirms the API can reach its configured database."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        ) from exc

    return {
        "status": "ready",
        "database": "ok",
        "commit": os.getenv("RENDER_GIT_COMMIT", "unknown"),
    }
