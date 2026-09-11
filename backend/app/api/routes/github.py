from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.integrations.github import GitHubClient
from app.models.user import User
from app.repositories.pull_request_repository import (
    PullRequestRepository,
)
from app.repositories.repository_repository import (
    RepositoryRepository,
)
from app.schemas.github import GitHubPRReviewRequest
from app.services.ai_review_service import AIReviewService
from app.services.github_diff_parser import parse_unified_diff
from app.services.github_review_publisher import (
    GitHubReviewPublisher,
)


router = APIRouter(
    prefix="/api/v1/github",
    tags=["GitHub"],
)


@router.post(
    "/pull-request-review",
    status_code=status.HTTP_201_CREATED,
)
def review_github_pull_request(
    data: GitHubPRReviewRequest,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    repository_full_name = (
        f"{data.owner}/{data.repository}"
    )

    repository_repo = RepositoryRepository(db)

    repository = repository_repo.get_by_provider_external_id(
        provider="github",
        external_id=repository_full_name,
    )

    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "DevFlow repository mapping not found. "
                "Create a repository record with "
                "provider='github' and "
                f"external_id='{repository_full_name}'."
            ),
        )

    github = GitHubClient()

    try:
        pull_data = github.get_pull_request(
            owner=data.owner,
            repo=data.repository,
            pull_number=data.pull_number,
        )

        diff = github.get_pull_request_diff(
            owner=data.owner,
            repo=data.repository,
            pull_number=data.pull_number,
        )

    except httpx.HTTPStatusError as exc:
        response = exc.response

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"GitHub pull request #{data.pull_number} "
                    f"was not found in {repository_full_name}."
                ),
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "GitHub API request failed with "
                f"status {response.status_code}."
            ),
        ) from exc

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"GitHub connection failed: {exc}",
        ) from exc

    parsed_files = parse_unified_diff(diff)

    reviewable_files = [
        parsed_file
        for parsed_file in parsed_files
        if parsed_file.content.strip()
        and parsed_file.reviewable_lines
    ]

    if not reviewable_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "GitHub pull request does not contain "
                "reviewable text file changes."
            ),
        )

    pull_request_repo = PullRequestRepository(db)

    pull_request = (
        pull_request_repo.get_by_external_number(
            repository_id=repository.id,
            external_number=data.pull_number,
        )
    )

    if pull_request is None:
        title = pull_data.get(
            "title",
            f"GitHub Pull Request #{data.pull_number}",
        )

        description = pull_data.get("body")

        head = pull_data.get("head", {})
        base = pull_data.get("base", {})

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
            external_number=data.pull_number,
            title=title,
            description=description,
            author_id=current_user.id,
            source_branch=source_branch,
            target_branch=target_branch,
            status=status_value,
        )

    review = AIReviewService(db).run_review_for_files(
        pull_request_id=pull_request.id,
        user_id=current_user.id,
        parsed_files=reviewable_files,
    )

    return review


@router.post(
    "/reviews/{review_id}/publish",
)
def publish_github_review(
    review_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    publisher = GitHubReviewPublisher(db)

    try:
        return publisher.publish(
            review_id=review_id,
            user_id=current_user.id,
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc