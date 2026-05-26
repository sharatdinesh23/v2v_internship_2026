import asyncio
from typing import Dict, Any, List, Set
from datetime import datetime
import logging

from database import supabase

logger = logging.getLogger("BackgroundSync")

# Simple In-Memory Cache for User Sessions
# In a distributed production environment, this should ideally be Redis.
# { user_id: { "role": str, "internship_id": str, "metadata": dict, "last_synced": datetime } }
ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}

async def update_user_session_cache(user_id: str, profile_data: Dict[str, Any]):
    """Update or register a session in the background-ready registry."""
    ACTIVE_SESSIONS[user_id] = {
        "role": profile_data.get("role"),
        "internship_id": profile_data.get("internship_id"),
        "last_synced": datetime.now(),
        "metadata": profile_data
    }

async def sync_all_active_users():
    """
    Background worker that refreshes profiles for all users currently marked as active.
    This ensures that when an admin changes an internship or role, the user's next
    request (using cached context) is up to date without a fresh database hop on every dependency call.
    """
    while True:
        try:
            if not ACTIVE_SESSIONS:
                await asyncio.sleep(60)
                continue

            user_ids = list(ACTIVE_SESSIONS.keys())
            logger.info(f"Starting background sync for {len(user_ids)} users.")

            # Batch fetch updated profile contexts
            # Supabase doesn't easily support batch complex selects with relations in one 'in', 
            # so we iterate for safety or do a single broad select.
            for uid in user_ids:
                try:
                    # Import here to avoid circular dependencies if necessary
                    from core.security import get_profile_context
                    new_ctx = get_profile_context(uid)
                    await update_user_session_cache(uid, new_ctx)
                except Exception as sync_exc:
                    logger.error(f"Failed to sync user {uid}: {str(sync_exc)}", exc_info=True)
                
                # Small throttle to avoid hitting Supabase rate limits
                await asyncio.sleep(0.5)

            logger.info("Background session sync completed.")
        except Exception as e:
            logger.error(f"Background Sync Master Loop Error: {str(e)}", exc_info=True)
        
        # Sync every 5 minutes
        await asyncio.sleep(300)
