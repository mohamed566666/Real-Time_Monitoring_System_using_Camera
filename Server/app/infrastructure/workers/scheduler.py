import asyncio
import logging
from typing import List, Dict, Any, Callable, Awaitable
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ScheduledTask:

    name: str
    func: Callable[..., Awaitable[Any]]
    interval_seconds: int
    args: tuple = ()
    kwargs: dict = None


class Scheduler:

    def __init__(self):
        self.tasks: List[ScheduledTask] = []
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False

    def add_task(
        self, name: str, func: Callable, interval_seconds: int, *args, **kwargs
    ):
        task = ScheduledTask(
            name=name,
            func=func,
            interval_seconds=interval_seconds,
            args=args,
            kwargs=kwargs,
        )
        self.tasks.append(task)
        logger.info(f"[Scheduler] Added task: {name} (every {interval_seconds}s)")

    async def start(self):
        self.is_running = True
        for task in self.tasks:
            worker_task = asyncio.create_task(
                self._run_task(task), name=f"scheduler_{task.name}"
            )
            self.running_tasks[task.name] = worker_task

        logger.info(f"[Scheduler] Started {len(self.tasks)} tasks")

    async def stop(self):
        self.is_running = False
        for name, task in self.running_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        logger.info("[Scheduler] Stopped all tasks")

    async def _run_task(self, task: ScheduledTask):
        while self.is_running:
            try:
                start_time = datetime.utcnow()

                if task.kwargs:
                    await task.func(*task.args, **task.kwargs)
                else:
                    await task.func(*task.args)

                execution_time = (datetime.utcnow() - start_time).total_seconds()

                logger.debug(
                    f"[Scheduler] Task '{task.name}' completed in {execution_time:.2f}s"
                )

            except Exception as e:
                logger.error(f"[Scheduler] Task '{task.name}' failed: {e}")

            await asyncio.sleep(task.interval_seconds)
