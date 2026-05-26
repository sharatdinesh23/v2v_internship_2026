"""Login page for InternPortal."""
import reflex as rx
from internship_portal.styles import COLORS, btn_primary_style, btn_ghost_style, input_style, page_style


def role_btn(label: str, role: str, active_role: str) -> rx.Component:
    is_active = active_role == role
    return rx.button(
        label,
        background=f"linear-gradient(135deg, {COLORS['primary_dim']}, {COLORS['primary']})" if is_active else "transparent",
        color=COLORS["primary"] if not is_active else "white",
        border=f"1px solid {COLORS['primary_dim']}",
        border_radius="9999px",
        padding="8px 20px",
        font_size="0.8rem",
        font_weight="600",
        cursor="pointer",
        transition="all 0.2s ease",
        _hover={"background": f"linear-gradient(135deg, {COLORS['primary_dim']}, {COLORS['primary']})", "color": "white"},
    )


from internship_portal.state import AppState, api_request
from internship_portal.logger import logger

class LoginState(AppState):
    role: str = "student"
    email: str = ""
    password: str = ""
    show_password: bool = False

    def set_role(self, role: str):
        self.role = role # Only used for UI styling now!

    def set_email(self, val: str):
        self.email = val

    def set_password(self, val: str):
        self.password = val

    def toggle_show_password(self):
        self.show_password = not self.show_password

    async def handle_login(self):
        """Dynamic backend JWT evaluation natively mapping actual Database identities."""
        if not self.email or not self.password:
            return rx.window_alert("Please enter both email and password")

        try:
            data = await api_request(
                self.api_url,
                "POST",
                "/api/auth/login",
                json={"email": self.email, "password": self.password},
            )
            self.auth_token = data.get("access_token", "")
            self.current_user_id = data.get("user", {}).get("id", "")
            self.internship_id = data.get("internship_id") or ""
            self.internship_name = data.get("internship_name") or ""
            self.selected_internship = self.internship_name or "N/A"
            self.current_role = data.get("role", "student")
            self.profile_name = data.get("user", {}).get("name", "")
            self.profile_email = data.get("user", {}).get("email", "")
            self.is_logged_in = True
            
            logger.bind(user_id=self.current_user_id, service="frontend").info(f"Frontend User login successful: {self.email}")
            
            self.email = ""
            self.password = ""

            if self.current_role == "teacher":
                return rx.redirect("/teacher-dashboard")
            if self.current_role == "admin":
                return rx.redirect("/admin-dashboard")
            return rx.redirect("/student-dashboard")
        except Exception as e:
            logger.bind(service="frontend", error_code="FRONTEND_LOGIN_FAIL").warning(f"Frontend User login failed for {self.email}: {e}")
            return rx.window_alert(f"Login Failed: {str(e)}")




def login_page() -> rx.Component:
    return rx.box(
        # Dot grid background
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
            # ── Left Branding Panel ──────────────────────────────────────────
            rx.box(
                rx.vstack(
                    rx.box(
                        # rx.text("⚡", font_size="2rem"),
                        rx.image(src="/channels4_profile.jpg", width="120%", height="auto"),
                        background=f"linear-gradient(135deg, {COLORS['primary_dim']}, {COLORS['primary']})",
                        border_radius="16px",
                        padding="16px",
                        width="64px",
                        height="64px",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        margin_bottom="8px",
                    ),
                    rx.text("V2V Classes", font_size="2rem", font_weight="800", color=COLORS["on_surface"], letter_spacing="-0.03em"),
                    rx.text(
                        "Empowering Diploma Students",
                        font_size="1rem",
                        color=COLORS["on_surface_variant"],
                        text_align="center",
                        max_width="280px",
                    ),
                    rx.divider(border_color=f"rgba(163,166,255,0.15)", margin_y="32px", width="60px"),
                    rx.vstack(
                        rx.hstack(
                            rx.text("✓", color=COLORS["primary"], font_weight="700"),
                            rx.text("Track attendance in real-time", font_size="0.9rem", color=COLORS["on_surface_variant"]),
                            gap="10px", align="center",
                        ),
                        rx.hstack(
                            rx.text("✓", color=COLORS["primary"], font_weight="700"),
                            rx.text("Submit assignments with ease", font_size="0.9rem", color=COLORS["on_surface_variant"]),
                            gap="10px", align="center",
                        ),
                        rx.hstack(
                            rx.text("✓", color=COLORS["primary"], font_weight="700"),
                            rx.text("Monitor your progress", font_size="0.9rem", color=COLORS["on_surface_variant"]),
                            gap="10px", align="center",
                        ),
                        rx.hstack(
                            rx.text("✓", color=COLORS["primary"], font_weight="700"),
                            rx.text("Role-based access control", font_size="0.9rem", color=COLORS["on_surface_variant"]),
                            gap="10px", align="center",
                        ),
                        gap="16px",
                        align_items="flex_start",
                    ),
                    # Decorative orb
                    rx.box(
                        position="absolute",
                        bottom="10%",
                        left="10%",
                        width="200px",
                        height="200px",
                        border_radius="50%",
                        background=f"radial-gradient(circle, rgba(96,99,238,0.25), transparent)",
                        filter="blur(40px)",
                        pointer_events="none",
                    ),
                    gap="16px",
                    align="center",
                    justify="center",
                    height="100%",
                    position="relative",
                    z_index="1",
                ),
                width="45%",
                height="100vh",
                background=f"linear-gradient(160deg, {COLORS['surface_low']} 0%, {COLORS['surface_container']} 100%)",
                display="flex",
                align_items="center",
                justify_content="center",
                position="relative",
                overflow="hidden",
            ),
            # ── Right Login Form Panel ───────────────────────────────────────
            rx.center(
                rx.box(
                    rx.vstack(
                        rx.text("Welcome Back", font_size="2rem", font_weight="800", color=COLORS["on_surface"], letter_spacing="-0.02em"),
                        rx.text("Sign in to your Internship Portal account", font_size="0.875rem", color=COLORS["on_surface_variant"]),
                        # Role selector
                        # rx.hstack(
                        #     rx.button("Student", on_click=LoginState.set_role("student"),
                        #         background=rx.cond(LoginState.role == "student", f"linear-gradient(135deg, {COLORS['primary_dim']}, {COLORS['primary']})", "transparent"),
                        #         color=rx.cond(LoginState.role == "student", "white", COLORS["primary"]),
                        #         border=f"1px solid {COLORS['primary_dim']}", border_radius="9999px", padding="8px 20px", font_size="0.8rem", font_weight="600", cursor="pointer", transition="all 0.2s ease"),
                        #     rx.button("Teacher", on_click=LoginState.set_role("teacher"),
                        #         background=rx.cond(LoginState.role == "teacher", f"linear-gradient(135deg, {COLORS['primary_dim']}, {COLORS['primary']})", "transparent"),
                        #         color=rx.cond(LoginState.role == "teacher", "white", COLORS["primary"]),
                        #         border=f"1px solid {COLORS['primary_dim']}", border_radius="9999px", padding="8px 20px", font_size="0.8rem", font_weight="600", cursor="pointer", transition="all 0.2s ease"),
                        #     rx.button("Admin", on_click=LoginState.set_role("admin"),
                        #         background=rx.cond(LoginState.role == "admin", f"linear-gradient(135deg, {COLORS['primary_dim']}, {COLORS['primary']})", "transparent"),
                        #         color=rx.cond(LoginState.role == "admin", "white", COLORS["primary"]),
                        #         border=f"1px solid {COLORS['primary_dim']}", border_radius="9999px", padding="8px 20px", font_size="0.8rem", font_weight="600", cursor="pointer", transition="all 0.2s ease"),
                        #     gap="8px",
                        #     background=COLORS["surface_low"],
                        #     border_radius="9999px",
                        #     padding="4px",
                        # ),
                        # Email field
                        rx.vstack(
                            rx.text("Email", font_size="0.8rem", font_weight="600", color=COLORS["on_surface_variant"]),
                            rx.hstack(
                                rx.text("✉", font_size="0.9rem", color=COLORS["on_surface_variant"]),
                                rx.input(
                                    value=LoginState.email,
                                    placeholder="you@college.edu",
                                    on_change=LoginState.set_email,
                                    type="email",
                                    background="transparent",
                                    border="none",
                                    outline="none",
                                    color=COLORS["on_surface"],
                                    font_size="0.875rem",
                                    width="100%",
                                    _placeholder={"color": COLORS["on_surface_variant"]},
                                ),
                                background=COLORS["surface_high"],
                                border_radius="10px",
                                padding="12px 16px",
                                align="center",
                                gap="10px",
                                width="100%",
                            ),
                            gap="6px",
                            width="100%",
                            align_items="flex_start",
                        ),
                        # Password field
                        rx.vstack(
                            rx.hstack(
                                rx.text("Password", font_size="0.8rem", font_weight="600", color=COLORS["on_surface_variant"]),
                                rx.spacer(),
                                rx.text("Forgot Password?", font_size="0.75rem", color=COLORS["primary"], cursor="pointer"),
                                width="100%", align="center",
                            ),
                            rx.hstack(
                                rx.text("🔒", font_size="0.9rem", color=COLORS["on_surface_variant"]),
                                rx.input(
                                    value=LoginState.password,
                                    placeholder="Enter your password",
                                    on_change=LoginState.set_password,
                                    type=rx.cond(LoginState.show_password, "text", "password"),
                                    background="transparent",
                                    border="none",
                                    outline="none",
                                    color=COLORS["on_surface"],
                                    font_size="0.875rem",
                                    width="100%",
                                    _placeholder={"color": COLORS["on_surface_variant"]},
                                ),
                                rx.text(
                                    rx.cond(LoginState.show_password, "🙈", "👁"),
                                    font_size="0.9rem",
                                    cursor="pointer",
                                    on_click=LoginState.toggle_show_password,
                                    color=COLORS["on_surface_variant"],
                                ),
                                background=COLORS["surface_high"],
                                border_radius="10px",
                                padding="12px 16px",
                                align="center",
                                gap="10px",
                                width="100%",
                            ),
                            gap="6px",
                            width="100%",
                            align_items="flex_start",
                        ),
                        # Sign In button
                        rx.button(
                            "Sign In →",
                            on_click=LoginState.handle_login,
                            background=f"linear-gradient(135deg, {COLORS['primary_dim']}, {COLORS['primary']})",
                            color="white",
                            border_radius="9999px",
                            padding="14px",
                            font_weight="700",
                            font_size="0.95rem",
                            width="100%",
                            cursor="pointer",
                            border="none",
                            box_shadow=f"0 0 20px rgba(96, 99, 238, 0.4)",
                            _hover={"box_shadow": f"0 0 35px rgba(163, 166, 255, 0.5)", "transform": "translateY(-1px)"},
                            transition="all 0.2s ease",
                        ),
                        # Divider
                        # rx.hstack(
                        #     rx.divider(border_color=f"rgba(60, 73, 90, 0.4)", flex="1"),
                        #     rx.text("or continue with", font_size="0.75rem", color=COLORS["on_surface_variant"], white_space="nowrap"),
                        #     rx.divider(border_color=f"rgba(60, 73, 90, 0.4)", flex="1"),
                        #     align="center", gap="12px", width="100%",
                        # ),
                        # # Google button
                        # rx.button(
                        #     rx.hstack(
                        #         rx.text("G", font_weight="800", color="#4285F4", font_size="1rem"),
                        #         rx.text("Sign in with Google", font_weight="600", font_size="0.875rem"),
                        #         gap="10px", align="center",
                        #     ),
                        #     background=COLORS["surface_high"],
                        #     color=COLORS["on_surface"],
                        #     border_radius="9999px",
                        #     padding="12px",
                        #     width="100%",
                        #     border="none",
                        #     cursor="pointer",
                        #     _hover={"background": COLORS["surface_highest"]},
                        #     transition="all 0.2s ease",
                        # ),
                        # Register link
                        rx.hstack(
                            rx.text("Don't have an account?", font_size="0.8rem", color=COLORS["on_surface_variant"]),
                            rx.link("Register here", href="/register", font_size="0.8rem", color=COLORS["primary"], font_weight="600", text_decoration="none"),
                            gap="4px",
                        ),
                        # SSL badge
                        rx.hstack(
                            rx.text("🔐", font_size="0.8rem"),
                            rx.text("Secured by SSL", font_size="0.7rem", color=COLORS["on_surface_variant"]),
                            gap="6px",
                        ),
                        gap="20px",
                        align_items="flex_start",
                        width="100%",
                    ),
                    background="rgba(8, 27, 44, 0.75)",
                    backdrop_filter="blur(24px)",
                    border="1px solid rgba(60, 73, 90, 0.2)",
                    border_radius="24px",
                    padding="40px",
                    width="420px",
                    box_shadow=f"0 0 60px rgba(96, 99, 238, 0.08)",
                ),
                height="100vh",
                flex="1",
            ),
            width="100%",
            gap="0",
        ),
        **page_style,
        position="relative",
        overflow="hidden",
    )
