"""Teacher Notes page for InternPortal."""
import reflex as rx

from internship_portal.components import kpi_card, page_header, sidebar
from internship_portal.state import AppState
from internship_portal.styles import COLORS, btn_ghost_style, btn_primary_style, main_content_style, page_style


def teacher_notes() -> rx.Component:
    note_action_btn_style = {
        "height": "30px",
        "min_width": "64px",
        "padding": "0 12px",
        "font_size": "0.75rem",
        "font_weight": "600",
        "border_radius": "8px",
    }

    def render_note(item: dict) -> rx.Component:
        return rx.box(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text(item.get("title", "Untitled"), font_weight="700", font_size="1rem", color=COLORS["on_surface"]),
                        rx.text(
                            f"Posted: {item.get('created_at_display', 'N/A')}",
                            font_size="0.72rem",
                            color=COLORS["on_surface_variant"],
                        ),
                        gap="2px",
                        align_items="flex_start",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.button(
                            "Edit",
                            variant="soft",
                            style={**note_action_btn_style, "background": "rgba(163, 166, 255, 0.18)", "color": COLORS["primary"]},
                            on_click=lambda: AppState.open_note_editor(
                                item["id"],
                                item["title"],
                                item["markdown_content"],
                                item["internship_id"],
                            ),
                        ),
                        rx.button(
                            "Delete",
                            variant="soft",
                            style={**note_action_btn_style, "background": "rgba(255, 107, 122, 0.16)", "color": COLORS["error"]},
                            on_click=lambda: AppState.delete_note_action(item["id"]),
                        ),
                        gap="8px",
                    ),
                    width="100%",
                    align="start",
                ),
                rx.divider(border_color="rgba(60, 73, 90, 0.2)", margin_y="8px"),
                rx.box(
                    rx.markdown(item.get("markdown_content", "")),
                    width="100%",
                    max_height="260px",
                    overflow="hidden",
                    padding="12px",
                    background=COLORS["surface_high"],
                    border_radius="10px",
                    position="relative",
                    _after={
                        "content": '""',
                        "position": "absolute",
                        "bottom": "0",
                        "left": "0",
                        "right": "0",
                        "height": "60px",
                        "background": f"linear-gradient(transparent, {COLORS['surface_container']})",
                        "border_radius": "0 0 10px 10px",
                        "pointer_events": "none",
                    },
                ),
                width="100%",
                align_items="flex_start",
                gap="6px",
            ),
            background=COLORS["surface_container"],
            border_radius="16px",
            padding="18px",
            border=f"1px solid rgba(60, 73, 90, 0.2)",
            width="100%",
            transition="box-shadow 0.2s ease",
            _hover={"box_shadow": "0 4px 24px rgba(163, 166, 255, 0.08)"},
        )

    return rx.box(
        sidebar(active_page="notes", role="teacher"),
        rx.box(
            page_header("Notes & Resources", "", ""),
            rx.vstack(
                rx.hstack(
                    rx.link(rx.button("+ New Note (.md)", style=btn_primary_style), href="/create-note"),
                    width="100%",
                    justify="end",
                    gap="12px",
                ),
                rx.grid(
                    kpi_card("Total Notes", AppState.teacher_notes_list.length().to(str), "📝", COLORS["primary"]),
                    columns=rx.breakpoints(initial="1", sm="2"),
                    width="100%",
                    gap="24px",
                    margin_bottom="24px",
                ),
                rx.box(
                    rx.text("Notes (.md)", font_size="1.1rem", font_weight="700", margin_bottom="16px", color=COLORS["on_surface"]),
                    rx.cond(
                        AppState.teacher_notes_list.length() > 0,
                        rx.grid(
                            rx.foreach(AppState.teacher_notes_list, render_note),
                            columns=rx.breakpoints(initial="1", md="2"),
                            width="100%",
                            gap="20px",
                        ),
                        rx.center(
                            rx.vstack(
                                rx.text("📝", font_size="2.5rem"),
                                rx.text("No notes posted yet.", color=COLORS["on_surface_variant"], font_size="0.9rem"),
                                rx.link(rx.button("+ Create First Note", style=btn_ghost_style), href="/create-note"),
                                gap="12px",
                                align="center",
                            ),
                            padding="48px",
                        ),
                    ),
                    width="100%",
                    background=COLORS["surface_container"],
                    border=f"1px solid rgba(60, 73, 90, 0.2)",
                    border_radius="16px",
                    padding="20px",
                ),
                width="100%",
                max_width="1400px",
                margin="0 auto",
                align_items="flex_start",
            ),
            style=main_content_style,
        ),
        on_mount=AppState.on_load_teacher_assignments_page,
        **page_style,
    )
