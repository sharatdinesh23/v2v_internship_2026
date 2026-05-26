import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List

import httpx
import reflex as rx


def _relation_to_dict(value: Any) -> dict:
    if isinstance(value, list):
        return value[0] if value else {}
    return value or {}


def _format_datetime(value: str | None) -> str:
    if not value:
        return "N/A"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y, %I:%M %p")
    except ValueError:
        return value


def _format_date(value: str | None) -> str:
    if not value:
        return "N/A"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y")
    except ValueError:
        return value


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _normalize_external_url(value: str | None) -> str:
    if not value:
        return ""

    url = value.strip()
    if not url:
        return ""

    if url.startswith(("http://", "https://", "mailto:", "tel:")):
        return url
    if url.startswith("//"):
        return f"https:{url}"
    return f"https://{url}"


def _detail_from_payload(payload: Any, fallback: str) -> str:
    if isinstance(payload, dict):
        return payload.get("detail") or payload.get("message") or payload.get("error") or fallback
    if isinstance(payload, str) and payload:
        return payload
    return fallback


async def api_request(
    base_url: str,
    method: str,
    path: str,
    *,
    token: str = "",
    json: dict | None = None,
    params: dict | None = None,
) -> Any:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
        response = await client.request(
            method,
            f"{base_url}{path}",
            headers=headers,
            json=json,
            params=params,
        )

    try:
        payload = response.json()
    except ValueError:
        payload = response.text

    if response.status_code >= 400:
        raise RuntimeError(_detail_from_payload(payload, response.text))
    return payload


def normalize_assignment(item: dict) -> dict:
    internship = _relation_to_dict(item.get("Internships"))
    return {
        **item,
        "internship_name": internship.get("name", ""),
        "due_date_display": _format_datetime(item.get("due_date")),
        "created_at_display": _format_datetime(item.get("created_at")),
    }


def normalize_submission(item: dict) -> dict:
    assignment = _relation_to_dict(item.get("Assignments"))
    profile = _relation_to_dict(item.get("Profiles"))
    repo_link = item.get("repo_link", "")
    grade = item.get("grade") or "-"
    return {
        **item,
        "assignment_title": assignment.get("title", "Unknown"),
        "assignment_name": assignment.get("title", "Unknown"),
        "assignment_due_date": assignment.get("due_date"),
        "assignment_due_date_display": _format_datetime(assignment.get("due_date")),
        "student_name": profile.get("name", ""),
        "student_email": profile.get("email", ""),
        "submitted_at_display": _format_datetime(item.get("submitted_at")),
        "repo_link": repo_link,
        "repo_link_url": _normalize_external_url(repo_link),
        "grade": grade,
        "is_graded": item.get("status") == "Graded" or grade not in {"", "-"},
    }


def normalize_internship(item: dict) -> dict:
    teachers = item.get("teachers") or []
    return {
        **item,
        "teacher_names": ", ".join(teacher["name"] for teacher in teachers) if teachers else "Unassigned",
        "teacher_ids": item.get("teacher_ids") or [],
    }


def normalize_teacher(item: dict) -> dict:
    internship = _relation_to_dict(item.get("Internships"))
    return {
        **item,
        "internship_name": internship.get("name", "Unassigned"),
    }


def normalize_note(item: dict) -> dict:
    internship = _relation_to_dict(item.get("Internships"))
    return {
        **item,
        "internship_name": internship.get("name", ""),
        "created_at_display": _format_datetime(item.get("created_at")),
    }


class AppState(rx.State):
    api_url: str = "http://127.0.0.1:8888"

    auth_token: str = rx.Cookie("")
    current_user_id: str = rx.Cookie("")
    current_role: str = rx.Cookie("")
    internship_id: str = rx.Cookie("")
    internship_name: str = rx.Cookie("")
    is_logged_in: bool = False

    selected_internship_id: str = ""
    selected_internship: str = "N/A"

    show_attendance_modal: bool = False
    show_code_review_modal: bool = False
    show_internship_modal: bool = False
    show_submission_modal: bool = False
    show_note_modal: bool = False
    selected_note: Dict[str, Any] = {}

    profile_name: str = ""
    profile_email: str = ""
    profile_phone: str = ""
    profile_dept: str = ""
    profile_program: str = ""
    profile_bio: str = ""
    profile_role_label: str = ""

    current_password: str = ""
    new_password: str = ""
    confirm_password: str = ""
    two_fa_enabled: bool = True

    teacher_assignments_total: int = 0
    teacher_students_total: int = 0
    teacher_submissions_total: int = 0
    teacher_on_time: int = 0
    admin_assignments_total: int = 0
    admin_students_total: int = 0
    admin_submissions_total: int = 0
    admin_on_time: int = 0
    student_attendance: int = 0
    student_total_submissions: int = 0
    student_on_time: int = 0
    student_late: int = 0

    editing_internship_id: str = ""
    new_internship_name: str = ""
    new_internship_desc: str = ""
    selected_teacher_ids: List[str] = []
    teacher_name_input: str = ""
    teacher_email_input: str = ""
    teacher_password_input: str = ""
    teacher_internship_id: str = ""
    student_name_input: str = ""
    student_email_input: str = ""
    student_password_input: str = ""
    student_college_input: str = ""
    student_internship_id: str = ""
    student_bulk_upload_summary: str = ""

    assignment_title_input: str = ""
    assignment_description_input: str = ""
    assignment_doc_link_input: str = ""
    assignment_due_date_input: str = ""
    assignment_internship_id: str = ""
    note_title_input: str = ""
    note_file_name_input: str = ""
    note_markdown_input: str = ""
    note_internship_id: str = ""
    editing_note_id: str = ""

    submission_assignment: str = ""
    submission_repo_link: str = ""
    submission_file_name: str = ""
    submission_modal_title: str = "Submit Assignment"
    submission_submit_label: str = "Submit Work"

    selected_assignment_id: str = ""
    selected_assignment_title: str = ""

    attendance_date: str = datetime.utcnow().date().isoformat()
    attendance_statuses: Dict[str, str] = {}

    metric_total_assignments: int = 0
    metric_total_students: int = 0
    metric_total_submissions: int = 0
    metric_on_time_count: int = 0
    metric_late_count: int = 0
    metric_pending_reviews: int = 0

    all_internships: List[Dict[str, Any]] = []
    active_internships: List[Dict[str, Any]] = []
    available_teachers: List[Dict[str, Any]] = []
    student_assignments: List[Dict[str, Any]] = []
    student_submissions_history: List[Dict[str, Any]] = []
    teacher_active_assignments_list: List[Dict[str, Any]] = []
    teacher_notes_list: List[Dict[str, Any]] = []
    teacher_pending_submissions: List[Dict[str, Any]] = []
    students: List[Dict[str, Any]] = []
    attendance_records: List[Dict[str, Any]] = []
    attendance_chart_data: List[Dict[str, Any]] = []
    review_submissions: List[Dict[str, Any]] = []
    active_submissions: List[Dict[str, Any]] = []
    student_notes: List[Dict[str, Any]] = []

    def set_profile_name(self, val: str):
        self.profile_name = val

    def set_profile_phone(self, val: str):
        self.profile_phone = val

    def set_profile_email(self, val: str):
        self.profile_email = val

    def set_profile_dept(self, val: str):
        self.profile_dept = val

    def set_profile_bio(self, val: str):
        self.profile_bio = val

    def set_current_password(self, val: str):
        self.current_password = val

    def set_new_password(self, val: str):
        self.new_password = val

    def set_confirm_password(self, val: str):
        self.confirm_password = val

    def set_new_internship_name(self, val: str):
        self.new_internship_name = val

    def set_new_internship_desc(self, val: str):
        self.new_internship_desc = val

    def set_teacher_name_input(self, val: str):
        self.teacher_name_input = val

    def set_teacher_email_input(self, val: str):
        self.teacher_email_input = val

    def set_teacher_password_input(self, val: str):
        self.teacher_password_input = val

    def set_teacher_internship_id(self, val: str):
        self.teacher_internship_id = val

    def set_student_name_input(self, val: str):
        self.student_name_input = val

    def set_student_email_input(self, val: str):
        self.student_email_input = val

    def set_student_password_input(self, val: str):
        self.student_password_input = val

    def set_student_college_input(self, val: str):
        self.student_college_input = val

    def set_student_internship_id(self, val: str):
        self.student_internship_id = val

    def set_assignment_title_input(self, val: str):
        self.assignment_title_input = val

    def set_assignment_description_input(self, val: str):
        self.assignment_description_input = val

    def set_assignment_doc_link_input(self, val: str):
        self.assignment_doc_link_input = val

    def set_assignment_due_date_input(self, val: str):
        self.assignment_due_date_input = val

    def set_assignment_internship_id(self, val: str):
        self.assignment_internship_id = val

    def set_note_title_input(self, val: str):
        self.note_title_input = val

    def set_note_file_name_input(self, val: str):
        self.note_file_name_input = val

    def set_note_markdown_input(self, val: str):
        self.note_markdown_input = val

    def set_note_internship_id(self, val: str):
        self.note_internship_id = val

    def insert_markdown_template(self, template_key: str):
        templates = {
            "h1": "# Heading 1",
            "h2": "## Heading 2",
            "h3": "### Heading 3",
            "bold": "**bold text**",
            "italic": "*italic text*",
            "strike": "~~strikethrough~~",
            "inline_code": "`inline code`",
            "blockquote": "> Block quote",
            "ul": "- List item",
            "ol": "1. Numbered item",
            "task": "- [ ] Task item",
            "link": "[Link text](https://example.com)",
            "image": "![Alt text](https://example.com/image.png)",
            "hr": "---",
            "code_block": "```python\n# code here\n```",
            "table": "| Column 1 | Column 2 |\n| --- | --- |\n| Value 1 | Value 2 |",
            "math": "$$\\nE = mc^2\\n$$",
        }
        snippet = templates.get(template_key, "")
        if not snippet:
            return
        if self.note_markdown_input.strip():
            self.note_markdown_input = f"{self.note_markdown_input.rstrip()}\n\n{snippet}"
        else:
            self.note_markdown_input = snippet

    def open_note_modal(self, note: dict):
        self.selected_note = note
        self.show_note_modal = True

    def close_note_modal(self):
        self.show_note_modal = False
        self.selected_note = {}

    def set_submission_assignment(self, val: str):
        self.submission_assignment = val

    def set_submission_repo_link(self, val: str):
        self.submission_repo_link = val

    def set_attendance_date(self, val: str):
        self.attendance_date = val

    def get_auth_header(self):
        return {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}

    def _clear_session(self):
        self.auth_token = ""
        self.current_user_id = ""
        self.current_role = ""
        self.internship_id = ""
        self.internship_name = ""
        self.is_logged_in = False

    def _dashboard_route(self) -> str:
        if self.current_role == "teacher":
            return "/teacher-dashboard"
        if self.current_role == "admin":
            return "/admin-dashboard"
        return "/student-dashboard"

    def _reset_metrics(self):
        self.metric_total_assignments = 0
        self.metric_total_students = 0
        self.metric_total_submissions = 0
        self.metric_on_time_count = 0
        self.metric_late_count = 0
        self.metric_pending_reviews = 0

    def _apply_metrics(self, data: dict):
        self.metric_total_assignments = int(data.get("total_assignments", 0))
        self.metric_total_students = int(data.get("total_students", 0))
        self.metric_total_submissions = int(data.get("total_submissions", 0))
        self.metric_on_time_count = int(data.get("on_time_count", 0))
        self.metric_late_count = int(data.get("late_count", 0))
        self.metric_pending_reviews = int(data.get("pending_reviews", 0))

        self.teacher_assignments_total = self.metric_total_assignments
        self.teacher_students_total = self.metric_total_students
        self.teacher_submissions_total = self.metric_total_submissions
        self.teacher_on_time = self.metric_on_time_count
        self.admin_assignments_total = self.metric_total_assignments
        self.admin_students_total = self.metric_total_students
        self.admin_submissions_total = self.metric_total_submissions
        self.admin_on_time = self.metric_on_time_count

    def _set_selected_internship_name(self):
        current_id = self.selected_internship_id
        if not current_id:
            self.selected_internship = "All Internships" if self.current_role == "admin" else (self.internship_name or "Unassigned")
            return

        # Check active list first
        match = next((item for item in self.active_internships if item["id"] == current_id), None)
        if not match:
            # Check all list
            match = next((item for item in self.all_internships if item["id"] == current_id), None)
            
        if match:
            self.selected_internship = match["name"]
        else:
            self.selected_internship = self.internship_name or "Unassigned"

    def _session_expired_redirect(self, exc: Exception):
        if "Authentication Denied: Session Invalidated." in str(exc):
            self._clear_session()
            return rx.redirect("/")
        return None

    async def _ensure_role(self, allowed_roles: List[str] | None = None):
        if not self.auth_token:
            return rx.redirect("/")
        try:
            await self.fetch_profile()
        except Exception:
            self._clear_session()
            return rx.redirect("/")

        if allowed_roles and self.current_role not in allowed_roles:
            return rx.redirect(self._dashboard_route())
        return None

    async def fetch_profile(self):
        profile = await api_request(self.api_url, "GET", "/api/users/profile", token=self.auth_token)
        self.current_user_id = profile.get("id", "")
        self.current_role = profile.get("role", "")
        self.internship_id = profile.get("internship_id") or ""
        self.internship_name = profile.get("internship_name") or ""
        self.selected_internship = self.internship_name or "N/A"
        self.selected_internship_id = self.internship_id
        self.profile_name = profile.get("name", "")
        self.profile_email = profile.get("email", "")
        self.profile_role_label = profile.get("role", "").title()
        self.profile_dept = self.internship_name or self.profile_role_label
        self.is_logged_in = bool(self.auth_token)
        return profile

    async def save_profile(self):
        if not self.profile_name.strip():
            return rx.window_alert("Name is required.")
        try:
            payload = {"name": self.profile_name.strip()}
            if self.selected_internship_id:
                payload["internship_id"] = self.selected_internship_id
                
            await api_request(
                self.api_url,
                "PUT",
                "/api/users/profile",
                token=self.auth_token,
                json=payload,
            )
            await self.fetch_profile()
            
            # Proactively refresh dashboard data based on role
            if self.current_role == "student":
                await self.on_load_student_dashboard()
            elif self.current_role == "teacher":
                await self.on_load_teacher_dashboard()
            elif self.current_role == "admin":
                await self.on_load_admin_dashboard()
                
            return rx.toast.success("Profile updated successfully!")
        except Exception as exc:
            return rx.window_alert(f"Profile update failed: {exc}")

    async def update_password(self):
        if not self.current_password or not self.new_password:
            return rx.window_alert("Please fill in all password fields.")
        if self.new_password != self.confirm_password:
            return rx.window_alert("Passwords do not match.")
        try:
            await api_request(
                self.api_url,
                "PUT",
                "/api/users/password",
                token=self.auth_token,
                json={
                    "current_password": self.current_password,
                    "new_password": self.new_password,
                },
            )
            self.current_password = ""
            self.new_password = ""
            self.confirm_password = ""
            return rx.toast.success("Password updated successfully!")
        except Exception as exc:
            return rx.window_alert(f"Password update failed: {exc}")

    async def fetch_active_internships(self):
        internships = await api_request(self.api_url, "GET", "/api/system/internships/active")
        self.active_internships = [normalize_internship(item) for item in internships if item.get("is_active", True)]
        return self.active_internships

    async def fetch_internships(self):
        internships = await api_request(self.api_url, "GET", "/api/system/internships", token=self.auth_token)
        self.all_internships = [normalize_internship(item) for item in internships]
        if self.current_role == "admin" and self.all_internships and not self.selected_internship_id:
            self.selected_internship_id = self.all_internships[0]["id"]
        self._set_selected_internship_name()
        return self.all_internships

    async def fetch_teachers(self):
        teachers = await api_request(self.api_url, "GET", "/api/system/teachers", token=self.auth_token)
        self.available_teachers = [normalize_teacher(item) for item in teachers]
        return self.available_teachers

    async def fetch_students(self, internship_id: str | None = None):
        params = {}
        if self.current_role == "admin" and internship_id:
            params["internship_id"] = internship_id
        students = await api_request(
            self.api_url,
            "GET",
            "/api/users/students",
            token=self.auth_token,
            params=params or None,
        )
        self.students = students
        return students

    async def fetch_assignments(self):
        assignments = await api_request(self.api_url, "GET", "/api/assignments/", token=self.auth_token)
        return [normalize_assignment(item) for item in assignments]

    async def fetch_notes(self):
        notes = await api_request(self.api_url, "GET", "/api/notes/", token=self.auth_token)
        return [normalize_note(item) for item in notes]

    async def fetch_student_submissions(self, apply_assignment_states: bool = True):
        submissions = await api_request(self.api_url, "GET", "/api/submissions/student", token=self.auth_token)
        self.student_submissions_history = [normalize_submission(item) for item in submissions]
        if apply_assignment_states:
            self._apply_student_assignment_states()
        self.metric_total_submissions = len(self.student_submissions_history)
        self.metric_on_time_count = sum(1 for item in self.student_submissions_history if item.get("status") != "Late")
        self.student_total_submissions = self.metric_total_submissions
        self.student_on_time = self.metric_on_time_count
        self.student_late = sum(1 for item in self.student_submissions_history if item.get("status") == "Late")
        return self.student_submissions_history

    def _apply_student_assignment_states(self):
        submission_map: Dict[str, Dict[str, Any]] = {}
        graded_submission_ids: set[str] = set()
        for item in self.student_submissions_history:
            assignment_id = str(item.get("assignment_id") or "")
            if assignment_id and assignment_id not in submission_map:
                submission_map[assignment_id] = item
            if assignment_id and item.get("is_graded"):
                graded_submission_ids.add(assignment_id)

        updated_assignments = []
        now = datetime.now(timezone.utc)

        for assignment in self.student_assignments:
            assignment_id = str(assignment.get("id", ""))
            submission = submission_map.get(assignment_id)
            if submission:
                card_status = "Late" if submission.get("status") == "Late" else "Submitted"
                has_submission = True
                is_graded = bool(submission.get("is_graded"))
                submission_repo_link = submission.get("repo_link", "")
                submission_repo_link_url = submission.get("repo_link_url", "")
                submission_grade = submission.get("grade", "-")
            else:
                due_date = _parse_datetime(assignment.get("due_date"))
                has_submission = False
                is_graded = False
                card_status = "Late" if due_date and now > due_date else "Due"
                submission_repo_link = ""
                submission_repo_link_url = ""
                submission_grade = "-"

            updated_assignments.append(
                {
                    **assignment,
                    "submission_status": card_status,
                    "has_submission": has_submission,
                    "can_resubmit": has_submission and not is_graded and assignment_id not in graded_submission_ids,
                    "is_graded": is_graded,
                    "submission_repo_link": submission_repo_link,
                    "submission_repo_link_url": submission_repo_link_url,
                    "submission_grade": submission_grade,
                }
            )

        self.student_assignments = updated_assignments

    async def fetch_analytics(self, internship_id: str | None = None):
        params = {}
        if self.current_role == "admin" and internship_id:
            params["internship_id"] = internship_id
        data = await api_request(
            self.api_url,
            "GET",
            "/api/analytics/dashboard",
            token=self.auth_token,
            params=params or None,
        )
        self._apply_metrics(data)
        return data

    async def fetch_analytics_safe(self, internship_id: str | None = None):
        try:
            return await self.fetch_analytics(internship_id)
        except Exception:
            self._reset_metrics()
            return {}

    async def fetch_attendance_summary(self, internship_id: str | None = None):
        params = {}
        if self.current_role == "admin" and internship_id:
            params["internship_id"] = internship_id
        data = await api_request(
            self.api_url,
            "GET",
            "/api/attendance/summary",
            token=self.auth_token,
            params=params or None,
        )
        self.attendance_records = data.get("records", [])
        self.attendance_chart_data = data.get("chart", [])
        if self.current_role == "student":
            current_student = next(
                (item for item in self.attendance_records if item.get("student_id") == self.current_user_id),
                self.attendance_records[0] if self.attendance_records else None,
            )
            self.student_attendance = int(current_student["attendance_pct"]) if current_student else 0
        return data

    async def fetch_review_submissions(self, assignment_id: str):
        submissions = await api_request(
            self.api_url,
            "GET",
            f"/api/submissions/assignment/{assignment_id}",
            token=self.auth_token,
        )
        self.review_submissions = [normalize_submission(item) for item in submissions]
        self.teacher_pending_submissions = [item for item in self.review_submissions if item.get("status") != "Graded"]
        return self.review_submissions

    async def refresh_admin_scope_data(self):
        assignments, notes = await asyncio.gather(self.fetch_assignments(), self.fetch_notes())
        current_id = self.selected_internship_id
        self.teacher_active_assignments_list = (
            [item for item in assignments if item.get("internship_id") == current_id] if current_id else assignments
        )
        self.teacher_notes_list = [item for item in notes if item.get("internship_id") == current_id] if current_id else notes
        try:
            await asyncio.gather(
                self.fetch_analytics_safe(current_id),
                self.fetch_students(current_id),
                self.fetch_attendance_summary(current_id),
            )
        except Exception as exc:
            redirect = self._session_expired_redirect(exc)
            if redirect:
                return redirect
            raise
        self._set_selected_internship_name()

    async def on_load_register(self):
        self.selected_internship_id = ""
        await self.fetch_active_internships()

    async def on_load_student_dashboard(self):
        redirect = await self._ensure_role(["student"])
        if redirect:
            return redirect

        assignments_result, notes_result, submissions_result, attendance_result = await asyncio.gather(
            self.fetch_assignments(),
            self.fetch_notes(),
            self.fetch_student_submissions(apply_assignment_states=False),
            self.fetch_attendance_summary(self.internship_id),
            return_exceptions=True,
        )

        if isinstance(assignments_result, Exception):
            redirect = self._session_expired_redirect(assignments_result)
            if redirect:
                return redirect
            raise assignments_result

        if isinstance(submissions_result, Exception):
            redirect = self._session_expired_redirect(submissions_result)
            if redirect:
                return redirect
            raise submissions_result

        if isinstance(notes_result, Exception):
            redirect = self._session_expired_redirect(notes_result)
            if redirect:
                return redirect
            raise notes_result

        self.student_assignments = assignments_result
        self.student_notes = notes_result
        self.metric_total_assignments = len(self.student_assignments)
        self._apply_student_assignment_states()

        if isinstance(attendance_result, Exception):
            redirect = self._session_expired_redirect(attendance_result)
            if redirect:
                return redirect
            self.attendance_records = []
            self.attendance_chart_data = []
            self.student_attendance = 0
        self.selected_internship = self.internship_name or "Unassigned"

    async def on_load_teacher_dashboard(self):
        redirect = await self._ensure_role(["teacher"])
        if redirect:
            return redirect

        try:
            assignments, notes, _ = await asyncio.gather(
                self.fetch_assignments(),
                self.fetch_notes(),
                self.fetch_analytics_safe(),
            )
        except Exception as exc:
            redirect = self._session_expired_redirect(exc)
            if redirect:
                return redirect
            raise
        self.teacher_active_assignments_list = assignments
        self.teacher_notes_list = notes
        self.selected_internship = self.internship_name or "Unassigned"

    async def on_load_teacher_assignments_page(self):
        redirect = await self._ensure_role(["teacher"])
        if redirect:
            return redirect

        try:
            assignments, notes, _ = await asyncio.gather(
                self.fetch_assignments(),
                self.fetch_notes(),
                self.fetch_analytics_safe(),
            )
        except Exception as exc:
            redirect = self._session_expired_redirect(exc)
            if redirect:
                return redirect
            raise
        self.teacher_active_assignments_list = assignments
        self.teacher_notes_list = notes

    async def on_load_teacher_students_page(self):
        redirect = await self._ensure_role(["teacher"])
        if redirect:
            return redirect

        try:
            await asyncio.gather(self.fetch_students(), self.fetch_analytics_safe())
        except Exception as exc:
            redirect = self._session_expired_redirect(exc)
            if redirect:
                return redirect
            raise

    async def on_load_teacher_reports_page(self):
        redirect = await self._ensure_role(["teacher"])
        if redirect:
            return redirect

        try:
            await asyncio.gather(self.fetch_analytics_safe(), self.fetch_attendance_summary())
        except Exception as exc:
            redirect = self._session_expired_redirect(exc)
            if redirect:
                return redirect
            raise

    async def on_load_admin_dashboard(self):
        redirect = await self._ensure_role(["admin"])
        if redirect:
            return redirect

        await self.fetch_internships()
        redirect = await self.refresh_admin_scope_data()
        if redirect:
            return redirect

    async def on_load_internships(self):
        redirect = await self._ensure_role(["admin"])
        if redirect:
            return redirect

        await asyncio.gather(self.fetch_internships(), self.fetch_teachers())

    async def on_load_admin_teachers_page(self):
        redirect = await self._ensure_role(["admin"])
        if redirect:
            return redirect

        await asyncio.gather(self.fetch_internships(), self.fetch_teachers())
        if not self.teacher_internship_id:
            self.teacher_internship_id = self.selected_internship_id or (self.all_internships[0]["id"] if self.all_internships else "")

    async def on_load_admin_assignments_page(self):
        redirect = await self._ensure_role(["admin"])
        if redirect:
            return redirect

        await self.fetch_internships()
        assignments, notes, _ = await asyncio.gather(
            self.fetch_assignments(),
            self.fetch_notes(),
            self.fetch_analytics_safe(self.selected_internship_id or None),
        )
        self.teacher_active_assignments_list = (
            [item for item in assignments if item.get("internship_id") == self.selected_internship_id]
            if self.selected_internship_id
            else assignments
        )
        self.teacher_notes_list = (
            [item for item in notes if item.get("internship_id") == self.selected_internship_id]
            if self.selected_internship_id
            else notes
        )

    async def on_load_admin_students_page(self):
        redirect = await self._ensure_role(["admin"])
        if redirect:
            return redirect

        await self.fetch_internships()
        await asyncio.gather(
            self.fetch_students(self.selected_internship_id or None),
            self.fetch_analytics_safe(self.selected_internship_id or None),
        )
        if not self.student_internship_id:
            self.student_internship_id = self.selected_internship_id or (self.all_internships[0]["id"] if self.all_internships else "")

    async def on_load_admin_attendance_page(self):
        redirect = await self._ensure_role(["admin"])
        if redirect:
            return redirect

        await self.fetch_internships()
        await asyncio.gather(
            self.fetch_students(self.selected_internship_id or None),
            self.fetch_attendance_summary(self.selected_internship_id or None),
        )

    async def on_load_admin_reports_page(self):
        redirect = await self._ensure_role(["admin"])
        if redirect:
            return redirect

        await self.fetch_internships()
        await asyncio.gather(
            self.fetch_analytics_safe(self.selected_internship_id or None),
            self.fetch_attendance_summary(self.selected_internship_id or None),
        )

    async def on_load_create_assignment(self):
        redirect = await self._ensure_role(["teacher", "admin"])
        if redirect:
            return redirect

        if self.current_role == "admin":
            await self.fetch_internships()
            if self.selected_internship_id and not self.assignment_internship_id:
                self.assignment_internship_id = self.selected_internship_id
        else:
            self.assignment_internship_id = self.internship_id

    async def on_load_create_note(self):
        redirect = await self._ensure_role(["teacher", "admin"])
        if redirect:
            return redirect

        if self.current_role == "admin":
            await self.fetch_internships()
            if self.selected_internship_id and not self.note_internship_id:
                self.note_internship_id = self.selected_internship_id
        else:
            self.note_internship_id = self.internship_id

    async def on_load_settings(self):
        redirect = await self._ensure_role(["student", "teacher", "admin"])
        if redirect:
            return redirect
        await self.fetch_active_internships()

    async def set_selected_internship(self, value: str):
        self.selected_internship_id = value
        self._set_selected_internship_name()
        if self.current_role == "admin":
            redirect = await self.refresh_admin_scope_data()
            if redirect:
                return redirect

    def toggle_teacher_selection(self, teacher_id: str):
        if teacher_id in self.selected_teacher_ids:
            self.selected_teacher_ids = [item for item in self.selected_teacher_ids if item != teacher_id]
        else:
            self.selected_teacher_ids = [*self.selected_teacher_ids, teacher_id]

    def open_internship_modal(self, item: Dict[str, Any] | None = None):
        if item and isinstance(item, dict):
            self.editing_internship_id = item.get("id", "")
            self.new_internship_name = item.get("name", "")
            self.new_internship_desc = item.get("description", "")
            self.selected_teacher_ids = item.get("teacher_ids", [])
        else:
            self.editing_internship_id = ""
            self.new_internship_name = ""
            self.new_internship_desc = ""
            self.selected_teacher_ids = []
        self.show_internship_modal = True

    def close_internship_modal(self):
        self.show_internship_modal = False

    async def save_internship(self):
        if not self.new_internship_name.strip():
            return rx.window_alert("Internship name is required.")
        try:
            payload = {
                "name": self.new_internship_name.strip(),
                "description": self.new_internship_desc.strip(),
                "teacher_ids": self.selected_teacher_ids,
            }
            if self.editing_internship_id:
                await api_request(
                    self.api_url,
                    "PUT",
                    f"/api/system/internships/{self.editing_internship_id}",
                    token=self.auth_token,
                    json=payload,
                )
            else:
                await api_request(
                    self.api_url,
                    "POST",
                    "/api/system/internships",
                    token=self.auth_token,
                    json=payload,
                )
            self.close_internship_modal()
            await asyncio.gather(self.fetch_internships(), self.fetch_teachers())
            return rx.toast.success("Internship saved successfully!")
        except Exception as exc:
            return rx.window_alert(f"Save failed: {exc}")

    async def set_internship_status(self, internship_id: str, is_active: bool):
        try:
            await api_request(
                self.api_url,
                "PUT",
                f"/api/system/internships/{internship_id}",
                token=self.auth_token,
                json={"is_active": is_active},
            )
            await self.fetch_internships()
            action = "activated" if is_active else "deactivated"
            return rx.toast.success(f"Internship {action} successfully!")
        except Exception as exc:
            action = "Activate" if is_active else "Deactivate"
            return rx.window_alert(f"{action} failed: {exc}")

    async def delete_internship(self, internship_id: str):
        return await self.set_internship_status(internship_id, False)

    async def create_teacher_access(self):
        name = self.teacher_name_input.strip()
        email = self.teacher_email_input.strip().lower()
        password = self.teacher_password_input.strip()
        internship_id = self.teacher_internship_id or None

        if not name or not email or not password:
            return rx.window_alert("Please fill in the teacher name, email, and temporary password.")
        if len(password) < 8:
            return rx.window_alert("Temporary password must be at least 8 characters long.")

        try:
            await api_request(
                self.api_url,
                "POST",
                "/api/system/teachers",
                token=self.auth_token,
                json={
                    "name": name,
                    "email": email,
                    "password": password,
                    "internship_id": internship_id,
                },
            )
            self.teacher_name_input = ""
            self.teacher_email_input = ""
            self.teacher_password_input = ""
            self.teacher_internship_id = ""
            await asyncio.gather(self.fetch_teachers(), self.fetch_internships())
            return rx.toast.success("Teacher access created successfully!")
        except Exception as exc:
            return rx.window_alert(f"Teacher access creation failed: {exc}")

    async def create_student_access(self):
        name = self.student_name_input.strip()
        email = self.student_email_input.strip().lower()
        password = self.student_password_input.strip()
        college_name = self.student_college_input.strip()
        internship_id = self.student_internship_id or self.selected_internship_id or None

        if not name or not email or not password:
            return rx.window_alert("Please fill in student name, email, and temporary password.")
        if len(password) < 8:
            return rx.window_alert("Temporary password must be at least 8 characters long.")

        try:
            await api_request(
                self.api_url,
                "POST",
                "/api/system/students",
                token=self.auth_token,
                json={
                    "name": name,
                    "email": email,
                    "password": password,
                    "college_name": college_name or None,
                    "internship_id": internship_id,
                },
            )
            self.student_name_input = ""
            self.student_email_input = ""
            self.student_password_input = ""
            self.student_college_input = ""
            await self.fetch_students(self.selected_internship_id or None)
            await self.fetch_analytics_safe(self.selected_internship_id or None)
            return rx.toast.success("Student access created successfully!")
        except Exception as exc:
            return rx.window_alert(f"Student access creation failed: {exc}")

    async def download_students_template(self):
        try:
            async with httpx.AsyncClient(timeout=60.0, trust_env=False) as client:
                response = await client.get(
                    f"{self.api_url}/api/system/students/template",
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                )
            if response.status_code >= 400:
                detail = response.text
                try:
                    detail = response.json().get("detail", detail)
                except Exception:
                    pass
                return rx.window_alert(f"Template download failed: {detail}")

            filename = "students_bulk_template.xlsx"
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / filename
            with file_path.open("wb") as f:
                f.write(response.content)

            return rx.download(url=rx.get_upload_url(filename))
        except Exception as exc:
            return rx.window_alert(f"Template download failed: {exc}")

    async def upload_students_bulk_file(self, files: list[rx.UploadFile]):
        if not files:
            return rx.window_alert("Please choose an .xlsx file first.")
        try:
            workbook_file = files[0]
            content = await workbook_file.read()
            async with httpx.AsyncClient(timeout=120.0, trust_env=False) as client:
                response = await client.post(
                    f"{self.api_url}/api/system/students/bulk-upload",
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                    files={
                        "file": (
                            workbook_file.name,
                            content,
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )
                    },
                )
            payload = response.json() if response.content else {}
            if response.status_code >= 400:
                detail = payload.get("detail") if isinstance(payload, dict) else str(payload)
                return rx.window_alert(f"Bulk upload failed: {detail}")

            self.student_bulk_upload_summary = (
                f"Created: {payload.get('created', 0)} | "
                f"Updated: {payload.get('updated', 0)} | "
                f"Skipped: {payload.get('skipped', 0)}"
            )
            await self.fetch_students(self.selected_internship_id or None)
            await self.fetch_analytics_safe(self.selected_internship_id or None)
            return [
                rx.clear_selected_files("student_bulk_upload"),
                rx.toast.success("Bulk upload completed."),
            ]
        except Exception as exc:
            return rx.window_alert(f"Bulk upload failed: {exc}")

    def open_submission_modal(self, assignment_id: str = "", title: str = "", repo_link: str = "", button_label: str = "Submit Work"):
        if assignment_id:
            self.submission_assignment = assignment_id
        if title:
            self.selected_assignment_title = title
        self.submission_repo_link = repo_link
        self.submission_submit_label = button_label or "Submit Work"
        self.submission_modal_title = "Resubmit Assignment" if self.submission_submit_label.startswith("Resubmit") else "Submit Assignment"
        self.show_submission_modal = True

    def close_submission_modal(self):
        self.show_submission_modal = False
        self.submission_assignment = ""
        self.submission_repo_link = ""
        self.selected_assignment_title = ""
        self.submission_modal_title = "Submit Assignment"
        self.submission_submit_label = "Submit Work"

    async def submit_assignment_action(self):
        if not self.submission_assignment:
            return rx.window_alert("Please choose an assignment.")
        if not self.submission_repo_link.strip():
            return rx.window_alert("Please provide your repository link.")
        try:
            action_label = self.submission_submit_label
            normalized_repo_link = _normalize_external_url(self.submission_repo_link)
            await api_request(
                self.api_url,
                "POST",
                "/api/submissions/",
                token=self.auth_token,
                json={
                    "assignment_id": self.submission_assignment,
                    "repo_link": normalized_repo_link,
                },
            )
            self.close_submission_modal()
            await self.on_load_student_dashboard()
            action_message = "resubmitted" if action_label.startswith("Resubmit") else "submitted"
            return rx.toast.success(f"Assignment {action_message} successfully!")
        except Exception as exc:
            return rx.window_alert(f"Submission failed: {exc}")

    async def open_code_review(self, assignment_id: str, title: str):
        self.selected_assignment_id = assignment_id
        self.selected_assignment_title = title
        self.show_code_review_modal = True
        try:
            await self.fetch_review_submissions(assignment_id)
        except Exception as exc:
            self.review_submissions = []
            return rx.window_alert(f"Failed to load submissions: {exc}")

    def close_code_review(self):
        self.show_code_review_modal = False
        self.selected_assignment_id = ""
        self.selected_assignment_title = ""
        self.review_submissions = []

    async def grade_submission_action(self, submission_id: str, grade: str):
        try:
            await api_request(
                self.api_url,
                "PUT",
                f"/api/submissions/{submission_id}/grade",
                token=self.auth_token,
                json={"grade": grade},
            )
            if self.selected_assignment_id:
                await self.fetch_review_submissions(self.selected_assignment_id)
            scope_id = self.selected_internship_id if self.current_role == "admin" else None
            await self.fetch_analytics_safe(scope_id)
            return rx.toast.success("Submission graded successfully!")
        except Exception as exc:
            return rx.window_alert(f"Grading failed: {exc}")

    def open_attendance_modal(self):
        self.attendance_statuses = {student["id"]: "Present" for student in self.students}
        self.show_attendance_modal = True

    def close_attendance_modal(self):
        self.show_attendance_modal = False

    def set_attendance_status(self, student_id: str, status: str):
        self.attendance_statuses = {**self.attendance_statuses, student_id: status}

    async def submit_attendance(self):
        if not self.students:
            return rx.window_alert("No students available for attendance.")
        try:
            payload = {
                "date": self.attendance_date,
                "records": [
                    {
                        "student_id": student["id"],
                        "status": self.attendance_statuses.get(student["id"], "Present"),
                    }
                    for student in self.students
                ],
            }
            await api_request(
                self.api_url,
                "POST",
                "/api/attendance/",
                token=self.auth_token,
                json=payload,
            )
            self.close_attendance_modal()
            await self.fetch_attendance_summary(self.selected_internship_id or None if self.current_role == "admin" else None)
            return rx.toast.success("Attendance saved successfully!")
        except Exception as exc:
            return rx.window_alert(f"Attendance save failed: {exc}")

    async def create_assignment_action(self):
        if not self.assignment_title_input.strip():
            return rx.window_alert("Assignment title is required.")
        if not self.assignment_description_input.strip():
            return rx.window_alert("Assignment description is required.")
        if not self.assignment_due_date_input:
            return rx.window_alert("Please choose a due date.")

        internship_id = self.internship_id if self.current_role == "teacher" else self.assignment_internship_id
        if not internship_id:
            return rx.window_alert("Please choose an internship.")

        try:
            await api_request(
                self.api_url,
                "POST",
                "/api/assignments/",
                token=self.auth_token,
                json={
                    "internship_id": internship_id,
                    "title": self.assignment_title_input.strip(),
                    "description": self.assignment_description_input.strip(),
                    "doc_link": self.assignment_doc_link_input.strip() or None,
                    "due_date": f"{self.assignment_due_date_input}T23:59:00",
                },
            )
            self.assignment_title_input = ""
            self.assignment_description_input = ""
            self.assignment_doc_link_input = ""
            self.assignment_due_date_input = ""
            if self.current_role == "teacher":
                await self.on_load_teacher_assignments_page()
                return [rx.toast.success("Assignment published successfully!"), rx.redirect("/teacher-assignments")]

            await self.on_load_admin_assignments_page()
            return [rx.toast.success("Assignment published successfully!"), rx.redirect("/admin-assignments")]
        except Exception as exc:
            return rx.window_alert(f"Assignment creation failed: {exc}")

    async def create_note_action(self):
        if not self.note_title_input.strip():
            return rx.window_alert("Note title is required.")
        if not self.note_markdown_input.strip():
            return rx.window_alert("Markdown content is required.")

        internship_id = self.internship_id if self.current_role == "teacher" else self.note_internship_id
        if not internship_id:
            return rx.window_alert("Please choose an internship.")

        file_name = self.note_title_input.strip().lower().replace(" ", "-")
        if not file_name.endswith(".md"):
            file_name = f"{file_name}.md"

        try:
            if self.editing_note_id:
                await api_request(
                    self.api_url,
                    "PUT",
                    f"/api/notes/{self.editing_note_id}",
                    token=self.auth_token,
                    json={
                        "internship_id": internship_id,
                        "title": self.note_title_input.strip(),
                        "markdown_content": self.note_markdown_input.strip(),
                    },
                )
            else:
                await api_request(
                    self.api_url,
                    "POST",
                    "/api/notes/",
                    token=self.auth_token,
                    json={
                        "internship_id": internship_id,
                        "title": self.note_title_input.strip(),
                        "file_name": file_name,
                        "markdown_content": self.note_markdown_input.strip(),
                    },
                )
            self.note_title_input = ""
            self.note_file_name_input = ""
            self.note_markdown_input = ""
            self.editing_note_id = ""
            if self.current_role == "teacher":
                await self.on_load_teacher_assignments_page()
                return [rx.toast.success("Note saved successfully!"), rx.redirect("/teacher-assignments")]

            await self.on_load_admin_assignments_page()
            return [rx.toast.success("Note saved successfully!"), rx.redirect("/admin-assignments")]
        except Exception as exc:
            return rx.window_alert(f"Note save failed: {exc}")

    def open_note_editor(
        self,
        note_id: str,
        title: str,
        markdown_content: str,
        internship_id: str,
    ):
        self.editing_note_id = note_id
        self.note_title_input = title
        self.note_markdown_input = markdown_content
        self.note_internship_id = internship_id
        return rx.redirect("/create-note")

    def cancel_note_edit(self):
        self.editing_note_id = ""
        self.note_title_input = ""
        self.note_markdown_input = ""
        self.note_internship_id = ""
        self.note_file_name_input = ""
        return rx.redirect("/teacher-assignments" if self.current_role == "teacher" else "/admin-assignments")

    async def delete_note_action(self, note_id: str):
        try:
            await api_request(
                self.api_url,
                "DELETE",
                f"/api/notes/{note_id}",
                token=self.auth_token,
            )
            if self.current_role == "teacher":
                await self.on_load_teacher_assignments_page()
            else:
                await self.on_load_admin_assignments_page()
            return rx.toast.success("Note deleted successfully.")
        except Exception as exc:
            return rx.window_alert(f"Delete note failed: {exc}")

    def handle_logout(self):
        self._clear_session()
        return rx.redirect("/")
