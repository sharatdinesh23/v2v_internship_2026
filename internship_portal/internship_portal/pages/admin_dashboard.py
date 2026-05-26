"""Admin Dashboard page for InternPortal."""
import reflex as rx

from internship_portal.components import kpi_card, page_header, sidebar, status_badge
from internship_portal.pages.teacher_dashboard import code_review_modal, teacher_active_assignments
from internship_portal.state import AppState
from internship_portal.styles import COLORS, btn_ghost_style, btn_primary_style, main_content_style, page_style, table_style, td_style, th_style


def attendance_table() -> rx.Component:
    def render_row(record: dict) -> rx.Component:
        status_color = rx.cond(record["status"] == "Good", COLORS["success"], COLORS["warning"])
        return rx.table.row(
            rx.table.cell(record.get("name", "Unknown"), style=td_style),
            rx.table.cell(record.get("present", 0), style=td_style),
            rx.table.cell(record.get("absent", 0), style=td_style),
            rx.table.cell(record.get("late", 0), style=td_style),
            rx.table.cell(f"{record.get('attendance_pct', 0)}%", style=td_style),
            rx.table.cell(status_badge(record.get("status", "Good"), status_color), style=td_style),
        )

    return rx.box(
        rx.cond(
            AppState.attendance_records.length() > 0,
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Student", style=th_style),
                        rx.table.column_header_cell("Present", style=th_style),
                        rx.table.column_header_cell("Absent", style=th_style),
                        rx.table.column_header_cell("Late", style=th_style),
                        rx.table.column_header_cell("Attendance %", style=th_style),
                        rx.table.column_header_cell("Status", style=th_style),
                    )
                ),
                rx.table.body(rx.foreach(AppState.attendance_records, render_row)),
                style=table_style,
            ),
            rx.center(rx.text("No attendance summary available yet.", color=COLORS["on_surface_variant"], padding="40px")),
        ),
        border=f"1px solid rgba(60, 73, 90, 0.2)",
        border_radius="16px",
        overflow="hidden",
        width="100%",
    )


def attendance_chart() -> rx.Component:
    return rx.box(
        rx.cond(
            AppState.attendance_chart_data.length() > 0,
            rx.recharts.line_chart(
                rx.recharts.line(data_key="present", type_="monotone", stroke=COLORS["primary"], stroke_width=3),
                rx.recharts.line(data_key="absent", type_="monotone", stroke=COLORS["error"], stroke_width=2),
                rx.recharts.x_axis(data_key="date", stroke=COLORS["on_surface_variant"]),
                rx.recharts.y_axis(stroke=COLORS["on_surface_variant"]),
                rx.recharts.tooltip(content_style={"backgroundColor": COLORS["surface_high"], "border": f"1px solid {COLORS['outline_variant']}", "borderRadius": "8px"}),
                data=AppState.attendance_chart_data,
                width="100%",
                height=260,
            ),
            rx.center(rx.text("No attendance chart data available.", color=COLORS["on_surface_variant"], padding="40px")),
        ),
        background="rgba(18, 39, 60, 0.3)",
        border_radius="16px",
        padding="24px",
        border=f"1px solid rgba(60, 73, 90, 0.15)",
        width="100%",
    )


def log_attendance_modal() -> rx.Component:
    def student_row(student: dict) -> rx.Component:
        return rx.hstack(
            rx.text(student.get("name", "Unknown"), flex="1"),
            rx.select.root(
                rx.select.trigger(background=COLORS["surface_high"], color=COLORS["on_surface"], border="none", border_radius="8px", padding="8px 12px", min_width="140px"),
                rx.select.content(
                    rx.select.item("Present", value="Present"),
                    rx.select.item("Absent", value="Absent"),
                    rx.select.item("Late", value="Late"),
                    background=COLORS["surface_high"],
                    color=COLORS["on_surface"],
                ),
                default_value="Present",
                on_change=lambda value: AppState.set_attendance_status(student["id"], value),
            ),
            width="100%",
            align="center",
            border_bottom=f"1px solid rgba(60, 73, 90, 0.2)",
            padding_y="8px",
        )

    return rx.cond(
        AppState.show_attendance_modal,
        rx.box(
            rx.center(
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("Log Student Attendance", font_size="1.2rem", font_weight="700", color=COLORS["on_surface"]),
                            rx.spacer(),
                            rx.text("X", cursor="pointer", font_size="1.2rem", color=COLORS["on_surface_variant"], _hover={"color": COLORS["error"]}, on_click=AppState.close_attendance_modal),
                            width="100%",
                            align="center",
                        ),
                        rx.divider(border_color=f"rgba(60, 73, 90, 0.3)", margin_y="16px"),
                        rx.vstack(
                            rx.text("Attendance Date", font_size="0.8rem", color=COLORS["on_surface_variant"]),
                            rx.input(type="date", value=AppState.attendance_date, on_change=AppState.set_attendance_date, background=COLORS["surface_high"], border="none", border_radius="8px", color=COLORS["on_surface"]),
                            width="100%",
                            align_items="flex_start",
                        ),
                        rx.vstack(rx.foreach(AppState.students, student_row), width="100%", margin_top="16px"),
                        rx.hstack(
                            rx.button("Save Attendance", style=btn_primary_style, on_click=AppState.submit_attendance, flex="1"),
                            rx.button("Cancel", style=btn_ghost_style, on_click=AppState.close_attendance_modal, flex="1"),
                            width="100%",
                            gap="16px",
                        ),
                        width="100%",
                        align_items="flex_start",
                    ),
                    background=COLORS["surface_container"],
                    padding="32px",
                    border_radius="24px",
                    width="640px",
                    max_width="92vw",
                    box_shadow=f"0 0 60px rgba(0, 0, 0, 0.5)",
                    border=f"1px solid rgba(60, 73, 90, 0.3)",
                ),
                width="100vw",
                height="100vh",
            ),
            position="fixed",
            top="0",
            left="0",
            width="100vw",
            height="100vh",
            background="rgba(2, 15, 30, 0.8)",
            backdrop_filter="blur(8px)",
            z_index="1000",
        ),
        rx.box(),
    )


def admin_dashboard() -> rx.Component:
    return rx.box(
        sidebar(active_page="dashboard", role="admin"),
        rx.box(
            page_header("Admin Dashboard", "Create Assignment", "/create-assignment"),
            rx.vstack(
                rx.hstack(
                    rx.text("Current Internship:", font_size="0.875rem", font_weight="600", color=COLORS["on_surface_variant"]),
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
                    align="center",
                    gap="12px",
                    margin_bottom="24px",
                ),
                rx.grid(
                    kpi_card("Assignments", AppState.metric_total_assignments.to(str), "AS", COLORS["primary"]),
                    kpi_card("Students", AppState.metric_total_students.to(str), "ST", COLORS["tertiary"]),
                    kpi_card("Submissions", AppState.metric_total_submissions.to(str), "SB", COLORS["primary"]),
                    kpi_card("Pending Reviews", AppState.metric_pending_reviews.to(str), "RV", COLORS["warning"]),
                    columns=rx.breakpoints(initial="1", sm="2", lg="4"),
                    width="100%",
                    gap="24px",
                    margin_bottom="32px",
                ),
                rx.hstack(
                    rx.text("Active Assignments Overview", font_size="1.25rem", font_weight="700"),
                    rx.spacer(),
                    rx.button("Refresh", variant="ghost", on_click=AppState.on_load_admin_dashboard),
                    rx.link(
                        rx.button("Teacher Access", style=btn_ghost_style),
                        href="/admin-teachers",
                        text_decoration="none",
                    ),
                    align="center",
                    width="100%",
                    margin_bottom="20px",
                ),
                teacher_active_assignments(),
                rx.divider(border_color=f"rgba(60, 73, 90, 0.3)", margin_y="40px"),
                rx.hstack(
                    rx.text("Attendance Management", font_size="1.25rem", font_weight="700"),
                    rx.spacer(),
                    rx.button("+ Add New Attendance", style=btn_primary_style, on_click=AppState.open_attendance_modal),
                    align="center",
                    width="100%",
                    margin_bottom="20px",
                ),
                rx.hstack(
                    rx.box(attendance_table(), width="65%"),
                    rx.box(rx.text("Attendance Trend", font_weight="600"), attendance_chart(), width="35%", padding="24px", background=COLORS["surface_container"], border_radius="16px"),
                    width="100%",
                    gap="24px",
                    align_items="flex_start",
                ),
                width="100%",
                max_width="1400px",
                margin="0 auto",
                align_items="flex_start",
                padding_bottom="60px",
            ),
            style=main_content_style,
        ),
        code_review_modal(),
        log_attendance_modal(),
        on_mount=AppState.on_load_admin_dashboard,
        **page_style,
    )
