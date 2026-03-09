import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class CleanupWorker:

    def __init__(self, heartbeat_repo, session_repo):
        self.heartbeat_repo = heartbeat_repo
        self.session_repo = session_repo
        self.is_running = False
        self.task: Optional[asyncio.Task] = None

    async def start(self):
        self.is_running = True
        self.task = asyncio.create_task(self._run())
        logger.info("[CleanupWorker] Started - cleaning every 24 hours")

    async def stop(self):
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("[CleanupWorker] Stopped")

    async def _run(self):
        while self.is_running:
            try:
                deleted_count = await self.heartbeat_repo.cleanup_old_heartbeats(days=7)

                if deleted_count > 0:
                    logger.info(
                        f"[CleanupWorker] Deleted {deleted_count} old heartbeats"
                    )

            except Exception as e:
                logger.error(f"[CleanupWorker] Error: {e}")

            await asyncio.sleep(24 * 60 * 60)
