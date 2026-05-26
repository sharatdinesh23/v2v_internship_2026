from functools import lru_cache

import httpx
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, Depends, HTTPException, Query

from core.security import get_profile_context, verify_supabase_jwt, verify_teacher_or_admin
from database import SUPABASE_KEY, SUPABASE_URL, supabase
from schemas.core import PasswordUpdate, ProfileUpdate

router = APIRouter(prefix="/api/users", tags=["Users"])
ph = PasswordHasher()


@lru_cache(maxsize=8)
def _get_role_id(role_name: str) -> str | None:
    role_res = supabase.table("Roles").select("id").eq("role_name", role_name).limit(1).execute()
    return role_res.data[0]["id"] if role_res.data else None


@lru_cache(maxsize=1)
def _profiles_has_college_name() -> bool:
    try:
        supabase.table("Profiles").select("college_name").limit(1).execute()
        return True
    except Exception:
        return False


@router.get("/profile", status_code=200)
async def get_profile(auth_data: dict = Depends(verify_supabase_jwt)):
    profile = auth_data["profile"]
    return {
        "id": profile["id"],
        "name": profile["name"],
        "email": profile["email"] or auth_data["user"]["email"],
        "role": profile["role"],
        "role_id": profile["role_id"],
        "internship_id": profile["internship_id"],
        "internship_name": profile["internship_name"],
        "created_at": profile["created_at"],
    }


@router.put("/profile", status_code=200)
async def update_profile(
    payload: ProfileUpdate,
    auth_data: dict = Depends(verify_supabase_jwt),
):
    try:
        user_id = auth_data["user"]["id"]
        update_data = {"name": payload.name}
        if payload.internship_id:
            update_data["internship_id"] = str(payload.internship_id)
        
        res = supabase.table("Profiles").update(update_data).eq("id", user_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Profile not found.")

        if SUPABASE_URL and SUPABASE_KEY:
            try:
                async with httpx.AsyncClient(timeout=20.0, trust_env=False) as client:
                    await client.put(
                        f"{SUPABASE_URL}/auth/v1/user",
                        headers={
                            "apikey": SUPABASE_KEY,
                            "Authorization": f"Bearer {auth_data['token']}",
                            "Content-Type": "application/json",
                        },
                        json={"data": {"name": payload.name}},
                    )
            except Exception:
                pass

        return get_profile_context(user_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/password", status_code=200)
async def update_password(
    payload: PasswordUpdate,
    auth_data: dict = Depends(verify_supabase_jwt),
):
    try:
        if payload.current_password == payload.new_password:
            raise HTTPException(status_code=400, detail="New password must be different from the current password.")

        user_id = auth_data["user"]["id"]
        
        # 1. Fetch the user's current hashed password from the database
        user_res = supabase.table("Profiles").select("password").eq("id", user_id).execute()
        if not user_res.data:
            raise HTTPException(status_code=404, detail="User profile not found.")
            
        db_password = user_res.data[0].get("password")
        if not db_password:
             raise HTTPException(status_code=400, detail="Current password state is invalid in database.")

        # 2. Verify current password
        try:
            ph.verify(db_password, payload.current_password)
        except VerifyMismatchError:
            raise HTTPException(status_code=401, detail="Current password is incorrect.")

        # 3. Hash and Update
        new_hashed_password = ph.hash(payload.new_password)
        update_res = supabase.table("Profiles").update({"password": new_hashed_password}).eq("id", user_id).execute()
        
        if not update_res.data:
            raise HTTPException(status_code=500, detail="Failed to update password in database.")

        return {"message": "Password updated successfully."}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/students", status_code=200)
async def get_students(
    internship_id: str | None = Query(default=None),
    auth_data: dict = Depends(verify_teacher_or_admin),
):
    try:
        student_role_id = _get_role_id("student")
        if not student_role_id:
            return []

        effective_internship_id = auth_data["internship_id"] if auth_data["role"] == "teacher" else internship_id
        query = (
            supabase.table("Profiles")
            .select(
                "id, name, email, internship_id, Internships(name)"
                + (", college_name" if _profiles_has_college_name() else "")
            )
            .eq("role_id", student_role_id)
            .order("name")
        )
        if effective_internship_id:
            query = query.eq("internship_id", effective_internship_id)
        elif auth_data["role"] == "teacher":
            return []

        rows = query.execute().data or []
        students = []
        for row in rows:
            internship = row.get("Internships") or {}
            if isinstance(internship, list):
                internship = internship[0] if internship else {}
            students.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "email": row["email"],
                    "college_name": row.get("college_name", ""),
                    "internship_id": row.get("internship_id"),
                    "internship_name": internship.get("name", ""),
                }
            )
        return students
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
