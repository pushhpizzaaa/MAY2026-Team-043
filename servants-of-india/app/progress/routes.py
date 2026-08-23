"""Volunteer progress across the 5 fixed categories + star count."""
from flask import Blueprint, g

from ..extensions import db
from ..models import ProgressStatus, ServiceCategory, UserRole, VolunteerProgress
from ..utils.decorators import role_required
from ..utils.responses import ok

progress_bp = Blueprint("progress", __name__, url_prefix="/api/progress")


@progress_bp.get("/me")
@role_required(UserRole.VOLUNTEER)
def my_progress():
    volunteer = g.current_user
    categories = ServiceCategory.query.order_by(ServiceCategory.name).all()

    existing = {
        p.category_id: p
        for p in VolunteerProgress.query.filter_by(volunteer_id=volunteer.id).all()
    }

    items = []
    completed = 0
    for cat in categories:
        prog = existing.get(cat.id)
        status = prog.status if prog else ProgressStatus.NOT_STARTED
        if status == ProgressStatus.COMPLETED:
            completed += 1
        items.append({
            "category_id": cat.id,
            "category_name": cat.name,
            "status": status,
        })

    total = len(categories)
    return ok({
        "categories": items,
        "completed_count": completed,      # "stars" earned
        "total_categories": total,
        "stars": completed,
        "all_completed": total > 0 and completed == total,
    })
