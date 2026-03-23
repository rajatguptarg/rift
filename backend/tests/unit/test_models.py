"""Unit tests for core models."""
from __future__ import annotations

import pytest
from src.models.common import (
    CursorPage,
    PageParams,
    ErrorDetail,
    ErrorResponse,
    SortOrder,
)
from src.models.batch_change import BatchChangeState, VALID_TRANSITIONS


class TestCursorPage:
    def test_empty_items(self):
        page: CursorPage[str] = CursorPage(items=[])
        assert page.items == []
        assert page.next_cursor is None
        assert page.total is None

    def test_with_items_and_cursor(self):
        page: CursorPage[str] = CursorPage(
            items=["a", "b"], next_cursor="abc", total=10
        )
        assert len(page.items) == 2
        assert page.next_cursor == "abc"
        assert page.total == 10


class TestPageParams:
    def test_defaults(self):
        params = PageParams()
        assert params.cursor is None
        assert params.limit == 25

    def test_custom_limit(self):
        params = PageParams(limit=50)
        assert params.limit == 50

    def test_limit_min_enforced(self):
        with pytest.raises(Exception):
            PageParams(limit=0)

    def test_limit_max_enforced(self):
        with pytest.raises(Exception):
            PageParams(limit=101)


class TestErrorModels:
    def test_error_detail(self):
        detail = ErrorDetail(code="NOT_FOUND", message="Resource not found")
        assert detail.code == "NOT_FOUND"
        assert detail.message == "Resource not found"
        assert detail.details == {}

    def test_error_response(self):
        detail = ErrorDetail(code="ERR", message="msg")
        resp = ErrorResponse(error=detail)
        assert resp.error.code == "ERR"


class TestBatchChangeState:
    def test_all_states_exist(self):
        states = [s.value for s in BatchChangeState]
        assert "DRAFT" in states
        assert "ACTIVE" in states
        assert "ARCHIVED" in states

    def test_valid_draft_transitions(self):
        transitions = VALID_TRANSITIONS[BatchChangeState.DRAFT]
        assert BatchChangeState.PREVIEW_RUNNING in transitions
        assert BatchChangeState.ARCHIVED in transitions

    def test_sort_order_values(self):
        assert SortOrder.ASC == "asc"
        assert SortOrder.DESC == "desc"
