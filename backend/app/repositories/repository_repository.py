from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.repository import Repository


class RepositoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, repository_id: int) -> Repository | None:
        return self.db.get(Repository, repository_id)

    def get_by_external_id(
        self,
        project_id: int,
        external_id: str,
    ) -> Repository | None:
        statement = select(Repository).where(
            Repository.project_id == project_id,
            Repository.external_id == external_id,
        )
        return self.db.scalar(statement)

    def get_by_provider_external_id(
        self,
        provider: str,
        external_id: str,
    ) -> Repository | None:
        statement = (
            select(Repository)
            .where(
                Repository.provider == provider,
                Repository.external_id == external_id,
            )
            .order_by(Repository.id.desc())
        )
        return self.db.scalar(statement)

    def get_by_project(self, project_id: int) -> list[Repository]:
        statement = (
            select(Repository)
            .where(Repository.project_id == project_id)
            .order_by(Repository.id.desc())
        )

        return list(self.db.scalars(statement).all())

    def create(
        self,
        project_id: int,
        provider: str,
        external_id: str | None,
        clone_url: str,
        default_branch: str,
    ) -> Repository:
        repository = Repository(
            project_id=project_id,
            provider=provider,
            external_id=external_id,
            clone_url=clone_url,
            default_branch=default_branch,
        )

        self.db.add(repository)
        self.db.commit()
        self.db.refresh(repository)

        return repository