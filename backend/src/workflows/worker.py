from __future__ import annotations

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from src.core.config import settings
from src.core.logging import configure_logging, get_logger
from src.workflows.activities.workspace_runner import (
    capture_diff,
    clone_repository,
    execute_steps,
)
from src.workflows.apply_workflow import ApplyWorkflow
from src.workflows.preview_workflow import PreviewWorkflow

logger = get_logger(__name__)

TASK_QUEUE = settings.temporal_task_queue


async def run_worker() -> None:
    configure_logging()
    client = await Client.connect(settings.temporal_host, namespace=settings.temporal_namespace)
    logger.info("Temporal worker starting", task_queue=TASK_QUEUE)

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[PreviewWorkflow, ApplyWorkflow],
        activities=[clone_repository, execute_steps, capture_diff],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(run_worker())
