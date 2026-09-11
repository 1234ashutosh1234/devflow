from pydantic import BaseModel, ConfigDict, Field


class PullRequestCreate(BaseModel):
    external_number: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    source_branch: str = Field(min_length=1, max_length=255)
    target_branch: str = Field(min_length=1, max_length=255)
    status: str = Field(default="open", min_length=1, max_length=50)


class PullRequestResponse(BaseModel):
    id: int
    repository_id: int
    external_number: int
    title: str
    description: str | None
    author_id: int
    source_branch: str
    target_branch: str
    status: str

    model_config = ConfigDict(from_attributes=True)