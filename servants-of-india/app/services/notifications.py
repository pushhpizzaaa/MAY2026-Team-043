"""Helper to create in-app notifications."""
from ..extensions import db
from ..models import Notification


def notify(user_id: str, ntype: str, message: str, commit: bool = True) -> Notification:
    note = Notification(user_id=user_id, type=ntype, message=message)
    db.session.add(note)
    if commit:
        db.session.commit()
    return note
