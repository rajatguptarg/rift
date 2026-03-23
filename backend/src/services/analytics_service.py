from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.adapters.mongo.changeset_repo import ChangesetRepository
from src.models.analytics import BatchChangeStats, BurndownDaily
from src.models.changeset import ChangesetState, CIState, ReviewDecision


class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._repo = ChangesetRepository(db)

    async def compute_stats(self, batch_change_id: str) -> BatchChangeStats:
        changesets = await self._repo.find_by_batch_change(batch_change_id, limit=5000)
        stats = BatchChangeStats(batch_change_id=batch_change_id)
        stats.total = len(changesets)
        for cs in changesets:
            match cs.state:
                case ChangesetState.UNPUBLISHED:
                    stats.unpublished += 1
                case ChangesetState.OPEN:
                    stats.open += 1
                case ChangesetState.DRAFT:
                    stats.draft += 1
                case ChangesetState.MERGED:
                    stats.merged += 1
                case ChangesetState.CLOSED:
                    stats.closed += 1
                case ChangesetState.ARCHIVED:
                    stats.archived += 1
            if cs.ci_state == CIState.PASSED:
                stats.ci_passed += 1
            elif cs.ci_state == CIState.FAILED:
                stats.ci_failed += 1
            if cs.review_state == ReviewDecision.APPROVED:
                stats.review_approved += 1
        return stats

    async def compute_burndown(
        self, batch_change_id: str, days: int = 30
    ) -> list[BurndownDaily]:
        changesets = await self._repo.find_by_batch_change(batch_change_id, limit=5000)
        today = date.today()
        start = today - timedelta(days=days)

        by_day: dict[date, dict[str, int]] = defaultdict(
            lambda: {"total": 0, "merged": 0, "closed": 0, "open": 0}
        )

        for cs in changesets:
            d = cs.created_at.date()
            if d < start:
                d = start
            by_day[d]["total"] += 1
            if cs.state == ChangesetState.MERGED and cs.merged_at:
                by_day[cs.merged_at.date()]["merged"] += 1
            elif cs.state == ChangesetState.CLOSED:
                by_day[d]["closed"] += 1
            else:
                by_day[d]["open"] += 1

        result = []
        for day_offset in range(days + 1):
            d = start + timedelta(days=day_offset)
            day_data = by_day.get(d, {"total": 0, "merged": 0, "closed": 0, "open": 0})
            result.append(
                BurndownDaily(
                    batch_change_id=batch_change_id,
                    date=d,
                    **day_data,
                )
            )
        return result
