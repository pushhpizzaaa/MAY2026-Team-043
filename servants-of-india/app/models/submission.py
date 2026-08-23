from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from ..extensions import db
from .enums import SubmissionStatus
from .mixins import PkMixin
from .mixins import utcnow


class Submission(PkMixin, db.Model):
    __tablename__ = "submissions"

    volunteer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey("service_categories.id"), nullable=False)
    event_id = Column(String(36), ForeignKey("events.id"), nullable=True)
    image_url = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default=SubmissionStatus.PENDING)
    submitted_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    volunteer = relationship("User")
    category = relationship("ServiceCategory")
    event = relationship("Event")
    review = relationship("SubmissionReview", uselist=False, back_populates="submission")

    def to_dict(self, include_review: bool = False) -> dict:
        data = {
            "id": self.id,
            "volunteer_id": self.volunteer_id,
            "volunteer_name": self.volunteer.full_name if self.volunteer else None,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "event_id": self.event_id,
            "event_title": self.event.title if self.event else None,
            "image_url": self.image_url,
            "description": self.description,
            "status": self.status,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
        }
        if include_review and self.review:
            data["review"] = self.review.to_dict()
        return data
