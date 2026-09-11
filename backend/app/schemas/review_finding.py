from pydantic import BaseModel, ConfigDict


class ReviewFindingResponse(BaseModel):
    id: int
    code_review_id: int

    filename: str | None

    category: str
    severity: str
    title: str
    description: str
    line_number: int | None
    suggestion: str
    confidence: float

    model_config = ConfigDict(
        from_attributes=True,
    )