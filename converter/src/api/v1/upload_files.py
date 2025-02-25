import tempfile
from http import HTTPStatus
import aiofile

from fastapi import APIRouter, File, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse

from core.settings import settings
#from services.helper import decode_val

upload_file_router = APIRouter()


@upload_file_router.post(
    "/upload",
    summary="upload file",
    description="Upload file for convert.",
)
async def upload_file(file: UploadFile = File(...)):
    """
    Асинхронно загружает файл на сервер.
    """

    # Асинхронно сохраняем файл
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file_path = tmp_file.name  # Полный путь к временному файлу
            with open(tmp_file_path, "wb") as buffer:
                while chunk := await file.read(1024):  # Читаем файл по частям
                    buffer.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {e}")

    return {"filename": file.filename, "local": tmp_file_path, "message": "Файл успешно загружен"}
