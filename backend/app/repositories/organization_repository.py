from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import (
    Organization,
    OrganizationMember,
)


class OrganizationRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        organization_id: int,
    ) -> Organization | None:
        return self.db.get(
            Organization,
            organization_id,
        )

    def get_by_slug(
        self,
        slug: str,
    ) -> Organization | None:
        statement = select(Organization).where(
            Organization.slug == slug
        )

        return self.db.scalar(statement)

    def get_by_owner(
        self,
        owner_id: int,
    ) -> list[Organization]:
        statement = (
            select(Organization)
            .where(
                Organization.owner_id == owner_id
            )
            .order_by(
                Organization.id.desc()
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_membership(
        self,
        organization_id: int,
        user_id: int,
    ) -> OrganizationMember | None:
        statement = select(
            OrganizationMember
        ).where(
            OrganizationMember.organization_id
            == organization_id,
            OrganizationMember.user_id == user_id,
        )

        return self.db.scalar(statement)

    def get_members(
        self,
        organization_id: int,
    ) -> list[OrganizationMember]:
        statement = (
            select(OrganizationMember)
            .where(
                OrganizationMember.organization_id
                == organization_id
            )
            .order_by(
                OrganizationMember.id
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def create_membership(
        self,
        organization_id: int,
        user_id: int,
        role: str,
    ) -> OrganizationMember:
        membership = OrganizationMember(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
        )

        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)

        return membership

    def create(
        self,
        name: str,
        slug: str,
        owner_id: int,
    ) -> Organization:
        organization = Organization(
            name=name,
            slug=slug,
            owner_id=owner_id,
        )

        self.db.add(organization)
        self.db.flush()

        membership = OrganizationMember(
            organization_id=organization.id,
            user_id=owner_id,
            role="owner",
        )

        self.db.add(membership)

        self.db.commit()
        self.db.refresh(organization)

        return organization