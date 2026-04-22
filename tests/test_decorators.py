"""Tests for @migadu_tool and @migadu_bulk_tool."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import Context, FastMCP
from pydantic import BaseModel

from migadu_mcp.utils.decorators import (
    _extract_ctx,
    migadu_bulk_tool,
    migadu_tool,
    resolve_domain,
)


class SampleSchema(BaseModel):
    value: str


def _make_ctx() -> Context:
    """Build a Context-shaped AsyncMock that passes isinstance checks."""
    ctx = MagicMock(spec=Context)
    ctx.info = AsyncMock()
    ctx.warning = AsyncMock()
    ctx.error = AsyncMock()
    return ctx


def test_extract_ctx_finds_positional() -> None:
    ctx = _make_ctx()
    assert _extract_ctx((ctx, "x"), {}) is ctx


def test_extract_ctx_finds_kwarg() -> None:
    ctx = _make_ctx()
    assert _extract_ctx((), {"ctx": ctx}) is ctx


def test_extract_ctx_returns_none_when_absent() -> None:
    assert _extract_ctx(("x", 1), {"other": "y"}) is None


def test_resolve_domain_uses_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MIGADU_DOMAIN", "from-env.example")
    import migadu_mcp.config as cfg

    monkeypatch.setattr(cfg, "_config", None)
    assert resolve_domain(None) == "from-env.example"


def test_resolve_domain_prefers_explicit() -> None:
    assert resolve_domain("explicit.example") == "explicit.example"


def test_resolve_domain_raises_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MIGADU_DOMAIN", raising=False)
    import migadu_mcp.config as cfg

    monkeypatch.setattr(cfg, "_config", None)
    with pytest.raises(ValueError):
        resolve_domain(None)


@pytest.mark.asyncio
async def test_migadu_tool_registers_and_runs() -> None:
    mcp = FastMCP("test")

    @migadu_tool(mcp, read_only=True)
    async def my_read_tool(x: str, ctx: Context) -> dict[str, Any]:
        return {"got": x}

    ctx = _make_ctx()
    result = await my_read_tool("hello", ctx)  # type: ignore[call-arg]
    assert result == {"got": "hello"}


@pytest.mark.asyncio
async def test_migadu_tool_logs_error_and_reraises() -> None:
    mcp = FastMCP("test")

    @migadu_tool(mcp)
    async def failing(ctx: Context) -> dict[str, Any]:
        raise RuntimeError("boom")

    ctx = _make_ctx()
    with pytest.raises(RuntimeError, match="boom"):
        await failing(ctx)  # type: ignore[call-arg]
    ctx.error.assert_awaited()


@pytest.mark.asyncio
async def test_migadu_tool_summarizes_when_over_budget() -> None:
    mcp = FastMCP("test")

    @migadu_tool(mcp, summarize_response=True, max_tokens=50)
    async def big_list(ctx: Context) -> dict[str, Any]:
        return {"mailboxes": [{"address": f"u{i}@x.com"} for i in range(200)]}

    ctx = _make_ctx()
    result = await big_list(ctx)  # type: ignore[call-arg]
    assert "mailboxes_summary" in result
    assert result["mailboxes_summary"]["total_count"] == 200


@pytest.mark.asyncio
async def test_migadu_bulk_tool_processes_all_items() -> None:
    mcp = FastMCP("test")

    @migadu_bulk_tool(mcp, SampleSchema, entity="sample")
    async def process(item: SampleSchema, ctx: Context) -> dict[str, Any]:
        return {"processed": item.value, "success": True}

    ctx = _make_ctx()
    result = await process(  # type: ignore[call-arg]
        [{"value": "a"}, {"value": "b"}], ctx
    )
    assert result["total_successful"] == 2
    assert result["total_failed"] == 0
    assert result["success"] is True


@pytest.mark.asyncio
async def test_migadu_bulk_tool_captures_per_item_validation_errors() -> None:
    mcp = FastMCP("test")

    @migadu_bulk_tool(mcp, SampleSchema, entity="sample")
    async def process(item: SampleSchema, ctx: Context) -> dict[str, Any]:
        return {"processed": item.value, "success": True}

    ctx = _make_ctx()
    result = await process(  # type: ignore[call-arg]
        [{"value": "ok"}, {"wrong_field": "x"}], ctx
    )
    assert result["total_successful"] == 1
    assert result["total_failed"] == 1
    assert result["success"] is False
    # The failing item should have error details
    failed = [r for r in result["items"] if not r.get("success", True)]
    assert len(failed) == 1
    assert "error" in failed[0]


@pytest.mark.asyncio
async def test_migadu_bulk_tool_captures_per_item_runtime_errors() -> None:
    mcp = FastMCP("test")

    @migadu_bulk_tool(mcp, SampleSchema, entity="sample")
    async def process(item: SampleSchema, ctx: Context) -> dict[str, Any]:
        if item.value == "bad":
            raise RuntimeError("oops")
        return {"processed": item.value, "success": True}

    ctx = _make_ctx()
    result = await process(  # type: ignore[call-arg]
        [{"value": "ok"}, {"value": "bad"}], ctx
    )
    assert result["total_successful"] == 1
    assert result["total_failed"] == 1


@pytest.mark.asyncio
async def test_migadu_bulk_tool_accepts_single_dict() -> None:
    """Bulk wrappers auto-wrap a lone dict into a one-item list."""
    mcp = FastMCP("test")

    @migadu_bulk_tool(mcp, SampleSchema, entity="sample")
    async def process(item: SampleSchema, ctx: Context) -> dict[str, Any]:
        return {"processed": item.value, "success": True}

    ctx = _make_ctx()
    result = await process({"value": "a"}, ctx)  # type: ignore[call-arg, arg-type]
    assert result["total_requested"] == 1
    assert result["total_successful"] == 1
