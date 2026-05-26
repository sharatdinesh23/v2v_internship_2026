"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config
from internship_portal.state import AppState
from internship_portal.pages import (
    login_page, register_page, student_dashboard,
    teacher_dashboard, admin_dashboard, settings_page,
    teacher_assignments, teacher_notes, teacher_students, teacher_reports,
    create_assignment, create_note, admin_assignments, admin_notes, admin_students,
    admin_attendance, admin_reports, admin_internships_page, admin_teachers_page
)


class State(rx.State):
    """The app state."""


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Welcome to Reflex!", size="9"),
            rx.text(
                "Get started by editing ",
                rx.code(f"{config.app_name}/{config.app_name}.py"),
                size="5",
            ),
            rx.link(
                rx.button("Check out our docs!"),
                href="https://reflex.dev/docs/getting-started/introduction/",
                is_external=True,
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
    )


app = rx.App(
    theme=rx.theme(appearance="dark", has_background=True, radius="large"),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
    ],
    admin_dash=False,
)

app.add_page(login_page, route="/", title="Login | InternPortal")
app.add_page(register_page, route="/register", title="Register | InternPortal")
app.add_page(student_dashboard, route="/student-dashboard", title="Student Dashboard | InternPortal")
app.add_page(teacher_dashboard, route="/teacher-dashboard", title="Teacher Dashboard | InternPortal")
app.add_page(teacher_assignments, route="/teacher-assignments", title="Teacher Assignments")
app.add_page(teacher_notes, route="/teacher-notes", title="Teacher Notes")
app.add_page(teacher_students, route="/teacher-students", title="Teacher Students")
app.add_page(teacher_reports, route="/teacher-reports", title="Teacher Reports")
app.add_page(admin_dashboard, route="/admin-dashboard", title="Admin Dashboard | InternPortal")
app.add_page(admin_assignments, route="/admin-assignments", title="Admin Assignments")
app.add_page(admin_notes, route="/admin-notes", title="Admin Notes")
app.add_page(admin_students, route="/admin-students", title="Admin Students")
app.add_page(admin_attendance, route="/admin-attendance", title="Admin Attendance")
app.add_page(admin_reports, route="/admin-reports", title="Admin Reports")
app.add_page(admin_internships_page, route="/admin-internships", title="Admin Internships")
app.add_page(admin_teachers_page, route="/admin-teachers", title="Teacher Access")
app.add_page(create_assignment, route="/create-assignment", title="Create Assignment")
app.add_page(create_note, route="/create-note", title="Create Note")
app.add_page(settings_page, route="/settings", title="Settings | InternPortal")
