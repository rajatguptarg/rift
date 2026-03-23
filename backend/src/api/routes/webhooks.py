from __future__ import annotations

from fastapi import APIRouter, Request

from src.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/github")
async def github_webhook(request: Request) -> dict:
    await request.json()
    event_type = request.headers.get("X-GitHub-Event", "")
    logger.info("GitHub webhook received", event=event_type)
    # TODO: route to reconciliation service
    return {"received": True, "event": event_type}


@router.post("/gitlab")
async def gitlab_webhook(request: Request) -> dict:
    await request.json()
    event_type = request.headers.get("X-Gitlab-Event", "")
    logger.info("GitLab webhook received", event=event_type)
    return {"received": True, "event": event_type}
