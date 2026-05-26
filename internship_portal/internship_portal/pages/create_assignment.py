"""Create Assignment page for InternPortal."""
import reflex as rx

from internship_portal.components import page_header, sidebar
from internship_portal.state import AppState
from internship_portal.styles import COLORS, btn_ghost_style, btn_primary_style, input_style, main_content_style, page_style


def internship_selector() -> rx.Component:
    return rx.cond(
        AppState.current_role == "admin",
        rx.vstack(
            rx.text("Internship", font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="600"),
            rx.select.root(
                rx.select.trigger(background=COLORS["surface_high"], color=COLORS["on_surface"], border="none", border_radius="10px", padding="12px 16px", width="100%"),
                rx.select.content(
                    rx.foreach(AppState.all_internships, lambda internship: rx.select.item(internship["name"], value=internship["id"])),
                    background=COLORS["surface_high"],
                    color=COLORS["on_surface"],
                ),
                value=AppState.assignment_internship_id,
                on_change=AppState.set_assignment_internship_id,
            ),
            width="100%",
            align_items="flex_start",
            margin_bottom="16px",
        ),
        rx.box(),
    )


def create_assignment() -> rx.Component:
    return rx.box(
        rx.cond(AppState.current_role == "teacher", sidebar(active_page="assignments", role="teacher")),
        rx.cond(AppState.current_role == "admin", sidebar(active_page="assignments", role="admin")),
        rx.box(
            page_header("Create Assignment", "", ""),
            rx.vstack(
                rx.text("Assignment Details", font_size="1.25rem", font_weight="700", margin_bottom="16px"),
                rx.box(
                    rx.vstack(
                        internship_selector(),
                        rx.vstack(
                            rx.text("Assignment Name", font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="600"),
                            rx.input(value=AppState.assignment_title_input, on_change=AppState.set_assignment_title_input, placeholder="e.g. Build a Web App", style=input_style),
                            width="100%",
                            align_items="flex_start",
                            margin_bottom="16px",
                        ),
                        rx.vstack(
                            rx.text("Assignment Description", font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="600"),
                            rx.text_area(value=AppState.assignment_description_input, on_change=AppState.set_assignment_description_input, placeholder="Detailed instructions...", style=input_style, min_height="120px"),
                            width="100%",
                            align_items="flex_start",
                            margin_bottom="16px",
                        ),
                        rx.grid(
                            rx.vstack(
                                rx.text("Assignment Document Link", font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="600"),
                                rx.input(value=AppState.assignment_doc_link_input, on_change=AppState.set_assignment_doc_link_input, placeholder="https://drive.google.com/...", style=input_style),
                                width="100%",
                                align_items="flex_start",
                            ),
                            rx.vstack(
                                rx.text("Assignment Due Date", font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="600"),
                                rx.input(type="date", value=AppState.assignment_due_date_input, on_change=AppState.set_assignment_due_date_input, style=input_style),
                                width="100%",
                                align_items="flex_start",
                            ),
                            columns=rx.breakpoints(initial="1", sm="2"),
                            gap="16px",
                            width="100%",
                            margin_bottom="24px",
                        ),
                        rx.hstack(
                            rx.button("Publish Assignment", style=btn_primary_style, on_click=AppState.create_assignment_action),
                            rx.link(rx.button("Cancel", style=btn_ghost_style), href=rx.cond(AppState.current_role == "admin", "/admin-assignments", "/teacher-assignments")),
                            gap="12px",
                            width="100%",
                        ),
                        width="100%",
                        align_items="flex_start",
                    ),
                    background="rgba(18, 39, 60, 0.4)",
                    backdrop_filter="blur(16px)",
                    border=f"1px solid rgba(60, 73, 90, 0.2)",
                    border_radius="16px",
                    padding="32px",
                    width="100%",
                    max_width="900px",
                ),
                width="100%",
                align_items="flex_start",
            ),
            style=main_content_style,
        ),
        on_mount=AppState.on_load_create_assignment,
        **page_style,
    )
