"""Certificate generation, retrieval, download, and public verification."""
from flask import Blueprint, current_app, g, request

from ..extensions import db
from ..models import (
    Certificate,
    NotificationType,
    ProgressStatus,
    ServiceCategory,
    UserRole,
    VolunteerProgress,
)
from ..services.certificate_service import (
    generate_unique_identifiers,
    render_certificate_pdf,
)
from ..services.notifications import notify
from ..services.storage import storage
from ..utils.decorators import login_required, role_required
from ..utils.responses import error, ok

certificates_bp = Blueprint("certificates", __name__, url_prefix="/api")


def _verify_url(code: str) -> str:
    # Frontend public verify page; falls back to API base if not configured.
    base = current_app.config.get("FRONTEND_URL") or "http://localhost:5173"
    return f"{base}/verify/{code}"


@certificates_bp.post("/certificates/generate")
@role_required(UserRole.VOLUNTEER)
def generate_certificate():
    """Idempotent: returns the existing certificate if already issued."""
    volunteer = g.current_user

    existing = Certificate.query.filter_by(volunteer_id=volunteer.id).first()
    if existing:
        return ok(existing.to_dict())

    # Rule 11: all 5 categories must be completed.
    categories = ServiceCategory.query.order_by(ServiceCategory.name).all()
    progress = {
        p.category_id: p.status
        for p in VolunteerProgress.query.filter_by(volunteer_id=volunteer.id).all()
    }
    if not categories or any(
        progress.get(c.id) != ProgressStatus.COMPLETED for c in categories
    ):
        return error("All 5 categories must be completed before generating a certificate", 400)

    number, code = generate_unique_identifiers()
    pdf_bytes = render_certificate_pdf(
        volunteer_name=volunteer.full_name,
        certificate_number=number,
        verification_code=code,
        categories=[c.name for c in categories],
        verify_url=_verify_url(code),
    )
    stored_path = storage.save("certificates", f"{number}.pdf", pdf_bytes, "application/pdf")
    pdf_url = storage.public_url("certificates", stored_path)

    cert = Certificate(
        volunteer_id=volunteer.id,
        certificate_number=number,
        verification_code=code,
        pdf_url=pdf_url,
    )
    db.session.add(cert)
    notify(
        volunteer.id,
        NotificationType.CERTIFICATE,
        f"Your certificate {number} has been generated! 🏆",
        commit=False,
    )
    db.session.commit()
    return ok(cert.to_dict())


@certificates_bp.get("/certificates")
@role_required(UserRole.SUPER_ADMIN)
def list_certificates():
    """Super Admin: record of every volunteer who received a certificate."""
    certs = Certificate.query.order_by(Certificate.issued_at.desc()).all()
    items = []
    for c in certs:
        data = c.to_dict()
        data["volunteer_email"] = c.volunteer.email if c.volunteer else None
        items.append(data)
    return ok(items)


@certificates_bp.get("/certificates/me")
@role_required(UserRole.VOLUNTEER)
def my_certificate():
    cert = Certificate.query.filter_by(volunteer_id=g.current_user.id).first()
    if not cert:
        return error("No certificate yet", 404)
    return ok(cert.to_dict())


@certificates_bp.get("/certificates/<cert_id>/download")
@login_required
def download_certificate(cert_id):
    cert = Certificate.query.get(cert_id)
    if not cert:
        return error("Certificate not found", 404)
    user = g.current_user
    if user.role == UserRole.VOLUNTEER and cert.volunteer_id != user.id:
        return error("Forbidden", 403)
    # Returns the (possibly signed) storage URL for the client to download.
    return ok({"download_url": cert.pdf_url})


@certificates_bp.get("/verify/<verification_code>")
def verify_certificate(verification_code):
    """PUBLIC — no auth. Returns validity + a certificate summary."""
    cert = Certificate.query.filter_by(verification_code=verification_code).first()
    if not cert:
        return ok({"valid": False})
    return ok({
        "valid": True,
        "certificate": {
            "volunteer_name": cert.volunteer.full_name if cert.volunteer else None,
            "certificate_number": cert.certificate_number,
            "issued_at": cert.issued_at.isoformat() if cert.issued_at else None,
        },
    })
