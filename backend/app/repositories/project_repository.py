from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        project_id: int,
    ) -> Project | None:
        return self.db.get(Project, project_id)

    def get_by_organization(
        self,
        organization_id: int,
    ) -> list[Project]:
        statement = (
            select(Project)
            .where(
                Project.organization_id
                == organization_id
            )
            .order_by(Project.id.desc())
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_by_key(
        self,
        organization_id: int,
        key: str,
    ) -> Project | None:
        statement = select(Project).where(
            Project.organization_id
            == organization_id,
            Project.key == key,
        )

        return self.db.scalar(statement)

    def create(
        self,
        organization_id: int,
        name: str,
        key: str,
        description: str | None,
        created_by_id: int,
    ) -> Project:
        project = Project(
            organization_id=organization_id,
            name=name,
            key=key,
            description=description,
            created_by_id=created_by_id,
        )

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        return project