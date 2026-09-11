import json

from openai import OpenAI

from app.core.config import get_settings
from app.schemas.ai_review_result import AIReviewResult


class OpenAIReviewProvider:
    def __init__(self) -> None:
        settings = get_settings()

        if not settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured"
            )

        self.client = OpenAI(
            api_key=settings.openai_api_key
        )

        self.model = settings.openai_model

    def review(
        self,
        content: str,
        filename: str | None = None,
    ) -> AIReviewResult:
        filename_text = filename or "unknown"

        system_prompt = """
You are DevFlow, an expert software code reviewer.

Analyze the supplied source code carefully.

Look for:
- security vulnerabilities
- correctness bugs
- performance problems
- maintainability problems
- problematic coding patterns

Only report issues that are reasonably supported by the supplied code.

For every finding:
- choose a category
- choose severity
- provide a concise title
- explain the issue
- provide a line number when possible
- provide a concrete remediation suggestion
- give a confidence score between 0 and 1

Return only the requested structured result.
"""

        user_prompt = (
            f"Filename: {filename_text}\n\n"
            "Source code:\n"
            "```text\n"
            f"{content}\n"
            "```"
        )

        response_schema = {
            "type": "json_schema",
            "name": "devflow_code_review",
            "description": "Structured DevFlow code review result",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                    },
                    "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 100,
                    },
                    "findings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "category": {
                                    "type": "string",
                                },
                                "severity": {
                                    "type": "string",
                                },
                                "title": {
                                    "type": "string",
                                },
                                "description": {
                                    "type": "string",
                                },
                                "line_number": {
                                    "type": [
                                        "integer",
                                        "null",
                                    ],
                                },
                                "suggestion": {
                                    "type": [
                                        "string",
                                        "null",
                                    ],
                                },
                                "confidence": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                            },
                            "required": [
                                "category",
                                "severity",
                                "title",
                                "description",
                                "line_number",
                                "suggestion",
                                "confidence",
                            ],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": [
                    "summary",
                    "score",
                    "findings",
                ],
                "additionalProperties": False,
            },
        }

        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
            text={
                "format": response_schema,
            },
        )

        if not response.output_text:
            raise RuntimeError(
                "OpenAI returned an empty review response"
            )

        payload = json.loads(
            response.output_text
        )

        return AIReviewResult.model_validate(payload)