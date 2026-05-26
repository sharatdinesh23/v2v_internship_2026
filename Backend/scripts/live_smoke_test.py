from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import app  # noqa: E402


def _env_or_arg(value: str | None, env_key: str) -> str | None:
    return value or os.getenv(env_key)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a live Supabase-backed smoke test against the FastAPI app.")
    parser.add_argument("--teacher-email")
    parser.add_argument("--teacher-password")
    parser.add_argument("--admin-email")
    parser.add_argument("--admin-password")
    parser.add_argument("--internship-id")
    parser.add_argument("--origin", default="http://127.0.0.1:3000")
    return parser.parse_args()


def _expect(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def _json_or_text(response) -> Any:
    try:
        return response.json()
    except Exception:
        return response.text


def _request(
    client: TestClient,
    method: str,
    path: str,
    *,
    token: str | None = None,
    expected: int | None = None,
    expected_in: set[int] | None = None,
    **kwargs,
):
    headers = dict(kwargs.pop("headers", {}))
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = client.request(method, path, headers=headers, **kwargs)
    if expected is not None and response.status_code != expected:
        raise AssertionError(f"{method} {path} returned {response.status_code}, expected {expected}: {_json_or_text(response)}")
    if expected_in is not None and response.status_code not in expected_in:
        raise AssertionError(
            f"{method} {path} returned {response.status_code}, expected one of {sorted(expected_in)}: {_json_or_text(response)}"
        )
    return response, _json_or_text(response)


def _login(client: TestClient, email: str, password: str) -> dict[str, Any]:
    response, payload = _request(
        client,
        "POST",
        "/api/auth/login",
        expected=200,
        json={"email": email, "password": password},
    )
    _expect(bool(payload.get("access_token")), f"Login for {email} did not return an access token.")
    return payload


def main():
    args = _parse_args()
    teacher_email = _env_or_arg(args.teacher_email, "INTEGRATION_TEACHER_EMAIL")
    teacher_password = _env_or_arg(args.teacher_password, "INTEGRATION_TEACHER_PASSWORD")
    admin_email = _env_or_arg(args.admin_email, "INTEGRATION_ADMIN_EMAIL")
    admin_password = _env_or_arg(args.admin_password, "INTEGRATION_ADMIN_PASSWORD")

    _expect(bool(teacher_email and teacher_password), "Teacher credentials are required.")
    _expect(bool(admin_email and admin_password), "Admin credentials are required.")

    student_email = f"integration.student.{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.{uuid4().hex[:6]}@example.com"
    student_password = "Integration123!"
    updated_student_password = "Integration123!Updated"
    student_name = "Integration Student"
    renamed_student_name = "Integration Student Updated"
    assignment_title = f"Integration Assignment {datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    attendance_date = (datetime.now(timezone.utc).date() + timedelta(days=90)).isoformat()

    summary: dict[str, Any] = {
        "student_email": student_email,
        "attendance_date": attendance_date,
    }

    with TestClient(app) as client:
        health_response, health_payload = _request(client, "GET", "/", expected=200)
        summary["health"] = health_payload

        cors_response, _ = _request(
            client,
            "OPTIONS",
            "/api/auth/login",
            expected_in={200, 204},
            headers={
                "Origin": args.origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )
        _expect(cors_response.headers.get("access-control-allow-origin") == args.origin, "Expected CORS origin was not allowed.")
        summary["cors_origin"] = cors_response.headers.get("access-control-allow-origin")

        unauthorized_response, _ = _request(client, "GET", "/api/users/profile", expected_in={401, 403})
        summary["unauthorized_profile_status"] = unauthorized_response.status_code

        teacher_login = _login(client, teacher_email, teacher_password)
        admin_login = _login(client, admin_email, admin_password)
        teacher_token = teacher_login["access_token"]
        admin_token = admin_login["access_token"]
        _expect(teacher_login["role"] == "teacher", "Teacher credentials did not log in as teacher.")
        _expect(admin_login["role"] == "admin", "Admin credentials did not log in as admin.")

        internships_response, internships = _request(client, "GET", "/api/system/internships/active", expected=200)
        _expect(bool(internships), "No active internships were returned.")
        internship_id = args.internship_id or teacher_login.get("internship_id") or internships[0]["id"]
        summary["internship_id"] = internship_id
        summary["active_internship_count"] = len(internships)

        register_response, register_payload = _request(
            client,
            "POST",
            "/api/auth/register",
            expected=201,
            json={
                "name": student_name,
                "email": student_email,
                "password": student_password,
                "internship_id": internship_id,
            },
        )
        summary["registered_student_id"] = register_payload["user_id"]

        student_login = _login(client, student_email, student_password)
        student_token = student_login["access_token"]
        _expect(student_login["role"] == "student", "Registered user did not log in as a student.")
        summary["student_initial_role"] = student_login["role"]

        profile_response, profile_payload = _request(client, "GET", "/api/users/profile", token=student_token, expected=200)
        _expect(profile_payload["internship_id"] == internship_id, "Student profile internship did not match the registered internship.")
        summary["student_profile_name"] = profile_payload["name"]

        _, updated_profile = _request(
            client,
            "PUT",
            "/api/users/profile",
            token=student_token,
            expected=200,
            json={"name": renamed_student_name},
        )
        _expect(updated_profile["name"] == renamed_student_name, "Profile update did not persist the new name.")
        summary["student_profile_updated"] = updated_profile["name"]

        _request(
            client,
            "PUT",
            "/api/users/password",
            token=student_token,
            expected=200,
            json={"current_password": student_password, "new_password": updated_student_password},
        )

        student_login = _login(client, student_email, updated_student_password)
        student_token = student_login["access_token"]
        summary["student_password_relogin"] = "ok"

        due_date = (datetime.now(timezone.utc) + timedelta(days=7)).replace(microsecond=0).isoformat()
        _, assignment_payload = _request(
            client,
            "POST",
            "/api/assignments/",
            token=teacher_token,
            expected=201,
            json={
                "internship_id": internship_id,
                "title": assignment_title,
                "description": "This assignment is created by the live smoke test to verify teacher flows.",
                "doc_link": "https://github.com/sharatdinesh23/InternPortal",
                "due_date": due_date,
            },
        )
        assignment_id = assignment_payload["id"]
        summary["assignment_id"] = assignment_id

        _, student_assignments = _request(client, "GET", "/api/assignments/", token=student_token, expected=200)
        _expect(any(item["id"] == assignment_id for item in student_assignments), "Student assignments did not include the teacher-created assignment.")
        summary["student_assignment_count"] = len(student_assignments)

        student_forbidden_assignment, _ = _request(
            client,
            "POST",
            "/api/assignments/",
            token=student_token,
            expected=403,
            json={
                "internship_id": internship_id,
                "title": "Student Should Not Create This",
                "description": "Students should not be able to create assignments through the protected route.",
                "doc_link": None,
                "due_date": due_date,
            },
        )
        summary["student_create_assignment_status"] = student_forbidden_assignment.status_code

        _, submission_payload = _request(
            client,
            "POST",
            "/api/submissions/",
            token=student_token,
            expected=201,
            json={
                "assignment_id": assignment_id,
                "repo_link": f"https://github.com/example/{uuid4().hex}",
            },
        )
        submission_id = submission_payload["id"]
        summary["submission_id"] = submission_id

        resubmission_response, resubmission_payload = _request(
            client,
            "POST",
            "/api/submissions/",
            token=student_token,
            expected=201,
            json={
                "assignment_id": assignment_id,
                "repo_link": f"https://github.com/example/{uuid4().hex}",
            },
        )
        _expect(resubmission_payload["id"] == submission_id, "Ungraded resubmission should update the existing submission record.")
        summary["resubmission_status"] = resubmission_response.status_code
        summary["resubmission_id"] = resubmission_payload["id"]

        _, teacher_students = _request(client, "GET", "/api/users/students", token=teacher_token, expected=200)
        _expect(any(student["email"] == student_email for student in teacher_students), "Teacher student list did not include the newly registered student.")
        summary["teacher_student_count"] = len(teacher_students)

        _, submissions_for_assignment = _request(
            client,
            "GET",
            f"/api/submissions/assignment/{assignment_id}",
            token=teacher_token,
            expected=200,
        )
        _expect(any(item["id"] == submission_id for item in submissions_for_assignment), "Teacher submission review list did not include the student's submission.")

        _, graded_submission = _request(
            client,
            "PUT",
            f"/api/submissions/{submission_id}/grade",
            token=teacher_token,
            expected=200,
            json={"grade": "A", "feedback": "Excellent repository hygiene."},
        )
        _expect(graded_submission["status"] == "Graded", "Teacher grading did not mark the submission as graded.")

        blocked_resubmission_response, blocked_resubmission_payload = _request(
            client,
            "POST",
            "/api/submissions/",
            token=student_token,
            expected=409,
            json={
                "assignment_id": assignment_id,
                "repo_link": f"https://github.com/example/{uuid4().hex}",
            },
        )
        summary["blocked_resubmission_status"] = blocked_resubmission_response.status_code
        summary["blocked_resubmission_detail"] = blocked_resubmission_payload.get("detail")

        _, student_history = _request(client, "GET", "/api/submissions/student", token=student_token, expected=200)
        matching_history = next((item for item in student_history if item["id"] == submission_id), None)
        _expect(matching_history is not None, "Student history did not include the created submission.")
        _expect(matching_history["status"] == "Graded", "Student history did not reflect the graded submission.")

        _, teacher_dashboard = _request(client, "GET", "/api/analytics/dashboard", token=teacher_token, expected=200)
        _expect(teacher_dashboard["total_assignments"] >= 1, "Teacher analytics did not count the created assignment.")
        _expect(teacher_dashboard["total_students"] >= 1, "Teacher analytics did not count the registered student.")
        _expect(teacher_dashboard["total_submissions"] >= 1, "Teacher analytics did not count the student submission.")
        summary["teacher_dashboard"] = teacher_dashboard

        _, admin_dashboard = _request(
            client,
            "GET",
            "/api/analytics/dashboard",
            token=admin_token,
            expected=200,
            params={"internship_id": internship_id},
        )
        _expect(admin_dashboard["total_assignments"] >= 1, "Admin analytics did not count the internship assignment.")
        summary["admin_dashboard"] = admin_dashboard

        _, attendance_payload = _request(
            client,
            "POST",
            "/api/attendance/",
            token=teacher_token,
            expected=201,
            json={
                "date": attendance_date,
                "records": [{"student_id": summary["registered_student_id"], "status": "Present"}],
            },
        )
        summary["attendance_message"] = attendance_payload["message"]

        duplicate_attendance_response, duplicate_attendance_payload = _request(
            client,
            "POST",
            "/api/attendance/",
            token=teacher_token,
            expected=409,
            json={
                "date": attendance_date,
                "records": [{"student_id": summary["registered_student_id"], "status": "Present"}],
            },
        )
        summary["duplicate_attendance_status"] = duplicate_attendance_response.status_code
        summary["duplicate_attendance_detail"] = duplicate_attendance_payload.get("detail")

        _, attendance_summary = _request(
            client,
            "GET",
            "/api/attendance/summary",
            token=teacher_token,
            expected=200,
            params={"date_from": attendance_date, "date_to": attendance_date},
        )
        student_summary = next((row for row in attendance_summary["records"] if row["student_id"] == summary["registered_student_id"]), None)
        _expect(student_summary is not None, "Attendance summary did not include the registered student.")
        _expect(student_summary["present"] >= 1, "Attendance summary did not count the recorded present day.")
        summary["attendance_summary"] = student_summary

        student_forbidden_students, _ = _request(client, "GET", "/api/users/students", token=student_token, expected=403)
        teacher_forbidden_admin, _ = _request(client, "GET", "/api/system/teachers", token=teacher_token, expected=403)
        summary["student_forbidden_students_status"] = student_forbidden_students.status_code
        summary["teacher_forbidden_admin_status"] = teacher_forbidden_admin.status_code

        _, admin_teachers = _request(client, "GET", "/api/system/teachers", token=admin_token, expected=200)
        _, admin_internships = _request(client, "GET", "/api/system/internships", token=admin_token, expected=200)
        _expect(any(row["id"] == internship_id for row in admin_internships), "Admin internship list did not include the tested internship.")
        summary["admin_teacher_count"] = len(admin_teachers)
        summary["admin_internship_count"] = len(admin_internships)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
