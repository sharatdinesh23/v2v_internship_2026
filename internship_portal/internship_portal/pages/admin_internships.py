"""Admin Internship Management page for InternPortal."""
import reflex as rx

from internship_portal.components import page_header, sidebar
from internship_portal.state import AppState
from internship_portal.styles import COLORS, btn_ghost_style, btn_primary_style, input_style, main_content_style, page_style, table_style, td_style, th_style


def internship_modal() -> rx.Component:
    def teacher_chip(teacher: dict) -> rx.Component:
        is_selected = AppState.selected_teacher_ids.contains(teacher["id"])
        return rx.button(
            teacher["name"],
            on_click=lambda: AppState.toggle_teacher_selection(teacher["id"]),
            background=rx.cond(is_selected, f"linear-gradient(135deg, {COLORS['primary_dim']}, {COLORS['primary']})", COLORS["surface_high"]),
            color=rx.cond(is_selected, "white", COLORS["on_surface"]),
            border="none",
            border_radius="9999px",
            padding="8px 14px",
            font_size="0.8rem",
            cursor="pointer",
        )

    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title(
                    rx.cond(AppState.editing_internship_id != "", "Edit Internship", "Create New Internship"),
                    color=COLORS["on_surface"],
                ),
                rx.dialog.description(
                    "Define internship details and assign teachers.",
                    color=COLORS["on_surface_variant"],
                    margin_bottom="16px",
                ),
                rx.vstack(
                    rx.text("Internship Name", font_size="0.8rem", font_weight="600"),
                    rx.input(
                        placeholder="e.g. Web Development Summer 2026",
                        value=AppState.new_internship_name,
                        on_change=AppState.set_new_internship_name,
                        style=input_style,
                        width="100%",
                    ),
                    rx.text("Description", font_size="0.8rem", font_weight="600", margin_top="12px"),
                    rx.text_area(
                        placeholder="Enter program details...",
                        value=AppState.new_internship_desc,
                        on_change=AppState.set_new_internship_desc,
                        style=input_style,
                        width="100%",
                        height="100px",
                    ),
                    rx.text("Assign Teachers", font_size="0.8rem", font_weight="600", margin_top="12px"),
                    rx.flex(
                        rx.foreach(AppState.available_teachers, teacher_chip),
                        gap="10px",
                        flex_wrap="wrap",
                        width="100%",
                    ),
                    width="100%",
                    align_items="flex_start",
                ),
                rx.hstack(
                    rx.dialog.close(rx.button("Cancel", style=btn_ghost_style, on_click=AppState.close_internship_modal)),
                    rx.button("Save Internship", style=btn_primary_style, on_click=AppState.save_internship),
                    width="100%",
                    justify="end",
                    gap="12px",
                    margin_top="24px",
                ),
                width="100%",
            ),
            background=COLORS["surface_container"],
            border=f"1px solid rgba(60, 73, 90, 0.3)",
            border_radius="24px",
            padding="32px",
            max_width="620px",
        ),
        open=AppState.show_internship_modal,
        on_open_change=lambda _: AppState.close_internship_modal(),
    )


def internships_table() -> rx.Component:
    def render_row(item: dict) -> rx.Component:
        status_color = rx.cond(item["is_active"], COLORS["success"], COLORS["error"])
        status_text = rx.cond(item["is_active"], "Active", "Inactive")
        return rx.table.row(
            rx.table.cell(rx.text(item["name"], font_weight="600"), style=td_style),
            rx.table.cell(rx.text(item.get("description", ""), color=COLORS["on_surface_variant"], max_width="260px"), style=td_style),
            rx.table.cell(rx.text(item.get("teacher_names", "Unassigned")), style=td_style),
            rx.table.cell(
                rx.box(
                    rx.text(status_text, font_size="0.7rem", font_weight="600"),
                    background=rx.cond(item["is_active"], "rgba(94, 255, 144, 0.1)", "rgba(255, 94, 94, 0.1)"),
                    color=status_color,
                    border_radius="9999px",
                    padding="4px 12px",
                    display="inline_block",
                ),
                style=td_style,
            ),
            rx.table.cell(
                rx.hstack(
                    rx.button("Edit", size="1", color_scheme="blue", variant="ghost", on_click=lambda: AppState.open_internship_modal(item)),
                    rx.button("Activate", size="1", color_scheme="green", variant="ghost", on_click=lambda: AppState.set_internship_status(item["id"], True)),
                    rx.button("Deactivate", size="1", color_scheme="red", variant="ghost", on_click=lambda: AppState.set_internship_status(item["id"], False)),
                    gap="8px",
                    flex_wrap="wrap",
                ),
                style=td_style,
            ),
        )

    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Program Name", style=th_style),
                    rx.table.column_header_cell("Description", style=th_style),
                    rx.table.column_header_cell("Teachers", style=th_style),
                    rx.table.column_header_cell("Status", style=th_style),
                    rx.table.column_header_cell("Actions", style=th_style),
                )
            ),
            rx.table.body(rx.foreach(AppState.all_internships, render_row)),
            style=table_style,
        ),
        border=f"1px solid rgba(60, 73, 90, 0.2)",
        border_radius="16px",
        overflow="hidden",
        width="100%",
        margin_top="16px",
    )


def admin_internships_page() -> rx.Component:
    return rx.box(
        sidebar(active_page="internships", role="admin"),
        rx.box(
            page_header("Internship Management", "", ""),
            rx.vstack(
                rx.hstack(
                    rx.button("+ Create New Program", style=btn_primary_style, on_click=AppState.open_internship_modal),
                    rx.link(
                        rx.button("Teacher Access", style=btn_ghost_style),
                        href="/admin-teachers",
                        text_decoration="none",
                    ),
                    rx.spacer(),
                    rx.button("Refresh List", variant="soft", on_click=AppState.on_load_internships),
                    width="100%",
                    margin_bottom="16px",
                ),
                internships_table(),
                width="100%",
                max_width="1400px",
                margin="0 auto",
                align_items="flex_start",
                padding_bottom="60px",
            ),
            style=main_content_style,
        ),
        internship_modal(),
        on_mount=AppState.on_load_internships,
        **page_style,
    )
