import os

import aiofiles.os as aios
import redis.asyncio as asyncio_redis
from redis.asyncio.client import PubSub
from redis.asyncio.client import Redis as ClientRedis

from core.settings import settings
from core.logger import logger
from db.redis import RedisClient, get_redis
from services.converter_files import convert_xlsx_to_xls


async def delete_file_async(file_path: str):
    try:
        # Проверяем, существует ли файл
        if not await aios.path.exists(file_path):
            print(f"Файл {file_path} не найден")
            return

        # Асинхронное удаление файла
        await aios.remove(file_path)
        print(f"Файл {file_path} успешно удален")
    except Exception as e:
        print(f"Ошибка при удалении файла {file_path}: {e}")


async def listen_to_redis_events():
    redis: RedisClient = await get_redis()
    client: ClientRedis = asyncio_redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    )
    pubsub: PubSub = client.pubsub()

    await pubsub.psubscribe("__keyevent@0__:set", "__keyevent@0__:expired")

    while True:
        message = await pubsub.get_message()
        if message and message["type"] == "pmessage":
            channel = message["channel"].decode("utf-8")
            key = message["data"].decode("utf-8")
            file_path = os.path.join(
                settings.BASE_DIR, settings.UPLOAD_DIR, "%s", key
            )
            try:
                value = await redis.get(name=key)
                value = int(value.decode("utf-8"))
            except Exception:
                value = None
            if channel == "__keyevent@0__:set" and value == settings.LOAD:
                await convert_xlsx_to_xls(key)
                await redis.set(
                    name=key, value=settings.CONVERTED, ex=settings.TTL
                )
                await delete_file_async(file_path % ("in"))
            elif channel == "__keyevent@0__:expired":
                await delete_file_async(file_path % ("out"))

async def clear_files():
    logger.info("clear files 777")
    print("clear files 777")
