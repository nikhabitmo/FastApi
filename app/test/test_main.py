import sys
import os
from tkinter.scrolledtext import example

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_get_form():
    response = client.get("/")
    assert response.status_code == 200
    assert "Загрузите текстовый файл" in response.text

def test_upload_example_file_valid():
    file_path = os.path.join(os.path.dirname(__file__), "example_file.txt")

    with open(file_path, "rb") as f:
        files = {"file": ("example_file.txt", f, "text/plain")}
        response = client.post("/upload", files=files)

    assert response.status_code == 200
    assert "Топ-50 слов по IDF" in response.text

def test_empty_file():
    files = {"file": ("empty.txt", "", "text/plain")}
    response = client.post("/upload", files=files)
    assert response.status_code == 200
    assert "Загрузите текстовый файл" in response.text

def test_too_large_file():
    big_text = "большой " * (1024 * 1024)
    files = {"file": ("big.txt", big_text, "text/plain")}
    response = client.post("/upload", files=files)
    assert response.status_code == 200
    assert "Файл слишком большой" in response.text
