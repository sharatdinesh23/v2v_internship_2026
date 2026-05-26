"""Admin Teacher Access page for InternPortal."""
import reflex as rx

from internship_portal.components import kpi_card, page_header, sidebar, status_badge
from internship_portal.state import AppState
from internship_portal.styles import COLORS, btn_ghost_style, btn_primary_style, input_style, main_content_style, page_style, table_style, td_style, th_style


def teacher_access_form() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.vstack(
                rx.text("Grant Teacher Access", font_size="1.25rem", font_weight="700", color=COLORS["on_surface"]),
                rx.text(
                    "Create a login for a teacher and optionally attach them to an internship.",
                    color=COLORS["on_surface_variant"],
                    font_size="0.875rem",
                ),
                gap="6px",
                align_items="flex_start",
                width="100%",
            ),
            rx.grid(
                rx.vstack(
                    rx.text("Teacher Name", font_size="0.8rem", font_weight="600", color=COLORS["on_surface_variant"]),
                    rx.input(
                        value=AppState.teacher_name_input,
                        on_change=AppState.set_teacher_name_input,
                        placeholder="Dr. Sarah Khan",
                        style=input_style,
                    ),
                    gap="6px",
                    align_items="flex_start",
                ),
                rx.vstack(
                    rx.text("Teacher Email", font_size="0.8rem", font_weight="600", color=COLORS["on_surface_variant"]),
                    rx.input(
                        value=AppState.teacher_email_input,
                        on_change=AppState.set_teacher_email_input,
                        placeholder="teacher@college.edu",
                        type="email",
                        style=input_style,
                    ),
                    gap="6px",
                    align_items="flex_start",
                ),
                columns=rx.breakpoints(initial="1", sm="2"),
                gap="16px",
                width="100%",
            ),
            rx.grid(
                rx.vstack(
                    rx.text("Temporary Password", font_size="0.8rem", font_weight="600", color=COLORS["on_surface_variant"]),
                    rx.input(
                        value=AppState.teacher_password_input,
                        on_change=AppState.set_teacher_password_input,
                        placeholder="Create a temporary password",
                        type="password",
                        style=input_style,
                    ),
                    rx.text(
                        "The teacher can change this password later from Settings.",
                        color=COLORS["on_surface_variant"],
                        font_size="0.75rem",
                    ),
                    gap="6px",
                    align_items="flex_start",
                ),
                rx.vstack(
                    rx.text("Assign Internship", font_size="0.8rem", font_weight="600", color=COLORS["on_surface_variant"]),
                    rx.select.root(
                        rx.select.trigger(
                            placeholder="Optional: choose a program",
                            background=COLORS["surface_high"],
                            color=COLORS["on_surface"],
                            border="none",
                            border_radius="8px",
                            padding="12px 16px",
                            width="100%",
                        ),
                        rx.select.content(
                            rx.foreach(
                                AppState.all_internships,
                                lambda internship: rx.select.item(internship["name"], value=internship["id"]),
                            ),
                            background=COLORS["surface_high"],
                            color=COLORS["on_surface"],
                        ),
                        value=AppState.teacher_internship_id,
                        on_change=AppState.set_teacher_internship_id,
                    ),
                    rx.text(
                        "Leave it blank if the teacher will be assigned later.",
                        color=COLORS["on_surface_variant"],
                        font_size="0.75rem",
                    ),
                    gap="6px",
                    align_items="flex_start",
                ),
                columns=rx.breakpoints(initial="1", sm="2"),
                gap="16px",
                width="100%",
            ),
            rx.hstack(
                rx.button("Create Teacher Access", style=btn_primary_style, on_click=AppState.create_teacher_access),
                rx.button("Refresh", style=btn_ghost_style, on_click=AppState.on_load_admin_teachers_page),
                width="100%",
                gap="12px",
                align="center",
            ),
            gap="22px",
            width="100%",
            align_items="flex_start",
        ),
        background=COLORS["surface_container"],
        border_radius="20px",
        padding="28px",
        border=f"1px solid rgba(60, 73, 90, 0.2)",
        box_shadow="0 0 40px rgba(163, 166, 255, 0.04)",
        width="100%",
    )


def teacher_directory_table() -> rx.Component:
    def render_row(teacher: dict) -> rx.Component:
        return rx.table.row(
            rx.table.cell(rx.text(teacher.get("name", "Unknown"), font_weight="600"), style=td_style),
            rx.table.cell(rx.text(teacher.get("email", "-"), color=COLORS["on_surface_variant"]), style=td_style),
            rx.table.cell(rx.text(teacher.get("internship_name", "Unassigned")), style=td_style),
            rx.table.cell(status_badge("Enabled", COLORS["success"]), style=td_style),
        )

    return rx.box(
        rx.cond(
            AppState.available_teachers.length() > 0,
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Teacher", style=th_style),
                        rx.table.column_header_cell("Email", style=th_style),
                        rx.table.column_header_cell("Internship", style=th_style),
                        rx.table.column_header_cell("Access", style=th_style),
                    )
                ),
                rx.table.body(rx.foreach(AppState.available_teachers, render_row)),
                style=table_style,
            ),
            rx.center(
                rx.text(
                    "No teacher accounts have been created yet.",
                    color=COLORS["on_surface_variant"],
                    padding="40px",
                )
            ),
        ),
        border=f"1px solid rgba(60, 73, 90, 0.2)",
        border_radius="16px",
        overflow_x="auto",
        width="100%",
    )


def admin_teachers_page() -> rx.Component:
    return rx.box(
        sidebar(active_page="teachers", role="admin"),
        rx.box(
            page_header("Teacher Access", "", ""),
            rx.vstack(
                rx.grid(
                    kpi_card("Teachers", AppState.available_teachers.length().to(str), "TR", COLORS["primary"]),
                    kpi_card("Programs", AppState.all_internships.length().to(str), "IN", COLORS["tertiary"]),
                    columns=rx.breakpoints(initial="1", sm="2"),
                    width="100%",
                    gap="24px",
                    margin_bottom="24px",
                ),
                rx.grid(
                    teacher_access_form(),
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text("Teacher Directory", font_size="1.25rem", font_weight="700"),
                                rx.spacer(),
                                rx.button("Reload", variant="ghost", on_click=AppState.on_load_admin_teachers_page),
                                align="center",
                                width="100%",
                            ),
                            teacher_directory_table(),
                            gap="18px",
                            width="100%",
                            align_items="flex_start",
                        ),
                        background=COLORS["surface_container"],
                        border_radius="20px",
                        padding="28px",
                        border=f"1px solid rgba(60, 73, 90, 0.2)",
                        box_shadow="0 0 40px rgba(163, 166, 255, 0.04)",
                        width="100%",
                    ),
                    columns=rx.breakpoints(initial="1", xl="2"),
                    gap="24px",
                    width="100%",
                ),
                width="100%",
                max_width="1400px",
                margin="0 auto",
                align_items="flex_start",
                padding_bottom="60px",
            ),
            style=main_content_style,
        ),
        on_mount=AppState.on_load_admin_teachers_page,
        **page_style,
    )
