"""Auth models — SQLAlchemy ORM models for users, orgs, API keys, and sessions.

Implements multi-tenancy with organization-scoped data access.
"""

from __future__ import annotations

import enum
from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""


class Role(enum.StrEnum):
    """User roles for RBAC."""

    ADMIN = "admin"
    ENGINEER = "engineer"
    VIEWER = "viewer"
    AUDITOR = "auditor"


class Organization(Base):
    """Multi-tenant organization."""

    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    devin_api_key_encrypted = Column(Text, nullable=True)
    settings_json = Column(Text, nullable=True, default="{}")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    users = relationship("User", back_populates="organization")
    api_keys = relationship("APIKey", back_populates="organization")


class User(Base):
    """Application user."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.ENGINEER)
    is_active = Column(Boolean, default=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    last_login = Column(DateTime(timezone=True), nullable=True)

    organization = relationship("Organization", back_populates="users")


class APIKey(Base):
    """API key for programmatic access."""

    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True)
    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    scopes = Column(Text, nullable=True, default="*")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    organization = relationship("Organization", back_populates="api_keys")


class AuthSession(Base):
    """Authentication session tracking (not Devin session)."""

    __tablename__ = "auth_sessions"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    jwt_id = Column(String(36), nullable=False, unique=True, index=True)
    ip_address = Column(String(45), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
