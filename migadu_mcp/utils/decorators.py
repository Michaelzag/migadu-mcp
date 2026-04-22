"""Tool registration decorators.

`@migadu_tool` — read/single-target tools. Optional response summarization.
`@migadu_bulk_tool` — mutation tools that accept `list[dict]` and validate each item
against a Pydantic schema, returning a bulk-result envelope.

Both decorators register the resulting function with FastMCP and handle:
  - Standard logging via ctx (start/success/error)
  - Error propagation (single-target re-raises; bulk captures per-item)
  - Annotation hints (readOnlyHint, destructiveHint, idempotentHint)
"""

import inspect
from functools import wraps
from typing import Any, Awaitable, Callable, Optional, Tuple, Type, TypeVar

from fastmcp import Context, FastMCP
from pydantic import BaseModel

from migadu_mcp.utils.schemas import validate_with_schema
from migadu_mcp.utils.summarize import DEFAULT_MAX_TOKENS, summarize

ToolFunc = TypeVar("ToolFunc", bound=Callable[..., Awaitable[dict[str, Any]]])


def _extract_ctx(args: Tuple[Any, ...], kwargs: dict[str, Any]) -> Optional[Context]:
    for arg in args:
        if isinstance(arg, Context):
            return arg
    ctx = kwargs.get("ctx")
    return ctx if isinstance(ctx, Context) else None


def migadu_tool(
    mcp: FastMCP,
    *,
    read_only: bool = False,
    destructive: bool = False,
    idempotent: bool = True,
    summarize_response: bool = False,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> Callable[
    [Callable[..., Awaitable[dict[str, Any]]]], Callable[..., Awaitable[dict[str, Any]]]
]:
    """Register a single-target tool with FastMCP.

    The decorated function is called as-is with its original signature. Errors are
    logged via ctx and re-raised. If `summarize_response=True`, dict responses are
    passed through the static summarizer.
    """
    annotations = {
        "readOnlyHint": read_only,
        "destructiveHint": destructive,
        "idempotentHint": idempotent,
        "openWorldHint": True,
    }

    def decorator(
        func: Callable[..., Awaitable[dict[str, Any]]],
    ) -> Callable[..., Awaitable[dict[str, Any]]]:
        func_name = getattr(func, "__name__", "tool")

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
            ctx = _extract_ctx(args, kwargs)
            try:
                result = await func(*args, **kwargs)
            except Exception as exc:
                if ctx is not None:
                    await ctx.error(f"❌ {func_name} failed: {exc}")
                raise
            if summarize_response and isinstance(result, dict):
                return summarize(result, max_tokens=max_tokens)
            return result

        # Preserve the original function's signature with resolved annotations so
        # FastMCP's Pydantic-based schema builder sees real types (not strings from
        # `from __future__ import annotations`). Evaluation can fail for exotic
        # annotations; in that case FastMCP falls back to the raw (string) form.
        try:
            resolved = dict(inspect.get_annotations(func, eval_str=True))
            setattr(func, "__annotations__", resolved)
        except Exception:  # nosec B110 — best-effort annotation resolution
            pass
        setattr(wrapper, "__signature__", inspect.signature(func))
        setattr(wrapper, "__annotations__", dict(getattr(func, "__annotations__", {})))
        # Register with FastMCP as a side effect; return the wrapper so the function
        # remains directly callable (tests and internal dispatch).
        mcp.tool(annotations=annotations)(wrapper)
        return wrapper

    return decorator


def migadu_bulk_tool(
    mcp: FastMCP,
    schema: Type[BaseModel],
    *,
    entity: str,
    destructive: bool = False,
    idempotent: bool = True,
) -> Callable[..., Any]:
    """Register a bulk mutation tool.

    The decorated function processes ONE validated item at a time. The outer tool
    accepts `list[dict]`, validates each, calls the inner function, and returns a
    bulk-result envelope with per-item success/failure.
    """
    annotations = {
        "readOnlyHint": False,
        "destructiveHint": destructive,
        "idempotentHint": idempotent,
        "openWorldHint": True,
    }

    def decorator(
        process_one: Callable[..., Awaitable[dict[str, Any]]],
    ) -> Callable[..., Awaitable[dict[str, Any]]]:
        async def bulk_wrapper(items: list, ctx: Context) -> dict:
            normalized: list[dict[str, Any]] = (
                [items] if isinstance(items, dict) else list(items)
            )
            total = len(normalized)
            plural = entity if total == 1 else f"{entity}s"
            await ctx.info(f"🔄 Processing {total} {plural}")

            results: list[dict[str, Any]] = []
            for item in normalized:
                try:
                    validated = validate_with_schema(item, schema)
                    result = await process_one(validated, ctx)
                    results.append(result)
                except Exception as exc:
                    results.append({"error": str(exc), "item": item, "success": False})

            successful = sum(1 for r in results if r.get("success", True))
            failed = total - successful

            if failed == 0:
                await ctx.info(f"✅ Processed {successful}/{total} {plural}")
            else:
                await ctx.warning(
                    f"⚠️ Processed {successful}/{total} {plural}; {failed} failed"
                )

            return {
                "items": results,
                "total_requested": total,
                "total_successful": successful,
                "total_failed": failed,
                "success": failed == 0,
            }

        bulk_wrapper.__name__ = getattr(process_one, "__name__", "bulk_tool")
        bulk_wrapper.__qualname__ = getattr(
            process_one, "__qualname__", bulk_wrapper.__name__
        )
        bulk_wrapper.__doc__ = getattr(process_one, "__doc__", None)
        mcp.tool(annotations=annotations)(bulk_wrapper)
        return bulk_wrapper

    return decorator


def resolve_domain(domain: Optional[str]) -> str:
    """Resolve an optional domain arg against `MIGADU_DOMAIN` env var."""
    if domain:
        return domain
    from migadu_mcp.config import get_config

    default = get_config().default_domain
    if not default:
        raise ValueError("No domain provided and MIGADU_DOMAIN is not set")
    return default
