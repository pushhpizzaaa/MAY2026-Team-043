"""Pluggable file-storage adapter.

Exposes a single `storage` object with `save(bucket, filename, data, content_type)`
returning a publicly reachable URL, plus `public_url(bucket, path)`.

Two backends, selected by the STORAGE_BACKEND env var:
  - LocalStorage    : writes to backend/uploads/<bucket>/, served by Flask (default)
  - SupabaseStorage : pushes to Supabase Storage buckets (production / PRD target)

The rest of the app depends only on this interface, so switching backends is a
one-line env change with no code impact.
"""
import os
import uuid
from abc import ABC, abstractmethod

from flask import current_app


def unique_filename(original: str) -> str:
    ext = os.path.splitext(original)[1].lower() or ".bin"
    return f"{uuid.uuid4().hex}{ext}"


class StorageBackend(ABC):
    @abstractmethod
    def save(self, bucket: str, filename: str, data: bytes, content_type: str) -> str:
        """Persist bytes and return a URL/path stored in the DB."""

    @abstractmethod
    def public_url(self, bucket: str, path: str) -> str:
        """Resolve a stored path to a reachable URL (may be signed)."""


class LocalStorage(StorageBackend):
    """Saves under backend/uploads/<bucket>/ and serves via the /uploads route."""

    def __init__(self, upload_dir: str, base_url: str):
        self.upload_dir = upload_dir
        self.base_url = base_url.rstrip("/")

    def _bucket_dir(self, bucket: str) -> str:
        path = os.path.join(self.upload_dir, bucket)
        os.makedirs(path, exist_ok=True)
        return path

    def save(self, bucket: str, filename: str, data: bytes, content_type: str) -> str:
        dest = os.path.join(self._bucket_dir(bucket), filename)
        with open(dest, "wb") as f:
            f.write(data)
        # Store a relative path; public_url turns it into a full URL.
        return f"{bucket}/{filename}"

    def public_url(self, bucket: str, path: str) -> str:
        # `path` already looks like "<bucket>/<filename>".
        return f"{self.base_url}/uploads/{path}"


class SupabaseStorage(StorageBackend):
    """Pushes files to Supabase Storage buckets using the service-role client."""

    def __init__(self, url: str, service_key: str):
        # Imported lazily so local-only setups don't need the supabase package.
        from supabase import create_client

        self.client = create_client(url, service_key)

    def save(self, bucket: str, filename: str, data: bytes, content_type: str) -> str:
        self.client.storage.from_(bucket).upload(
            path=filename,
            file=data,
            file_options={"content-type": content_type, "upsert": "true"},
        )
        return f"{bucket}/{filename}"

    def public_url(self, bucket: str, path: str) -> str:
        # path is "<bucket>/<filename>"; strip the bucket prefix for the SDK call.
        object_path = path.split("/", 1)[1] if "/" in path else path
        try:
            signed = self.client.storage.from_(bucket).create_signed_url(object_path, 3600)
            return signed.get("signedURL") or signed.get("signedUrl")
        except Exception:
            return self.client.storage.from_(bucket).get_public_url(object_path)


class StorageProxy:
    """Lazily builds the configured backend on first use (needs app context)."""

    _backend: StorageBackend | None = None

    def _resolve(self) -> StorageBackend:
        if self._backend is not None:
            return self._backend
        cfg = current_app.config
        if cfg["STORAGE_BACKEND"] == "supabase" and cfg["SUPABASE_URL"]:
            self._backend = SupabaseStorage(
                cfg["SUPABASE_URL"], cfg["SUPABASE_SERVICE_ROLE_KEY"]
            )
        else:
            self._backend = LocalStorage(cfg["UPLOAD_DIR"], cfg["PUBLIC_BASE_URL"])
        return self._backend

    def save(self, bucket, filename, data, content_type):
        return self._resolve().save(bucket, filename, data, content_type)

    def public_url(self, bucket, path):
        return self._resolve().public_url(bucket, path)


storage = StorageProxy()
