import asyncio
import logging

from app.db.session import async_session_maker
from app.services.booking_service import BookingService

logger = logging.getLogger("myaloca.scheduler")

# Background scheduler task handle
_scheduler_task: asyncio.Task | None = None
_stop_event = asyncio.Event()


async def _run_no_show_checker(interval_seconds: int = 60) -> None:
    logger.info("Auto-Release No-Show Scheduler iniciado.")
    while not _stop_event.is_set():
        try:
            async with async_session_maker() as session:
                expired_count = await BookingService.process_no_shows(session)
                if expired_count > 0:
                    logger.info(f"[AUTO-RELEASE] {expired_count} reservas sem check-in expiradas.")
        except Exception as e:
            logger.error(f"[AUTO-RELEASE ERROR] Falha ao processar no-shows: {e}")

        try:
            await asyncio.wait_for(_stop_event.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            pass
    logger.info("Auto-Release No-Show Scheduler finalizado.")


def start_scheduler(interval_seconds: int = 60) -> None:
    global _scheduler_task
    _stop_event.clear()
    _scheduler_task = asyncio.create_task(_run_no_show_checker(interval_seconds))


def stop_scheduler() -> None:
    _stop_event.set()
    if _scheduler_task and not _scheduler_task.done():
        _scheduler_task.cancel()
