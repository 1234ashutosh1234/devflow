from pydantic import BaseModel, Field


class AIReviewRequest(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=200_000,
    )

    filename: str | None = Field(
        default=None,
        max_length=255,
    )