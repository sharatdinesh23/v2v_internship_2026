from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Query

from core.security import verify_teacher_or_admin
from database import supabase

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@lru_cache(maxsize=8)
def _get_role_id(role_name: str) -> str | None:
    role_res = supabase.table("Roles").select("id").eq("role_name", role_name).limit(1).execute()
    return role_res.data[0]["id"] if role_res.data else None


@router.get("/dashboard", status_code=200)
async def get_dashboard_analytics(
    internship_id: str | None = Query(default=None),
    auth_data: dict = Depends(verify_teacher_or_admin),
):
    try:
        effective_internship_id = auth_data["internship_id"] if auth_data["role"] == "teacher" else internship_id

        assignment_query = supabase.table("Assignments").select("id, internship_id")
        if effective_internship_id:
            assignment_query = assignment_query.eq("internship_id", effective_internship_id)
        elif auth_data["role"] == "teacher":
            return {
                "total_assignments": 0,
                "total_students": 0,
                "total_submissions": 0,
                "on_time_count": 0,
                "late_count": 0,
                "pending_reviews": 0,
            }
        assignments = assignment_query.execute().data or []
        assignment_ids = [row["id"] for row in assignments]

        student_role_id = _get_role_id("student")
        student_query = supabase.table("Profiles").select("id").eq("role_id", student_role_id)
        if effective_internship_id:
            student_query = student_query.eq("internship_id", effective_internship_id)
        students = student_query.execute().data or []

        submissions = []
        if assignment_ids:
            submissions = supabase.table("Submissions").select("id, status").in_("assignment_id", assignment_ids).execute().data or []
        elif not effective_internship_id:
            submissions = supabase.table("Submissions").select("id, status").execute().data or []

        return {
            "total_assignments": len(assignments),
            "total_students": len(students),
            "total_submissions": len(submissions),
            "on_time_count": sum(1 for row in submissions if row.get("status") != "Late"),
            "late_count": sum(1 for row in submissions if row.get("status") == "Late"),
            "pending_reviews": sum(1 for row in submissions if row.get("status") != "Graded"),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
