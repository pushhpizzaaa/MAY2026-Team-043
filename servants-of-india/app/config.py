"""Central application configuration, loaded from environment variables."""
import os
from datetime import timedelta

from dotenv import load_dotenv

# Load .env from the backend/ directory (one level up from this file's package).
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class Config:
    """Base config. Values come from the environment; sane fallbacks for local dev."""

    # --- Database ---
    # Fall back to a local SQLite file so the app can boot even without Supabase
    # credentials configured yet. Set DATABASE_URL to your Supabase Postgres URI.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'sob_dev.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- JWT ---
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-insecure-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # --- Supabase ---
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    # --- Storage ---
    STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")  # "local" | "supabase"
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
    PROOF_BUCKET = "proof-submissions"
    CERT_BUCKET = "certificates"
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}

    # --- Misc ---
    ENV = os.getenv("FLASK_ENV", "development")
    PORT = int(os.getenv("PORT", "5000"))
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", f"http://localhost:{os.getenv('PORT', '5000')}")
