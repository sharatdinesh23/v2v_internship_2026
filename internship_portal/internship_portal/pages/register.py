"""Registration page for InternPortal."""
import reflex as rx

from internship_portal.components import status_badge
from internship_portal.state import AppState, api_request
from internship_portal.styles import COLORS, btn_ghost_style, btn_primary_style, input_style, page_style


def active_program_cards() -> rx.Component:
    def render_program(item: dict) -> rx.Component:
        return rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text(item.get("name", "Untitled Program"), font_size="1rem", font_weight="700", color=COLORS["on_surface"]),
                    status_badge("Active", COLORS["success"]),
                    width="100%",
                    align="center",
                ),
                rx.text(
                    item.get("description", "No description provided."),
                    font_size="0.8rem",
                    color=COLORS["on_surface_variant"],
                    line_height="1.6",
                    line_limit=3,
                ),
                rx.hstack(
                    rx.button(
                        "Choose Program",
                        style=btn_ghost_style,
                        on_click=lambda: RegisterState.set_register_internship(item["id"]),
                    ),
                    rx.text("Select this active program for your account.", font_size="0.75rem", color=COLORS["on_surface_variant"]),
                    width="100%",
                    align="center",
                ),
                gap="12px",
                align_items="flex_start",
            ),
            background=COLORS["surface_container"],
            border=f"1px solid rgba(60, 73, 90, 0.2)",
            border_radius="16px",
            padding="18px",
            width="100%",
        )

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("Active Programs", font_size="1rem", font_weight="700", color=COLORS["on_surface"]),
                rx.text(
                    "Only internships marked active are available for new student registrations.",
                    font_size="0.8rem",
                    color=COLORS["on_surface_variant"],
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.cond(
                RegisterState.active_internships.length() > 0,
                rx.grid(
                    rx.foreach(RegisterState.active_internships, render_program),
                    columns=rx.breakpoints(initial="1", md="2"),
                    gap="14px",
                    width="100%",
                ),
                rx.center(
                    rx.text("No active internship programs are available right now.", color=COLORS["on_surface_variant"]),
                    padding="12px 0",
                    width="100%",
                ),
            ),
            gap="14px",
            width="100%",
            align_items="flex_start",
        ),
        width="100%",
        margin_top="6px",
    )


class RegisterState(AppState):
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""

    def set_first_name(self, val: str):
        self.first_name = val

    def set_last_name(self, val: str):
        self.last_name = val

    def set_email(self, val: str):
        self.email = val

    def set_password(self, val: str):
        self.password = val

    def set_confirm_password(self, val: str):
        self.confirm_password = val

    def set_register_internship(self, val: str):
        self.selected_internship_id = val

    async def handle_register(self):
        full_name = f"{self.first_name.strip()} {self.last_name.strip()}".strip()
        if not full_name or not self.email or not self.password:
            return rx.window_alert("Please complete all required fields.")
        if self.password != self.confirm_password:
            return rx.window_alert("Passwords do not match.")

        try:
            await api_request(
                self.api_url,
                "POST",
                "/api/auth/register",
                json={
                    "name": full_name,
                    "email": self.email,
                    "password": self.password,
                    "internship_id": self.selected_internship_id or None,
                },
            )
            self.first_name = ""
            self.last_name = ""
            self.email = ""
            self.password = ""
            self.confirm_password = ""
            self.selected_internship_id = ""
            return [rx.toast.success("Account created successfully!"), rx.redirect("/")]
        except Exception as exc:
            return rx.window_alert(f"Registration failed: {exc}")


def register_page() -> rx.Component:
    return rx.box(
        rx.box(
            position="fixed",
            top="0",
            left="0",
            right="0",
            bottom="0",
            background_image=f"radial-gradient(circle, rgba(163,166,255,0.08) 1px, transparent 1px)",
            background_size="24px 24px",
            pointer_events="none",
            z_index="0",
        ),
        rx.hstack(
            rx.box(
                rx.vstack(
                    rx.box(
                        rx.text("Join", font_size="1.1rem", font_weight="700", color="white"),
                        background=f"linear-gradient(135deg, {COLORS['primary_dim']}, {COLORS['primary']})",
                        border_radius="16px",
                        padding="16px 18px",
                        margin_bottom="8px",
                    ),
                    rx.text("Student Registration", font_size="2rem", font_weight="800", color=COLORS["on_surface"]),
                    rx.text(
                        "Create your student account to track assignments, attendance, and progress.",
                        font_size="1rem",
                        color=COLORS["on_surface_variant"],
                        text_align="center",
                        max_width="320px",
                    ),
                    rx.divider(border_color=f"rgba(163,166,255,0.15)", margin_y="32px", width="60px"),
                    rx.vstack(
                        rx.hstack(rx.text("1", color=COLORS["primary"], font_weight="700"), rx.text("Choose your internship", color=COLORS["on_surface_variant"]), gap="10px"),
                        rx.hstack(rx.text("2", color=COLORS["primary"], font_weight="700"), rx.text("Create your credentials", color=COLORS["on_surface_variant"]), gap="10px"),
                        rx.hstack(rx.text("3", color=COLORS["primary"], font_weight="700"), rx.text("Sign in and start working", color=COLORS["on_surface_variant"]), gap="10px"),
                        gap="16px",
                        align_items="flex_start",
                    ),
                    gap="16px",
                    align="center",
                    justify="center",
                    height="100%",
                ),
                width="40%",
                height="100vh",
                background=f"linear-gradient(160deg, {COLORS['surface_low']} 0%, {COLORS['surface_container']} 100%)",
                display="flex",
                align_items="center",
                justify_content="center",
                padding="24px",
            ),
            rx.center(
                rx.box(
                    rx.vstack(
                        rx.text("Create Your Account", font_size="2rem", font_weight="800", color=COLORS["on_surface"]),
                        rx.text("Public signup is available for students only.", color=COLORS["on_surface_variant"]),
                        rx.hstack(
                            rx.vstack(
                                rx.text("First Name", font_size="0.8rem", font_weight="600", color=COLORS["on_surface_variant"]),
                                rx.input(value=RegisterState.first_name, on_change=RegisterState.set_first_name, placeholder="John", style=input_style),
                                gap="6px",
                                width="100%",
                                align_items="flex_start",
                            ),
                            rx.vstack(
                                rx.text("Last Name", font_size="0.8rem", font_weight="600", color=COLORS["on_surface_variant"]),
                                rx.input(value=RegisterState.last_name, on_change=RegisterState.set_last_name, placeholder="Doe", style=input_style),
                                gap="6px",
                                width="100%",
                                align_items="flex_start",
                            ),
                            gap="16px",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Email Address", font_size="0.8rem", font_weight="600", color=COLORS["on_surface_variant"]),
                            rx.input(value=RegisterState.email, on_change=RegisterState.set_email, placeholder="student@college.edu", type="email", style=input_style),
                            gap="6px",
                            width="100%",
                            align_items="flex_start",
                        ),
                        rx.vstack(
                            rx.text("Internship Program", font_size="0.8rem", font_weight="600", color=COLORS["on_surface_variant"]),
                            rx.select.root(
                                rx.select.trigger(placeholder="Select an active internship", style=input_style, width="100%"),
                                rx.select.content(
                                    rx.foreach(
                                        RegisterState.active_internships,
                                        lambda item: rx.select.item(item["name"], value=item["id"]),
                                    ),
                                    background=COLORS["surface_high"],
                                    color=COLORS["on_surface"],
                                ),
                                on_change=RegisterState.set_register_internship,
                                value=RegisterState.selected_internship_id,
                            ),
                            rx.text("Optional: leave blank if your program will be assigned later.", font_size="0.75rem", color=COLORS["on_surface_variant"]),
                            gap="6px",
                            width="100%",
                            align_items="flex_start",
                        ),
                        # active_program_cards(),
                        rx.hstack(
                            rx.vstack(
                                rx.text("Password", font_size="0.8rem", font_weight="600", color=COLORS["on_surface_variant"]),
                                rx.input(value=RegisterState.password, on_change=RegisterState.set_password, placeholder="Create a password", type="password", style=input_style),
                                gap="6px",
                                width="100%",
                                align_items="flex_start",
                            ),
                            rx.vstack(
                                rx.text("Confirm Password", font_size="0.8rem", font_weight="600", color=COLORS["on_surface_variant"]),
                                rx.input(value=RegisterState.confirm_password, on_change=RegisterState.set_confirm_password, placeholder="Repeat your password", type="password", style=input_style),
                                gap="6px",
                                width="100%",
                                align_items="flex_start",
                            ),
                            gap="16px",
                            width="100%",
                        ),
                        rx.button("Create Account", on_click=RegisterState.handle_register, style=btn_primary_style, width="100%"),
                        rx.hstack(
                            rx.text("Already have an account?", font_size="0.8rem", color=COLORS["on_surface_variant"]),
                            rx.link("Sign In", href="/", font_size="0.8rem", color=COLORS["primary"], font_weight="600", text_decoration="none"),
                            gap="4px",
                        ),
                        gap="18px",
                        width="100%",
                        align_items="flex_start",
                    ),
                    background="rgba(8, 27, 44, 0.75)",
                    backdrop_filter="blur(24px)",
                    border="1px solid rgba(60, 73, 90, 0.2)",
                    border_radius="24px",
                    padding="40px",
                    width="560px",
                    box_shadow=f"0 0 60px rgba(96, 99, 238, 0.08)",
                ),
                height="100vh",
                flex="1",
            ),
            width="100%",
            gap="0",
        ),
        on_mount=RegisterState.on_load_register,
        **page_style,
        position="relative",
        overflow="hidden",
    )
