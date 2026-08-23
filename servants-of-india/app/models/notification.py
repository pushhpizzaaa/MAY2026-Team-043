from sqlalchemy import Boolean, Column, ForeignKey, String, Text

from ..extensions import db
from .mixins import PkMixin, TimestampMixin


class Notification(PkMixin, TimestampMixin, db.Model):
    __tablename__ = "notifications"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(20), nullable=False)  # approval | rejection | certificate | system
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
