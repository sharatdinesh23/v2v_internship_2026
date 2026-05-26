import sys
import asyncio
import httpx
from loguru import logger

# Remove default to configure custom formatting
logger.remove()

# Add standard terminal output for Reflex server
logger.add(
    sys.stdout,
    format="<cyan>{time:YYYY-MM-DD HH:mm:ss.SSS}</cyan> | <level>{level: <8}</level> | <yellow>{name}</yellow>:<yellow>{function}</yellow>:<yellow>{line}</yellow> - <level>{message}</level>",
    level="DEBUG",
)

# API URL for log streaming (FastAPI backend port is 8888 by default)
API_URL = "http://127.0.0.1:8888"

def stream_to_backend(level, message, user_id=None, session_id=None, error_code=None):
    payload = {
        "level": level,
        "message": message,
        "user_id": user_id,
        "session_id": session_id,
        "error_code": error_code
    }
    
    async def post_log():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(f"{API_URL}/api/system/logs", json=payload)
        except Exception as e:
            sys.stderr.write(f"Failed to stream frontend log to backend: {e}\n")
            
    try:
        # Schedule the task on the current running loop or start one
        loop = asyncio.get_running_loop()
        loop.create_task(post_log())
    except RuntimeError:
        # Fallback if no running event loop (e.g. startup/scripts context)
        try:
            httpx.post(f"{API_URL}/api/system/logs", json=payload, timeout=5.0)
        except Exception as e:
            sys.stderr.write(f"Failed to stream frontend log (sync fallback): {e}\n")

def db_log_sink(message):
    record = message.record
    level = record["level"].name
    msg = record["message"]
    
    extra = record["extra"]
    user_id = extra.get("user_id")
    session_id = extra.get("session_id")
    error_code = extra.get("error_code")
    
    stream_to_backend(level, msg, user_id, session_id, error_code)

# Add database sink for INFO, WARNING, ERROR, CRITICAL levels
logger.add(
    db_log_sink,
    level="INFO",
)
