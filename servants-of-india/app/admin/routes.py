"""System-wide dashboard statistics for Super Admin (and per-owner for managers)."""
from flask import Blueprint, g

from ..models import (
    Certificate,
    Event,
    EventStatus,
    Submission,
    SubmissionStatus,
    User,
    UserRole,
    UserStatus,
)
from ..utils.decorators import role_required
from ..utils.responses import ok

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/stats")
@role_required(UserRole.EVENT_MANAGER, UserRole.SUPER_ADMIN)
def stats():
    user = g.current_user

    if user.role == UserRole.SUPER_ADMIN:
        submissions_by_status = {
            s: Submission.query.filter_by(status=s).count() for s in SubmissionStatus.ALL
        }
        events_by_status = {
            s: Event.query.filter_by(status=s).count() for s in EventStatus.ALL
        }
        data = {
            "scope": "system",
            "users": {
                "total": User.query.count(),
                "volunteers": User.query.filter_by(role=UserRole.VOLUNTEER).count(),
                "event_managers": User.query.filter_by(role=UserRole.EVENT_MANAGER).count(),
                "admins": User.query.filter_by(role=UserRole.SUPER_ADMIN).count(),
                "blocked": User.query.filter_by(status=UserStatus.BLOCKED).count(),
            },
            "events": Event.query.count(),
            "events_by_status": events_by_status,
            "submissions": submissions_by_status,
            "certificates_issued": Certificate.query.count(),
        }
    else:
        # Event Manager: every count is scoped to the events they created.
        own_events = Event.query.filter_by(created_by=user.id)
        own_by_status = {
            s: own_events.filter_by(status=s).count() for s in EventStatus.ALL
        }
        # Submissions counted only for this manager's own events.
        own_submissions = Submission.query.join(
            Event, Submission.event_id == Event.id
        ).filter(Event.created_by == user.id)
        submissions_by_status = {
            s: own_submissions.filter(Submission.status == s).count()
            for s in SubmissionStatus.ALL
        }
        data = {
            "scope": "own",
            "events": own_events.count(),
            "events_by_status": own_by_status,
            "submissions": submissions_by_status,
        }
    return ok(data)
