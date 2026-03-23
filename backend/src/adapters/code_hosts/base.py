from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PullRequest:
    external_id: str
    url: str
    title: str
    state: str
    is_draft: bool
    head_branch: str
    base_branch: str
    ci_state: str | None = None
    review_state: str | None = None
    merged_at: str | None = None


class CodeHostAdapter(ABC):
    """Strategy interface for code host operations."""

    @abstractmethod
    async def create_pull_request(
        self,
        repo_ref: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str,
        is_draft: bool = False,
    ) -> PullRequest:
        ...

    @abstractmethod
    async def update_pull_request(
        self,
        repo_ref: str,
        pr_id: str,
        title: str | None = None,
        body: str | None = None,
        state: str | None = None,
    ) -> PullRequest:
        ...

    @abstractmethod
    async def get_pull_request(self, repo_ref: str, pr_id: str) -> PullRequest:
        ...

    @abstractmethod
    async def push_branch(
        self,
        repo_ref: str,
        branch: str,
        patch: bytes,
        commit_message: str,
    ) -> str:
        """Returns the commit SHA."""
        ...

    @abstractmethod
    async def resolve_repositories(self, search_query: str) -> list[str]:
        """Resolve a batch spec `on` search query to a list of repo refs."""
        ...
