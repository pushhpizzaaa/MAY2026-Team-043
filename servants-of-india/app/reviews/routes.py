"""Approve / reject submissions. Approval auto-completes progress + notifies."""
from flask import Blueprint, g, request

from ..extensions import db
from ..models import (
    NotificationType,
    ProgressStatus,
    ReviewDecision,
    Submission,
    SubmissionReview,
    SubmissionStatus,
    UserRole,
    VolunteerProgress,
)
from ..services.notifications import notify
from ..utils.decorators import role_required
from ..utils.responses import error, ok

# Reviews live under /api/submissions/:id/{approve,reject} per the PRD.
reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/submissions")


def _ensure_can_review(submission):
    """Event Managers may only review proofs linked to events they created.
    Super Admins may review any. Returns an error response or None."""
    user = g.current_user
    if user.role == UserRole.EVENT_MANAGER:
        if not submission.event or submission.event.created_by != user.id:
            return error("You can only review submissions for your own events", 403)
    return None


def _record_review(submission, decision, remarks):
    review = SubmissionReview(
        submission_id=submission.id,
        reviewed_by=g.current_user.id,
        decision=decision,
        remarks=remarks,
    )
    db.session.add(review)
    return review


@reviews_bp.post("/<submission_id>/approve")
@role_required(UserRole.EVENT_MANAGER, UserRole.SUPER_ADMIN)
def approve(submission_id):
    sub = Submission.query.get(submission_id)
    if not sub:
        return error("Submission not found", 404)
    denied = _ensure_can_review(sub)
    if denied:
        return denied
    if sub.status != SubmissionStatus.PENDING:
        return error(f"Submission already {sub.status}", 409)

    sub.status = SubmissionStatus.APPROVED
    _record_review(sub, ReviewDecision.APPROVED, (request.get_json(silent=True) or {}).get("remarks"))

    # Rule 6: mark the matching progress row completed.
    progress = VolunteerProgress.query.filter_by(
        volunteer_id=sub.volunteer_id, category_id=sub.category_id
    ).first()
    if not progress:
        progress = VolunteerProgress(volunteer_id=sub.volunteer_id, category_id=sub.category_id)
        db.session.add(progress)
    progress.status = ProgressStatus.COMPLETED

    notify(
        sub.volunteer_id,
        NotificationType.APPROVAL,
        f"Your submission for '{sub.category.name}' was approved. 🎉",
        commit=False,
    )
    db.session.commit()
    return ok(sub.to_dict(include_review=True))


@reviews_bp.post("/<submission_id>/reject")
@role_required(UserRole.EVENT_MANAGER, UserRole.SUPER_ADMIN)
def reject(submission_id):
    data = request.get_json(silent=True) or {}
    remarks = (data.get("remarks") or "").strip()
    if not remarks:
        return error("A rejection reason (remarks) is required", 422)

    sub = Submission.query.get(submission_id)
    if not sub:
        return error("Submission not found", 404)
    denied = _ensure_can_review(sub)
    if denied:
        return denied
    if sub.status != SubmissionStatus.PENDING:
        return error(f"Submission already {sub.status}", 409)

    sub.status = SubmissionStatus.REJECTED
    _record_review(sub, ReviewDecision.REJECTED, remarks)

    # Reset progress to not_started so the volunteer can resubmit (rule 5).
    progress = VolunteerProgress.query.filter_by(
        volunteer_id=sub.volunteer_id, category_id=sub.category_id
    ).first()
    if progress and progress.status != ProgressStatus.COMPLETED:
        progress.status = ProgressStatus.NOT_STARTED

    notify(
        sub.volunteer_id,
        NotificationType.REJECTION,
        f"Your submission for '{sub.category.name}' was rejected: {remarks}",
        commit=False,
    )
    db.session.commit()
    return ok(sub.to_dict(include_review=True))
