"""Student Dashboard page for InternPortal."""
import reflex as rx

from internship_portal.components import kpi_card, page_header, sidebar, status_badge
from internship_portal.state import AppState
from internship_portal.styles import COLORS, btn_ghost_style, btn_primary_style, main_content_style, page_style, table_style, td_style, th_style


def submission_modal() -> rx.Component:
    return rx.cond(
        AppState.show_submission_modal,
        rx.box(
            rx.center(
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text(AppState.submission_modal_title, font_size="1.5rem", font_weight="700", color=COLORS["on_surface"]),
                            rx.spacer(),
                            rx.text("X", cursor="pointer", font_size="1.2rem", color=COLORS["on_surface_variant"], _hover={"color": COLORS["error"]}, on_click=AppState.close_submission_modal),
                            width="100%",
                            align="center",
                        ),
                        rx.divider(border_color=f"rgba(60, 73, 90, 0.3)", margin_y="16px"),
                        rx.vstack(
                            rx.text("Assignment", font_size="0.8rem", font_weight="600", color=COLORS["on_surface_variant"]),
                            rx.select.root(
                                rx.select.trigger(placeholder="Choose an assignment", background=COLORS["surface_high"], color=COLORS["on_surface"], border="none", border_radius="8px", width="100%", padding="12px"),
                                rx.select.content(
                                    rx.foreach(
                                        AppState.student_assignments,
                                        lambda assignment: rx.select.item(assignment["title"], value=assignment["id"]),
                                    ),
                                    background=COLORS["surface_high"],
                                    color=COLORS["on_surface"],
                                ),
                                value=AppState.submission_assignment,
                                on_change=AppState.set_submission_assignment,
                            ),
                            gap="8px",
                            width="100%",
                            align_items="flex_start",
                        ),
                        rx.vstack(
                            rx.text("Repository Link", font_size="0.8rem", font_weight="600", color=COLORS["on_surface_variant"]),
                            rx.input(
                                value=AppState.submission_repo_link,
                                on_change=AppState.set_submission_repo_link,
                                placeholder="https://github.com/your-project",
                                background=COLORS["surface_high"],
                                color=COLORS["on_surface"],
                                border="none",
                                border_radius="10px",
                                padding="12px 16px",
                                width="100%",
                                height="50px",
                            ),
                            rx.text("Paste the GitHub or repository URL for your submission.", font_size="0.75rem", color=COLORS["on_surface_variant"]),
                            gap="8px",
                            width="100%",
                            align_items="flex_start",
                        ),
                        rx.hstack(
                            rx.button("Cancel", on_click=AppState.close_submission_modal, style=btn_ghost_style, flex="1"),
                            rx.button(AppState.submission_submit_label, on_click=AppState.submit_assignment_action, style=btn_primary_style, flex="1"),
                            width="100%",
                            gap="16px",
                        ),
                        width="100%",
                        align_items="flex_start",
                    ),
                    background=COLORS["surface_container"],
                    padding="32px",
                    border_radius="24px",
                    width="500px",
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


def note_reader_modal() -> rx.Component:
    """Full-screen modal to read the complete note."""
    return rx.cond(
        AppState.show_note_modal,
        rx.box(
            rx.center(
                rx.box(
                    rx.vstack(
                        # Header
                        rx.hstack(
                            rx.vstack(
                                rx.text(
                                    AppState.selected_note.get("title", "Note"),
                                    font_size="1.4rem",
                                    font_weight="700",
                                    color=COLORS["on_surface"],
                                    line_height="1.3",
                                ),
                                rx.text(
                                    f"Posted: {AppState.selected_note.get('created_at_display', 'N/A')}",
                                    font_size="0.75rem",
                                    color=COLORS["on_surface_variant"],
                                ),
                                gap="4px",
                                align_items="flex_start",
                            ),
                            rx.spacer(),
                            rx.box(
                                rx.text("✕", font_size="1.1rem", color=COLORS["on_surface_variant"]),
                                cursor="pointer",
                                padding="6px 10px",
                                border_radius="8px",
                                _hover={"background": "rgba(255,107,122,0.12)", "color": COLORS["error"]},
                                on_click=AppState.close_note_modal,
                                transition="all 0.15s ease",
                            ),
                            width="100%",
                            align="start",
                        ),
                        rx.divider(border_color=f"rgba(60, 73, 90, 0.3)", margin_y="16px"),
                        # Scrollable markdown content
                        rx.box(
                            rx.markdown(AppState.selected_note.get("markdown_content", "")),
                            width="100%",
                            overflow_y="auto",
                            max_height="60vh",
                            padding_right="8px",
                        ),
                        rx.hstack(
                            rx.button(
                                "Close",
                                on_click=AppState.close_note_modal,
                                style=btn_ghost_style,
                            ),
                            width="100%",
                            justify="end",
                            margin_top="16px",
                        ),
                        width="100%",
                        align_items="flex_start",
                        gap="0",
                    ),
                    background=COLORS["surface_container"],
                    padding="32px",
                    border_radius="24px",
                    width=rx.breakpoints(initial="95vw", md="720px"),
                    max_width="720px",
                    box_shadow="0 0 80px rgba(0, 0, 0, 0.6)",
                    border=f"1px solid rgba(60, 73, 90, 0.3)",
                    max_height="90vh",
                    overflow="hidden",
                ),
                width="100vw",
                height="100vh",
            ),
            position="fixed",
            top="0",
            left="0",
            width="100vw",
            height="100vh",
            background="rgba(2, 15, 30, 0.85)",
            backdrop_filter="blur(10px)",
            z_index="1100",
        ),
        rx.box(),
    )


def assignments_panel() -> rx.Component:
    def render_assignment(item: dict) -> rx.Component:
        status_color = rx.cond(
            item.get("submission_status") == "Submitted",
            COLORS["success"],
            rx.cond(item.get("submission_status") == "Late", COLORS["error"], COLORS["warning"]),
        )
        return rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text(item.get("title", "Untitled"), font_weight="700", color=COLORS["on_surface"]),
                    rx.spacer(),
                    status_badge(item.get("submission_status", "Due"), status_color),
                    width="100%",
                ),
                rx.text(item.get("description", ""), color=COLORS["on_surface_variant"], font_size="0.875rem", line_limit=2),
                rx.text(f"Due: {item.get('due_date_display', 'N/A')}", font_size="0.75rem", color=COLORS["on_surface_variant"]),
                rx.cond(
                    item.get("has_submission"),
                    rx.cond(
                        item.get("can_resubmit"),
                        rx.button(
                            "Resubmit Work",
                            on_click=lambda: AppState.open_submission_modal(
                                item["id"],
                                item["title"],
                                item.get("submission_repo_link", ""),
                                "Resubmit Work",
                            ),
                            style=btn_primary_style,
                            width="100%",
                        ),
                        rx.button(
                            "Graded",
                            style=btn_ghost_style,
                            width="100%",
                            disabled=True,
                            opacity="0.7",
                            cursor="not-allowed",
                        ),
                    ),
                    rx.button(
                        "Submit Work",
                        on_click=lambda: AppState.open_submission_modal(item["id"], item["title"], "", "Submit Work"),
                        style=btn_primary_style,
                        width="100%",
                    ),
                ),
                gap="10px",
                width="100%",
                align_items="flex_start",
            ),
            background=COLORS["surface_container"],
            border_radius="16px",
            padding="20px",
            border=f"1px solid rgba(60, 73, 90, 0.2)",
            width="100%",
        )

    return rx.box(
        rx.text("Assigned Work", font_size="1.25rem", font_weight="700", margin_bottom="16px"),
        rx.cond(
            AppState.student_assignments.length() > 0,
            rx.grid(
                rx.foreach(AppState.student_assignments, render_assignment),
                columns=rx.breakpoints(initial="1", md="2"),
                width="100%",
                gap="20px",
            ),
            rx.center(rx.text("No assignments available right now.", color=COLORS["on_surface_variant"], padding="40px")),
        ),
        width="100%",
    )


def notes_panel() -> rx.Component:
    def render_note(item: dict) -> rx.Component:
        return rx.box(
            rx.vstack(
                # Title row
                rx.hstack(
                    rx.text("📝", font_size="1rem", color=COLORS["primary"]),
                    rx.text(
                        item.get("title", "Untitled"),
                        font_weight="700",
                        font_size="0.95rem",
                        color=COLORS["on_surface"],
                        line_limit=2,
                    ),
                    width="100%",
                    align="start",
                    gap="8px",
                ),
                # Date
                rx.text(
                    f"Posted: {item.get('created_at_display', 'N/A')}",
                    font_size="0.72rem",
                    color=COLORS["on_surface_variant"],
                ),
                rx.divider(border_color="rgba(60, 73, 90, 0.15)", margin_y="8px"),
                # Short preview — plain text
                rx.box(
                    rx.text(
                        item.get("markdown_content", ""),
                        color=COLORS["on_surface_variant"],
                        font_size="0.85rem",
                        line_limit=4,
                        line_height="1.6",
                        white_space="pre-wrap",
                    ),
                    width="100%",
                    padding="10px 12px",
                    background=COLORS["surface_high"],
                    border_radius="10px",
                ),
                # Read More button
                rx.button(
                    rx.hstack(
                        rx.text("Read More", font_size="0.8rem", font_weight="600"),
                        rx.text("→", font_size="0.85rem"),
                        gap="4px",
                        align="center",
                    ),
                    on_click=lambda: AppState.open_note_modal(item),
                    background="transparent",
                    color=COLORS["primary"],
                    border=f"1px solid {COLORS['primary']}",
                    border_radius="8px",
                    padding="6px 14px",
                    height="32px",
                    font_size="0.8rem",
                    cursor="pointer",
                    width="100%",
                    _hover={"background": "rgba(163, 166, 255, 0.12)"},
                    transition="all 0.15s ease",
                    margin_top="4px",
                ),
                width="100%",
                align_items="flex_start",
                gap="8px",
            ),
            background=COLORS["surface_container"],
            border_radius="16px",
            padding="18px",
            border=f"1px solid rgba(60, 73, 90, 0.2)",
            width="100%",
            transition="box-shadow 0.2s ease",
            _hover={"box_shadow": "0 4px 20px rgba(163, 166, 255, 0.08)", "border_color": "rgba(163, 166, 255, 0.25)"},
        )

    return rx.box(
        rx.text("Notes & Resources", font_size="1.25rem", font_weight="700", margin_bottom="16px"),
        rx.cond(
            AppState.student_notes.length() > 0,
            rx.grid(
                rx.foreach(AppState.student_notes, render_note),
                columns=rx.breakpoints(initial="1", md="2", lg="3"),
                width="100%",
                gap="20px",
            ),
            rx.center(rx.text("No notes posted yet.", color=COLORS["on_surface_variant"], padding="40px")),
        ),
        width="100%",
    )


def submissions_table() -> rx.Component:
    def render_row(record: dict) -> rx.Component:
        status_color = rx.cond(record["status"] == "Graded", COLORS["success"], rx.cond(record["status"] == "Late", COLORS["warning"], COLORS["primary"]))
        return rx.table.row(
            rx.table.cell(f"#{record.get('id', '')}", style=td_style),
            rx.table.cell(record.get("assignment_title", "Unknown"), style=td_style, font_weight="600"),
            rx.table.cell(record.get("submitted_at_display", "N/A"), style=td_style, color=COLORS["on_surface_variant"]),
            rx.table.cell(status_badge(record.get("status", "Pending"), status_color), style=td_style),
            rx.table.cell(record.get("grade", "-"), style=td_style),
            rx.table.cell(
                rx.link("Open", href=record.get("repo_link_url", "#"), is_external=True, color=COLORS["primary"]),
                style=td_style,
            ),
            _hover={"background": "rgba(255, 255, 255, 0.02)"},
        )

    return rx.box(
        rx.cond(
            AppState.student_submissions_history.length() > 0,
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("ID", style=th_style),
                        rx.table.column_header_cell("Assignment", style=th_style),
                        rx.table.column_header_cell("Submitted On", style=th_style),
                        rx.table.column_header_cell("Status", style=th_style),
                        rx.table.column_header_cell("Grade", style=th_style),
                        rx.table.column_header_cell("Repo", style=th_style),
                    ),
                ),
                rx.table.body(rx.foreach(AppState.student_submissions_history, render_row)),
                style=table_style,
            ),
            rx.center(rx.text("No submissions found yet. Time to get to work!", color=COLORS["on_surface_variant"], padding="40px")),
        ),
        border=f"1px solid rgba(60, 73, 90, 0.2)",
        border_radius="16px",
        overflow_x="auto",
        width="100%",
    )


def student_dashboard() -> rx.Component:
    return rx.box(
        sidebar(active_page="dashboard", role="student"),
        rx.box(
            page_header("Student Dashboard", "Submit Assignment", ""),
            rx.vstack(
                rx.grid(
                    kpi_card("Assignments", f"{AppState.metric_total_assignments}", "AS", COLORS["tertiary"]),
                    kpi_card("Submissions", f"{AppState.metric_total_submissions}", "SB", COLORS["primary"]),
                    kpi_card("On-Time", f"{AppState.metric_on_time_count}", "OK", COLORS["success"]),
                    columns=rx.breakpoints(initial="1", sm="2", lg="4"),
                    width="100%",
                    gap="24px",
                    margin_bottom="32px",
                ),
                assignments_panel(),
                notes_panel(),
                rx.text("Submission History", font_size="1.25rem", font_weight="700", margin_bottom="16px"),
                submissions_table(),
                width="100%",
                max_width="1200px",
                margin="0 auto",
                align_items="flex_start",
            ),
            style=main_content_style,
        ),
        submission_modal(),
        note_reader_modal(),
        on_mount=AppState.on_load_student_dashboard,
        **page_style,
    )
