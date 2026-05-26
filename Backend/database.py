import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv(Path(__file__).resolve().parent / ".env")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ADMIN_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ADMIN_KEY")
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN")
JWT_SECRET = os.environ.get("JWT_SECRET", "default-insecure-secret-key-please-change")

def _looks_like_service_role_key(value: str | None) -> bool:
    if not value:
        return False
    lowered = value.lower()
    return "service_role" in lowered or "sb_secret_" in lowered


if not SUPABASE_SERVICE_ROLE_KEY and _looks_like_service_role_key(SUPABASE_KEY):
    SUPABASE_SERVICE_ROLE_KEY = SUPABASE_KEY

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or a Supabase key in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase_admin: Client | None = (
    create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY) if SUPABASE_SERVICE_ROLE_KEY else None
)
