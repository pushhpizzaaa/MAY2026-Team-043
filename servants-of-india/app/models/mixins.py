"""Reusable column helpers shared by all models."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String


def gen_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PkMixin:
    """UUID primary key stored as a 36-char string (portable Postgres/SQLite)."""

    id = Column(String(36), primary_key=True, default=gen_uuid)


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
