"""Read-only listing of the 5 fixed service categories.

No create/update/delete — categories are seeded once (business rule 2). This endpoint
exists only so the frontend can populate category pickers (event form, filters).
"""
from flask import Blueprint

from ..models import ServiceCategory
from ..utils.decorators import login_required
from ..utils.responses import ok

categories_bp = Blueprint("categories", __name__, url_prefix="/api/categories")


@categories_bp.get("")
@login_required
def list_categories():
    cats = ServiceCategory.query.order_by(ServiceCategory.name).all()
    return ok([c.to_dict() for c in cats])
