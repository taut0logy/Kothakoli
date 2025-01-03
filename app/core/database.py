from prisma import Prisma
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self._client = None

    async def connect(self):
        """Initialize database connection."""
        if not self._client:
            self._client = Prisma()
            await self._client.connect()
            logger.info("Connected to database")
        return self._client

    async def disconnect(self):
        """Disconnect from database."""
        if self._client:
            await self._client.disconnect()
            self._client = None
            logger.info("Disconnected from database")

    @asynccontextmanager
    async def get_client(self):
        """Async context manager for database operations."""
        if not self._client:
            await self.connect()
        try:
            yield self._client
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise
        # Connection stays open for reuse

db = Database() 