from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    key: str = Field(min_length=2, max_length=20)
    description: str | None = Field(
        default=None,
        max_length=2000,
    )


class ProjectResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    key: str
    description: str | None
    created_by_id: int

    model_config = {
        "from_attributes": True,
    }