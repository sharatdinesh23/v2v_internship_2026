"""Admin Reports page for InternPortal."""
import reflex as rx

from internship_portal.components import kpi_card, page_header, sidebar
from internship_portal.pages.admin_dashboard import attendance_chart, attendance_table
from internship_portal.state import AppState
from internship_portal.styles import COLORS, main_content_style, page_style


def admin_reports() -> rx.Component:
    return rx.box(
        sidebar(active_page="reports", role="admin"),
        rx.box(
            page_header("Global Analytics & Reports", "", ""),
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
                    kpi_card("Assignments", AppState.metric_total_assignments.to(str), "AS", COLORS["primary"]),
                    kpi_card("Students", AppState.metric_total_students.to(str), "ST", COLORS["tertiary"]),
                    kpi_card("Submissions", AppState.metric_total_submissions.to(str), "SB", COLORS["primary"]),
                    kpi_card("Late", AppState.metric_late_count.to(str), "LT", COLORS["warning"]),
                    columns=rx.breakpoints(initial="1", sm="2", lg="4"),
                    width="100%",
                    gap="24px",
                    margin_bottom="24px",
                ),
                attendance_chart(),
                attendance_table(),
                width="100%",
                max_width="1400px",
                margin="0 auto",
                align_items="flex_start",
                gap="24px",
            ),
            style=main_content_style,
        ),
        on_mount=AppState.on_load_admin_reports_page,
        **page_style,
    )
