import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1.upload_files import upload_file_router
from core.logger import LOGGING  # , logger
from core.settings import settings
from db import redis
from services.tasks import clear_files, listen_to_redis_events

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    task = asyncio.create_task(listen_to_redis_events())
    scheduler.add_job(
            clear_files,
            trigger=IntervalTrigger(minutes=1),
            id='clear_files',
            replace_existing=True
        )
    scheduler.start()
    yield
    await redis.redis.close()
    task.cancel()
    await task
    scheduler.shutdown()

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(upload_file_router, prefix="/api/v1/files", tags=["files"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.INFO,
        reload=settings.APP_RELOAD,
    )
