import os
import pytest
from fastapi.testclient import TestClient
from main import app  # Импортируйте ваше FastAPI приложение

client = TestClient(app)

UPLOAD_DIR = "uploads"


@pytest.fixture(autouse=True)
def cleanup_upload_dir():
    # Очистка папки uploads перед каждым тестом
    if os.path.exists(UPLOAD_DIR):
        for file_name in os.listdir(UPLOAD_DIR):
            os.remove(os.path.join(UPLOAD_DIR, file_name))


def test_upload_file():
    # Создаем тестовый файл
    file_content = b"Test file content"
    files = {"file": ("test_file.txt", file_content)}

    # Отправляем файл на сервер
    response = client.post("/upload/", files=files)
    assert response.status_code == 200
    assert response.json() == {"filename": "test_file.txt"}

    # Проверяем, что файл был сохранен
    file_path = os.path.join(UPLOAD_DIR, "test_file.txt")
    assert os.path.exists(file_path)
    with open(file_path, "rb") as f:
        assert f.read() == file_content


def test_download_file():
    # Создаем тестовый файл
    file_content = b"Test file content"
    file_path = os.path.join(UPLOAD_DIR, "test_file.txt")
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Скачиваем файл
    response = client.get("/download/test_file.txt")
    assert response.status_code == 200
    assert response.content == file_content


def test_download_nonexistent_file():
    # Пытаемся скачать несуществующий файл
    response = client.get("/download/nonexistent_file.txt")
    assert response.status_code == 404
    assert response.json() == {"detail": "Файл не найден"}
