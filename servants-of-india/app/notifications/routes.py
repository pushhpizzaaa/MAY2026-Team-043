"""In-app notifications for the current user."""
from flask import Blueprint, g

from ..extensions import db
from ..models import Notification
from ..utils.decorators import login_required
from ..utils.responses import error, ok

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@notifications_bp.get("")
@login_required
def list_notifications():
    notes = (
        Notification.query.filter_by(user_id=g.current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    unread = sum(1 for n in notes if not n.is_read)
    return ok({"notifications": [n.to_dict() for n in notes], "unread_count": unread})


@notifications_bp.patch("/<note_id>/read")
@login_required
def mark_read(note_id):
    note = Notification.query.get(note_id)
    if not note or note.user_id != g.current_user.id:
        return error("Notification not found", 404)
    note.is_read = True
    db.session.commit()
    return ok(note.to_dict())
