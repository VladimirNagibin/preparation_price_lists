import os
import uuid
from http import HTTPStatus

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
)
from fastapi.responses import FileResponse
from pydantic import UUID4

from core.settings import settings
from db.redis import RedisClient, get_redis

upload_file_router = APIRouter()


@upload_file_router.post(
    "/send_convert",
    summary="send file",
    description="Upload file for convert.",
)
async def upload_file(
    file: UploadFile = File(...), redis: RedisClient = Depends(get_redis)
) -> dict[str, str]:
    """
    Асинхронно загружает файл на сервер.
    """
    try:
        file_name = str(uuid.uuid4())
        tmp_file_path = os.path.join(
            settings.BASE_DIR, settings.UPLOAD_DIR, "in", file_name
        )
        with open(tmp_file_path, "wb") as buffer:
            while chunk := await file.read(settings.CHUNK):
                buffer.write(chunk)
        await redis.set(name=file_name, value=settings.LOAD, ex=settings.TTL)
    except Exception as e:  # error details
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Ошибка при загрузке файла: {e}",
        )

    return {
        "filename": file.filename,
        "token": file_name,
        "message": "Файл успешно загружен",
    }


@upload_file_router.get(
    "/get_convert",
    summary="get file",
    description="Get converted file.",
)
async def get_file(
    id: UUID4, response: Response, redis: RedisClient = Depends(get_redis)
) -> FileResponse:
    """
    Асинхронно получает файл с сервера.
    """
    file_path = os.path.join(
        settings.BASE_DIR, settings.UPLOAD_DIR, "out", str(id)
    )
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="File not found",
        )
    return FileResponse(file_path, filename="tmp.xls")
