"""Auth/RBAC decorators built on Flask-JWT-Extended.

`role_required` enforces role server-side on every protected route and also blocks
users whose account status is not `active`.
"""
from functools import wraps

from flask import g
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request

from ..models import User, UserStatus
from .responses import error


def _load_current_user():
    """Fetch the User for the JWT identity and stash it on `g.current_user`."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    g.current_user = user
    return user


def login_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = _load_current_user()
        if user is None:
            return error("User not found", 401)
        if user.status != UserStatus.ACTIVE:
            return error(f"Account is {user.status}", 403)
        return fn(*args, **kwargs)

    return wrapper


def role_required(*allowed_roles):
    """Restrict a route to the given role(s). Also enforces active status."""

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = _load_current_user()
            if user is None:
                return error("User not found", 401)
            if user.status != UserStatus.ACTIVE:
                return error(f"Account is {user.status}", 403)
            if user.role not in allowed_roles:
                return error("Forbidden: insufficient role", 403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
