"""Teacher Dashboard page for InternPortal."""
import reflex as rx

from internship_portal.components import kpi_card, page_header, sidebar, status_badge
from internship_portal.state import AppState
from internship_portal.styles import COLORS, btn_ghost_style, btn_primary_style, main_content_style, page_style, table_style, td_style, th_style


def code_review_modal() -> rx.Component:
    def render_submission(item: dict) -> rx.Component:
        status_color = rx.cond(item["status"] == "Graded", COLORS["success"], rx.cond(item["status"] == "Late", COLORS["warning"], COLORS["primary"]))
        return rx.table.row(
            rx.table.cell(item.get("student_name", "Unknown"), style=td_style),
            rx.table.cell(item.get("student_email", "-"), style=td_style),
            rx.table.cell(status_badge(item.get("status", "Pending"), status_color), style=td_style),
            rx.table.cell(
                rx.vstack(
                    rx.text(item.get("grade", "-"), font_weight="700"),
                    rx.select.root(
                        rx.select.trigger(
                            placeholder="Set grade",
                            background=COLORS["surface_high"],
                            color=COLORS["on_surface"],
                            border=f"1px solid rgba(60, 73, 90, 0.3)",
                            border_radius="10px",
                            padding="8px 12px",
                            min_width="120px",
                            font_weight="600",
                        ),
                        rx.select.content(
                            rx.select.item("A", value="A"),
                            rx.select.item("B", value="B"),
                            rx.select.item("C", value="C"),
                            rx.select.item("D", value="D"),
                            rx.select.item("F", value="F"),
                            background=COLORS["surface_high"],
                            color=COLORS["on_surface"],
                        ),
                        on_change=lambda grade: AppState.grade_submission_action(item["id"], grade),
                    ),
                    align_items="flex_start",
                    gap="8px",
                ),
                style=td_style,
            ),
            rx.table.cell(
                rx.link("Repo", href=item.get("repo_link_url", "#"), is_external=True, color=COLORS["primary"]),
                style=td_style,
            ),
        )

    return rx.cond(
        AppState.show_code_review_modal,
        rx.box(
            rx.center(
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.vstack(
                                rx.text("Submission Review", font_size="1.3rem", font_weight="700", color=COLORS["on_surface"]),
                                rx.text(AppState.selected_assignment_title, color=COLORS["on_surface_variant"]),
                                gap="2px",
                                align_items="flex_start",
                            ),
                            rx.spacer(),
                            rx.text("X", cursor="pointer", font_size="1.2rem", color=COLORS["on_surface_variant"], _hover={"color": COLORS["error"]}, on_click=AppState.close_code_review),
                            width="100%",
                            align="center",
                        ),
                        rx.divider(border_color=f"rgba(60, 73, 90, 0.3)", margin_y="16px"),
                        rx.text(
                            "Choose a grade from the dropdown to save it instantly.",
                            font_size="0.8rem",
                            color=COLORS["on_surface_variant"],
                            margin_bottom="8px",
                        ),
                        rx.cond(
                            AppState.review_submissions.length() > 0,
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("Student", style=th_style),
                                        rx.table.column_header_cell("Email", style=th_style),
                                        rx.table.column_header_cell("Status", style=th_style),
                                        rx.table.column_header_cell("Grade", style=th_style),
                                        rx.table.column_header_cell("Repo", style=th_style),
                                    )
                                ),
                                rx.table.body(rx.foreach(AppState.review_submissions, render_submission)),
                                style=table_style,
                            ),
                            rx.center(rx.text("No submissions available for this assignment yet.", color=COLORS["on_surface_variant"], padding="32px")),
                        ),
                        rx.hstack(
                            rx.button("Close", style=btn_ghost_style, flex="1", on_click=AppState.close_code_review),
                            width="100%",
                        ),
                        width="100%",
                        align_items="flex_start",
                    ),
                    background=COLORS["surface_container"],
                    padding="32px",
                    border_radius="24px",
                    width="900px",
                    max_width="95vw",
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


def teacher_active_assignments() -> rx.Component:
    def render_assignment(item: dict) -> rx.Component:
        return rx.table.row(
            rx.table.cell(
                rx.vstack(
                    rx.text(item.get("title", "Untitled"), font_weight="700", font_size="0.95rem"),
                    rx.text(
                        item.get("description", ""),
                        color=COLORS["on_surface_variant"],
                        font_size="0.8rem",
                        line_limit=2,
                    ),
                    gap="4px",
                    align_items="flex_start",
                ),
                style=td_style,
            ),
            rx.table.cell(
                rx.text(item.get("internship_name", "Unassigned"), color=COLORS["on_surface"]),
                style=td_style,
            ),
            rx.table.cell(
                rx.text(item.get("due_date_display", "N/A"), color=COLORS["on_surface_variant"]),
                style=td_style,
            ),
            rx.table.cell(
                rx.button(
                    "Review Hub",
                    variant="ghost",
                    color=COLORS["primary"],
                    size="1",
                    on_click=lambda: AppState.open_code_review(item["id"], item["title"]),
                ),
                style=td_style,
            ),
        )

    return rx.box(
        rx.cond(
            AppState.teacher_active_assignments_list.length() > 0,
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Assignment", style=th_style),
                            rx.table.column_header_cell("Internship", style=th_style),
                            rx.table.column_header_cell("Due Date", style=th_style),
                            rx.table.column_header_cell("Actions", style=th_style),
                        )
                    ),
                    rx.table.body(rx.foreach(AppState.teacher_active_assignments_list, render_assignment)),
                    style=table_style,
                ),
                width="100%",
                min_width="920px",
            ),
            rx.center(rx.text("No assignments created yet.", color=COLORS["on_surface_variant"], padding="40px")),
        ),
        width="100%",
        overflow_x="auto",
        border=f"1px solid rgba(60, 73, 90, 0.2)",
        border_radius="16px",
    )


def teacher_dashboard() -> rx.Component:
    return rx.box(
        sidebar(active_page="dashboard", role="teacher"),
        rx.box(
            page_header("Faculty Portal", "Create Assignment", "/create-assignment"),
            rx.vstack(
                rx.grid(
                    kpi_card("Active Assignments", AppState.metric_total_assignments.to(str), "AS", COLORS["primary"]),
                    kpi_card("Students", AppState.metric_total_students.to(str), "ST", COLORS["tertiary"]),
                    kpi_card("Pending Reviews", AppState.metric_pending_reviews.to(str), "RV", COLORS["warning"]),
                    kpi_card("Program", AppState.selected_internship, "IN", COLORS["success"]),
                    columns=rx.breakpoints(initial="1", sm="2", lg="4"),
                    width="100%",
                    gap="24px",
                    margin_bottom="32px",
                ),
                rx.hstack(
                    rx.text("Assignments", font_size="1.25rem", font_weight="700"),
                    rx.spacer(),
                    rx.button("Refresh", variant="ghost", font_size="0.875rem", on_click=AppState.on_load_teacher_dashboard),
                    align="center",
                    width="100%",
                    margin_bottom="20px",
                ),
                teacher_active_assignments(),
                width="100%",
                max_width="1400px",
                margin="0 auto",
                align_items="flex_start",
                padding_bottom="60px",
            ),
            style=main_content_style,
        ),
        code_review_modal(),
        on_mount=AppState.on_load_teacher_dashboard,
        **page_style,
    )
