"""Teacher Students page for InternPortal."""
import reflex as rx

from internship_portal.components import kpi_card, page_header, sidebar
from internship_portal.state import AppState
from internship_portal.styles import COLORS, main_content_style, page_style, table_style, td_style, th_style


def students_table() -> rx.Component:
    def render_row(student: dict) -> rx.Component:
        return rx.table.row(
            rx.table.cell(student.get("name", "Unknown"), style=td_style),
            rx.table.cell(student.get("email", "-"), style=td_style),
            rx.table.cell(rx.cond(student.get("college_name", "-"), student.get("college_name", "-"), "-"), style=td_style),
            rx.table.cell(student.get("internship_name", AppState.selected_internship), style=td_style),
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
            rx.center(rx.text("No students found for this internship.", color=COLORS["on_surface_variant"], padding="40px")),
        ),
        border=f"1px solid rgba(60, 73, 90, 0.2)",
        border_radius="16px",
        overflow="hidden",
        width="100%",
    )


def teacher_students() -> rx.Component:
    return rx.box(
        sidebar(active_page="students", role="teacher"),
        rx.box(
            page_header("Student Directory", "", ""),
            rx.vstack(
                rx.grid(
                    kpi_card("Students", AppState.metric_total_students.to(str), "ST", COLORS["primary"]),
                    kpi_card("Program", AppState.selected_internship, "IN", COLORS["tertiary"]),
                    columns=rx.breakpoints(initial="1", sm="2"),
                    width="100%",
                    gap="24px",
                    margin_bottom="24px",
                ),
                students_table(),
                width="100%",
                max_width="1400px",
                margin="0 auto",
                align_items="flex_start",
            ),
            style=main_content_style,
        ),
        on_mount=AppState.on_load_teacher_students_page,
        **page_style,
    )
