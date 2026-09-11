from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.membership import (
    MembershipCreate,
    MembershipResponse,
)
from app.services.organization_service import (
    OrganizationService,
)


router = APIRouter(
    prefix="/api/v1/organizations",
    tags=["Organization Members"],
)


@router.get(
    "/{organization_id}/members",
    response_model=list[MembershipResponse],
)
def list_members(
    organization_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    service = OrganizationService(db)

    return service.list_members(
        organization_id=organization_id,
        user_id=current_user.id,
    )


@router.post(
    "/{organization_id}/members",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    organization_id: int,
    data: MembershipCreate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    service = OrganizationService(db)

    return service.add_member(
        organization_id=organization_id,
        actor_id=current_user.id,
        user_id=data.user_id,
        role=data.role,
    )