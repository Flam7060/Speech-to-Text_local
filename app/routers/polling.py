from fastapi import APIRouter, UploadFile, File, Form
from pydantic import Field
from typing import Optional

from services.stt_service import get_text, transcribe_audio
from utils import convert_to_wav, validate_file

router = APIRouter()

@router.post("/upload")
async def audio_transcription(
    file: UploadFile = File(...),
    model: str = Form(..., 
        description="Чем больше модель, тем дольше обрабатывается аудиофайл. Возможные модели: 'tiny', 'base', 'small', 'medium'.",
        enum=["tiny", "base", "small", "medium"],
        example="small"
    ),
    language: Optional[str] = Form(
        None,
        description="Правильный выбор языка ускоряет процесс обработки аудиофайла.",
        enum=["ru", "en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko"],
        example="en" 
    )):
    """
    Принимает аудиофайл для транскрипции, проверяет его тип, конвертирует в WAV и запускает задачу транскрипции.
    """
    await validate_file(file)
    wav_file_location = await convert_to_wav(file)

    task = transcribe_audio.delay(
        wav_file_location, model, language)

    return {"task_id": task.id}




@router.get("/{task_id}")
async def audio_transcription_status(task_id: str):
    """
    Получает статус задачи транскрипции по идентификатору задачи.
    """
    return get_text(task_id)
