import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class HeartbeatWorker:

    def __init__(self, heartbeat_service, session_service):
        self.heartbeat_service = heartbeat_service
        self.session_service = session_service
        self.is_running = False
        self.task: Optional[asyncio.Task] = None

    async def start(self):
        self.is_running = True
        self.task = asyncio.create_task(self._run())
        logger.info("[HeartbeatWorker] Started - checking every 60 seconds")

    async def stop(self):
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("[HeartbeatWorker] Stopped")

    async def _run(self):
        while self.is_running:
            try:
                ended_sessions = await self.heartbeat_service.check_stale_sessions(
                    minutes=2
                )

                if ended_sessions:
                    logger.info(
                        f"[HeartbeatWorker] Ended {len(ended_sessions)} stale sessions "
                        f"due to heartbeat timeout"
                    )
                    for session_id in ended_sessions:
                        logger.info(f"[HeartbeatWorker] - Session {session_id} ended")

            except Exception as e:
                logger.error(f"[HeartbeatWorker] Error: {e}")

            await asyncio.sleep(60)
