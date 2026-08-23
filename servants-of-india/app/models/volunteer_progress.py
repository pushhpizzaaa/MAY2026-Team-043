from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from ..extensions import db
from .enums import ProgressStatus
from .mixins import PkMixin, utcnow


class VolunteerProgress(PkMixin, db.Model):
    __tablename__ = "volunteer_progress"
    __table_args__ = (
        UniqueConstraint("volunteer_id", "category_id", name="uq_volunteer_category"),
    )

    volunteer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey("service_categories.id"), nullable=False)
    status = Column(String(20), nullable=False, default=ProgressStatus.NOT_STARTED)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    category = relationship("ServiceCategory")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "volunteer_id": self.volunteer_id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "status": self.status,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
