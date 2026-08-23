"""One-time seed script.

Run after DB setup:  python seed.py

1. Inserts the 5 fixed service categories (idempotent).
2. Creates the first Super Admin account (credentials from .env or defaults),
   printing them to the console on first creation.
"""
import os

from app.app import create_app
from app.extensions import db
from app.models import ServiceCategory, User, UserRole, UserStatus
from app.utils.security import hash_password

CATEGORIES = [
    "Women's Care",
    "Child Welfare",
    "Elder Care & Orphanage",
    "Environmental Plantation",
    "Blood Donation",
]


def seed_categories():
    created = 0
    for name in CATEGORIES:
        if not ServiceCategory.query.filter_by(name=name).first():
            db.session.add(ServiceCategory(name=name))
            created += 1
    db.session.commit()
    print(f"Service categories: {created} created, {len(CATEGORIES) - created} already existed.")


def seed_super_admin():
    email = os.getenv("SEED_ADMIN_EMAIL", "admin@sob.local").strip().lower()
    password = os.getenv("SEED_ADMIN_PASSWORD", "Admin@12345")
    name = os.getenv("SEED_ADMIN_NAME", "Super Admin")

    if User.query.filter_by(email=email).first():
        print(f"Super Admin already exists: {email}")
        return

    admin = User(
        full_name=name,
        email=email,
        password_hash=hash_password(password),
        role=UserRole.SUPER_ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.session.add(admin)
    db.session.commit()
    print("=" * 52)
    print("  First Super Admin created — SAVE THESE CREDENTIALS:")
    print(f"    Email:    {email}")
    print(f"    Password: {password}")
    print("=" * 52)


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_categories()
        seed_super_admin()
        print("Seeding complete.")


if __name__ == "__main__":
    main()
