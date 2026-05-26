"""Admin Attendance page for InternPortal."""
import reflex as rx

from internship_portal.components import kpi_card, page_header, sidebar
from internship_portal.pages.admin_dashboard import attendance_chart, attendance_table, log_attendance_modal
from internship_portal.state import AppState
from internship_portal.styles import COLORS, btn_primary_style, main_content_style, page_style


def admin_attendance() -> rx.Component:
    return rx.box(
        sidebar(active_page="attendance", role="admin"),
        rx.box(
            page_header("Attendance Management", "", ""),
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
                    rx.spacer(),
                    rx.button("+ Add Attendance", style=btn_primary_style, on_click=AppState.open_attendance_modal),
                    width="100%",
                    margin_bottom="20px",
                ),
                rx.grid(
                    kpi_card("Students", AppState.metric_total_students.to(str), "ST", COLORS["primary"]),
                    kpi_card("On-Time", AppState.metric_on_time_count.to(str), "OK", COLORS["success"]),
                    columns=rx.breakpoints(initial="1", sm="2"),
                    width="100%",
                    gap="24px",
                    margin_bottom="24px",
                ),
                rx.hstack(
                    rx.box(attendance_table(), width="65%"),
                    rx.box(attendance_chart(), width="35%"),
                    width="100%",
                    gap="24px",
                    align_items="flex_start",
                ),
                width="100%",
                max_width="1400px",
                margin="0 auto",
                align_items="flex_start",
            ),
            style=main_content_style,
        ),
        log_attendance_modal(),
        on_mount=AppState.on_load_admin_attendance_page,
        **page_style,
    )
