"""Admin Students page for InternPortal."""
import reflex as rx

from internship_portal.components import kpi_card, page_header, sidebar
from internship_portal.state import AppState
from internship_portal.styles import (
    COLORS,
    btn_ghost_style,
    btn_primary_style,
    input_style,
    main_content_style,
    page_style,
    table_style,
    td_style,
    th_style,
)


def add_student_form() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text("Add Student Access", font_size="1.1rem", font_weight="700", color=COLORS["on_surface"]),
            rx.grid(
                rx.input(value=AppState.student_name_input, on_change=AppState.set_student_name_input, placeholder="Student name", style=input_style),
                rx.input(value=AppState.student_email_input, on_change=AppState.set_student_email_input, placeholder="student@college.edu", type="email", style=input_style),
                columns=rx.breakpoints(initial="1", sm="2"),
                gap="12px",
                width="100%",
            ),
            rx.grid(
                rx.input(value=AppState.student_password_input, on_change=AppState.set_student_password_input, placeholder="Temporary password", type="password", style=input_style),
                rx.input(value=AppState.student_college_input, on_change=AppState.set_student_college_input, placeholder="College name", style=input_style),
                columns=rx.breakpoints(initial="1", sm="2"),
                gap="12px",
                width="100%",
            ),
            rx.select.root(
                rx.select.trigger(placeholder="Assign Internship", style=input_style, width="100%"),
                rx.select.content(
                    rx.foreach(AppState.all_internships, lambda internship: rx.select.item(internship["name"], value=internship["id"])),
                    background=COLORS["surface_high"],
                    color=COLORS["on_surface"],
                ),
                value=AppState.student_internship_id,
                on_change=AppState.set_student_internship_id,
            ),
            rx.hstack(
                rx.button("Create Student Access", style=btn_primary_style, on_click=AppState.create_student_access),
                rx.button("Refresh", style=btn_ghost_style, on_click=AppState.on_load_admin_students_page),
                width="100%",
                gap="10px",
            ),
            width="100%",
            align_items="flex_start",
            gap="12px",
        ),
        background=COLORS["surface_container"],
        border=f"1px solid rgba(60, 73, 90, 0.2)",
        border_radius="16px",
        padding="20px",
        width="100%",
    )


def bulk_upload_section() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text("Bulk Add / Update Students", font_size="1.1rem", font_weight="700", color=COLORS["on_surface"]),
            rx.hstack(
                rx.button("Download Excel Template", style=btn_ghost_style, on_click=AppState.download_students_template),
                width="100%",
            ),
            rx.upload(
                rx.vstack(
                    rx.button("Choose Excel File (.xlsx)", variant="soft"),
                    rx.foreach(rx.selected_files("student_bulk_upload"), rx.text),
                    align_items="flex_start",
                    width="100%",
                ),
                id="student_bulk_upload",
                max_files=1,
                accept={".xlsx": ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]},
                border=f"1px dashed {COLORS['outline']}",
                border_radius="10px",
                padding="14px",
                width="100%",
            ),
            rx.hstack(
                rx.button(
                    "Upload Excel",
                    style=btn_primary_style,
                    on_click=AppState.upload_students_bulk_file(rx.upload_files(upload_id="student_bulk_upload")),
                ),
                rx.button("Clear", style=btn_ghost_style, on_click=rx.clear_selected_files("student_bulk_upload")),
                width="100%",
                gap="10px",
            ),
            rx.cond(
                AppState.student_bulk_upload_summary != "",
                rx.text(AppState.student_bulk_upload_summary, color=COLORS["on_surface_variant"], font_size="0.82rem"),
                rx.box(),
            ),
            width="100%",
            align_items="flex_start",
            gap="12px",
        ),
        background=COLORS["surface_container"],
        border=f"1px solid rgba(60, 73, 90, 0.2)",
        border_radius="16px",
        padding="20px",
        width="100%",
    )


def students_table() -> rx.Component:
    def render_row(student: dict) -> rx.Component:
        return rx.table.row(
            rx.table.cell(student.get("name", "Unknown"), style=td_style),
            rx.table.cell(student.get("email", "-"), style=td_style),
            rx.table.cell(rx.cond(student.get("college_name", "-"), student.get("college_name", "-"), "-"), style=td_style),
            rx.table.cell(student.get("internship_name", "-"), style=td_style),
        )

    return rx.box(
        rx.cond(
            AppState.students.length() > 0,
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Student", style=th_style),
                        rx.table.column_header_cell("Email", style=th_style),
                        rx.table.column_header_cell("College", style=th_style),
                        rx.table.column_header_cell("Internship", style=th_style),
                    )
                ),
                rx.table.body(rx.foreach(AppState.students, render_row)),
                style=table_style,
            ),
            rx.center(rx.text("No students found for the selected internship.", color=COLORS["on_surface_variant"], padding="40px")),
        ),
        border=f"1px solid rgba(60, 73, 90, 0.2)",
        border_radius="16px",
        overflow="hidden",
        width="100%",
    )


def admin_students() -> rx.Component:
    return rx.box(
        sidebar(active_page="students", role="admin"),
        rx.box(
            page_header("Global Student Directory", "", ""),
            rx.vstack(
                rx.hstack(
                    rx.text("Internship Filter", font_size="0.875rem", font_weight="600", color=COLORS["on_surface_variant"]),
                    rx.select.root(
                        rx.select.trigger(background=COLORS["surface_container"], color=COLORS["on_surface"], border=f"1px solid rgba(60, 73, 90, 0.3)", border_radius="8px", padding="8px 16px", min_width="220px", font_weight="600"),
                        rx.select.content(
                            rx.foreach(AppState.all_internships, lambda internship: rx.select.item(internship["name"], value=internship["id"])),
                            background=COLORS["surface_high"],
                            color=COLORS["on_surface"],
                        ),
                        value=AppState.selected_internship_id,
                        on_change=AppState.set_selected_internship,
                    ),
                    width="100%",
                    margin_bottom="20px",
                ),
                rx.grid(
                    kpi_card("Students", AppState.metric_total_students.to(str), "ST", COLORS["primary"]),
                    kpi_card("Assignments", AppState.metric_total_assignments.to(str), "AS", COLORS["tertiary"]),
                    columns=rx.breakpoints(initial="1", sm="2"),
                    width="100%",
                    gap="24px",
                    margin_bottom="24px",
                ),
                rx.grid(
                    add_student_form(),
                    bulk_upload_section(),
                    columns=rx.breakpoints(initial="1", xl="2"),
                    width="100%",
                    gap="18px",
                ),
                students_table(),
                width="100%",
                max_width="1400px",
                margin="0 auto",
                align_items="flex_start",
            ),
            style=main_content_style,
        ),
        on_mount=AppState.on_load_admin_students_page,
        **page_style,
    )
