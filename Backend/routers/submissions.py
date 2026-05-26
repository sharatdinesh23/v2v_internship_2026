from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from core.security import verify_student, verify_teacher_or_admin
from database import supabase
from schemas.core import GradeUpdate, SubmissionCreate, SubmissionStatus

router = APIRouter(prefix="/api/submissions", tags=["Submissions"])


def _normalize_repo_link(value: str | None) -> str:
    if not value:
        return ""

    link = value.strip()
    if not link:
        return ""

    if link.startswith(("http://", "https://", "mailto:", "tel:")):
        return link
    if link.startswith("//"):
        return f"https:{link}"
    return f"https://{link}"


def _get_assignment(assignment_id: str) -> dict | None:
    assignment_res = (
        supabase.table("Assignments")
        .select("id, title, due_date, internship_id")
        .eq("id", assignment_id)
        .limit(1)
        .execute()
    )
    return assignment_res.data[0] if assignment_res.data else None


def _ensure_assignment_scope(assignment: dict, auth_data: dict):
    if auth_data["role"] == "teacher" and assignment["internship_id"] != auth_data["internship_id"]:
        raise HTTPException(status_code=403, detail="Teacher cannot access submissions outside their internship.")


def _is_graded_submission(submission: dict) -> bool:
    grade = submission.get("grade")
    return submission.get("status") == SubmissionStatus.GRADED.value or grade not in (None, "", "-")


@router.post("/", status_code=201)
async def create_submission(
    sub: SubmissionCreate,
    auth_data: dict = Depends(verify_student),
):
    try:
        assignment_id = str(sub.assignment_id)
        assignment = _get_assignment(assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="Target Assignment configuration mismatch.")

        if auth_data["internship_id"] and assignment["internship_id"] != auth_data["internship_id"]:
            raise HTTPException(status_code=403, detail="Assignment does not belong to the student's internship.")

        existing_submissions = (
            supabase.table("Submissions")
            .select("id, status, grade")
            .eq("assignment_id", assignment_id)
            .eq("student_id", auth_data["user"]["id"])
            .order("submitted_at", desc=True)
            .execute()
        ).data or []

        due_date = datetime.fromisoformat(assignment["due_date"].replace("Z", "+00:00"))
        status = SubmissionStatus.LATE if datetime.now(timezone.utc) > due_date else SubmissionStatus.PENDING
        repo_link = _normalize_repo_link(sub.repo_link)
        submitted_at = datetime.now(timezone.utc).isoformat()

        if existing_submissions:
            if any(_is_graded_submission(submission) for submission in existing_submissions):
                raise HTTPException(status_code=409, detail="This assignment has already been graded and cannot be resubmitted.")

            current_submission = existing_submissions[0]
            res = (
                supabase.table("Submissions")
                .update(
                    {
                        "repo_link": repo_link,
                        "status": status.value,
                        "grade": None,
                        "submitted_at": submitted_at,
                    }
                )
                .eq("id", current_submission["id"])
                .execute()
            )
        else:
            payload = {
                "assignment_id": assignment_id,
                "student_id": auth_data["user"]["id"],
                "repo_link": repo_link,
                "status": status.value,
                "submitted_at": submitted_at,
            }
            res = supabase.table("Submissions").insert(payload).execute()

        if not res.data:
            raise HTTPException(status_code=400, detail="Submission could not be created.")
        return {**res.data[0], "repo_link": _normalize_repo_link(res.data[0].get("repo_link"))}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{submission_id}/grade", status_code=200)
async def grade_submission(
    submission_id: str,
    grade_data: GradeUpdate,
    auth_data: dict = Depends(verify_teacher_or_admin),
):
    try:
        submission_res = (
            supabase.table("Submissions")
            .select("id, assignment_id")
            .eq("id", submission_id)
            .limit(1)
            .execute()
        )
        if not submission_res.data:
            raise HTTPException(status_code=404, detail="Submission not found.")

        assignment = _get_assignment(submission_res.data[0]["assignment_id"])
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found for submission.")
        _ensure_assignment_scope(assignment, auth_data)

        res = (
            supabase.table("Submissions")
            .update({"grade": grade_data.grade, "status": SubmissionStatus.GRADED.value})
            .eq("id", submission_id)
            .execute()
        )
        if not res.data:
            raise HTTPException(status_code=404, detail="Execution updating failed natively.")
        return {**res.data[0], "repo_link": _normalize_repo_link(res.data[0].get("repo_link"))}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/assignment/{assignment_id}", status_code=200)
async def get_submissions_for_assignment(
    assignment_id: str,
    auth_data: dict = Depends(verify_teacher_or_admin),
):
    try:
        assignment = _get_assignment(assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found.")
        _ensure_assignment_scope(assignment, auth_data)

        res = (
            supabase.table("Submissions")
            .select("*, Profiles(name, email), Assignments(title, due_date)")
            .eq("assignment_id", assignment_id)
            .order("submitted_at", desc=True)
            .execute()
        )
        return [{**row, "repo_link": _normalize_repo_link(row.get("repo_link"))} for row in (res.data or [])]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/student", status_code=200)
async def get_my_submissions(auth_data: dict = Depends(verify_student)):
    try:
        res = (
            supabase.table("Submissions")
            .select("*, Assignments(title, due_date)")
            .eq("student_id", auth_data["user"]["id"])
            .order("submitted_at", desc=True)
            .execute()
        )
        return [{**row, "repo_link": _normalize_repo_link(row.get("repo_link"))} for row in (res.data or [])]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
