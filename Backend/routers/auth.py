from functools import lru_cache
import uuid
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from fastapi import APIRouter, HTTPException

from core.security import get_profile_context, create_jwt
from database import supabase
from schemas.core import UserLogin, UserRegister

ph = PasswordHasher()

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@lru_cache(maxsize=8)
def _get_role_id(role_name: str) -> str:
    role_res = supabase.table("Roles").select("id").eq("role_name", role_name).limit(1).execute()
    if not role_res.data:
        raise HTTPException(status_code=500, detail=f"System role '{role_name}' is not configured.")
    return role_res.data[0]["id"]


@router.post("/register", status_code=201)
async def register_user(user: UserRegister):
    try:
        student_role_id = _get_role_id("student")
        
        # Check if user already exists
        existing = supabase.table("Profiles").select("id").eq("email", user.email).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="User with this email already exists.")
            
        hashed_password = ph.hash(user.password)
        new_id = str(uuid.uuid4())
        
        insert_res = supabase.table("Profiles").insert(
            {
                "id": new_id,
                "name": user.name,
                "email": user.email,
                "password": hashed_password,
                "role_id": student_role_id,
                "internship_id": str(user.internship_id) if user.internship_id else None,
            }
        ).execute()

        if not insert_res.data:
            raise HTTPException(status_code=400, detail="Registration instantiation failed.")

        return {
            "message": "Student registered successfully.",
            "user_id": new_id,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/login", status_code=200)
async def login_user(user: UserLogin):
    try:
        user_res = supabase.table("Profiles").select("*").eq("email", user.email).execute()
        if not user_res.data:
            raise HTTPException(status_code=401, detail="Invalid authorization credentials parsed.")
            
        user_record = user_res.data[0]
        db_password = user_record.get("password")
        if not db_password:
             raise HTTPException(status_code=401, detail="Invalid authorization credentials parsed. (Account password missing)")
             
        try:
            ph.verify(db_password, user.password)
        except VerifyMismatchError:
            raise HTTPException(status_code=401, detail="Invalid authorization credentials parsed.")
            
        if ph.check_needs_rehash(db_password):
            new_hash = ph.hash(user.password)
            supabase.table("Profiles").update({"password": new_hash}).eq("id", user_record["id"]).execute()

        access_token = create_jwt(user_record["id"], user_record["email"])
        profile = get_profile_context(user_record["id"])

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_record["id"],
                "email": user_record["email"],
                "name": profile["name"],
            },
            "role": profile["role"] or "student",
            "internship_id": profile["internship_id"],
            "internship_name": profile["internship_name"],
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Authentication Failed: {str(exc)}") from exc
