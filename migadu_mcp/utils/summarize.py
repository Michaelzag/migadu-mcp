"""Static response summarizer.

Keeps tool responses under a rough token budget by truncating large lists to a sample
and attaching a count. No AI sampling, no external calls.
"""

from __future__ import annotations

import json
from typing import Any

DEFAULT_MAX_TOKENS = 2000
DEFAULT_SAMPLE_SIZE = 3

# Keys we recognize as list responses. The Migadu API consistently wraps list responses
# with one of these keys at the top level.
KNOWN_LIST_KEYS = (
    "mailboxes",
    "aliases",
    "address_aliases",  # Migadu's actual response key for list_aliases
    "identities",
    "forwardings",
    "rewrites",
    "domains",
)


def estimate_tokens(data: Any) -> int:
    """Rough heuristic: 1 token ≈ 4 characters."""
    return len(json.dumps(data, ensure_ascii=False)) // 4


def summarize(
    data: dict[str, Any],
    max_tokens: int = DEFAULT_MAX_TOKENS,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
) -> dict[str, Any]:
    """Return data as-is if under the token budget; otherwise return a summary with
    total count and a sample. Non-list dicts that exceed the budget get a generic
    summary with their keys.
    """
    if estimate_tokens(data) <= max_tokens:
        return data

    for key in KNOWN_LIST_KEYS:
        items = data.get(key)
        if isinstance(items, list):
            return _list_summary(data, key, items, sample_size)

    return {
        "response_summary": {
            "truncated": True,
            "estimated_tokens": estimate_tokens(data),
            "max_tokens": max_tokens,
            "keys": list(data.keys()),
            "note": "Response exceeded the token budget. Use a more specific tool to drill down.",
        }
    }


def _list_summary(
    data: dict[str, Any], key: str, items: list[Any], sample_size: int
) -> dict[str, Any]:
    total = len(items)
    sample = items[:sample_size]
    return {
        f"{key}_summary": {
            "truncated": True,
            "total_count": total,
            "returned_sample": len(sample),
            "note": "Response truncated. Use a `get_*` tool or query with a specific identifier for full details.",
        },
        "sample": sample,
    }
