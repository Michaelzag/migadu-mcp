#!/usr/bin/env python3
"""
Pydantic schemas for Migadu API requests and responses
Based on official API documentation: https://migadu.com/api/
"""

from typing import List, Optional, Union, Dict, Any, Type
from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from enum import Enum
import re


class PasswordMethod(str, Enum):
    """Password method options for mailbox creation"""
    PASSWORD = "password"
    INVITATION = "invitation"


class SpamAction(str, Enum):
    """Spam action options"""
    FOLDER = "folder"
    REJECT = "reject"
    # Add other spam actions as documented


class SpamAggressiveness(str, Enum):
    """Spam aggressiveness levels"""
    DEFAULT = "default"
    # Add other levels as documented


# Email validation function
def validate_email(email: str) -> str:
    """Simple email validation"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email.strip()):
        raise ValueError(f"Invalid email format: {email}")
    return email.strip()


# Utility functions for destinations handling
def normalize_destinations(destinations: Union[List[str], str]) -> List[str]:
    """Convert destinations from CSV string or list to list of validated emails"""
    if isinstance(destinations, str):
        # Split CSV string and strip whitespace
        emails = [dest.strip() for dest in destinations.split(',') if dest.strip()]
        return [validate_email(email) for email in emails]
    return [validate_email(dest) for dest in destinations]


def destinations_to_csv(destinations: List[str]) -> str:
    """Convert list of destinations to CSV string for API"""
    return ','.join(destinations)


# Mailbox Schemas
class MailboxCreateRequest(BaseModel):
    """Request schema for creating a mailbox"""
    target: str = Field(..., description="Email address or local part")
    name: str = Field(..., description="Display name for the mailbox")
    password: Optional[str] = Field(None, description="Password (required if password_method is 'password')")
    password_method: PasswordMethod = Field(PasswordMethod.PASSWORD, description="Password setup method")
    password_recovery_email: Optional[EmailStr] = Field(None, description="Recovery email for invitation method")
    is_internal: bool = Field(False, description="Restrict to internal-only messages")
    forwarding_to: Optional[EmailStr] = Field(None, description="External forwarding address")
    
    @model_validator(mode='after')
    def validate_password_method(self):
        if self.password_method == PasswordMethod.INVITATION:
            if not self.password_recovery_email:
                raise ValueError('password_recovery_email is required when password_method is invitation')
        elif self.password_method == PasswordMethod.PASSWORD:
            if not self.password:
                raise ValueError('password is required when password_method is password')
        
        return self


class MailboxUpdateRequest(BaseModel):
    """Request schema for updating a mailbox"""
    target: str = Field(..., description="Email address or local part")
    name: Optional[str] = Field(None, description="Update display name")
    may_send: Optional[bool] = Field(None, description="Allow/deny sending emails")
    may_receive: Optional[bool] = Field(None, description="Allow/deny receiving emails")
    may_access_imap: Optional[bool] = Field(None, description="Allow/deny IMAP access")
    may_access_pop3: Optional[bool] = Field(None, description="Allow/deny POP3 access")
    may_access_managesieve: Optional[bool] = Field(None, description="Allow/deny ManageSieve access")
    spam_action: Optional[SpamAction] = Field(None, description="Spam handling action")
    spam_aggressiveness: Optional[SpamAggressiveness] = Field(None, description="Spam filtering sensitivity")
    sender_denylist: Optional[str] = Field(None, description="Sender denylist rules")
    sender_allowlist: Optional[str] = Field(None, description="Sender allowlist rules")
    recipient_denylist: Optional[str] = Field(None, description="Recipient denylist rules")


class MailboxDeleteRequest(BaseModel):
    """Request schema for deleting a mailbox"""
    target: str = Field(..., description="Email address or local part")


class MailboxPasswordResetRequest(BaseModel):
    """Request schema for resetting mailbox password"""
    target: str = Field(..., description="Email address or local part")
    new_password: str = Field(..., description="New password for authentication")


class AutoresponderRequest(BaseModel):
    """Request schema for setting autoresponder"""
    target: str = Field(..., description="Email address or local part")
    active: bool = Field(..., description="Whether autoresponder is enabled")
    subject: Optional[str] = Field(None, description="Subject line for replies")
    body: Optional[str] = Field(None, description="Message content for replies")
    expires_on: Optional[date] = Field(None, description="Expiration date YYYY-MM-DD")
    
    @field_validator('expires_on')
    @classmethod
    def validate_expires_on(cls, v: Optional[date]) -> Optional[date]:
        if v and v <= date.today():
            raise ValueError('expires_on must be a future date')
        return v


# Alias Schemas
class AliasCreateRequest(BaseModel):
    """Request schema for creating an alias"""
    target: str = Field(..., description="Local part of alias")
    destinations: Union[List[EmailStr], str] = Field(..., description="List of email addresses or CSV string")
    domain: Optional[str] = Field(None, description="Domain name")
    is_internal: bool = Field(False, description="Internal-only flag")
    
    @field_validator('destinations', mode='before')
    @classmethod
    def normalize_destinations(cls, v: Union[List[str], str]) -> List[str]:
        return normalize_destinations(v)


class AliasUpdateRequest(BaseModel):
    """Request schema for updating an alias"""
    target: str = Field(..., description="Local part of alias")
    destinations: Union[List[EmailStr], str] = Field(..., description="New list of email addresses or CSV string")
    domain: Optional[str] = Field(None, description="Domain name")
    
    @field_validator('destinations', mode='before')
    @classmethod
    def normalize_destinations(cls, v: Union[List[str], str]) -> List[str]:
        return normalize_destinations(v)


class AliasDeleteRequest(BaseModel):
    """Request schema for deleting an alias"""
    target: str = Field(..., description="Local part of alias")
    domain: Optional[str] = Field(None, description="Domain name")


# Identity Schemas
class IdentityCreateRequest(BaseModel):
    """Request schema for creating an identity"""
    target: str = Field(..., description="Local part of identity address")
    mailbox: str = Field(..., description="Username of mailbox that owns this identity")
    name: str = Field(..., description="Display name for identity")
    password: str = Field(..., description="Password for SMTP authentication")
    domain: Optional[str] = Field(None, description="Domain name")


class IdentityUpdateRequest(BaseModel):
    """Request schema for updating an identity"""
    target: str = Field(..., description="Local part of identity address")
    mailbox: str = Field(..., description="Username of mailbox that owns this identity")
    domain: Optional[str] = Field(None, description="Domain name")
    name: Optional[str] = Field(None, description="Update display name")
    may_send: Optional[bool] = Field(None, description="Allow/deny sending from identity")
    may_receive: Optional[bool] = Field(None, description="Allow/deny receiving to identity")
    may_access_imap: Optional[bool] = Field(None, description="Allow/deny IMAP access")
    may_access_pop3: Optional[bool] = Field(None, description="Allow/deny POP3 access")
    may_access_managesieve: Optional[bool] = Field(None, description="Allow/deny ManageSieve access")
    footer_active: Optional[bool] = Field(None, description="Enable/disable footer")
    footer_plain_body: Optional[str] = Field(None, description="Plain text footer content")
    footer_html_body: Optional[str] = Field(None, description="HTML footer content")


class IdentityDeleteRequest(BaseModel):
    """Request schema for deleting an identity"""
    target: str = Field(..., description="Local part of identity address")
    mailbox: str = Field(..., description="Username of mailbox that owns this identity")
    domain: Optional[str] = Field(None, description="Domain name")


# Rewrite Schemas
class RewriteCreateRequest(BaseModel):
    """Request schema for creating a rewrite rule"""
    name: str = Field(..., description="Unique identifier/slug for the rule")
    local_part_rule: str = Field(..., description="Pattern to match (e.g., 'demo-*', 'support-*')")
    destinations: Union[List[EmailStr], str] = Field(..., description="List of email addresses or CSV string")
    domain: Optional[str] = Field(None, description="Domain name")
    order_num: Optional[int] = Field(None, description="Processing order (lower numbers processed first)")
    
    @field_validator('destinations', mode='before')
    @classmethod
    def normalize_destinations(cls, v: Union[List[str], str]) -> List[str]:
        return normalize_destinations(v)


class RewriteUpdateRequest(BaseModel):
    """Request schema for updating a rewrite rule"""
    name: str = Field(..., description="Current identifier/slug of the rule")
    domain: Optional[str] = Field(None, description="Domain name")
    new_name: Optional[str] = Field(None, description="New identifier/slug")
    local_part_rule: Optional[str] = Field(None, description="New pattern to match")
    destinations: Optional[Union[List[EmailStr], str]] = Field(None, description="New list of destinations or CSV string")
    order_num: Optional[int] = Field(None, description="New processing order")
    
    @field_validator('destinations', mode='before')
    @classmethod
    def normalize_destinations(cls, v: Optional[Union[List[str], str]]) -> Optional[List[str]]:
        if v is not None:
            return normalize_destinations(v)
        return v


class RewriteDeleteRequest(BaseModel):
    """Request schema for deleting a rewrite rule"""
    name: str = Field(..., description="Identifier/slug of the rule to delete")
    domain: Optional[str] = Field(None, description="Domain name")


# Forwarding Schemas (additional API endpoint)
class ForwardingCreateRequest(BaseModel):
    """Request schema for creating a forwarding"""
    address: EmailStr = Field(..., description="External email address to forward to")
    expires_on: Optional[date] = Field(None, description="Expiration date")
    remove_upon_expiry: Optional[bool] = Field(None, description="Remove forwarding when expired")
    
    @field_validator('expires_on')
    @classmethod
    def validate_expires_on(cls, v: Optional[date]) -> Optional[date]:
        if v and v <= date.today():
            raise ValueError('expires_on must be a future date')
        return v


class ForwardingUpdateRequest(BaseModel):
    """Request schema for updating a forwarding"""
    address: EmailStr = Field(..., description="External email address")
    is_active: Optional[bool] = Field(None, description="Enable/disable forwarding")
    expires_on: Optional[date] = Field(None, description="New expiration date")
    remove_upon_expiry: Optional[bool] = Field(None, description="Remove forwarding when expired")
    
    @field_validator('expires_on')
    @classmethod
    def validate_expires_on(cls, v: Optional[date]) -> Optional[date]:
        if v and v <= date.today():
            raise ValueError('expires_on must be a future date')
        return v


class ForwardingDeleteRequest(BaseModel):
    """Request schema for deleting a forwarding"""
    address: EmailStr = Field(..., description="External email address to remove")


# Response Schemas (for validation of API responses)
class MailboxResponse(BaseModel):
    """Response schema for mailbox operations"""
    address: str
    local_part: str
    domain_name: str
    name: str
    is_internal: bool
    may_send: bool
    may_receive: bool
    may_access_imap: bool
    may_access_pop3: bool
    may_access_managesieve: bool
    password_recovery_email: Optional[EmailStr]
    spam_action: str
    spam_aggressiveness: str
    sender_denylist: List[str] = Field(default_factory=list)
    sender_allowlist: List[str] = Field(default_factory=list)
    recipient_denylist: List[str] = Field(default_factory=list)
    autorespond_active: Optional[bool]
    autorespond_subject: Optional[str]
    autorespond_body: Optional[str]
    autorespond_expires_on: Optional[date]
    footer_active: bool
    footer_plain_body: Optional[str]
    footer_html_body: Optional[str]
    delegations: List[Dict[str, Any]] = Field(default_factory=list)
    identities: List[Dict[str, Any]] = Field(default_factory=list)


class AliasResponse(BaseModel):
    """Response schema for alias operations"""
    address: str
    local_part: str
    domain_name: str
    is_internal: bool
    destinations: List[EmailStr]


class IdentityResponse(BaseModel):
    """Response schema for identity operations"""
    address: str
    local_part: str
    domain_name: str
    name: str
    may_send: bool
    may_receive: bool
    may_access_imap: bool
    may_access_pop3: bool
    may_access_managesieve: bool
    footer_active: bool
    footer_plain_body: Optional[str]
    footer_html_body: Optional[str]


class RewriteResponse(BaseModel):
    """Response schema for rewrite operations"""
    name: str
    domain_name: str
    local_part_rule: str
    destinations: List[EmailStr]
    order_num: Optional[int]


class ForwardingResponse(BaseModel):
    """Response schema for forwarding operations"""
    address: EmailStr
    blocked_at: Optional[datetime]
    confirmation_sent_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    expires_on: Optional[date]
    is_active: bool
    remove_upon_expiry: Optional[bool]


# Utility functions for schema validation
def validate_schema(data: Dict[str, Any], schema_class: Type[BaseModel]) -> BaseModel:
    """Validate dictionary data against a Pydantic schema"""
    try:
        return schema_class(**data)
    except Exception as e:
        raise ValueError(f"Schema validation failed for {schema_class.__name__}: {e}")


def schema_to_api_dict(schema_instance: BaseModel, exclude_none: bool = True) -> Dict[str, Any]:
    """Convert Pydantic schema instance to dictionary for API calls"""
    data = schema_instance.model_dump(exclude_none=exclude_none)
    
    # Convert destinations list to CSV string for API compatibility
    if 'destinations' in data and isinstance(data['destinations'], list):
        data['destinations'] = destinations_to_csv(data['destinations'])
    
    return data