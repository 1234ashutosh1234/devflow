from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    owner_id: int

    model_config = {
        "from_attributes": True,
    }