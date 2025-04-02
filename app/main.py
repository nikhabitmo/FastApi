import os

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import uvicorn

load_dotenv()

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "1048576"))
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def handle_upload(request: Request, file: UploadFile):
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        return templates.TemplateResponse("upload.html", {
            "request": request,
            "error": "Файл слишком большой (макс. 1 МБ)"
        })

    try:
        text = content.decode("utf-8")
    except Exception:
        return templates.TemplateResponse("upload.html", {"request": request})

    text = text[:50000]

    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([text])
    except ValueError:
        return templates.TemplateResponse("upload.html", {
            "request": request,
            "error": "Файл пустой или не содержит слов для анализа"
        })

    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray()[0]

    words = text.lower().split()
    tf_counts = Counter(words)

    data = []
    for word, score in zip(feature_names, tfidf_scores):
        tf = tf_counts[word]
        idf = score / tf if tf > 0 else 0
        data.append({"word": word, "tf": tf, "idf": round(idf, 4)})

    data = sorted(data, key=lambda x: -x["idf"])[:50]

    return templates.TemplateResponse("result.html", {
        "request": request,
        "words": data
    })

if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)