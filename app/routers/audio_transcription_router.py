from typing import Optional
from fastapi import APIRouter, File, UploadFile, Query, HTTPException
from app.services.audio_transcription_service import convert_to_wav, transcribe_audio, get_text, add_task, task_exists, get_history

router = APIRouter()

ALLOWED_MIME_TYPES = [
    "audio/mpeg",      # MP3
    "audio/wav",       # WAV
    "audio/wave",      # WAV
    "audio/x-wav",     # WAV (старый тип)
    "audio/vnd.wave",  # WAV (нестандартный тип)
    "audio/ogg",       # OGG Vorbis
    "video/ogg",       # OGG Vorbis
    "audio/flac",      # FLAC
    "audio/x-flac",    # FLAC (старый тип)
    # WebM (включает аудиофайлы WebM с кодеком Opus или Vorbis)
    "audio/webm",
    "video/webm",
    'video/mp4',
    "audio/aac",       # AAC
    "audio/m4a",       # M4A (часто используется с AAC кодеком)
    "audio/opus"       # Opus

]


@router.post("/upload")
async def audio_transcription(
    file: UploadFile = File(...),
    token: str = Query(...),
    model: str = Query(..., enum=["tiny", "base", "small", "medium"],
                       description="Чем больше модель, тем дольше обрабатывается аудиофайл."),
    language: Optional[str] = Query(None, enum=["ru", "en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko"],
                                    description="Правильный выбор языка ускоряет процесс обработки аудиофайла."),
):
    """
    Принимает аудиофайл для транскрипции, проверяет его тип, конвертирует в WAV и запускает задачу транскрипции.
    """
    print(file.content_type)
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only audio files are allowed."
        )
    print(file.content_type)
    if task_exists(token, file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File with name '{
                file.filename}' already exists for this token."
        )

    wav_file_location = await convert_to_wav(file)
    print(wav_file_location)

    task = transcribe_audio.delay(wav_file_location, model, language)

    add_task(token, file.filename, task.id)

    return {"task_id": task.id}


@router.get("/history")
async def audio_transcription_history(token: str):
    """
    Получает историю транскрипции для заданного токена.
    """
    return get_history(token)


@router.get("/{task_id}")
async def audio_transcription_status(task_id: str):
    """
    Получает статус задачи транскрипции по идентификатору задачи.
    """
    return get_text(task_id)
