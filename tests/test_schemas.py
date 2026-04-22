"""Pydantic schema validation tests — focus on rejection cases."""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from migadu_mcp.utils.schemas import (
    AliasCreateRequest,
    AutoresponderRequest,
    DomainCreateRequest,
    ForwardingCreateRequest,
    MailboxCreateRequest,
    RewriteCreateRequest,
    validate_with_schema,
)


def test_mailbox_password_required_when_method_is_password() -> None:
    with pytest.raises(ValidationError):
        MailboxCreateRequest(
            target="alice@x.com", name="Alice", password_method="password"
        )


def test_mailbox_invitation_requires_recovery_email() -> None:
    with pytest.raises(ValidationError):
        MailboxCreateRequest(
            target="alice@x.com", name="Alice", password_method="invitation"
        )


def test_mailbox_invitation_accepts_recovery_email() -> None:
    MailboxCreateRequest(
        target="alice@x.com",
        name="Alice",
        password_method="invitation",
        password_recovery_email="recovery@x.com",
    )


def test_autoresponder_rejects_past_expiry() -> None:
    yesterday = date.today() - timedelta(days=1)
    with pytest.raises(ValidationError):
        AutoresponderRequest(target="alice", active=True, expires_on=yesterday)


def test_autoresponder_accepts_future_expiry() -> None:
    future = date.today() + timedelta(days=7)
    AutoresponderRequest(target="alice", active=True, expires_on=future)


def test_alias_destinations_list_form() -> None:
    req = AliasCreateRequest(target="info", destinations=["a@x.com", "b@x.com"])
    assert req.destinations == ["a@x.com", "b@x.com"]


def test_alias_destinations_csv_form() -> None:
    req = AliasCreateRequest(target="info", destinations="a@x.com, b@x.com")
    assert req.destinations == ["a@x.com", "b@x.com"]


def test_alias_rejects_empty_destinations() -> None:
    with pytest.raises(ValidationError):
        AliasCreateRequest(target="info", destinations=[])


def test_alias_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        AliasCreateRequest(target="info", destinations=["not-an-email"])


def test_rewrite_destinations_csv_form() -> None:
    req = RewriteCreateRequest(
        name="demo", local_part_rule="demo-*", destinations="a@x.com,b@x.com"
    )
    assert req.destinations == ["a@x.com", "b@x.com"]


def test_forwarding_rejects_invalid_address() -> None:
    with pytest.raises(ValidationError):
        ForwardingCreateRequest(mailbox="alice", address="not-an-email")


def test_forwarding_rejects_past_expiry() -> None:
    yesterday = date.today() - timedelta(days=1)
    with pytest.raises(ValidationError):
        ForwardingCreateRequest(
            mailbox="alice", address="bob@elsewhere.com", expires_on=yesterday
        )


def test_domain_create_defaults_to_external_dns() -> None:
    req = DomainCreateRequest(name="new.example")
    assert req.hosted_dns is False
    assert req.create_default_addresses is True


def test_validate_with_schema_formats_errors() -> None:
    with pytest.raises(ValueError) as exc:
        validate_with_schema({"target": "alice"}, MailboxCreateRequest)
    assert "Validation failed" in str(exc.value)
    # Missing required fields (name, password) should be mentioned
    assert "name" in str(exc.value)
