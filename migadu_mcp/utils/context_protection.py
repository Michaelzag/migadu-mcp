#!/usr/bin/env python3
"""
Context protection utilities to prevent AI context explosion
"""

import json
from typing import Dict, Any, List


def estimate_token_count(data: Any) -> int:
    """Estimate token count for data (rough approximation: 1 token ≈ 4 characters)"""
    json_str = json.dumps(data, ensure_ascii=False)
    return len(json_str) // 4


def truncate_response_if_needed(
    data: Dict[str, Any], max_tokens: int = 2000
) -> Dict[str, Any]:
    """
    Truncate response if it would exceed max_tokens, converting to summary format

    Args:
        data: Response data to check
        max_tokens: Maximum tokens allowed (default: 2000)

    Returns:
        Original data if under limit, or truncated summary if over limit
    """
    estimated_tokens = estimate_token_count(data)

    if estimated_tokens <= max_tokens:
        return data

    # If it's a list response, convert to summary
    if isinstance(data, dict):
        for key in ["mailboxes", "aliases", "identities", "forwardings", "rewrites"]:
            if key in data and isinstance(data[key], list):
                return _create_list_summary(data, key)

    # For other large responses, try to extract key summary info
    return _create_generic_summary(data, estimated_tokens, max_tokens)


def _create_list_summary(data: Dict[str, Any], list_key: str) -> Dict[str, Any]:
    """Create summary for list-based responses"""
    items = data[list_key]

    if not items:
        return data

    summary = {
        f"{list_key}_summary": {
            "total_count": len(items),
            "estimated_tokens": estimate_token_count(data),
            "truncated": True,
            "message": "Response truncated to prevent context explosion. Use specific get_ commands for details.",
        }
    }

    # Add type-specific summaries
    if list_key == "mailboxes":
        summary[f"{list_key}_summary"].update(_summarize_mailboxes(items))
    elif list_key == "aliases":
        summary[f"{list_key}_summary"].update(_summarize_aliases(items))
    elif list_key == "identities":
        summary[f"{list_key}_summary"].update(_summarize_identities(items))
    elif list_key == "forwardings":
        summary[f"{list_key}_summary"].update(_summarize_forwardings(items))
    elif list_key == "rewrites":
        summary[f"{list_key}_summary"].update(_summarize_rewrites(items))

    # Include first few items as examples
    if len(items) > 0:
        summary["sample_items"] = items[:3]  # Show first 3 as examples
        if len(items) > 3:
            summary[f"{list_key}_summary"]["remaining_count"] = len(items) - 3

    return summary


def _summarize_mailboxes(mailboxes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create mailbox-specific summary"""
    addresses = [mb.get("address", "unknown") for mb in mailboxes]
    internal_count = sum(1 for mb in mailboxes if mb.get("is_internal", False))
    active_count = sum(
        1
        for mb in mailboxes
        if mb.get("may_receive", True) and mb.get("may_send", True)
    )

    # Storage usage stats
    storage_usage = [mb.get("storage_usage", 0) for mb in mailboxes]
    total_storage = sum(storage_usage)

    return {
        "breakdown": {
            "total_mailboxes": len(mailboxes),
            "internal_only": internal_count,
            "external_accessible": len(mailboxes) - internal_count,
            "fully_active": active_count,
            "total_storage_mb": round(total_storage, 2),
        },
        "addresses": sorted(addresses),
        "suggestion": "Use get_mailbox(domain, local_part) or get_my_mailbox(local_part) for detailed info",
    }


def _summarize_aliases(aliases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create alias-specific summary"""
    addresses = [alias.get("address", "unknown") for alias in aliases]
    internal_count = sum(1 for alias in aliases if alias.get("is_internal", False))

    # Count destinations
    dest_counts = []
    for alias in aliases:
        destinations = alias.get("destinations", [])
        if isinstance(destinations, list):
            dest_counts.append(len(destinations))

    return {
        "breakdown": {
            "total_aliases": len(aliases),
            "internal_only": internal_count,
            "external_accessible": len(aliases) - internal_count,
            "avg_destinations": round(
                sum(dest_counts) / len(dest_counts) if dest_counts else 0, 1
            ),
        },
        "addresses": sorted(addresses),
        "suggestion": "Use get_alias(domain, local_part) for detailed destination info",
    }


def _summarize_identities(identities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create identity-specific summary"""
    addresses = [identity.get("address", "unknown") for identity in identities]
    send_enabled = sum(1 for identity in identities if identity.get("may_send", True))
    receive_enabled = sum(
        1 for identity in identities if identity.get("may_receive", True)
    )

    return {
        "breakdown": {
            "total_identities": len(identities),
            "can_send": send_enabled,
            "can_receive": receive_enabled,
        },
        "addresses": sorted(addresses),
        "suggestion": "Use get_identity(domain, mailbox, identity) for detailed info",
    }


def _summarize_forwardings(forwardings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create forwarding-specific summary"""
    destinations = [fwd.get("address", "unknown") for fwd in forwardings]
    active_count = sum(1 for fwd in forwardings if fwd.get("is_active", True))
    confirmed_count = sum(1 for fwd in forwardings if fwd.get("is_confirmed", False))

    return {
        "breakdown": {
            "total_forwardings": len(forwardings),
            "active": active_count,
            "confirmed": confirmed_count,
            "pending_confirmation": len(forwardings) - confirmed_count,
        },
        "destinations": sorted(destinations),
        "suggestion": "Use get_forwarding(domain, mailbox, address) for detailed status",
    }


def _summarize_rewrites(rewrites: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create rewrite-specific summary"""
    patterns = [rewrite.get("local_part_rule", "unknown") for rewrite in rewrites]
    names = [rewrite.get("name", "unknown") for rewrite in rewrites]

    return {
        "breakdown": {
            "total_rewrites": len(rewrites),
            "rule_names": sorted(names),
        },
        "patterns": sorted(patterns),
        "suggestion": "Use get_rewrite(domain, name) for detailed pattern and destination info",
    }


def _create_generic_summary(
    data: Dict[str, Any], estimated_tokens: int, max_tokens: int
) -> Dict[str, Any]:
    """Create generic summary for non-list responses"""
    return {
        "response_summary": {
            "estimated_tokens": estimated_tokens,
            "max_allowed": max_tokens,
            "truncated": True,
            "message": "Response was too large and has been truncated to prevent context explosion.",
            "data_keys": list(data.keys())
            if isinstance(data, dict)
            else ["non_dict_response"],
            "suggestion": "Use more specific queries to get targeted information",
        }
    }
