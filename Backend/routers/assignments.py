from fastapi import APIRouter, Depends, HTTPException

from core.security import verify_supabase_jwt, verify_teacher_or_admin
from database import supabase
from schemas.core import AssignmentCreate

router = APIRouter(prefix="/api/assignments", tags=["Assignments"])


@router.post("/", status_code=201)
async def create_assignment(
    assignment: AssignmentCreate,
    auth_data: dict = Depends(verify_teacher_or_admin),
):
    try:
        payload = assignment.model_dump()
        if auth_data["role"] == "teacher":
            if not auth_data["internship_id"]:
                raise HTTPException(status_code=400, detail="Teacher is not assigned to an internship.")
            payload["internship_id"] = str(auth_data["internship_id"])
        else:
            payload["internship_id"] = str(payload["internship_id"])

        payload["created_by"] = auth_data["user"]["id"]
        payload["due_date"] = payload["due_date"].isoformat()

        res = supabase.table("Assignments").insert(payload).execute()
        if not res.data:
            raise HTTPException(status_code=400, detail="Failed writing assignments.")
        return res.data[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/", status_code=200)
async def get_assignments(auth_data: dict = Depends(verify_supabase_jwt)):
    try:
        query = supabase.table("Assignments").select("*, Internships(name)").order("due_date", desc=False)
        if auth_data["role"] != "admin":
            if not auth_data["internship_id"]:
                return []
            query = query.eq("internship_id", auth_data["internship_id"])

        res = query.execute()
        return res.data
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
