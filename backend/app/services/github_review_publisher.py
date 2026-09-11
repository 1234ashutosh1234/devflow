from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.integrations.github import GitHubClient
from app.repositories.code_review_repository import (
    CodeReviewRepository,
)
from app.repositories.pull_request_repository import (
    PullRequestRepository,
)
from app.repositories.repository_repository import (
    RepositoryRepository,
)
from app.repositories.review_finding_repository import (
    ReviewFindingRepository,
)
from app.services.github_diff_parser import parse_unified_diff


class GitHubReviewPublisher:
    def __init__(self, db: Session):
        self.db = db
        self.github = GitHubClient()

        self.code_review_repository = CodeReviewRepository(db)
        self.pull_request_repository = (
            PullRequestRepository(db)
        )
        self.repository_repository = (
            RepositoryRepository(db)
        )
        self.finding_repository = (
            ReviewFindingRepository(db)
        )

    def publish(
        self,
        review_id: int,
        user_id: int,
    ) -> dict[str, Any]:
        review = self.code_review_repository.get_by_id(
            review_id
        )

        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Code review {review_id} was not found.",
            )

        pull_request = self.pull_request_repository.get_by_id(
            review.pull_request_id
        )

        if pull_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Pull request for code review "
                    f"{review_id} was not found."
                ),
            )

        repository = self.repository_repository.get_by_id(
            pull_request.repository_id
        )

        if repository is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repository mapping was not found.",
            )

        if repository.provider != "github":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "GitHub publishing requires a repository "
                    "with provider='github'."
                ),
            )

        repository_full_name = repository.external_id.strip()

        if "/" not in repository_full_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "GitHub repository external_id must be in "
                    "'owner/repository' format."
                ),
            )

        owner, repo_name = repository_full_name.split(
            "/",
            1,
        )

        try:
            pull_data = self.github.get_pull_request(
                owner=owner,
                repo=repo_name,
                pull_number=pull_request.external_number,
            )

            diff = self.github.get_pull_request_diff(
                owner=owner,
                repo=repo_name,
                pull_number=pull_request.external_number,
            )

        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "GitHub pull request lookup failed with "
                    f"status {exc.response.status_code}."
                ),
            ) from exc

        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"GitHub connection failed: {exc}",
            ) from exc

        head = pull_data.get("head") or {}
        head_sha = head.get("sha")

        if not head_sha:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "GitHub pull request did not return a "
                    "valid head commit SHA."
                ),
            )

        parsed_files = parse_unified_diff(diff)

        reviewable_lines_by_file = {
            parsed_file.filename: parsed_file.reviewable_lines
            for parsed_file in parsed_files
        }

        findings = self.finding_repository.get_by_code_review(
            review_id
        )

        comments: list[dict[str, Any]] = []
        skipped_findings = 0

        for finding in findings:
            filename = finding.filename
            line_number = finding.line_number

            if not filename or line_number is None:
                skipped_findings += 1
                continue

            valid_lines = reviewable_lines_by_file.get(
                filename
            )

            if not valid_lines:
                skipped_findings += 1
                continue

            if line_number not in valid_lines:
                skipped_findings += 1
                continue

            comments.append(
                {
                    "path": filename,
                    "line": line_number,
                    "side": "RIGHT",
                    "body": self._build_comment_body(
                        finding
                    ),
                }
            )

        summary = self._build_summary(
            review=review,
            finding_count=len(findings),
            comments_count=len(comments),
            skipped_count=skipped_findings,
        )

        event = self._choose_event(review)

        try:
            github_review = (
                self.github.submit_pull_request_review(
                    owner=owner,
                    repo=repo_name,
                    pull_number=pull_request.external_number,
                    body=summary,
                    event=event,
                    comments=comments,
                    commit_id=head_sha,
                )
            )

        except httpx.HTTPStatusError as exc:
            github_error = self._extract_github_error(exc)

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "GitHub review publishing failed: "
                    f"{github_error}"
                ),
            ) from exc

        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "GitHub connection failed while "
                    f"publishing: {exc}"
                ),
            ) from exc

        return {
            "published_by": "devflow_dev",
            "repository": repository_full_name,
            "pull_request_number": (
                pull_request.external_number
            ),
            "github_review_id": github_review.get("id"),
            "github_review_state": github_review.get("state"),
            "event": event,
            "comments_posted": len(comments),
            "comments_skipped": skipped_findings,
            "review_id": review.id,
            "score": review.score,
            "summary": review.summary,
        }

    @staticmethod
    def _build_comment_body(
        finding: Any,
    ) -> str:
        severity = str(
            finding.severity
        ).upper()

        parts = [
            f"**{severity}: {finding.title}**",
            "",
            finding.description,
        ]

        if finding.suggestion:
            parts.extend(
                [
                    "",
                    f"**Suggestion:** {finding.suggestion}",
                ]
            )

        confidence = getattr(
            finding,
            "confidence",
            None,
        )

        if confidence is not None:
            parts.extend(
                [
                    "",
                    f"Confidence: {confidence:.0%}",
                ]
            )

        return "\n".join(parts)

    @staticmethod
    def _build_summary(
        review: Any,
        finding_count: int,
        comments_count: int,
        skipped_count: int,
    ) -> str:
        score_text = (
            f"{review.score}/100"
            if review.score is not None
            else "not available"
        )

        summary_text = (
            review.summary
            or "Automated code review completed."
        )

        parts = [
            "## DevFlow AI Code Review",
            "",
            summary_text,
            "",
            f"**Score:** {score_text}",
            f"**Findings:** {finding_count}",
            f"**Inline comments:** {comments_count}",
        ]

        if skipped_count:
            parts.extend(
                [
                    f"**Skipped findings:** {skipped_count}",
                    "",
                    (
                        "Some findings could not be mapped to "
                        "reviewable GitHub diff lines."
                    ),
                ]
            )

        return "\n".join(parts)

    @staticmethod
    def _choose_event(review: Any) -> str:
        return "COMMENT"

    @staticmethod
    def _extract_github_error(
        exc: httpx.HTTPStatusError,
    ) -> str:
        try:
            payload = exc.response.json()

            message = payload.get(
                "message",
                "Unknown GitHub API error.",
            )

            errors = payload.get("errors")

            if errors:
                return (
                    f"{message}; errors={errors}"
                )

            return message

        except ValueError:
            return (
                exc.response.text
                or str(exc)
            )