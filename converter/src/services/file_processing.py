from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os
import asyncio

app = FastAPI()

# Папка для сохранения загруженных файлов
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Асинхронно загружает файл на сервер.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Асинхронно сохраняем файл
    try:
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024):  # Читаем файл по частям
                buffer.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {e}")

    return {"filename": file.filename, "message": "Файл успешно загружен"}