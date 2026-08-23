"""Proof submissions by volunteers + review queue for managers/admins."""
from flask import Blueprint, g, request

from ..extensions import db
from ..models import (
    Event,
    ProgressStatus,
    ServiceCategory,
    Submission,
    SubmissionStatus,
    UserRole,
    VolunteerProgress,
)
from ..services.storage import storage, unique_filename
from ..utils.decorators import login_required, role_required
from ..utils.responses import created, error, ok

submissions_bp = Blueprint("submissions", __name__, url_prefix="/api/submissions")

ALLOWED_EXT = {"jpg", "jpeg", "png"}


def _ext_ok(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@submissions_bp.post("")
@role_required(UserRole.VOLUNTEER)
def create_submission():
    """Multipart: image file + category_id, description, optional event_id."""
    volunteer = g.current_user
    category_id = request.form.get("category_id")
    description = (request.form.get("description") or "").strip()
    event_id = request.form.get("event_id") or None
    image = request.files.get("image")

    if not category_id or not description:
        return error("category_id and description are required", 422)
    if not image or image.filename == "":
        return error("A proof image is required", 422)
    if not _ext_ok(image.filename):
        return error("Image must be .jpg, .jpeg or .png", 422)

    category = ServiceCategory.query.get(category_id)
    if not category:
        return error("Invalid category_id", 422)
    if event_id and not Event.query.get(event_id):
        return error("Invalid event_id", 422)

    # --- Business rules ---
    # Rule 3: only one approved submission per category.
    if Submission.query.filter_by(
        volunteer_id=volunteer.id, category_id=category_id,
        status=SubmissionStatus.APPROVED,
    ).first():
        return error("You have already completed this category", 409)

    # Rule 4: only one pending submission per category at a time.
    if Submission.query.filter_by(
        volunteer_id=volunteer.id, category_id=category_id,
        status=SubmissionStatus.PENDING,
    ).first():
        return error("You already have a pending submission for this category", 409)

    # Persist the image via the storage adapter.
    data = image.read()
    if len(data) > 5 * 1024 * 1024:
        return error("File too large (max 5 MB)", 413)
    stored_path = storage.save(
        "proof-submissions",
        unique_filename(image.filename),
        data,
        image.mimetype or "image/jpeg",
    )
    public_url = storage.public_url("proof-submissions", stored_path)

    submission = Submission(
        volunteer_id=volunteer.id,
        category_id=category_id,
        event_id=event_id,
        image_url=public_url,
        description=description,
        status=SubmissionStatus.PENDING,
    )
    db.session.add(submission)

    # Move the category's progress row to `pending`.
    progress = VolunteerProgress.query.filter_by(
        volunteer_id=volunteer.id, category_id=category_id
    ).first()
    if not progress:
        progress = VolunteerProgress(volunteer_id=volunteer.id, category_id=category_id)
        db.session.add(progress)
    if progress.status != ProgressStatus.COMPLETED:
        progress.status = ProgressStatus.PENDING

    db.session.commit()
    return created(submission.to_dict())


@submissions_bp.get("/me")
@role_required(UserRole.VOLUNTEER)
def my_submissions():
    subs = (
        Submission.query.filter_by(volunteer_id=g.current_user.id)
        .order_by(Submission.submitted_at.desc())
        .all()
    )
    return ok([s.to_dict(include_review=True) for s in subs])


@submissions_bp.get("")
@role_required(UserRole.EVENT_MANAGER, UserRole.SUPER_ADMIN)
def review_queue():
    """Manager/Admin queue. Defaults to pending; supports ?status=."""
    status = request.args.get("status", SubmissionStatus.PENDING)
    query = Submission.query
    # Event Managers only see submissions tied to events they created.
    if g.current_user.role == UserRole.EVENT_MANAGER:
        query = query.join(Event, Submission.event_id == Event.id).filter(
            Event.created_by == g.current_user.id
        )
    if status and status != "all":
        # Use an explicit column (not filter_by) — after the Event join above,
        # filter_by(status=...) would bind to Event.status, not Submission.status.
        query = query.filter(Submission.status == status)
    subs = query.order_by(Submission.submitted_at.asc()).all()
    return ok([s.to_dict(include_review=True) for s in subs])


@submissions_bp.get("/<submission_id>")
@login_required
def get_submission(submission_id):
    sub = Submission.query.get(submission_id)
    if not sub:
        return error("Submission not found", 404)
    user = g.current_user
    # Volunteers may only view their own submissions.
    if user.role == UserRole.VOLUNTEER and sub.volunteer_id != user.id:
        return error("Forbidden", 403)
    return ok(sub.to_dict(include_review=True))
