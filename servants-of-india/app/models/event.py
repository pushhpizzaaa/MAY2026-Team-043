import re

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import relationship

from ..extensions import db
from .enums import EventStatus
from .mixins import PkMixin, TimestampMixin


def slugify(text: str) -> str:
    """Turn a title into a URL-friendly slug, e.g. 'Tree Plantation!' -> 'tree-plantation'."""
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return slug or "event"


class Event(PkMixin, TimestampMixin, db.Model):
    __tablename__ = "events"

    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    category_id = Column(String(36), ForeignKey("service_categories.id"), nullable=False)
    venue = Column(String(150), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(80), nullable=False)
    state = Column(String(80), nullable=False)
    event_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    capacity = Column(Integer)
    status = Column(String(20), nullable=False, default=EventStatus.UPCOMING)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    category = relationship("ServiceCategory")
    creator = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            # Human-readable, consistent URL slug: "<title-slug>-<short-id>".
            "slug": f"{slugify(self.title)}-{self.id[:8]}",
            "title": self.title,
            "description": self.description,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "venue": self.venue,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "start_time": self.start_time.strftime("%H:%M") if self.start_time else None,
            "end_time": self.end_time.strftime("%H:%M") if self.end_time else None,
            "capacity": self.capacity,
            "status": self.status,
            "created_by": self.created_by,
            "created_by_name": self.creator.full_name if self.creator else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
