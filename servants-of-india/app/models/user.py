from sqlalchemy import Column, String

from ..extensions import db
from .enums import UserRole, UserStatus
from .mixins import PkMixin, TimestampMixin


class User(PkMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    full_name = Column(String(120), nullable=False)
    email = Column(String(160), unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    phone = Column(String(20))
    location = Column(String(120))
    organization = Column(String(120))
    role = Column(String(20), nullable=False, default=UserRole.VOLUNTEER)
    status = Column(String(20), nullable=False, default=UserStatus.ACTIVE)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "organization": self.organization,
            "role": self.role,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
