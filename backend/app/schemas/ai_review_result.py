from pydantic import BaseModel, Field


class AIReviewFinding(BaseModel):
    category: str = Field(
        description="One of security, bug, performance, maintainability, or style."
    )

    severity: str = Field(
        description="One of critical, high, medium, or low."
    )

    title: str

    description: str

    line_number: int | None = None

    suggestion: str | None = None

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


class AIReviewResult(BaseModel):
    summary: str

    score: int = Field(
        ge=0,
        le=100,
    )

    findings: list[AIReviewFinding]