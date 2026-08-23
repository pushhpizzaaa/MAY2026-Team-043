from sqlalchemy import Column, String

from ..extensions import db
from .mixins import PkMixin, TimestampMixin


class ServiceCategory(PkMixin, TimestampMixin, db.Model):
    __tablename__ = "service_categories"

    # Fixed set of 5 rows, seeded once. No CRUD endpoints.
    name = Column(String(80), unique=True, nullable=False)

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}
