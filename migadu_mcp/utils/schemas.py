"""
Pydantic schemas for Migadu API requests.
Based on official API documentation: https://migadu.com/api/
"""

from __future__ import annotations

from datetime import date
from typing import Any, Literal, Type, Union

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)


SpamAction = Literal["folder", "reject", "none"]
SpamAggressiveness = Literal["default", "low", "normal", "high", "very_high"]
PasswordMethod = Literal["password", "invitation"]


def _split_csv(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def _coerce_destinations(value: Union[list[str], str, None]) -> Union[list[str], None]:
    """Accept list[email] or CSV string; return normalized list. Validation happens via EmailStr."""
    if value is None:
        return None
    if isinstance(value, str):
        return _split_csv(value)
    return list(value)


def destinations_to_csv(destinations: list[str]) -> str:
    return ",".join(destinations)


# ---- Mailbox ----


class MailboxCreateRequest(BaseModel):
    target: str = Field(..., description="Email address or local part")
    name: str = Field(..., description="Display name for the mailbox")
    password: str | None = Field(
        None, description="Password (required if password_method is 'password')"
    )
    password_method: PasswordMethod = Field(
        "password", description="Password setup method"
    )
    password_recovery_email: EmailStr | None = Field(
        None, description="Recovery email for invitation method"
    )
    is_internal: bool = Field(False, description="Restrict to internal-only messages")
    forwarding_to: EmailStr | None = Field(
        None, description="External forwarding address"
    )

    @model_validator(mode="after")
    def _check_password_method(self) -> "MailboxCreateRequest":
        if self.password_method == "invitation" and not self.password_recovery_email:  # nosec B105
            raise ValueError(
                "password_recovery_email is required when password_method is invitation"
            )
        if self.password_method == "password" and not self.password:  # nosec B105
            raise ValueError("password is required when password_method is password")
        return self


class MailboxUpdateRequest(BaseModel):
    target: str = Field(..., description="Email address or local part")
    name: str | None = None
    may_send: bool | None = None
    may_receive: bool | None = None
    may_access_imap: bool | None = None
    may_access_pop3: bool | None = None
    may_access_managesieve: bool | None = None
    spam_action: SpamAction | None = None
    spam_aggressiveness: SpamAggressiveness | None = None
    sender_denylist: str | None = None
    sender_allowlist: str | None = None
    recipient_denylist: str | None = None


class MailboxDeleteRequest(BaseModel):
    target: str = Field(..., description="Email address or local part")


class MailboxPasswordResetRequest(BaseModel):
    target: str = Field(..., description="Email address or local part")
    new_password: str = Field(..., description="New password for authentication")


class AutoresponderRequest(BaseModel):
    target: str = Field(..., description="Email address or local part")
    active: bool
    subject: str | None = None
    body: str | None = None
    expires_on: date | None = Field(None, description="Expiration date YYYY-MM-DD")

    @field_validator("expires_on")
    @classmethod
    def _future_expiry(cls, v: date | None) -> date | None:
        if v is not None and v <= date.today():
            raise ValueError("expires_on must be a future date")
        return v


# ---- Alias ----


class AliasCreateRequest(BaseModel):
    target: str = Field(..., description="Local part of alias")
    destinations: list[EmailStr] = Field(
        ..., description="List of email addresses or CSV string"
    )
    domain: str | None = None
    is_internal: bool = False

    @field_validator("destinations", mode="before")
    @classmethod
    def _coerce(cls, v: Union[list[str], str]) -> list[str]:
        coerced = _coerce_destinations(v)
        if not coerced:
            raise ValueError("destinations must be a non-empty list or CSV string")
        return coerced


class AliasUpdateRequest(BaseModel):
    target: str = Field(..., description="Local part of alias")
    destinations: list[EmailStr]
    domain: str | None = None

    @field_validator("destinations", mode="before")
    @classmethod
    def _coerce(cls, v: Union[list[str], str]) -> list[str]:
        coerced = _coerce_destinations(v)
        if not coerced:
            raise ValueError("destinations must be a non-empty list or CSV string")
        return coerced


class AliasDeleteRequest(BaseModel):
    target: str = Field(..., description="Local part of alias")
    domain: str | None = None


# ---- Identity ----


class IdentityCreateRequest(BaseModel):
    target: str = Field(..., description="Local part of identity address")
    mailbox: str = Field(..., description="Username of mailbox that owns this identity")
    name: str
    password: str
    domain: str | None = None


class IdentityUpdateRequest(BaseModel):
    target: str
    mailbox: str
    domain: str | None = None
    name: str | None = None
    may_send: bool | None = None
    may_receive: bool | None = None
    may_access_imap: bool | None = None
    may_access_pop3: bool | None = None
    may_access_managesieve: bool | None = None
    footer_active: bool | None = None
    footer_plain_body: str | None = None
    footer_html_body: str | None = None


class IdentityDeleteRequest(BaseModel):
    target: str
    mailbox: str
    domain: str | None = None


# ---- Rewrite ----


class RewriteCreateRequest(BaseModel):
    name: str = Field(..., description="Unique identifier/slug for the rule")
    local_part_rule: str = Field(
        ..., description="Pattern to match (e.g., 'demo-*', 'support-*')"
    )
    destinations: list[EmailStr]
    domain: str | None = None
    order_num: int | None = None

    @field_validator("destinations", mode="before")
    @classmethod
    def _coerce(cls, v: Union[list[str], str]) -> list[str]:
        coerced = _coerce_destinations(v)
        if not coerced:
            raise ValueError("destinations must be a non-empty list or CSV string")
        return coerced


class RewriteUpdateRequest(BaseModel):
    name: str
    domain: str | None = None
    new_name: str | None = None
    local_part_rule: str | None = None
    destinations: list[EmailStr] | None = None
    order_num: int | None = None

    @field_validator("destinations", mode="before")
    @classmethod
    def _coerce(cls, v: Union[list[str], str, None]) -> Union[list[str], None]:
        return _coerce_destinations(v)


class RewriteDeleteRequest(BaseModel):
    name: str
    domain: str | None = None


# ---- Forwarding ----


class ForwardingCreateRequest(BaseModel):
    mailbox: str = Field(
        ..., description="Mailbox local part the forwarding belongs to"
    )
    address: EmailStr = Field(..., description="External email address to forward to")
    domain: str | None = None
    expires_on: date | None = None
    remove_upon_expiry: bool | None = None

    @field_validator("expires_on")
    @classmethod
    def _future_expiry(cls, v: date | None) -> date | None:
        if v is not None and v <= date.today():
            raise ValueError("expires_on must be a future date")
        return v


class ForwardingUpdateRequest(BaseModel):
    mailbox: str
    address: EmailStr
    domain: str | None = None
    is_active: bool | None = None
    expires_on: date | None = None
    remove_upon_expiry: bool | None = None

    @field_validator("expires_on")
    @classmethod
    def _future_expiry(cls, v: date | None) -> date | None:
        if v is not None and v <= date.today():
            raise ValueError("expires_on must be a future date")
        return v


class ForwardingDeleteRequest(BaseModel):
    mailbox: str
    address: EmailStr
    domain: str | None = None


# ---- Domain ----


class DomainCreateRequest(BaseModel):
    name: str = Field(..., description="Domain name (e.g., example.com)")
    hosted_dns: bool = Field(
        False,
        description="Use Migadu's hosted DNS. Migadu recommends external DNS; keep False unless you know you need this.",
    )
    create_default_addresses: bool = Field(
        True,
        description="Create default postmaster/abuse/admin addresses on domain creation",
    )


class DomainUpdateRequest(BaseModel):
    name: str = Field(..., description="Domain name")
    description: str | None = None
    tags: str | None = None


class DomainActivateRequest(BaseModel):
    name: str = Field(..., description="Domain name")


# ---- Utility ----


def validate_with_schema(
    data: dict[str, Any], schema_class: Type[BaseModel]
) -> BaseModel:
    """Validate a dict against a Pydantic schema, re-raising clean error messages."""
    try:
        return schema_class(**data)
    except ValidationError as e:
        parts = []
        for err in e.errors():
            loc = ".".join(str(p) for p in err["loc"])
            parts.append(f"{loc}: {err['msg']}")
        raise ValueError(f"Validation failed: {'; '.join(parts)}") from e
