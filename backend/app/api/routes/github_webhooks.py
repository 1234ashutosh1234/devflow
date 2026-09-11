from __future__ import annotations

import hashlib
import hmac
import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.integrations.github import GitHubClient
from app.repositories.pull_request_repository import PullRequestRepository
from app.repositories.repository_repository import RepositoryRepository
from app.services.ai_review_service import AIReviewService
from app.services.github_diff_parser import parse_unified_diff
from app.services.github_review_publisher import GitHubReviewPublisher


router = APIRouter(
    prefix="/api/v1/github",
    tags=["GitHub Webhooks"],
)


# Prevent the same delivery/head revision from being processed repeatedly
# while this application process is running.
_processed_deliveries: set[str] = set()
_processed_review_heads: set[str] = set()


def verify_github_signature(
    payload: bytes,
    signature_header: str | None,
    secret: str,
) -> None:
    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing X-Hub-Signature-256 header.",
        )

    if not signature_header.startswith("sha256="):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid GitHub signature format.",
        )

    expected_signature = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
    )

    if not hmac.compare_digest(
        expected_signature,
        signature_header,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="GitHub webhook signature verification failed.",
        )


def _get_repository(
    db: Session,
    owner: str,
    repo_name: str,
):
    repository_full_name = f"{owner}/{repo_name}"

    repository_repo = RepositoryRepository(db)

    # The current DevFlow GitHub repository is mapped to project 1.
    repositories = repository_repo.get_by_project(
        project_id=1
    )

    repository = next(
        (
            item
            for item in repositories
            if item.provider == "github"
            and item.external_id == repository_full_name
        ),
        None,
    )

    return repository


def _get_reviewer_id(repository: Any) -> int:
    project = repository.project

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository project mapping not found.",
        )

    reviewer_id = getattr(project, "created_by_id", None)

    if reviewer_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Project creator is not configured. "
                "Cannot assign an automated review author."
            ),
        )

    return reviewer_id


@router.post("/webhook")
async def github_webhook(
    request: Request,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    x_github_event: Annotated[
        str | None,
        Header(alias="X-GitHub-Event"),
    ] = None,
    x_github_delivery: Annotated[
        str | None,
        Header(alias="X-GitHub-Delivery"),
    ] = None,
    x_hub_signature_256: Annotated[
        str | None,
        Header(alias="X-Hub-Signature-256"),
    ] = None,
) -> dict[str, Any]:
    settings = get_settings()

    if not settings.github_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub webhook secret is not configured.",
        )

    payload = await request.body()

    verify_github_signature(
        payload=payload,
        signature_header=x_hub_signature_256,
        secret=settings.github_webhook_secret,
    )

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook body is not valid JSON.",
        ) from exc

    event = x_github_event or "unknown"
    delivery_id = x_github_delivery or "unknown"

    # Ignore events that DevFlow does not process.
    if event != "pull_request":
        return {
            "accepted": True,
            "processed": False,
            "event": event,
            "delivery_id": delivery_id,
            "message": "Event acknowledged but not processed.",
        }

    action = data.get("action")

    supported_actions = {
        "opened",
        "synchronize",
        "reopened",
    }

    if action not in supported_actions:
        return {
            "accepted": True,
            "processed": False,
            "event": event,
            "action": action,
            "delivery_id": delivery_id,
            "message": (
                "Pull request action acknowledged "
                "but not scheduled for review."
            ),
        }

    # GitHub can retry deliveries. Avoid processing the exact same
    # delivery more than once during the current application lifetime.
    if delivery_id != "unknown" and delivery_id in _processed_deliveries:
        return {
            "accepted": True,
            "processed": False,
            "duplicate": True,
            "event": event,
            "action": action,
            "delivery_id": delivery_id,
            "message": "Webhook delivery was already processed.",
        }

    pull_request_data = data.get("pull_request") or {}
    repository_data = data.get("repository") or {}

    owner = (repository_data.get("owner") or {}).get("login")
    repo_name = repository_data.get("name")
    pull_number = pull_request_data.get("number")

    head_data = pull_request_data.get("head") or {}
    head_sha = head_data.get("sha")

    if not owner or not repo_name or not pull_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Webhook payload is missing repository owner, "
                "repository name, or pull request number."
            ),
        )

    if not head_sha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook payload is missing pull request head SHA.",
        )

    review_key = (
        f"{owner}/{repo_name}:"
        f"{pull_number}:"
        f"{head_sha}"
    )

    # Prevent duplicate review processing for the same PR revision.
    if review_key in _processed_review_heads:
        if delivery_id != "unknown":
            _processed_deliveries.add(delivery_id)

        return {
            "accepted": True,
            "processed": False,
            "duplicate": True,
            "event": event,
            "action": action,
            "delivery_id": delivery_id,
            "repository": f"{owner}/{repo_name}",
            "pull_request_number": pull_number,
            "head_sha": head_sha,
            "message": (
                "This pull request revision has already "
                "been reviewed."
            ),
        }

    repository = _get_repository(
        db=db,
        owner=owner,
        repo_name=repo_name,
    )

    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "DevFlow repository mapping not found for "
                f"{owner}/{repo_name}."
            ),
        )

    reviewer_id = _get_reviewer_id(repository)

    github = GitHubClient()

    try:
        pull_data = github.get_pull_request(
            owner=owner,
            repo=repo_name,
            pull_number=pull_number,
        )

        diff = github.get_pull_request_diff(
            owner=owner,
            repo=repo_name,
            pull_number=pull_number,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"GitHub request failed: {exc}",
        ) from exc

    parsed_files = parse_unified_diff(diff)

    # Ignore files that GitHub's diff parser could not make reviewable.
    parsed_files = [
        parsed_file
        for parsed_file in parsed_files
        if parsed_file.filename
        and parsed_file.content
    ]

    if not parsed_files:
        if delivery_id != "unknown":
            _processed_deliveries.add(delivery_id)

        _processed_review_heads.add(review_key)

        return {
            "accepted": True,
            "processed": False,
            "event": event,
            "action": action,
            "delivery_id": delivery_id,
            "repository": f"{owner}/{repo_name}",
            "pull_request_number": pull_number,
            "head_sha": head_sha,
            "files_reviewed": 0,
            "message": "No reviewable changed files were found.",
        }

    pull_request_repo = PullRequestRepository(db)

    pull_request = (
        pull_request_repo.get_by_external_number(
            repository_id=repository.id,
            external_number=pull_number,
        )
    )

    if pull_request is None:
        title = pull_data.get(
            "title",
            f"GitHub Pull Request #{pull_number}",
        )

        description = pull_data.get("body")

        head = pull_data.get("head") or {}
        base = pull_data.get("base") or {}

        source_branch = head.get(
            "ref",
            "unknown",
        )

        target_branch = base.get(
            "ref",
            repository.default_branch,
        )

        status_value = (
            "open"
            if pull_data.get("state") == "open"
            else "closed"
        )

        pull_request = pull_request_repo.create(
            repository_id=repository.id,
            external_number=pull_number,
            title=title,
            description=description,
            author_id=reviewer_id,
            source_branch=source_branch,
            target_branch=target_branch,
            status=status_value,
        )

    try:
        review = AIReviewService(db).run_review_for_files(
            pull_request_id=pull_request.id,
            user_id=reviewer_id,
            parsed_files=parsed_files,
        )

        publisher = GitHubReviewPublisher(db)

        publication = publisher.publish(
            review_id=review.id,
            user_id=reviewer_id,
        )

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Automatic GitHub review failed: {exc}",
        ) from exc

    if delivery_id != "unknown":
        _processed_deliveries.add(delivery_id)

    _processed_review_heads.add(review_key)

    return {
        "accepted": True,
        "processed": True,
        "event": event,
        "action": action,
        "delivery_id": delivery_id,
        "repository": f"{owner}/{repo_name}",
        "pull_request_number": pull_number,
        "head_sha": head_sha,
        "review_id": review.id,
        "review_status": review.status,
        "score": review.score,
        "files_reviewed": len(parsed_files),
        "summary": review.summary,
        "publication": publication,
        "message": (
            "GitHub pull request automatically reviewed "
            "and published to GitHub."
        ),
    }