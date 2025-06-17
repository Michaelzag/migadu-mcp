#!/usr/bin/env python3
"""
Object specifications for consolidated MCP operations
"""

from typing import Optional, List, Literal, Union
from dataclasses import dataclass


# Operation types for each entity
MailboxOperation = Literal[
    "create", "update", "delete", "reset_password", "set_autoresponder"
]
AliasOperation = Literal["create", "update", "delete"]
IdentityOperation = Literal["create", "update", "delete"]
RewriteOperation = Literal["create", "update", "delete"]
ForwardingOperation = Literal["create", "update", "delete"]


@dataclass
class MailboxCreateSpec:
    """Create a new mailbox"""

    target: str  # Email address or local part
    name: str  # Display name
    operation: Literal["create"] = "create"
    password: Optional[str] = None  # None for invitation method
    password_recovery_email: Optional[str] = None
    is_internal: bool = False
    forwarding_to: Optional[str] = None


@dataclass
class MailboxUpdateSpec:
    """Update mailbox settings"""

    target: str
    operation: Literal["update"] = "update"
    name: Optional[str] = None
    may_send: Optional[bool] = None
    may_receive: Optional[bool] = None
    may_access_imap: Optional[bool] = None
    may_access_pop3: Optional[bool] = None
    spam_action: Optional[str] = None
    spam_aggressiveness: Optional[str] = None


@dataclass
class MailboxDeleteSpec:
    """Delete a mailbox"""

    target: str
    operation: Literal["delete"] = "delete"


@dataclass
class MailboxPasswordResetSpec:
    """Reset mailbox password"""

    target: str
    new_password: str
    operation: Literal["reset_password"] = "reset_password"


@dataclass
class MailboxAutoresponderSpec:
    """Configure mailbox autoresponder"""

    target: str
    active: bool
    operation: Literal["set_autoresponder"] = "set_autoresponder"
    subject: Optional[str] = None
    body: Optional[str] = None
    expires_on: Optional[str] = None


@dataclass
class AliasCreateSpec:
    """Create a new alias"""

    target: str  # Local part
    destinations: List[str]
    operation: Literal["create"] = "create"
    domain: Optional[str] = None
    is_internal: bool = False


@dataclass
class AliasUpdateSpec:
    """Update alias destinations"""

    target: str
    destinations: List[str]
    operation: Literal["update"] = "update"
    domain: Optional[str] = None


@dataclass
class AliasDeleteSpec:
    """Delete an alias"""

    target: str
    operation: Literal["delete"] = "delete"
    domain: Optional[str] = None


@dataclass
class IdentityCreateSpec:
    """Create a new identity"""

    target: str  # Local part of identity
    mailbox: str  # Owner mailbox
    name: str
    password: str
    operation: Literal["create"] = "create"
    domain: Optional[str] = None


@dataclass
class IdentityUpdateSpec:
    """Update identity settings"""

    target: str
    mailbox: str
    operation: Literal["update"] = "update"
    domain: Optional[str] = None
    name: Optional[str] = None
    may_send: Optional[bool] = None
    may_receive: Optional[bool] = None


@dataclass
class IdentityDeleteSpec:
    """Delete an identity"""

    target: str
    mailbox: str
    operation: Literal["delete"] = "delete"
    domain: Optional[str] = None


@dataclass
class RewriteCreateSpec:
    """Create a new rewrite rule"""

    name: str  # Rule identifier
    local_part_rule: str  # Pattern (e.g., 'demo-*')
    destinations: List[str]
    operation: Literal["create"] = "create"
    domain: Optional[str] = None


@dataclass
class RewriteUpdateSpec:
    """Update rewrite rule"""

    name: str
    operation: Literal["update"] = "update"
    domain: Optional[str] = None
    new_name: Optional[str] = None
    local_part_rule: Optional[str] = None
    destinations: Optional[List[str]] = None


@dataclass
class RewriteDeleteSpec:
    """Delete a rewrite rule"""

    name: str
    operation: Literal["delete"] = "delete"
    domain: Optional[str] = None


@dataclass
class ForwardingCreateSpec:
    """Create external forwarding"""

    mailbox: str
    address: str  # External email
    operation: Literal["create"] = "create"
    domain: Optional[str] = None


@dataclass
class ForwardingUpdateSpec:
    """Update forwarding settings"""

    mailbox: str
    address: str
    operation: Literal["update"] = "update"
    domain: Optional[str] = None
    is_active: Optional[bool] = None
    expires_on: Optional[str] = None
    remove_upon_expiry: Optional[bool] = None


@dataclass
class ForwardingDeleteSpec:
    """Delete forwarding rule"""

    mailbox: str
    address: str
    operation: Literal["delete"] = "delete"
    domain: Optional[str] = None


# Union types for each manage_ tool
MailboxSpec = Union[
    MailboxCreateSpec,
    MailboxUpdateSpec,
    MailboxDeleteSpec,
    MailboxPasswordResetSpec,
    MailboxAutoresponderSpec,
]

AliasSpec = Union[AliasCreateSpec, AliasUpdateSpec, AliasDeleteSpec]

IdentitySpec = Union[IdentityCreateSpec, IdentityUpdateSpec, IdentityDeleteSpec]

RewriteSpec = Union[RewriteCreateSpec, RewriteUpdateSpec, RewriteDeleteSpec]

ForwardingSpec = Union[ForwardingCreateSpec, ForwardingUpdateSpec, ForwardingDeleteSpec]

# List or single item for each manage_ tool
MailboxSpecs = Union[MailboxSpec, List[MailboxSpec]]
AliasSpecs = Union[AliasSpec, List[AliasSpec]]
IdentitySpecs = Union[IdentitySpec, List[IdentitySpec]]
RewriteSpecs = Union[RewriteSpec, List[RewriteSpec]]
ForwardingSpecs = Union[ForwardingSpec, List[ForwardingSpec]]
