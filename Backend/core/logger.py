import sys
from loguru import logger
from database import supabase

# Remove default logger to configure customized output formats
logger.remove()

# Add standard terminal output
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
)

def db_log_sink(message):
    try:
        record = message.record
        level = record["level"].name
        msg = record["message"]
        
        # Extract structured metadata from extra context
        extra = record["extra"]
        user_id = extra.get("user_id")
        session_id = extra.get("session_id")
        error_code = extra.get("error_code")
        service = extra.get("service", "backend")
        
        # Store in Supabase SystemLogs table
        payload = {
            "log_level": level,
            "log_message": msg,
            "service": service,
        }
        if user_id:
            payload["user_id"] = str(user_id)
        if session_id:
            payload["session_id"] = str(session_id)
        if error_code:
            payload["error_code"] = str(error_code)
            
        supabase.table("SystemLogs").insert(payload).execute()
    except Exception as e:
        # Prevent infinite logging loop in case of DB insert failures
        sys.stderr.write(f"Failed writing log to database: {e}\n")

# Add the database sink for INFO, WARNING, ERROR, CRITICAL levels
logger.add(
    db_log_sink,
    level="INFO",
)
