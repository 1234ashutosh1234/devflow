from typing import Any

import httpx

from app.core.config import get_settings


class GitHubClient:
    def __init__(self) -> None:
        settings = get_settings()

        self.base_url = settings.github_api_url.rstrip("/")
        self.token = settings.github_token

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    def get_pull_request(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> dict[str, Any]:
        url = (
            f"{self.base_url}/repos/"
            f"{owner}/{repo}/pulls/{pull_number}"
        )

        response = httpx.get(
            url,
            headers=self._headers(),
            timeout=30.0,
        )

        self._raise_for_status(response)

        return response.json()

    def get_pull_request_diff(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> str:
        url = (
            f"{self.base_url}/repos/"
            f"{owner}/{repo}/pulls/{pull_number}"
        )

        headers = self._headers()
        headers["Accept"] = "application/vnd.github.v3.diff"

        response = httpx.get(
            url,
            headers=headers,
            timeout=30.0,
        )

        self._raise_for_status(response)

        return response.text

    def submit_pull_request_review(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        body: str,
        event: str = "COMMENT",
        comments: list[dict[str, Any]] | None = None,
        commit_id: str | None = None,
    ) -> dict[str, Any]:
        url = (
            f"{self.base_url}/repos/"
            f"{owner}/{repo}/pulls/{pull_number}/reviews"
        )

        payload: dict[str, Any] = {
            "body": body,
            "event": event,
        }

        if comments:
            payload["comments"] = comments

        if commit_id:
            payload["commit_id"] = commit_id

        response = httpx.post(
            url,
            headers=self._headers(),
            json=payload,
            timeout=30.0,
        )

        self._raise_for_status(response)

        return response.json()

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.is_success:
            return

        try:
            github_error = response.json()
        except ValueError:
            github_error = {
                "message": response.text,
            }

        message = github_error.get(
            "message",
            "GitHub API request failed.",
        )

        errors = github_error.get("errors")

        if errors:
            message = f"{message}; errors={errors}"

        raise httpx.HTTPStatusError(
            (
                f"GitHub API error {response.status_code}: "
                f"{message}"
            ),
            request=response.request,
            response=response,
        )