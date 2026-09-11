from pydantic import BaseModel, Field


class GitHubPRReviewRequest(BaseModel):
    owner: str = Field(
        min_length=1,
        max_length=100,
    )

    repository: str = Field(
        min_length=1,
        max_length=100,
    )

    pull_number: int = Field(
        gt=0,
    )