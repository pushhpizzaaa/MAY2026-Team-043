"""Event CRUD with ownership checks."""
from flask import Blueprint, g, request

from ..extensions import db
from ..models import Event, EventStatus, ServiceCategory, UserRole
from ..utils.decorators import login_required, role_required
from ..utils.responses import created, error, ok
from ..utils.validators import parse_date, parse_time, require_fields

events_bp = Blueprint("events", __name__, url_prefix="/api/events")

_REQUIRED = ["title", "description", "category_id", "venue", "address",
             "city", "state", "event_date", "start_time", "end_time"]


def _can_modify(event: Event) -> bool:
    user = g.current_user
    return user.role == UserRole.SUPER_ADMIN or event.created_by == user.id


@events_bp.get("")
@login_required
def list_events():
    query = Event.query
    category = request.args.get("category")
    status = request.args.get("status")
    if category:
        query = query.filter_by(category_id=category)
    if status:
        query = query.filter_by(status=status)
    events = query.order_by(Event.event_date.asc()).all()
    return ok([e.to_dict() for e in events])


@events_bp.get("/<identifier>")
@login_required
def get_event(identifier):
    """Resolve an event by raw UUID or by its "<title-slug>-<short-id>" slug."""
    event = Event.query.get(identifier)
    if not event:
        # Slug form: the trailing segment is the first 8 chars of the UUID.
        short_id = identifier.rsplit("-", 1)[-1]
        if short_id:
            event = Event.query.filter(Event.id.like(f"{short_id}%")).first()
    if not event:
        return error("Event not found", 404)
    return ok(event.to_dict())


@events_bp.post("")
@role_required(UserRole.EVENT_MANAGER, UserRole.SUPER_ADMIN)
def create_event():
    data = request.get_json(silent=True) or {}
    require_fields(data, _REQUIRED)
    if not ServiceCategory.query.get(data["category_id"]):
        return error("Invalid category_id", 422)

    event = Event(
        title=data["title"].strip(),
        description=data["description"].strip(),
        category_id=data["category_id"],
        venue=data["venue"].strip(),
        address=data["address"].strip(),
        city=data["city"].strip(),
        state=data["state"].strip(),
        event_date=parse_date(data["event_date"], "event_date"),
        start_time=parse_time(data["start_time"], "start_time"),
        end_time=parse_time(data["end_time"], "end_time"),
        capacity=data.get("capacity"),
        status=data.get("status", EventStatus.UPCOMING),
        created_by=g.current_user.id,
    )
    if event.status not in EventStatus.ALL:
        return error(f"status must be one of {', '.join(EventStatus.ALL)}", 422)
    db.session.add(event)
    db.session.commit()
    return created(event.to_dict())


@events_bp.put("/<event_id>")
@role_required(UserRole.EVENT_MANAGER, UserRole.SUPER_ADMIN)
def update_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return error("Event not found", 404)
    if not _can_modify(event):
        return error("You can only edit your own events", 403)

    data = request.get_json(silent=True) or {}
    if "category_id" in data and not ServiceCategory.query.get(data["category_id"]):
        return error("Invalid category_id", 422)

    for field in ("title", "description", "category_id", "venue", "address", "city", "state", "capacity"):
        if field in data:
            setattr(event, field, data[field])
    if "event_date" in data:
        event.event_date = parse_date(data["event_date"], "event_date")
    if "start_time" in data:
        event.start_time = parse_time(data["start_time"], "start_time")
    if "end_time" in data:
        event.end_time = parse_time(data["end_time"], "end_time")
    if "status" in data:
        if data["status"] not in EventStatus.ALL:
            return error(f"status must be one of {', '.join(EventStatus.ALL)}", 422)
        event.status = data["status"]

    db.session.commit()
    return ok(event.to_dict())


@events_bp.delete("/<event_id>")
@role_required(UserRole.EVENT_MANAGER, UserRole.SUPER_ADMIN)
def delete_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return error("Event not found", 404)
    if not _can_modify(event):
        return error("You can only delete your own events", 403)
    db.session.delete(event)
    db.session.commit()
    return ok({"message": "Event deleted"})
