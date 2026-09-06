from pydantic import BaseModel

from app.core.permissions import OrganizationRole


class MembershipCreate(BaseModel):
    user_id: int
    role: OrganizationRole


class MembershipResponse(BaseModel):
    id: int
    organization_id: int
    user_id: int
    role: OrganizationRole

    model_config = {
        "from_attributes": True,
    }