"""Authentication: volunteer self-registration, login, logout."""
from flask import Blueprint, request
from flask_jwt_extended import create_access_token

from ..extensions import db
from ..models import User, UserRole, UserStatus
from ..utils.responses import created, error, ok
from ..utils.security import hash_password, verify_password
from ..utils.validators import require_fields, valid_email

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    """Public sign-up — creates a Volunteer account only."""
    data = request.get_json(silent=True) or {}
    require_fields(data, ["full_name", "email", "password", "phone", "location"])

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
        role=UserRole.VOLUNTEER,
        status=UserStatus.ACTIVE,
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.id, additional_claims={"role": user.role})
    return created({"token": token, "user": user.to_dict()})


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["email", "password"])
    email = data["email"].strip().lower()

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(data["password"], user.password_hash):
        return error("Invalid email or password", 401)
    if user.status == UserStatus.BLOCKED:
        return error("Your account is blocked. Contact an administrator.", 403)
    if user.status == UserStatus.DEACTIVATED:
        return error("Your account is deactivated.", 403)

    token = create_access_token(identity=user.id, additional_claims={"role": user.role})
    return ok({"token": token, "user": user.to_dict()})


@auth_bp.post("/logout")
def logout():
    # Stateless JWT: logout is handled client-side by discarding the token.
    return ok({"message": "Logged out"})
