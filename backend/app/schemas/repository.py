from pydantic import BaseModel, ConfigDict, Field


class RepositoryCreate(BaseModel):
    provider: str = Field(min_length=2, max_length=50)
    external_id: str | None = Field(default=None, max_length=255)
    clone_url: str = Field(min_length=1, max_length=500)
    default_branch: str = Field(default="main", min_length=1, max_length=100)


class RepositoryResponse(BaseModel):
    id: int
    project_id: int
    provider: str
    external_id: str | None
    clone_url: str
    default_branch: str

    model_config = ConfigDict(from_attributes=True)