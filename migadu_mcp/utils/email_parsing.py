"""Email parsing helpers."""

from __future__ import annotations

from migadu_mcp.config import get_config


def parse_email_target(target: str) -> list[tuple[str, str]]:
    """Parse an email target into (domain, local_part) tuples.

    Accepts "local" or "local@domain". Bare local parts are resolved against
    MIGADU_DOMAIN. Returns a list for compatibility with callers that always
    index [0]; a future cleanup can flatten this.
    """
    item = target.strip()
    if "@" in item:
        local_part, domain = item.split("@", 1)
        return [(domain, local_part)]
    default = get_config().default_domain
    if not default:
        raise ValueError(
            f"No domain in '{item}' and MIGADU_DOMAIN is not set. "
            "Provide a full email (user@domain) or configure MIGADU_DOMAIN."
        )
    return [(default, item)]


def format_email_address(domain: str, local_part: str) -> str:
    return f"{local_part}@{domain}"
