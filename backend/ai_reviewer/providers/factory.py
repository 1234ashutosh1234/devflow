from app.core.config import get_settings
from ai_reviewer.agents.code_review_agent import AIReviewAgent
from ai_reviewer.providers.openai_provider import OpenAIReviewProvider


class ReviewProvider:
    def review(
        self,
        content: str,
        filename: str | None = None,
    ):
        raise NotImplementedError


class LocalReviewProvider(ReviewProvider):
    def __init__(self) -> None:
        self.agent = AIReviewAgent()

    def review(
        self,
        content: str,
        filename: str | None = None,
    ):
        findings = self.agent.analyze(
            content=content,
            filename=filename,
        )

        score = 100

        penalties = {
            "critical": 30,
            "high": 20,
            "medium": 10,
            "low": 4,
        }

        for finding in findings:
            score -= penalties.get(
                finding.severity.lower(),
                5,
            )

        score = max(
            0,
            min(100, score),
        )

        summary = (
            "Local automated review completed with "
            f"{len(findings)} finding(s)."
        )

        if not findings:
            summary = (
                "Local automated review found no issues."
            )

        return {
            "summary": summary,
            "score": score,
            "findings": findings,
        }


def get_review_provider():
    settings = get_settings()

    if (
        settings.ai_review_provider.lower() == "openai"
        and settings.openai_api_key
    ):
        return OpenAIReviewProvider()

    return LocalReviewProvider()