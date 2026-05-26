from functools import lru_cache
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query

from core.security import verify_supabase_jwt, verify_teacher_or_admin
from database import supabase
from schemas.core import AttendanceBatch

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@lru_cache(maxsize=8)
def _get_role_id(role_name: str) -> str | None:
    role_res = supabase.table("Roles").select("id").eq("role_name", role_name).limit(1).execute()
    return role_res.data[0]["id"] if role_res.data else None


def _get_students_for_scope(auth_data: dict, internship_id: str | None = None) -> list[dict]:
    effective_internship_id = auth_data["internship_id"] if auth_data["role"] == "teacher" else internship_id
    student_role_id = _get_role_id("student")
    if not student_role_id:
        return []

    query = supabase.table("Profiles").select("id, name, email, internship_id").eq("role_id", student_role_id)
    if effective_internship_id:
        query = query.eq("internship_id", effective_internship_id)
    elif auth_data["role"] == "teacher":
        return []
    return query.order("name").execute().data or []


def _build_summary(students: list[dict], attendance_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    summary = {
        student["id"]: {
            "student_id": student["id"],
            "name": student["name"],
            "email": student.get("email", ""),
            "present": 0,
            "absent": 0,
            "late": 0,
        }
        for student in students
    }
    chart_map = defaultdict(lambda: {"present": 0, "absent": 0, "late": 0})

    for row in attendance_rows:
        student_summary = summary.get(row["student_id"])
        if not student_summary:
            continue
        if row["status"] == "Present":
            student_summary["present"] += 1
            chart_map[row["date"]]["present"] += 1
        elif row["status"] == "Absent":
            student_summary["absent"] += 1
            chart_map[row["date"]]["absent"] += 1
        else:
            student_summary["late"] += 1
            chart_map[row["date"]]["late"] += 1

    records = []
    for item in summary.values():
        total_days = item["present"] + item["absent"] + item["late"]
        attendance_pct = round(((item["present"] + item["late"]) / total_days) * 100, 2) if total_days else 0.0
        records.append(
            {
                **item,
                "attendance_pct": attendance_pct,
                "status": "Good" if attendance_pct >= 75 else "At Risk",
            }
        )

    chart = [{"date": date_key, **counts} for date_key, counts in sorted(chart_map.items())]
    return records, chart


@router.post("/", status_code=201)
async def log_batch_attendance(
    batch: AttendanceBatch,
    auth_data: dict = Depends(verify_teacher_or_admin),
):
    try:
        if not batch.records:
            raise HTTPException(status_code=400, detail="At least one attendance record is required.")

        allowed_student_ids = {student["id"] for student in _get_students_for_scope(auth_data)}
        if auth_data["role"] == "teacher":
            for rec in batch.records:
                if str(rec.student_id) not in allowed_student_ids:
                    raise HTTPException(status_code=403, detail="Teacher can only log attendance for their internship students.")

        student_ids = [str(rec.student_id) for rec in batch.records]
        if len(student_ids) != len(set(student_ids)):
            raise HTTPException(status_code=400, detail="Duplicate students were included in the attendance batch.")

        existing_records = (
            supabase.table("Attendance")
            .select("student_id")
            .eq("date", batch.date)
            .in_("student_id", student_ids)
            .execute()
        )
        if existing_records.data:
            raise HTTPException(status_code=409, detail="Attendance has already been logged for one or more selected students on this date.")

        records_to_insert = [
            {
                "student_id": str(rec.student_id),
                "date": batch.date,
                "status": rec.status,
                        "recorded_by": auth_data["user"]["id"],
            }
            for rec in batch.records
        ]

        res = supabase.table("Attendance").insert(records_to_insert).execute()
        return {"message": f"Successfully mapped {len(res.data)} attendance records."}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/summary", status_code=200)
async def get_attendance_summary(
    internship_id: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    auth_data: dict = Depends(verify_supabase_jwt),
):
    try:
        if auth_data["role"] == "student":
            if not auth_data["internship_id"]:
                return {"records": [], "chart": []}

            student = {
                "id": auth_data["user"]["id"],
                "name": auth_data["profile"].get("name", ""),
                "email": auth_data["profile"].get("email", ""),
            }
            attendance_query = (
                supabase.table("Attendance")
                .select("student_id, date, status")
                .eq("student_id", student["id"])
                .order("date", desc=False)
            )
            if date_from:
                attendance_query = attendance_query.gte("date", date_from)
            if date_to:
                attendance_query = attendance_query.lte("date", date_to)
            attendance_rows = attendance_query.execute().data or []
            records, chart = _build_summary([student], attendance_rows)
            return {"records": records, "chart": chart}

        students = _get_students_for_scope(auth_data, internship_id)
        if not students:
            return {"records": [], "chart": []}

        student_ids = [student["id"] for student in students]
        query = supabase.table("Attendance").select("student_id, date, status").in_("student_id", student_ids).order("date", desc=False)
        if date_from:
            query = query.gte("date", date_from)
        if date_to:
            query = query.lte("date", date_to)
        attendance_rows = query.execute().data or []
        records, chart = _build_summary(students, attendance_rows)
        return {"records": records, "chart": chart}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
