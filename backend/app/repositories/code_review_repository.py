from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.code_review import CodeReview


class CodeReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, review_id: int) -> CodeReview | None:
        return self.db.get(CodeReview, review_id)

    def get_by_pull_request(
        self,
        pull_request_id: int,
    ) -> list[CodeReview]:
        statement = (
            select(CodeReview)
            .where(
                CodeReview.pull_request_id == pull_request_id
            )
            .order_by(CodeReview.id.desc())
        )

        return list(self.db.scalars(statement).all())

    def create(
        self,
        pull_request_id: int,
        reviewer_id: int | None,
        status: str,
        summary: str | None,
        score: int | None,
    ) -> CodeReview:
        review = CodeReview(
            pull_request_id=pull_request_id,
            reviewer_id=reviewer_id,
            status=status,
            summary=summary,
            score=score,
        )

        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)

        return review