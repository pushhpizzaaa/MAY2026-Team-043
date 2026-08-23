"""String enums used across models. Plain str subclasses keep them JSON-friendly
and portable across Postgres and SQLite."""


class UserRole:
    VOLUNTEER = "volunteer"
    EVENT_MANAGER = "event_manager"
    SUPER_ADMIN = "super_admin"
    ALL = (VOLUNTEER, EVENT_MANAGER, SUPER_ADMIN)


class UserStatus:
    ACTIVE = "active"
    BLOCKED = "blocked"
    DEACTIVATED = "deactivated"
    ALL = (ACTIVE, BLOCKED, DEACTIVATED)


class EventStatus:
    UPCOMING = "upcoming"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ALL = (UPCOMING, COMPLETED, CANCELLED)


class SubmissionStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ALL = (PENDING, APPROVED, REJECTED)


class ReviewDecision:
    APPROVED = "approved"
    REJECTED = "rejected"
    ALL = (APPROVED, REJECTED)


class ProgressStatus:
    NOT_STARTED = "not_started"
    PENDING = "pending"
    COMPLETED = "completed"
    ALL = (NOT_STARTED, PENDING, COMPLETED)


class NotificationType:
    APPROVAL = "approval"
    REJECTION = "rejection"
    CERTIFICATE = "certificate"
    SYSTEM = "system"
    ALL = (APPROVAL, REJECTION, CERTIFICATE, SYSTEM)


class CertificateType:
    """Placeholder for future certificate variants; kept for API symmetry."""
    COMPLETION = "completion"
