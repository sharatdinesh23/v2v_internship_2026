"""Teacher Reports page for InternPortal."""
import reflex as rx

from internship_portal.components import kpi_card, page_header, sidebar, status_badge
from internship_portal.state import AppState
from internship_portal.styles import COLORS, main_content_style, page_style, table_style, td_style, th_style


def attendance_summary_table() -> rx.Component:
    def render_row(item: dict) -> rx.Component:
        badge_color = rx.cond(item["status"] == "Good", COLORS["success"], COLORS["warning"])
        return rx.table.row(
            rx.table.cell(item.get("name", "Unknown"), style=td_style),
            rx.table.cell(item.get("present", 0), style=td_style),
            rx.table.cell(item.get("absent", 0), style=td_style),
            rx.table.cell(item.get("late", 0), style=td_style),
            rx.table.cell(f"{item.get('attendance_pct', 0)}%", style=td_style),
            rx.table.cell(status_badge(item.get("status", "Good"), badge_color), style=td_style),
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
                        rx.table.column_header_cell("Health", style=th_style),
                    )
                ),
                rx.table.body(rx.foreach(AppState.attendance_records, render_row)),
                style=table_style,
            ),
            rx.center(rx.text("Attendance summary will appear here once data is available.", color=COLORS["on_surface_variant"], padding="40px")),
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
                height=280,
            ),
            rx.center(rx.text("No attendance chart data available.", color=COLORS["on_surface_variant"], padding="40px")),
        ),
        background=COLORS["surface_container"],
        border_radius="16px",
        padding="24px",
        border=f"1px solid rgba(60, 73, 90, 0.2)",
        width="100%",
    )


def teacher_reports() -> rx.Component:
    return rx.box(
        sidebar(active_page="reports", role="teacher"),
        rx.box(
            page_header("Analytics & Reports", "", ""),
            rx.vstack(
                rx.grid(
                    kpi_card("Assignments", AppState.metric_total_assignments.to(str), "AS", COLORS["primary"]),
                    kpi_card("Students", AppState.metric_total_students.to(str), "ST", COLORS["tertiary"]),
                    kpi_card("Submissions", AppState.metric_total_submissions.to(str), "SB", COLORS["primary"]),
                    kpi_card("On-Time", AppState.metric_on_time_count.to(str), "OK", COLORS["success"]),
                    columns=rx.breakpoints(initial="1", sm="2", lg="4"),
                    width="100%",
                    gap="24px",
                    margin_bottom="24px",
                ),
                attendance_chart(),
                attendance_summary_table(),
                width="100%",
                max_width="1400px",
                margin="0 auto",
                align_items="flex_start",
                gap="24px",
            ),
            style=main_content_style,
        ),
        on_mount=AppState.on_load_teacher_reports_page,
        **page_style,
    )
