import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
#from fastapi_cache import FastAPICache
#from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis

from core.logger import LOGGING #, logger
from core.settings import settings
from db import redis


from api.v1.upload_files import upload_file_router

@asynccontextmanager
async def lifespan(app: FastAPI):
#    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
#    FastAPICache.init(RedisBackend(redis.redis), prefix="auth-cache")
    ...
    yield
    ...
#    await redis.redis.close()


app = FastAPI(
    title="settings.project_name",
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
        log_level=logging.DEBUG,
        reload=True #settings.app_reload,
    )