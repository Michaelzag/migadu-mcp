#!/usr/bin/env python3
"""
Advanced context protection utilities with AI-powered guidance
"""

import json
from typing import Dict, Any, List, Optional
from fastmcp import Context


def estimate_token_count(data: Any) -> int:
    """Estimate token count for data (rough approximation: 1 token ≈ 4 characters)"""
    json_str = json.dumps(data, ensure_ascii=False)
    return len(json_str) // 4


async def truncate_response_if_needed(
    data: Dict[str, Any],
    ctx: Optional[Context] = None,
    tool_name: str = "unknown",
    max_tokens: int = 2000,
) -> Dict[str, Any]:
    """
    Advanced context protection with AI-powered guidance messages

    Args:
        data: Response data to check
        ctx: FastMCP Context for sampling and logging
        tool_name: Name of the tool being called for context-aware guidance
        max_tokens: Maximum tokens allowed (default: 2000)

    Returns:
        Original data if under limit, or intelligent summary if over limit
    """
    estimated_tokens = estimate_token_count(data)

    if estimated_tokens <= max_tokens:
        return data

    # Log the truncation for transparency
    if ctx:
        await ctx.info(
            f"🛡️ Response protection: {estimated_tokens} tokens → truncating to prevent context overflow"
        )

    # If it's a list response, convert to intelligent summary
    if isinstance(data, dict):
        for key in ["mailboxes", "aliases", "identities", "forwardings", "rewrites"]:
            if key in data and isinstance(data[key], list):
                return await _create_intelligent_list_summary(data, key, ctx, tool_name)

    # For other large responses, try to extract key summary info
    return await _create_intelligent_generic_summary(
        data, estimated_tokens, max_tokens, ctx, tool_name
    )


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


async def _create_intelligent_list_summary(
    data: Dict[str, Any],
    list_key: str,
    ctx: Optional[Context] = None,
    tool_name: str = "unknown",
) -> Dict[str, Any]:
    """Create AI-powered intelligent summary for list-based responses"""
    items = data[list_key]

    if not items:
        return data

    # Get basic summary data
    basic_summary = _get_basic_list_summary(items, list_key)

    # Generate intelligent guidance message using AI sampling
    intelligent_guidance = await _generate_intelligent_guidance(
        items, list_key, tool_name, ctx
    )

    summary = {
        f"{list_key}_summary": {
            "total_count": len(items),
            "estimated_tokens": estimate_token_count(data),
            "truncated": True,
            "intelligent_guidance": intelligent_guidance,
            **basic_summary,
        }
    }

    # Include sample items for reference
    if len(items) > 0:
        summary["sample_items"] = items[:3]  # Show first 3 as examples
        if len(items) > 3:
            summary[f"{list_key}_summary"]["remaining_count"] = len(items) - 3

    return summary


async def _create_intelligent_generic_summary(
    data: Dict[str, Any],
    estimated_tokens: int,
    max_tokens: int,
    ctx: Optional[Context] = None,
    tool_name: str = "unknown",
) -> Dict[str, Any]:
    """Create intelligent summary for non-list responses"""

    # Generate context-aware guidance
    if ctx:
        prompt = f"""
        A {tool_name} API call returned {estimated_tokens} tokens (over {max_tokens} limit).
        Data keys: {list(data.keys()) if isinstance(data, dict) else ["non_dict_response"]}
        
        Generate a helpful, professional message explaining:
        1. What was returned and why it's truncated
        2. Specific guidance on how to get the information they need
        3. Keep it actionable and user-friendly (not technical)
        """

        try:
            smart_message = await ctx.sample(prompt, model_preferences="claude-3-haiku")
            guidance = _extract_text_from_sampling_response(smart_message)
        except Exception:
            guidance = "Response was too large and has been summarized. Use more specific queries to get detailed information."
    else:
        guidance = "Response was too large and has been summarized. Use more specific queries to get detailed information."

    return {
        "response_summary": {
            "estimated_tokens": estimated_tokens,
            "max_allowed": max_tokens,
            "truncated": True,
            "intelligent_guidance": guidance,
            "data_keys": list(data.keys())
            if isinstance(data, dict)
            else ["non_dict_response"],
        }
    }


async def _generate_intelligent_guidance(
    items: List[Dict[str, Any]],
    list_key: str,
    tool_name: str,
    ctx: Optional[Context] = None,
) -> str:
    """Generate AI-powered, context-aware guidance messages"""

    if not ctx:
        return _get_fallback_guidance(list_key, len(items))

    # Extract sample data for context
    sample_addresses = []
    for item in items[:3]:
        if "address" in item:
            sample_addresses.append(item["address"])
        elif "local_part" in item and "domain_name" in item:
            sample_addresses.append(f"{item['local_part']}@{item['domain_name']}")

    # Create smart prompt based on the tool and data
    prompt = f"""
    User called {tool_name} and got {len(items)} {list_key} back (too many for context).
    Sample addresses: {sample_addresses[:3]}
    
    Generate a helpful, professional response that:
    1. Explains what was found ({len(items)} {list_key})
    2. Shows specific examples of how to get details using REAL addresses from the data
    3. Uses the correct function names (get_my_mailbox, get_mailbox, get_alias, etc.)
    4. Keep it concise, actionable, and friendly
    
    Example format: "Found 87 mailboxes. For complete details, use: get_my_mailbox('admin') or get_my_mailbox('michael')"
    """

    try:
        smart_message = await ctx.sample(prompt, model_preferences="claude-3-haiku")
        return _extract_text_from_sampling_response(smart_message)
    except Exception:
        return _get_fallback_guidance(list_key, len(items))


def _get_fallback_guidance(list_key: str, count: int) -> str:
    """Fallback guidance when AI sampling is not available"""
    if list_key == "mailboxes":
        return f"Found {count} mailboxes. Use get_my_mailbox('username') for complete mailbox details."
    elif list_key == "aliases":
        return f"Found {count} aliases. Use get_alias('aliasname') for complete forwarding rules."
    elif list_key == "identities":
        return f"Found {count} identities. Use get_identity('identityname') for complete permissions."
    elif list_key == "forwardings":
        return f"Found {count} forwardings. Use get_forwarding() for complete status details."
    elif list_key == "rewrites":
        return f"Found {count} rewrite rules. Use get_rewrite() for complete pattern details."
    else:
        return f"Found {count} {list_key}. Use specific get_ commands for detailed information."


def _extract_text_from_sampling_response(response) -> str:
    """Safely extract text from FastMCP sampling response"""
    try:
        # Try different response formats
        if hasattr(response, "text"):
            return str(response.text).strip()
        elif hasattr(response, "content") and response.content:
            # If it's a list of content objects
            if isinstance(response.content, list) and len(response.content) > 0:
                first_content = response.content[0]
                if hasattr(first_content, "text"):
                    return str(first_content.text).strip()
        # Fallback to string conversion
        return str(response).strip()
    except Exception:
        return "Response summarized due to size limitations."


def _get_basic_list_summary(
    items: List[Dict[str, Any]], list_key: str
) -> Dict[str, Any]:
    """Get basic statistical summary for different item types"""
    if list_key == "mailboxes":
        return _summarize_mailboxes(items)
    elif list_key == "aliases":
        return _summarize_aliases(items)
    elif list_key == "identities":
        return _summarize_identities(items)
    elif list_key == "forwardings":
        return _summarize_forwardings(items)
    elif list_key == "rewrites":
        return _summarize_rewrites(items)
    else:
        return {"total_items": len(items)}
