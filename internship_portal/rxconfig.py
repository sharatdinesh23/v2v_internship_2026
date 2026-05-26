import reflex as rx

config = rx.Config(
    app_name="internship_portal",
    api_url="http://127.0.0.1:8010",
    backend_port=8010,
    frontend_port=3000,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)
