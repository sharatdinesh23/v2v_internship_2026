"""Shared UI components for the portal."""
import reflex as rx
from internship_portal.styles import COLORS, btn_primary_style, btn_ghost_style
from internship_portal.state import AppState


def nav_item(label: str, icon: str, href: str, active: bool = False) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.text(icon, font_size="1.1rem"),
            rx.text(label, font_size="0.875rem", font_weight="500"),
            align="center",
            gap="12px",
            padding="12px 16px",
            border_radius="12px",
            background=rx.cond(active, "rgba(163, 166, 255, 0.15)", "transparent"),
            color=rx.cond(active, COLORS["primary"], COLORS["on_surface_variant"]),
            width="100%",
            _hover={
                "background": "rgba(163, 166, 255, 0.08)",
                "color": COLORS["primary"],
            },
            cursor="pointer",
            transition="all 0.2s ease",
        ),
        href=href,
        text_decoration="none",
        width="100%",
    )


def sidebar(active_page: str = "dashboard", role: str = "student") -> rx.Component:
    """Glassmorphism collapsible sidebar."""
    items_student = [
        ("Dashboard", "⊞", "/student-dashboard", active_page == "dashboard"),
        ("Settings", "⚙", "/settings", active_page == "settings"),
    ]
    items_teacher = [
        ("Dashboard", "⊞", "/teacher-dashboard", active_page == "dashboard"),
        ("Assignments", "📋", "/teacher-assignments", active_page == "assignments"),
        ("Notes", "📝", "/teacher-notes", active_page == "notes"),
        ("Students", "👥", "/teacher-students", active_page == "students"),
        ("Reports", "📊", "/teacher-reports", active_page == "reports"),
        ("Settings", "⚙", "/settings", active_page == "settings"),
    ]
    items_admin = [
        ("Dashboard", "⊞", "/admin-dashboard", active_page == "dashboard"),
        ("Internships", "🏢", "/admin-internships", active_page == "internships"),
        ("Teachers", "T", "/admin-teachers", active_page == "teachers"),
        ("Assignments", "📋", "/admin-assignments", active_page == "assignments"),
        ("Notes", "📝", "/admin-notes", active_page == "notes"),
        ("Students", "👥", "/admin-students", active_page == "students"),
        ("Attendance", "📅", "/admin-attendance", active_page == "attendance"),
        ("Reports", "📊", "/admin-reports", active_page == "reports"),
        ("Settings", "⚙", "/settings", active_page == "settings"),
    ]
    items = items_student if role == "student" else (items_teacher if role == "teacher" else items_admin)

    return rx.box(
        rx.vstack(
            # Logo
            rx.hstack(
                rx.box(
                    rx.text("⚡", font_size="1.25rem"),
                    background=f"linear-gradient(135deg, {COLORS['primary_dim']}, {COLORS['primary']})",
                    border_radius="10px",
                    padding="8px",
                    width="36px",
                    height="36px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                rx.vstack(
                    rx.text("InternPortal", font_weight="700", font_size="0.95rem", color=COLORS["on_surface"]),
                    rx.text(role.capitalize(), font_size="0.65rem", color=COLORS["primary"], text_transform="uppercase", letter_spacing="0.08em"),
                    gap="0",
                    align_items="flex_start",
                ),
                align="center",
                gap="10px",
                padding_bottom="24px",
                padding_x="8px",
            ),
            # Nav items
            rx.vstack(
                *[nav_item(label, icon, href, active) for label, icon, href, active in items],
                gap="4px",
                width="100%",
                flex="1",
            ),
            # User info at bottom
            rx.divider(border_color=f"rgba(60, 73, 90, 0.3)", margin_y="16px"),
            rx.hstack(
                rx.box(
                    rx.text("RS", color="white", font_size="0.8rem", font_weight="700"),
                    background=f"linear-gradient(135deg, {COLORS['primary_dim']}, {COLORS['primary']})",
                    border_radius="50%",
                    width="36px",
                    height="36px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                rx.vstack(
                    rx.text(
                        rx.cond(AppState.profile_name != "", AppState.profile_name, AppState.current_role), 
                        font_size="0.8rem", font_weight="600", color=COLORS["on_surface"]
                    ),
                    rx.text(
                        rx.cond(AppState.profile_dept != "", AppState.profile_dept, "OFFICIAL"), 
                        font_size="0.7rem", color=COLORS["on_surface_variant"]
                    ),
                    gap="0",
                    align_items="flex_start",
                ),
                rx.spacer(),
                rx.button(
                    rx.text("->", color=COLORS["on_surface_variant"], font_size="1rem"),
                    on_click=AppState.handle_logout,
                    background="transparent",
                    border="none",
                    cursor="pointer",
                    title="Logout",
                    padding="0",
                ),
                align="center",
                gap="10px",
                padding_x="8px",
            ),
            gap="0",
            width="100%",
            height="100%",
            align_items="flex_start",
        ),
        position="fixed",
        top="0",
        left="0",
        width="260px",
        height="100vh",
        background="rgba(8, 27, 44, 0.85)",
        backdrop_filter="blur(24px)",
        border_right=f"1px solid rgba(60, 73, 90, 0.2)",
        padding="24px 16px",
        z_index="100",
        overflow_y="auto",
        display=rx.breakpoints(initial="none", md="flex"),
    )


def page_header(title: str, action_label: str = "", action_href: str = "") -> rx.Component:
    return rx.hstack(
        rx.text(title, font_size="1.5rem", font_weight="700", color=COLORS["on_surface"]),
        rx.spacer(),
        rx.hstack(
            rx.cond(
                action_label != "",
                rx.link(
                    rx.button(
                        rx.text("+ " + action_label),
                        style=btn_primary_style,
                    ),
                    href=action_href,
                ),
                rx.box(),
            ),
            rx.link(
                rx.box(
                    rx.text("RS", color="white", font_size="0.75rem", font_weight="700"),
                    background=f"linear-gradient(135deg, {COLORS['primary_dim']}, {COLORS['primary']})",
                    border_radius="50%",
                    width="36px",
                    height="36px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    cursor="pointer",
                ),
                href="/settings",
                text_decoration="none",
            ),
            gap="12px",
            align="center",
        ),
        width="100%",
        align="center",
        padding_bottom="24px",
        border_bottom=f"1px solid rgba(60, 73, 90, 0.2)",
        margin_bottom="28px",
    )


def kpi_card(label: str, value: str, icon: str, color: str = "#a3a6ff") -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.text(icon, font_size="1.4rem"),
                    background="rgba(163, 166, 255, 0.12)",
                    border_radius="12px",
                    padding="10px",
                    width="48px",
                    height="48px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                rx.spacer(),
                align="center",
                width="100%",
            ),
            rx.text(value, font_size="2rem", font_weight="700", color=COLORS["on_surface"], letter_spacing="-0.02em"),
            rx.text(label, font_size="0.8rem", color=COLORS["on_surface_variant"], font_weight="500"),
            gap="8px",
            align_items="flex_start",
        ),
        background=COLORS["surface_container"],
        border_radius="16px",
        padding="24px",
        flex="1",
        box_shadow="0 0 40px rgba(163, 166, 255, 0.04)",
        border_left=f"3px solid {color}",
        _hover={"box_shadow": f"0 0 30px rgba(163, 166, 255, 0.1)"},
        transition="all 0.2s ease",
    )


def status_badge(status: str, color: str | rx.Var = "#a3a6ff") -> rx.Component:
    return rx.box(
        rx.text(status, font_size="0.7rem", font_weight="600"),
        background="rgba(163, 166, 255, 0.1)", # Use a safe default for background
        color=color,
        border_radius="9999px",
        padding="4px 12px",
        text_transform="uppercase",
        letter_spacing="0.05em",
        display="inline_block",
        border=f"1px solid rgba(163, 166, 255, 0.2)",
    )


def search_filter_bar() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.text("🔍", font_size="0.9rem", color=COLORS["on_surface_variant"]),
            rx.input(
                placeholder="Search students or assignments...",
                background="transparent",
                border="none",
                color=COLORS["on_surface"],
                outline="none",
                font_size="0.875rem",
                width="220px",
                _placeholder={"color": COLORS["on_surface_variant"]},
            ),
            background=COLORS["surface_high"],
            border_radius="10px",
            padding="8px 16px",
            align="center",
            gap="8px",
        ),
        rx.select.root(
            rx.select.trigger(
                placeholder="Filter",
                background=COLORS["surface_high"],
                border="none",
                color=COLORS["on_surface"],
                border_radius="10px",
                padding="8px 16px",
                font_size="0.875rem",
            ),
            rx.select.content(
                rx.select.item("All", value="all"),
                rx.select.item("Submitted", value="submitted"),
                rx.select.item("Pending", value="pending"),
                background=COLORS["surface_high"],
                color=COLORS["on_surface"],
            ),
        ),
        rx.select.root(
            rx.select.trigger(
                placeholder="All Submissions",
                background=COLORS["surface_high"],
                border="none",
                color=COLORS["on_surface"],
                border_radius="10px",
                padding="8px 16px",
                font_size="0.875rem",
            ),
            rx.select.content(
                rx.select.item("All Submissions", value="all"),
                rx.select.item("On Time", value="on_time"),
                rx.select.item("Late", value="late"),
                background=COLORS["surface_high"],
                color=COLORS["on_surface"],
            ),
        ),
        gap="12px",
        flex_wrap="wrap",
    )
