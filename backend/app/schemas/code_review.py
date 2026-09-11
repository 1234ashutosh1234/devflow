from pydantic import BaseModel, ConfigDict, Field


class CodeReviewCreate(BaseModel):
    status: str = Field(
        default="pending",
        min_length=1,
        max_length=50,
    )
    summary: str | None = None
    score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class CodeReviewResponse(BaseModel):
    id: int
    pull_request_id: int
    reviewer_id: int | None
    status: str
    summary: str | None
    score: int | None

    model_config = ConfigDict(from_attributes=True)