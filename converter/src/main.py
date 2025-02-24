import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis

from core.logger import LOGGING, logger
from core.settings import settings
from db import redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    FastAPICache.init(RedisBackend(redis.redis), prefix="auth-cache")
    if settings.test:
        await create_database()
    yield
    await redis.redis.close()


def configure_tracer(jaeger_settings) -> None:
    """Конфигурирование трейсера Jaeger."""
    try:
        trace.set_tracer_provider(
            TracerProvider(
                resource=Resource(attributes={SERVICE_NAME: settings.project_name})
            )
        )
        otlp_exporter = OTLPSpanExporter(
            endpoint=f"http://{jaeger_settings.JAEGER_OTLP_HOST}:{jaeger_settings.JAEGER_OTLP_PORT}",
            insecure=True,
        )
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )
        logger.info("OTLPExporter успешно сконфигурирован!")
    except Exception as error:
        logger.info(f"OTLPExporter не удалось сконфигурировать: {error}")

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )


jaeger_settings = JaegerSettings()
if jaeger_settings.JAEGER_ENABLE:
    configure_tracer(jaeger_settings)
else:
    logger.info("Трассировка Jaeger не сконфигурирована!")


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
add_pagination(app)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(roles_router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(oauth_router, prefix="/api/v1/oauth", tags=["oauth"])


@app.middleware("http")
async def before_request(request: Request, call_next) -> ORJSONResponse:
    """Первичная обработка входящих запросов."""

    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        logger.warning("Отсутствует X-Request-Id в заголовке")
        response = await call_next(request=request)
        return response

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(
        "http", attributes={"http.request_id": request_id}
    ):
        try:
            response = await call_next(request=request)
        except Exception as error:
            logger.info(f"Ошибка обработки request: {error}")
            return ORJSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal Server Error"},
            )
    return response


FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=settings.app_reload,
    )