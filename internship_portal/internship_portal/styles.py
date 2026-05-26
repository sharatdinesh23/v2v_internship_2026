"""Design system tokens and shared styling for the portal."""
import reflex as rx

# ─── Color Palette ──────────────────────────────────────────────────────────────
COLORS = {
    "bg": "#020f1e",
    "surface": "#020f1e",
    "surface_low": "#041425",
    "surface_container": "#081b2c",
    "surface_high": "#0d2134",
    "surface_highest": "#12273c",
    "surface_bright": "#172d45",
    "primary": "#a3a6ff",
    "primary_dim": "#6063ee",
    "primary_container": "#9396ff",
    "on_primary": "#0f00a4",
    "on_surface": "#d9e7fc",
    "on_surface_variant": "#9eacc0",
    "outline": "#697789",
    "outline_variant": "#3c495a",
    "secondary": "#d8e3fb",
    "secondary_container": "#3c475a",
    "error": "#ff6e84",
    "success": "#4ade80",
    "warning": "#fbbf24",
    "amber": "#f59e0b",
    "tertiary": "#ffa5d9",
}

# ─── Typography ─────────────────────────────────────────────────────────────────
FONTS = {
    "family": "Inter, system-ui, sans-serif",
    "display": "2.5rem",
    "h1": "1.875rem",
    "h2": "1.5rem",
    "h3": "1.25rem",
    "body": "0.875rem",
    "label": "0.75rem",
}

# ─── Shared Component Styles ────────────────────────────────────────────────────
card_style = {
    "background": COLORS["surface_container"],
    "border_radius": "16px",
    "padding": "24px",
    "box_shadow": f"0 0 40px rgba(163, 166, 255, 0.04)",
}

glass_style = {
    "background": "rgba(18, 39, 60, 0.6)",
    "backdrop_filter": "blur(24px)",
    "border": f"1px solid rgba(60, 73, 90, 0.15)",
    "border_radius": "16px",
}

sidebar_style = {
    **glass_style,
    "width": "260px",
    "min_height": "100vh",
    "padding": "24px 16px",
    "display": "flex",
    "flex_direction": "column",
    "gap": "8px",
    "position": "fixed",
    "top": "0",
    "left": "0",
    "z_index": "100",
}

btn_primary_style = {
    "background": f"linear-gradient(135deg, {COLORS['primary_dim']}, {COLORS['primary']})",
    "color": "white",
    "border_radius": "9999px",
    "padding": "0 28px",
    "height": "48px",
    "display": "flex",
    "align_items": "center",
    "justify_content": "center",
    "font_weight": "600",
    "font_size": "0.9rem",
    "cursor": "pointer",
    "border": "none",
    "box_shadow": f"0 0 20px rgba(96, 99, 238, 0.3)",
    "_hover": {
        "box_shadow": f"0 0 30px rgba(163, 166, 255, 0.5)",
        "transform": "translateY(-1px)",
    },
    "transition": "all 0.2s ease",
}

btn_ghost_style = {
    "background": "transparent",
    "color": COLORS["primary"],
    "border_radius": "9999px",
    "padding": "0 28px",
    "height": "48px",
    "display": "flex",
    "align_items": "center",
    "justify_content": "center",
    "font_weight": "600",
    "font_size": "0.9rem",
    "cursor": "pointer",
    "border": f"1px solid rgba(60, 73, 90, 0.3)",
    "_hover": {
        "background": "rgba(163, 166, 255, 0.05)",
    },
    "transition": "all 0.2s ease",
}

input_style = {
    "background": COLORS["surface_high"],
    "border": "none",
    "border_radius": "8px",
    "padding": "8px 16px",
    "height": "48px",
    "color": COLORS["on_surface"],
    "font_size": "0.875rem",
    "width": "100%",
    "outline": "none",
    "_focus": {
        "border_bottom": f"1px solid {COLORS['primary']}",
    },
}

page_style = {
    "background": COLORS["bg"],
    "min_height": "100vh",
    "font_family": FONTS["family"],
    "color": COLORS["on_surface"],
}

main_content_style = {
    "margin_left": rx.breakpoints(initial="0", md="260px"),
    "padding": rx.breakpoints(initial="16px", md="32px"),
    "min_height": "100vh",
    "background": COLORS["bg"],
}

badge_style = {
    "border_radius": "9999px",
    "padding": "4px 12px",
    "font_size": "0.7rem",
    "font_weight": "600",
    "text_transform": "uppercase",
    "letter_spacing": "0.05em",
}

table_style = {
    "width": "100%",
    "border_collapse": "collapse",
    "background": COLORS["surface_container"],
    "border_radius": "16px",
    "overflow": "hidden",
}

th_style = {
    "padding": "14px 20px",
    "text_align": "left",
    "font_size": "0.7rem",
    "text_transform": "uppercase",
    "letter_spacing": "0.05em",
    "color": COLORS["on_surface_variant"],
    "background": COLORS["surface_high"],
    "font_weight": "600",
}

td_style = {
    "padding": "16px 20px",
    "font_size": "0.875rem",
    "color": COLORS["on_surface"],
    "border_bottom": f"1px solid rgba(60, 73, 90, 0.2)",
}
