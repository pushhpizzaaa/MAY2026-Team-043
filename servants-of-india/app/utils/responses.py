"""Consistent JSON response + error helpers."""
from flask import jsonify


def ok(data=None, status: int = 200):
    return jsonify({"success": True, "data": data}), status


def created(data=None):
    return ok(data, status=201)


def error(message: str, status: int = 400, details=None):
    payload = {"success": False, "error": message}
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status


class ApiError(Exception):
    """Raise anywhere in a request to short-circuit with a JSON error response."""

    def __init__(self, message: str, status: int = 400, details=None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.details = details
