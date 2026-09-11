from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.review_finding import ReviewFinding


class ReviewFindingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, finding_id: int) -> ReviewFinding | None:
        return self.db.get(ReviewFinding, finding_id)

    def create(
        self,
        code_review_id: int,
        category: str,
        severity: str,
        title: str,
        description: str,
        line_number: int | None,
        suggestion: str | None,
        confidence: float,
        filename: str | None = None,
    ) -> ReviewFinding:
        finding = ReviewFinding(
            code_review_id=code_review_id,
            filename=filename,
            category=category,
            severity=severity,
            title=title,
            description=description,
            line_number=line_number,
            suggestion=suggestion,
            confidence=confidence,
        )

        self.db.add(finding)
        self.db.flush()

        return finding

    def get_by_review(self, code_review_id: int) -> list[ReviewFinding]:
        statement = (
            select(ReviewFinding)
            .where(ReviewFinding.code_review_id == code_review_id)
            .order_by(
                ReviewFinding.line_number.asc().nulls_last(),
                ReviewFinding.id.asc(),
            )
        )

        return list(self.db.scalars(statement).all())

    def get_by_code_review(self, code_review_id: int) -> list[ReviewFinding]:
        """
        Backward-compatible alias used by AIReviewService.
        """
        return self.get_by_review(code_review_id)