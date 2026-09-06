import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.schemas.organization import OrganizationCreate


class OrganizationService:
    def __init__(self, db: Session):
        self.repository = OrganizationRepository(db)

    @staticmethod
    def generate_slug(name: str) -> str:
        slug = name.lower().strip()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")

        if not slug:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization name must contain letters or numbers",
            )

        return slug

    def create(
        self,
        data: OrganizationCreate,
        owner_id: int,
    ):
        slug = self.generate_slug(data.name)

        existing = self.repository.get_by_slug(slug)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Organization slug already exists",
            )

        return self.repository.create(
            name=data.name,
            slug=slug,
            owner_id=owner_id,
        )

    def get_user_organizations(
        self,
        user_id: int,
    ):
        return self.repository.get_by_owner(user_id)

    def get_user_membership(
        self,
        organization_id: int,
        user_id: int,
    ):
        membership = self.repository.get_membership(
            organization_id,
            user_id,
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization",
            )

        return membership