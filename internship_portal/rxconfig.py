import os
import reflex as rx

# Reflex frontend will connect to the backend event server at this URL
api_url = os.getenv("REFLEX_API_URL", "http://127.0.0.1:8010")

config = rx.Config(
    app_name="internship_portal",
    api_url=api_url,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)

