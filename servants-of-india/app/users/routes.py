"""User profile + Super Admin user management."""
from flask import Blueprint, g, request

from ..extensions import db
from ..models import User, UserRole, UserStatus
from ..utils.decorators import login_required, role_required
from ..utils.responses import created, error, ok
from ..utils.security import hash_password, verify_password
from ..utils.validators import require_fields, valid_email

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.get("/me")
@login_required
def get_me():
    return ok(g.current_user.to_dict())


@users_bp.put("/me")
@login_required
def update_me():
    data = request.get_json(silent=True) or {}
    user = g.current_user
    # Email is immutable; role/status can never be self-edited.
    for field in ("full_name", "phone", "location", "organization"):
        if field in data:
            value = (data.get(field) or "").strip()
            setattr(user, field, value or None)
    if not user.full_name:
        return error("full_name cannot be empty", 422)
    db.session.commit()
    return ok(user.to_dict())


@users_bp.put("/me/password")
@login_required
def change_password():
    """Any authenticated user can change their own password."""
    data = request.get_json(silent=True) or {}
    require_fields(data, ["current_password", "new_password"])
    user = g.current_user
    # Use 400 (not 401) so the frontend's auth interceptor does NOT treat a wrong
    # current password as an expired session and log the user out.
    if not verify_password(data["current_password"], user.password_hash):
        return error("Current password is incorrect", 400)
    if len(data["new_password"]) < 8:
        return error("New password must be at least 8 characters", 422)
    user.password_hash = hash_password(data["new_password"])
    db.session.commit()
    return ok({"message": "Password updated"})


@users_bp.get("")
@role_required(UserRole.SUPER_ADMIN)
def list_users():
    query = User.query
    role = request.args.get("role")
    status = request.args.get("status")
    if role:
        query = query.filter_by(role=role)
    if status:
        query = query.filter_by(status=status)
    users = query.order_by(User.created_at.desc()).all()
    return ok([u.to_dict() for u in users])


@users_bp.post("")
@role_required(UserRole.SUPER_ADMIN)
def create_privileged_user():
    """Super Admin creates an Event Manager or another Super Admin."""
    data = request.get_json(silent=True) or {}
    require_fields(data, ["full_name", "email", "password", "role"])
    role = data["role"]
    if role not in (UserRole.EVENT_MANAGER, UserRole.SUPER_ADMIN):
        return error("role must be event_manager or super_admin", 422)
    # An Event Manager must have an organization, phone and location.
    if role == UserRole.EVENT_MANAGER:
        for field in ("organization", "phone", "location"):
            if not (data.get(field) or "").strip():
                return error(f"{field.capitalize()} is required for an Event Manager", 422)
    email = data["email"].strip().lower()
    if not valid_email(email):
        return error("Invalid email address", 422)
    if len(data["password"]) < 8:
        return error("Password must be at least 8 characters", 422)
    if User.query.filter_by(email=email).first():
        return error("Email already registered", 409)

    user = User(
        full_name=data["full_name"].strip(),
        email=email,
        password_hash=hash_password(data["password"]),
        phone=(data.get("phone") or "").strip() or None,
        location=(data.get("location") or "").strip() or None,
        organization=(data.get("organization") or "").strip() or None,
        role=role,
        status=UserStatus.ACTIVE,
    )
    db.session.add(user)
    db.session.commit()
    return created(user.to_dict())


@users_bp.patch("/<user_id>/status")
@role_required(UserRole.SUPER_ADMIN)
def change_status(user_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in UserStatus.ALL:
        return error(f"status must be one of {', '.join(UserStatus.ALL)}", 422)
    user = User.query.get(user_id)
    if not user:
        return error("User not found", 404)
    if user.id == g.current_user.id:
        return error("You cannot change your own status", 400)
    user.status = status
    db.session.commit()
    return ok(user.to_dict())
