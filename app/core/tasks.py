from fastapi import BackgroundTasks
from app.services.auth_service import auth_service
import asyncio
import logging

logger = logging.getLogger(__name__)

async def cleanup_expired_tokens():
    """Background task to clean up expired tokens."""
    while True:
        try:
            await auth_service.cleanup_expired_tokens()
            await asyncio.sleep(3600)  # Run every hour
        except Exception as e:
            logger.error(f"Token cleanup error: {str(e)}")
            await asyncio.sleep(60)  # Wait a minute before retrying

def start_background_tasks(background_tasks: BackgroundTasks):
    """Start background tasks."""
    background_tasks.add_task(cleanup_expired_tokens) 