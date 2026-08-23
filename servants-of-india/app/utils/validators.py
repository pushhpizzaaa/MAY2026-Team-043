"""Lightweight request validation helpers.

Kept intentionally simple (no external schema lib) for MVP clarity.
"""
import re
from datetime import datetime

from .responses import ApiError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def require_fields(data: dict, fields: list[str]) -> None:
    if not isinstance(data, dict):
        raise ApiError("Invalid JSON body", 400)
    missing = [f for f in fields if not str(data.get(f, "")).strip()]
    if missing:
        raise ApiError(f"Missing required fields: {', '.join(missing)}", 422)


def valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))


def parse_date(value: str, field: str = "date"):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise ApiError(f"Invalid {field}, expected YYYY-MM-DD", 422)


def parse_time(value: str, field: str = "time"):
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).time()
        except (ValueError, TypeError):
            continue
    raise ApiError(f"Invalid {field}, expected HH:MM", 422)
