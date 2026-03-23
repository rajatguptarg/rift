from __future__ import annotations

import httpx

from src.adapters.code_hosts.base import CodeHostAdapter, PullRequest
from src.core.logging import get_logger

logger = get_logger(__name__)


class GitLabAdapter(CodeHostAdapter):
    """GitLab code host adapter using the GitLab REST API."""

    def __init__(self, token: str, base_url: str = "https://gitlab.com") -> None:
        self._token = token
        self._base = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=f"{self._base}/api/v4",
            headers=self._headers,
            timeout=30,
        )

    async def create_pull_request(
        self,
        repo_ref: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str,
        is_draft: bool = False,
    ) -> PullRequest:
        encoded = repo_ref.replace("/", "%2F")
        prefix = "Draft: " if is_draft else ""
        async with self._client() as client:
            resp = await client.post(
                f"/projects/{encoded}/merge_requests",
                json={
                    "title": f"{prefix}{title}",
                    "description": body,
                    "source_branch": head_branch,
                    "target_branch": base_branch,
                    "draft": is_draft,
                },
            )
            resp.raise_for_status()
            return self._map_mr(resp.json())

    async def update_pull_request(
        self,
        repo_ref: str,
        pr_id: str,
        title: str | None = None,
        body: str | None = None,
        state: str | None = None,
    ) -> PullRequest:
        encoded = repo_ref.replace("/", "%2F")
        payload: dict = {}
        if title:
            payload["title"] = title
        if body:
            payload["description"] = body
        if state == "closed":
            payload["state_event"] = "close"
        async with self._client() as client:
            resp = await client.put(f"/projects/{encoded}/merge_requests/{pr_id}", json=payload)
            resp.raise_for_status()
            return self._map_mr(resp.json())

    async def get_pull_request(self, repo_ref: str, pr_id: str) -> PullRequest:
        encoded = repo_ref.replace("/", "%2F")
        async with self._client() as client:
            resp = await client.get(f"/projects/{encoded}/merge_requests/{pr_id}")
            resp.raise_for_status()
            return self._map_mr(resp.json())

    async def push_branch(
        self,
        repo_ref: str,
        branch: str,
        patch: bytes,
        commit_message: str,
    ) -> str:
        logger.info("push_branch stub (gitlab)", repo=repo_ref, branch=branch)
        return "stub-sha"

    async def resolve_repositories(self, search_query: str) -> list[str]:
        async with self._client() as client:
            resp = await client.get("/projects", params={"search": search_query, "per_page": 100})
            resp.raise_for_status()
            return [p["path_with_namespace"] for p in resp.json()]

    def _map_mr(self, data: dict) -> PullRequest:
        return PullRequest(
            external_id=str(data["iid"]),
            url=data["web_url"],
            title=data["title"],
            state=data["state"],
            is_draft=data.get("draft", False),
            head_branch=data["source_branch"],
            base_branch=data["target_branch"],
            merged_at=data.get("merged_at"),
        )
