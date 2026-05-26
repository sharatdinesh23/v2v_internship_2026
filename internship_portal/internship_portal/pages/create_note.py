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
                value=AppState.note_internship_id,
                on_change=AppState.set_note_internship_id,
            ),
            width="100%",
            align_items="flex_start",
            margin_bottom="16px",
        ),
        rx.box(),
    )


def create_note() -> rx.Component:
    def markdown_toolbar() -> rx.Component:
        actions = [
            ("H1", "h1"), ("H2", "h2"), ("H3", "h3"),
            ("B", "bold"), ("I", "italic"), ("S", "strike"),
            ("</>", "inline_code"), ("Quote", "blockquote"),
            ("UL", "ul"), ("OL", "ol"), ("Task", "task"),
            ("Link", "link"), ("Image", "image"), ("HR", "hr"),
            ("Code", "code_block"), ("Table", "table"), ("Math", "math"),
        ]
        return rx.hstack(
            rx.foreach(
                actions,
                lambda action: rx.button(
                    action[0],
                    size="1",
                    variant="soft",
                    on_click=AppState.insert_markdown_template(action[1]),
                ),
            ),
            width="100%",
            gap="8px",
            wrap="wrap",
            margin_bottom="10px",
        )

    return rx.box(
        rx.cond(AppState.current_role == "teacher", sidebar(active_page="assignments", role="teacher")),
        rx.cond(AppState.current_role == "admin", sidebar(active_page="assignments", role="admin")),
        rx.box(
            page_header(rx.cond(AppState.editing_note_id != "", "Edit Note (.md)", "Create Note (.md)"), "", ""),
            rx.vstack(
                rx.text("Note Details", font_size="1.25rem", font_weight="700", margin_bottom="16px"),
                rx.box(
                    rx.vstack(
                        internship_selector(),
                        rx.vstack(
                            rx.text("Note Title", font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="600"),
                            rx.input(value=AppState.note_title_input, on_change=AppState.set_note_title_input, placeholder="e.g. Week-3 Backend Patterns", style=input_style),
                            width="100%",
                            align_items="flex_start",
                            margin_bottom="16px",
                        ),
                        rx.vstack(
                            rx.text("Markdown Content", font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="600"),
                            markdown_toolbar(),
                            rx.grid(
                                rx.text_area(
                                    value=AppState.note_markdown_input,
                                    on_change=AppState.set_note_markdown_input,
                                    placeholder="# Topic\n\n- Point 1\n- Point 2\n\n```python\nprint('hello')\n```",
                                    style=input_style,
                                    min_height="320px",
                                    font_family="monospace",
                                ),
                                rx.box(
                                    rx.text("Preview", font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="600", margin_bottom="8px"),
                                    rx.box(
                                        rx.markdown(AppState.note_markdown_input),
                                        min_height="280px",
                                        background=COLORS["surface_high"],
                                        border=f"1px solid rgba(60, 73, 90, 0.25)",
                                        border_radius="10px",
                                        padding="12px",
                                        overflow_y="auto",
                                    ),
                                    width="100%",
                                ),
                                columns=rx.breakpoints(initial="1", lg="2"),
                                gap="14px",
                                width="100%",
                            ),
                            width="100%",
                            align_items="flex_start",
                            margin_bottom="24px",
                        ),
                        rx.hstack(
                            rx.button(rx.cond(AppState.editing_note_id != "", "Update Note", "Publish Note"), style=btn_primary_style, on_click=AppState.create_note_action),
                            rx.button("Cancel", style=btn_ghost_style, on_click=AppState.cancel_note_edit),
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
        on_mount=AppState.on_load_create_note,
        **page_style,
    )
