from __future__ import annotations

from typing import Any, Iterable

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ai_reviewer.providers.factory import get_review_provider

from app.core.permissions import OrganizationRole
from app.repositories.code_review_repository import CodeReviewRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.pull_request_repository import PullRequestRepository
from app.repositories.repository_repository import RepositoryRepository
from app.repositories.review_finding_repository import (
    ReviewFindingRepository,
)


class AIReviewService:
    def __init__(self, db: Session):
        self.db = db

        self.code_review_repository = CodeReviewRepository(db)
        self.finding_repository = ReviewFindingRepository(db)
        self.pull_request_repository = PullRequestRepository(db)
        self.repository_repository = RepositoryRepository(db)
        self.organization_repository = OrganizationRepository(db)

    def _get_pull_request_and_check_access(
        self,
        pull_request_id: int,
        user_id: int,
    ):
        pull_request = self.pull_request_repository.get_by_id(
            pull_request_id
        )

        if pull_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pull request not found",
            )

        repository = self.repository_repository.get_by_id(
            pull_request.repository_id
        )

        if repository is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repository not found",
            )

        project = repository.project

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        membership = (
            self.organization_repository.get_membership(
                organization_id=project.organization_id,
                user_id=user_id,
            )
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of the organization",
            )

        try:
            role = OrganizationRole(membership.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid organization role",
            )

        role_levels = {
            OrganizationRole.VIEWER: 10,
            OrganizationRole.DEVELOPER: 20,
            OrganizationRole.ADMIN: 30,
            OrganizationRole.OWNER: 40,
        }

        if role_levels[role] < role_levels[
            OrganizationRole.DEVELOPER
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient organization permissions",
            )

        return pull_request

    @staticmethod
    def _extract_review_result(result: Any) -> tuple[
        str,
        int | None,
        list[Any],
    ]:
        if hasattr(result, "findings"):
            return (
                result.summary,
                result.score,
                result.findings,
            )

        return (
            result["summary"],
            result["score"],
            result["findings"],
        )

    def run_review(
        self,
        pull_request_id: int,
        user_id: int,
        content: str,
        filename: str | None = None,
    ):
        pull_request = self._get_pull_request_and_check_access(
            pull_request_id=pull_request_id,
            user_id=user_id,
        )

        provider = get_review_provider()

        try:
            result = provider.review(
                content=content,
                filename=filename,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI review provider failed: {exc}",
            ) from exc

        summary, score, findings = self._extract_review_result(
            result
        )

        status_value = (
            "completed"
            if not findings
            else "completed_with_findings"
        )

        review = self.code_review_repository.create(
            pull_request_id=pull_request.id,
            reviewer_id=user_id,
            status=status_value,
            summary=summary,
            score=score,
        )

        for finding in findings:
            self.finding_repository.create(
                code_review_id=review.id,
                category=finding.category,
                severity=finding.severity,
                title=finding.title,
                description=finding.description,
                line_number=finding.line_number,
                suggestion=finding.suggestion,
                confidence=finding.confidence,
                filename=filename,
            )

        self.db.commit()
        self.db.refresh(review)

        return review

    def run_review_for_files(
        self,
        pull_request_id: int,
        user_id: int,
        parsed_files: Iterable[Any],
    ):
        pull_request = self._get_pull_request_and_check_access(
            pull_request_id=pull_request_id,
            user_id=user_id,
        )

        provider = get_review_provider()

        files = [
            parsed_file
            for parsed_file in parsed_files
            if parsed_file.content.strip()
        ]

        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No reviewable source files were found.",
            )

        all_findings: list[tuple[Any, str]] = []
        scores: list[int] = []

        for parsed_file in files:
            try:
                result = provider.review(
                    content=parsed_file.content,
                    filename=parsed_file.filename,
                )
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=(
                        "AI review provider failed for "
                        f"'{parsed_file.filename}': {exc}"
                    ),
                ) from exc

            summary, score, findings = (
                self._extract_review_result(result)
            )

            if score is not None:
                scores.append(int(score))

            for finding in findings:
                all_findings.append(
                    (finding, parsed_file.filename)
                )

        status_value = (
            "completed"
            if not all_findings
            else "completed_with_findings"
        )

        average_score: int | None = None

        if scores:
            average_score = round(
                sum(scores) / len(scores)
            )

        review = self.code_review_repository.create(
            pull_request_id=pull_request.id,
            reviewer_id=user_id,
            status=status_value,
            summary=(
                "Local automated review completed with "
                f"{len(all_findings)} finding(s) across "
                f"{len(files)} file(s)."
            ),
            score=average_score,
        )

        for finding, filename in all_findings:
            self.finding_repository.create(
                code_review_id=review.id,
                category=finding.category,
                severity=finding.severity,
                title=finding.title,
                description=finding.description,
                line_number=finding.line_number,
                suggestion=finding.suggestion,
                confidence=finding.confidence,
                filename=filename,
            )

        self.db.commit()
        self.db.refresh(review)

        return review

    def list_findings(
        self,
        review_id: int,
        user_id: int,
    ):
        review = self.code_review_repository.get_by_id(
            review_id
        )

        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Code review not found",
            )

        self._get_pull_request_and_check_access(
            pull_request_id=review.pull_request_id,
            user_id=user_id,
        )

        return self.finding_repository.get_by_code_review(
            review_id
        )