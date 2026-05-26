"""Admin Assignments page for InternPortal."""
import reflex as rx

from internship_portal.components import kpi_card, page_header, sidebar
from internship_portal.pages.teacher_dashboard import code_review_modal, teacher_active_assignments
from internship_portal.state import AppState
from internship_portal.styles import COLORS, btn_primary_style, main_content_style, page_style


def admin_assignments() -> rx.Component:
    return rx.box(
        sidebar(active_page="assignments", role="admin"),
        rx.box(
            page_header("Assignments", "", ""),
            rx.vstack(
                rx.hstack(
                    rx.link(rx.button("+ New Assignment", style=btn_primary_style), href="/create-assignment"),
                    width="100%",
                    justify="end",
                    gap="12px",
                ),
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
                    kpi_card("Assignments", AppState.metric_total_assignments.to(str), "AS", COLORS["primary"]),
                    kpi_card("Pending Reviews", AppState.metric_pending_reviews.to(str), "RV", COLORS["warning"]),
                    columns=rx.breakpoints(initial="1", sm="2"),
                    width="100%",
                    gap="24px",
                    margin_bottom="24px",
                ),
                rx.box(
                    rx.text("Assignments", font_size="1.1rem", font_weight="700", margin_bottom="10px"),
                    teacher_active_assignments(),
                    width="100%",
                    background=COLORS["surface_container"],
                    border=f"1px solid rgba(60, 73, 90, 0.2)",
                    border_radius="16px",
                    padding="16px",
                ),
                width="100%",
                max_width="1400px",
                margin="0 auto",
                align_items="flex_start",
            ),
            style=main_content_style,
        ),
        code_review_modal(),
        on_mount=AppState.on_load_admin_assignments_page,
        **page_style,
    )
