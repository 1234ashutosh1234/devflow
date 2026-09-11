from datetime import datetime

from pydantic import BaseModel, Field


class DashboardReviewItem(BaseModel):
    review_id: int
    pull_request_id: int
    pull_request_number: int
    pull_request_title: str
    project_name: str
    repository_name: str
    review_status: str
    score: int | None
    finding_count: int = Field(ge=0)
    created_at: datetime


class DashboardSummaryResponse(BaseModel):
    total_pull_requests: int = Field(ge=0)
    total_reviews: int = Field(ge=0)
    total_findings: int = Field(ge=0)
    average_score: float | None = Field(default=None, ge=0, le=100)
    recent_reviews: list[DashboardReviewItem]