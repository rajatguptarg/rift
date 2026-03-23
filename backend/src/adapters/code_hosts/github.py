from __future__ import annotations

import httpx

from src.adapters.code_hosts.base import CodeHostAdapter, PullRequest
from src.core.logging import get_logger

logger = get_logger(__name__)


class GitHubAdapter(CodeHostAdapter):
    """GitHub code host adapter using the GitHub REST API."""

    API_BASE = "https://api.github.com"

    def __init__(self, token: str, base_url: str | None = None) -> None:
        self._token = token
        self._base = base_url or self.API_BASE
        self._headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self._base, headers=self._headers, timeout=30)

    async def create_pull_request(
        self,
        repo_ref: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str,
        is_draft: bool = False,
    ) -> PullRequest:
        async with self._client() as client:
            resp = await client.post(
                f"/repos/{repo_ref}/pulls",
                json={
                    "title": title,
                    "body": body,
                    "head": head_branch,
                    "base": base_branch,
                    "draft": is_draft,
                },
            )
            resp.raise_for_status()
            data = resp.json()
        return self._map_pr(data)

    async def update_pull_request(
        self,
        repo_ref: str,
        pr_id: str,
        title: str | None = None,
        body: str | None = None,
        state: str | None = None,
    ) -> PullRequest:
        payload: dict = {}
        if title:
            payload["title"] = title
        if body:
            payload["body"] = body
        if state:
            payload["state"] = state
        async with self._client() as client:
            resp = await client.patch(f"/repos/{repo_ref}/pulls/{pr_id}", json=payload)
            resp.raise_for_status()
            return self._map_pr(resp.json())

    async def get_pull_request(self, repo_ref: str, pr_id: str) -> PullRequest:
        async with self._client() as client:
            resp = await client.get(f"/repos/{repo_ref}/pulls/{pr_id}")
            resp.raise_for_status()
            return self._map_pr(resp.json())

    async def push_branch(
        self,
        repo_ref: str,
        branch: str,
        patch: bytes,
        commit_message: str,
    ) -> str:
        # Simplified: actual implementation would apply the patch via commits API
        logger.info("push_branch stub", repo=repo_ref, branch=branch)
        return "stub-sha"

    async def resolve_repositories(self, search_query: str) -> list[str]:
        async with self._client() as client:
            resp = await client.get(
                "/search/repositories",
                params={"q": search_query, "per_page": 100},
            )
            resp.raise_for_status()
            return [item["full_name"] for item in resp.json().get("items", [])]

    def _map_pr(self, data: dict) -> PullRequest:
        return PullRequest(
            external_id=str(data["number"]),
            url=data["html_url"],
            title=data["title"],
            state=data["state"],
            is_draft=data.get("draft", False),
            head_branch=data["head"]["ref"],
            base_branch=data["base"]["ref"],
            merged_at=data.get("merged_at"),
        )
