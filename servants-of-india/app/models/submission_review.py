from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from ..extensions import db
from .mixins import PkMixin, utcnow


class SubmissionReview(PkMixin, db.Model):
    __tablename__ = "submission_reviews"

    submission_id = Column(String(36), ForeignKey("submissions.id"), nullable=False, index=True)
    reviewed_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    decision = Column(String(20), nullable=False)  # approved | rejected
    remarks = Column(Text)
    reviewed_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    submission = relationship("Submission", back_populates="review")
    reviewer = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "submission_id": self.submission_id,
            "reviewed_by": self.reviewed_by,
            "reviewer_name": self.reviewer.full_name if self.reviewer else None,
            "decision": self.decision,
            "remarks": self.remarks,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }
