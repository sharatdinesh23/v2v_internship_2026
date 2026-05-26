from typing import Any
import jwt
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import supabase, JWT_SECRET

limiter = Limiter(key_func=get_remote_address)
security = HTTPBearer()

def create_jwt(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def _relation_to_dict(value: Any) -> dict:
    if isinstance(value, list):
        return value[0] if value else {}
    return value or {}


def get_profile_context(user_id: str) -> dict:
    profile_res = (
        supabase.table("Profiles")
        .select("id, name, email, role_id, internship_id, created_at, Roles(role_name), Internships(name)")
        .eq("id", user_id)
        .execute()
    )
    row = profile_res.data[0] if profile_res.data else {}
    role_data = _relation_to_dict(row.get("Roles"))
    internship_data = _relation_to_dict(row.get("Internships"))
    return {
        "id": row.get("id", user_id),
        "name": row.get("name", ""),
        "email": row.get("email", ""),
        "role_id": row.get("role_id"),
        "role": role_data.get("role_name", ""),
        "internship_id": row.get("internship_id"),
        "internship_name": internship_data.get("name", ""),
        "created_at": row.get("created_at"),
    }


async def verify_supabase_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Decode the JWT and attach profile context."""
    from core.background import ACTIVE_SESSIONS, update_user_session_cache
    import asyncio
    
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject.")

        # Performance optimization: check background cache first
        if user_id in ACTIVE_SESSIONS:
            profile = ACTIVE_SESSIONS[user_id]["metadata"]
        else:
            profile = get_profile_context(user_id)
            if not profile or not profile.get("id"):
                raise HTTPException(status_code=401, detail="User profile not found.")
            # Seed the background cache with the verified user
            # We must use the current running loop
            loop = asyncio.get_running_loop()
            loop.create_task(update_user_session_cache(user_id, profile))

        return {
            "user": {"id": user_id, "email": payload.get("email")}, # mocked object that has what functions expect
            "token": token,
            "role": profile["role"],
            "internship_id": profile["internship_id"],
            "profile": profile,
        }
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Authentication Denied: Session Invalidated (Expired).") from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=f"Authentication Denied: Invalid Token.") from exc
    except HTTPException:
        raise
    except Exception as exc:
        print(f"🔥 SECURITY EXCEPTION: {str(exc)}")
        raise HTTPException(status_code=500, detail=f"Internal Security Verification Error: {str(exc)}") from exc


def verify_teacher_or_admin(auth_data: dict = Depends(verify_supabase_jwt)):
    """Require teacher or admin privileges."""
    if auth_data["role"] not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Action Requires Teacher or Admin Authority.")
    return auth_data


def verify_admin(auth_data: dict = Depends(verify_supabase_jwt)):
    """Require admin privileges."""
    if auth_data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Action strict natively requires Admin Authority.")
    return auth_data


def verify_student(auth_data: dict = Depends(verify_supabase_jwt)):
    """Require student privileges."""
    if auth_data["role"] != "student":
        raise HTTPException(status_code=403, detail="Forbidden: Action requires Student authority.")
    return auth_data
