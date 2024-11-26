
from fastapi import APIRouter, Depends, File, UploadFile
from schemas.stt_schemas import TranscriptionRequestParams
from services.stt_service import transcribe_audio, get_text, add_task, get_history
from utils import validate_file, check_task_existence, convert_to_wav
router = APIRouter()


@router.post("/upload")
async def audio_transcription(
    file: UploadFile = File(...),
    params: TranscriptionRequestParams = Depends()
):
    """
    Принимает аудиофайл для транскрипции, проверяет его тип, конвертирует в WAV и запускает задачу транскрипции.
    """
    await validate_file(file)

    await check_task_existence(params.token, file.filename)

    wav_file_location = await convert_to_wav(file)

    task = transcribe_audio.delay(
        wav_file_location, params.model, params.language)

    # сохраняем задачу в историю
    add_task(params.token, file.filename, task.id)

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
