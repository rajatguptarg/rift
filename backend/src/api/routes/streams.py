from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.api.dependencies import CurrentUserDep, DBDep
from src.adapters.mongo.workspace_execution_repo import WorkspaceExecutionRepository
from src.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


async def _workspace_event_stream(
    batch_change_id: str,
    run_id: str,
    db,
) -> AsyncGenerator[str, None]:
    """Poll workspace execution states and emit SSE events."""
    repo = WorkspaceExecutionRepository(db)
    seen_states: dict[str, str] = {}

    for _ in range(600):  # max ~10 min at 1s polling
        items = await repo.find_by_run(run_id)
        for item in items:
            prev = seen_states.get(item.id)
            if prev != item.state:
                seen_states[item.id] = item.state
                payload = json.dumps(
                    {
                        "id": item.id,
                        "repo_ref": item.repo_ref,
                        "state": item.state,
                        "duration_seconds": item.duration_seconds,
                        "error_message": item.error_message,
                    }
                )
                yield f"data: {payload}\n\n"

        # Check if all done
        all_terminal = all(
            we.state in ("SUCCEEDED", "FAILED", "SKIPPED", "CANCELLED")
            for we in items
        ) if items else False

        if all_terminal:
            yield "data: {\"event\": \"done\"}\n\n"
            break

        await asyncio.sleep(1)


@router.get("/batch-changes/{batch_change_id}/runs/{run_id}/stream")
async def stream_run(
    batch_change_id: str,
    run_id: str,
    db: DBDep,
    current_user: CurrentUserDep,
) -> StreamingResponse:
    return StreamingResponse(
        _workspace_event_stream(batch_change_id, run_id, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
