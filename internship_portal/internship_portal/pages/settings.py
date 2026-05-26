"""Settings page for InternPortal."""
import reflex as rx

from internship_portal.components import page_header, sidebar
from internship_portal.state import AppState
from internship_portal.styles import COLORS, btn_ghost_style, btn_primary_style, input_style, main_content_style, page_style
import httpx


class SettingState(AppState):
    pass

def settings_page() -> rx.Component:
    return rx.box(
        rx.cond(AppState.current_role == "student", sidebar(active_page="settings", role="student")),
        rx.cond(AppState.current_role == "teacher", sidebar(active_page="settings", role="teacher")),
        rx.cond(AppState.current_role == "admin", sidebar(active_page="settings", role="admin")),
        rx.box(
            page_header("Settings", "", ""),
            rx.vstack(
                rx.flex(
                    rx.box(
                        rx.vstack(
                            rx.text("Profile Information", font_size="1.1rem", font_weight="700", margin_bottom="16px"),
                            rx.vstack(
                                rx.text("Full Name", font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="600"),
                                rx.input(value=AppState.profile_name, on_change=AppState.set_profile_name, style=input_style),
                                width="100%",
                                align_items="flex_start",
                                margin_bottom="16px",
                            ),
                            rx.vstack(
                                rx.text("Email Address", font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="600"),
                                rx.input(value=AppState.profile_email, style=input_style, disabled=True, opacity="0.6"),
                                width="100%",
                                align_items="flex_start",
                                margin_bottom="16px",
                            ),
                            rx.grid(
                                rx.vstack(
                                    rx.text("Role", font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="600"),
                                    rx.input(value=AppState.profile_role_label, style=input_style, disabled=True, opacity="0.6"),
                                    width="100%",
                                    align_items="flex_start",
                                ),
                                rx.vstack(
                                    rx.text("Internship", font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="600"),
                                    rx.select.root(
                                rx.select.trigger(placeholder="Select an active internship", style=input_style, width="100%"),
                                rx.select.content(
                                    rx.foreach(
                                        AppState.active_internships,
                                        lambda item: rx.select.item(item["name"], value=item["id"]),
                                    ),
                                    background=COLORS["surface_high"],
                                    color=COLORS["on_surface"],
                                ),
                                on_change=AppState.set_selected_internship,
                                value=AppState.selected_internship_id,
                            ),
                                    width="100%",
                                    align_items="flex_start",
                                ),
                                columns=rx.breakpoints(initial="1", sm="2"),
                                gap="16px",
                                width="100%",
                                margin_bottom="24px",
                            ),
                            rx.grid(
                                rx.button("Save Changes", on_click=AppState.save_profile, style=btn_primary_style),
                                rx.link(
                                    rx.button("Back to Dashboard", style=btn_ghost_style),
                                    href=rx.cond(
                                        AppState.current_role == "admin",
                                        "/admin-dashboard",
                                        rx.cond(
                                            AppState.current_role == "teacher",
                                            "/teacher-dashboard",
                                            "/student-dashboard",
                                        ),
                                    ),
                                    text_decoration="none",
                                ),
                                columns=rx.breakpoints(initial="1", sm="2"),
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
                        width=rx.breakpoints(initial="100%", lg="55%"),
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Change Password", font_size="1.1rem", font_weight="700", margin_bottom="16px"),
                            rx.vstack(
                                rx.text("Current Password", font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="600"),
                                rx.input(type="password", value=AppState.current_password, on_change=AppState.set_current_password, style=input_style, placeholder="Current password"),
                                width="100%",
                                align_items="flex_start",
                                margin_bottom="16px",
                            ),
                            rx.vstack(
                                rx.text("New Password", font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="600"),
                                rx.input(type="password", value=AppState.new_password, on_change=AppState.set_new_password, style=input_style, placeholder="New password"),
                                width="100%",
                                align_items="flex_start",
                                margin_bottom="16px",
                            ),
                            rx.vstack(
                                rx.text("Confirm New Password", font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="600"),
                                rx.input(type="password", value=AppState.confirm_password, on_change=AppState.set_confirm_password, style=input_style, placeholder="Repeat new password"),
                                width="100%",
                                align_items="flex_start",
                                margin_bottom="24px",
                            ),
                            rx.button("Update Password", on_click=AppState.update_password, style=btn_primary_style, width="100%"),
                            width="100%",
                            align_items="flex_start",
                        ),
                        background="rgba(18, 39, 60, 0.4)",
                        backdrop_filter="blur(16px)",
                        border=f"1px solid rgba(60, 73, 90, 0.2)",
                        border_radius="16px",
                        padding="32px",
                        width=rx.breakpoints(initial="100%", lg="45%"),
                    ),
                    flex_direction=rx.breakpoints(initial="column", lg="row"),
                    gap="24px",
                    width="100%",
                    align_items="stretch",
                ),
                width="100%",
                max_width="1400px",
                margin="0 auto",
                align_items="flex_start",
                padding_bottom="60px",
            ),
            style=main_content_style,
        ),
        on_mount=AppState.on_load_settings,
        **page_style,
    )


