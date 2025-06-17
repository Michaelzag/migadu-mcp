"""
Email address and domain parsing utilities for smart MCP tool handling
"""

import re
from typing import Union, List, Tuple
from migadu_mcp.config import get_config


def parse_email_target(target: Union[str, List[str]]) -> List[Tuple[str, str]]:
    """Parse email target(s) into (domain, local_part) tuples with smart domain resolution.
    
    Args:
        target: Single email/local_part or list of emails/local_parts
        
    Returns:
        List of (domain, local_part) tuples
        
    Raises:
        ValueError: If domain cannot be determined
        
    Examples:
        parse_email_target("april") -> [("default-domain.com", "april")]
        parse_email_target("april@company.com") -> [("company.com", "april")]
        parse_email_target(["april", "bob@other.com"]) -> [("default-domain.com", "april"), ("other.com", "bob")]
    """
    if isinstance(target, str):
        targets = [target]
    else:
        targets = target
    
    result = []
    default_domain = None
    
    for item in targets:
        if "@" in item:
            # Full email address provided
            local_part, domain = item.split("@", 1)
            result.append((domain, local_part))
        else:
            # Local part only - need default domain
            if default_domain is None:
                config = get_config()
                default_domain = config.get_default_domain()
                if not default_domain:
                    raise ValueError(
                        f"No domain specified for '{item}' and MIGADU_DOMAIN not configured. "
                        "Either provide full email addresses (user@domain.com) or set MIGADU_DOMAIN environment variable."
                    )
            result.append((default_domain, item))
    
    return result


def format_email_address(domain: str, local_part: str) -> str:
    """Format domain and local_part into full email address"""
    return f"{local_part}@{domain}"


def validate_email_format(email: str) -> bool:
    """Basic email format validation"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))


def extract_domains(targets: List[Tuple[str, str]]) -> List[str]:
    """Extract unique domains from parsed targets"""
    return list(set(domain for domain, _ in targets))


def group_by_domain(targets: List[Tuple[str, str]]) -> dict[str, List[str]]:
    """Group targets by domain for batch operations"""
    grouped: dict[str, List[str]] = {}
    for domain, local_part in targets:
        if domain not in grouped:
            grouped[domain] = []
        grouped[domain].append(local_part)
    return grouped