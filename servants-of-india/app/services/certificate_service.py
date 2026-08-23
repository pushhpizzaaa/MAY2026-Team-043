"""Certificate generation: unique-number allocation + ReportLab PDF rendering."""
import io
import secrets
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from ..extensions import db
from ..models import Certificate


def _year() -> int:
    return datetime.now(timezone.utc).year


def generate_unique_identifiers() -> tuple[str, str]:
    """Return (certificate_number, verification_code) unique across the table,
    retrying on the (rare) collision."""
    year = _year()
    for _ in range(25):
        seq = secrets.randbelow(99999) + 1
        number = f"SOB-{year}-{seq:05d}"
        code = secrets.token_urlsafe(12)
        exists = Certificate.query.filter(
            (Certificate.certificate_number == number)
            | (Certificate.verification_code == code)
        ).first()
        if not exists:
            return number, code
    raise RuntimeError("Could not allocate a unique certificate number")


def render_certificate_pdf(
    volunteer_name: str,
    certificate_number: str,
    verification_code: str,
    categories: list[str],
    verify_url: str,
) -> bytes:
    """Render a simple, clean landscape completion certificate and return PDF bytes."""
    buf = io.BytesIO()
    width, height = landscape(A4)
    c = canvas.Canvas(buf, pagesize=landscape(A4))

    navy = colors.HexColor("#0f2b46")
    saffron = colors.HexColor("#d97706")
    grey = colors.HexColor("#475569")

    # Border
    c.setStrokeColor(navy)
    c.setLineWidth(3)
    c.rect(15 * mm, 15 * mm, width - 30 * mm, height - 30 * mm)
    c.setStrokeColor(saffron)
    c.setLineWidth(1)
    c.rect(18 * mm, 18 * mm, width - 36 * mm, height - 36 * mm)

    center = width / 2

    c.setFillColor(saffron)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(center, height - 40 * mm, "SERVANTS OF BHARAT")

    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(center, height - 62 * mm, "Certificate of Completion")

    c.setFillColor(grey)
    c.setFont("Helvetica", 13)
    c.drawCentredString(center, height - 78 * mm, "This certifies that")

    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(center, height - 92 * mm, volunteer_name)

    c.setFillColor(grey)
    c.setFont("Helvetica", 12)
    c.drawCentredString(
        center,
        height - 106 * mm,
        "has completed volunteer service across all five categories:",
    )

    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(center, height - 116 * mm, "  •  ".join(categories))

    # Footer: number + verification
    c.setFont("Helvetica", 9)
    c.setFillColor(grey)
    c.drawString(25 * mm, 25 * mm, f"Certificate No: {certificate_number}")
    issued = datetime.now(timezone.utc).strftime("%d %b %Y")
    c.drawRightString(width - 25 * mm, 25 * mm, f"Issued: {issued}")
    c.drawCentredString(center, 20 * mm, f"Verify at: {verify_url}")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()
