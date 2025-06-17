#!/usr/bin/env python3
"""
Generic bulk processing utilities for handling JSON objects uniformly
"""

from typing import Dict, Any, List, Callable, Iterator, Type
from functools import wraps
from fastmcp import Context
from pydantic import BaseModel, ValidationError


def ensure_iterable(items: Any) -> Iterator[Any]:
    """
    Convert single item or iterable to iterator - works for ANY type

    Args:
        items: Single item or iterable of items

    Returns:
        Iterator over the items

    Examples:
        ensure_iterable({"target": "april"}) -> Iterator[{"target": "april"}]
        ensure_iterable([{"target": "april"}, {"target": "bob"}]) -> Iterator[dict, dict]
    """
    # Check if it's iterable but not a string, dict, or bytes
    if hasattr(items, "__iter__") and not isinstance(items, (str, dict, bytes)):
        return iter(items)
    else:
        return iter([items])


def bulk_processor(processor_func: Callable) -> Callable:
    """
    Decorator that makes any single-item processor work with bulk items

    Args:
        processor_func: Async function that processes a single item dict

    Returns:
        Wrapped function that can handle single items or lists

    Usage:
        @bulk_processor
        async def process_single_mailbox(item: Dict[str, Any], ctx: Context) -> Dict[str, Any]:
            # Handle single mailbox logic
            return {"mailbox": "created", "success": True}

        # Now can be called with single item or list:
        await process_single_mailbox({"target": "april", "name": "April"}, ctx)
        await process_single_mailbox([{...}, {...}, {...}], ctx)
    """

    @wraps(processor_func)
    async def wrapper(items: Any, *args, **kwargs) -> Dict[str, Any]:
        results = []
        total_requested = 0

        for item in ensure_iterable(items):
            total_requested += 1
            try:
                result = await processor_func(item, *args, **kwargs)
                results.append(result)
            except Exception as e:
                # Include failed items with error information
                error_result = {"error": str(e), "item": str(item), "success": False}
                results.append(error_result)

        # Calculate success metrics
        successful_results = [r for r in results if r.get("success", True)]
        failed_results = [r for r in results if not r.get("success", True)]

        return {
            "items": results,
            "total_requested": total_requested,
            "total_processed": len(results),
            "total_successful": len(successful_results),
            "total_failed": len(failed_results),
            "success": len(failed_results) == 0,
        }

    return wrapper


async def log_bulk_operation_start(
    ctx: Context, operation: str, count: int, entity_type: str
):
    """Log the start of a bulk operation"""
    if count == 1:
        await ctx.info(f"🔄 {operation} {entity_type}")
    else:
        await ctx.info(f"🔄 {operation} {count} {entity_type}s")


async def log_bulk_operation_result(
    ctx: Context, operation: str, result: Dict[str, Any], entity_type: str
):
    """Log the result of a bulk operation"""
    total = result.get("total_requested", 0)
    successful = result.get("total_successful", 0)
    failed = result.get("total_failed", 0)

    if total == 1:
        if failed == 0:
            await ctx.info(f"✅ {operation} {entity_type} completed successfully")
        else:
            await ctx.error(f"❌ {operation} {entity_type} failed")
    else:
        if failed == 0:
            await ctx.info(
                f"✅ {operation} completed: {successful}/{total} {entity_type}s processed successfully"
            )
        else:
            await ctx.warning(
                f"⚠️ {operation} completed with issues: {successful}/{total} {entity_type}s succeeded, {failed} failed"
            )


def validate_required_fields(
    item: Dict[str, Any], required_fields: List[str], operation: str
) -> None:
    """Validate that required fields are present in the item dict"""
    missing_fields = [field for field in required_fields if field not in item]
    if missing_fields:
        raise ValueError(
            f"{operation} requires fields: {', '.join(missing_fields)}. Missing: {', '.join(missing_fields)}"
        )


def get_field_with_default(
    item: Dict[str, Any], field: str, default: Any = None
) -> Any:
    """Get field from dict with default value if not present"""
    return item.get(field, default)


def validate_with_schema(
    data: Dict[str, Any], schema_class: Type[BaseModel]
) -> BaseModel:
    """Validate dictionary data against a Pydantic schema"""
    try:
        return schema_class(**data)
    except ValidationError as e:
        # Format validation errors for better readability
        error_messages = []
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_messages.append(f"{field}: {message}")

        raise ValueError(f"Validation failed: {'; '.join(error_messages)}")
    except Exception as e:
        raise ValueError(f"Schema validation failed: {e}")


def bulk_processor_with_schema(schema_class: Type[BaseModel]):
    """
    Decorator factory that creates a bulk processor with Pydantic schema validation.

    Args:
        schema_class: Pydantic BaseModel class for validation

    Returns:
        Decorator that validates input data and processes items in bulk

    Usage:
        from migadu_mcp.utils.schemas import MailboxCreateRequest

        @bulk_processor_with_schema(MailboxCreateRequest)
        async def process_create_mailbox(validated_item: MailboxCreateRequest, ctx: Context) -> Dict[str, Any]:
            # Use validated_item.target, validated_item.name, etc.
            return {"success": True}
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(items: Any, *args, **kwargs) -> Dict[str, Any]:
            results = []
            total_requested = 0

            for item in ensure_iterable(items):
                total_requested += 1
                try:
                    # Validate with Pydantic schema
                    validated_item = validate_with_schema(item, schema_class)

                    # Call the original function with validated data
                    result = await func(validated_item, *args, **kwargs)
                    results.append(result)

                except Exception as e:
                    # Include failed items with error information
                    error_result = {
                        "error": str(e),
                        "item": str(item),
                        "success": False,
                    }
                    results.append(error_result)

            # Calculate success metrics
            successful_results = [r for r in results if r.get("success", True)]
            failed_results = [r for r in results if not r.get("success", True)]

            return {
                "items": results,
                "total_requested": total_requested,
                "total_processed": len(results),
                "total_successful": len(successful_results),
                "total_failed": len(failed_results),
                "success": len(failed_results) == 0,
            }

        return wrapper

    return decorator
