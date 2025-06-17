"""
Tool helper utilities for consistent cross-cutting concerns
"""

import functools
from typing import Dict, Any, Callable, Optional
from fastmcp import Context
from migadu_mcp.utils.context_protection import truncate_response_if_needed


def with_context_protection(max_tokens: int = 2000):
    """Decorator to apply context protection to tool responses"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Dict[str, Any]:
            # Extract ctx from args/kwargs
            ctx = None
            for arg in args:
                if isinstance(arg, Context):
                    ctx = arg
                    break
            if not ctx:
                ctx = kwargs.get("ctx")

            result = await func(*args, **kwargs)

            if ctx and isinstance(result, dict):
                protected_result = await truncate_response_if_needed(
                    result, ctx=ctx, tool_name=func.__name__, max_tokens=max_tokens
                )

                # Check if response was summarized and log accordingly
                summary_keys = [
                    key for key in protected_result.keys() if key.endswith("_summary")
                ]
                if summary_keys:
                    await ctx.info(
                        "📊 Response summarized. Use specific get_* functions for details."
                    )

                return protected_result

            return result

        return wrapper

    return decorator


def with_default_domain():
    """Decorator to inject default domain for convenience functions"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Dict[str, Any]:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()

            # Inject domain as first argument after ctx
            new_args = list(args)
            if len(new_args) > 0 and isinstance(new_args[0], Context):
                new_args.insert(1, domain)
            else:
                new_args.insert(0, domain)

            return await func(*new_args, **kwargs)

        return wrapper

    return decorator


async def log_operation_start(ctx: Context, operation: str, target: str):
    """Standardized operation start logging"""
    await ctx.info(f"📋 {operation}: {target}")


async def log_operation_success(
    ctx: Context, operation: str, target: str, count: Optional[int] = None
):
    """Standardized operation success logging"""
    if count is not None:
        await ctx.info(f"✅ {operation} completed: found {count} items for {target}")
    else:
        await ctx.info(f"✅ {operation} completed: {target}")


async def log_operation_error(ctx: Context, operation: str, target: str, error: str):
    """Standardized operation error logging"""
    await ctx.error(f"❌ {operation} failed for {target}: {error}")
