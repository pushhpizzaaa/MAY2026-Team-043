from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from ..extensions import db
from .mixins import PkMixin, utcnow


class Certificate(PkMixin, db.Model):
    __tablename__ = "certificates"

    volunteer_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    certificate_number = Column(String(40), unique=True, nullable=False)
    verification_code = Column(String(40), unique=True, nullable=False, index=True)
    pdf_url = Column(Text)
    issued_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    volunteer = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "volunteer_id": self.volunteer_id,
            "volunteer_name": self.volunteer.full_name if self.volunteer else None,
            "certificate_number": self.certificate_number,
            "verification_code": self.verification_code,
            "pdf_url": self.pdf_url,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
        }
