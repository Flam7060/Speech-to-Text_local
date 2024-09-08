from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import audio_transcription_router as audio
from app.routers import frontend_router as front

app = FastAPI(
    title="Auth Service",
    description="Сервис аутентификации пользователей",
    version="1.0.0",
)

# Разрешить CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или укажите конкретные адреса
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audio.router, prefix="/audio-transcription",
                   tags=["Audio to Text"])
app.include_router(front.router)


app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/status")
async def root():
    return {"message": "Service is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")