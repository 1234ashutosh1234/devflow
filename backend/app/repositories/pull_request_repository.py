from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pull_request import PullRequest


class PullRequestRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, pull_request_id: int) -> PullRequest | None:
        return self.db.get(PullRequest, pull_request_id)

    def get_by_external_number(
        self,
        repository_id: int,
        external_number: int,
    ) -> PullRequest | None:
        statement = select(PullRequest).where(
            PullRequest.repository_id == repository_id,
            PullRequest.external_number == external_number,
        )

        return self.db.scalar(statement)

    def get_by_repository(
        self,
        repository_id: int,
    ) -> list[PullRequest]:
        statement = (
            select(PullRequest)
            .where(PullRequest.repository_id == repository_id)
            .order_by(PullRequest.id.desc())
        )

        return list(self.db.scalars(statement).all())

    def create(
        self,
        repository_id: int,
        external_number: int,
        title: str,
        description: str | None,
        author_id: int,
        source_branch: str,
        target_branch: str,
        status: str,
    ) -> PullRequest:
        pull_request = PullRequest(
            repository_id=repository_id,
            external_number=external_number,
            title=title,
            description=description,
            author_id=author_id,
            source_branch=source_branch,
            target_branch=target_branch,
            status=status,
        )

        self.db.add(pull_request)
        self.db.commit()
        self.db.refresh(pull_request)

        return pull_request