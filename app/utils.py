from json import loads
import os


from fastapi import HTTPException, UploadFile
from aiofiles import open as aio_open
from uuid import uuid4
from pydub import AudioSegment
from redis import Redis, RedisError

R = Redis(host="localhost", port=6379, decode_responses=True, db=0)


ALLOWED_AUDIO_MIME_TYPES = {
    "audio/mpeg",      # MP3
    "audio/wav",       # WAV
    "audio/wave",      # WAV
    "audio/x-wav",     # WAV (старый тип)
    "audio/vnd.wave",  # WAV (нестандартный тип)
    "audio/ogg",       # OGG Vorbis
    "audio/flac",      # FLAC
    "audio/x-flac",    # FLAC (старый тип)
    "audio/webm",      # WebM аудио
    "audio/aac",       # AAC
    "audio/m4a",       # M4A (AAC)
    "audio/opus"       # Opus
}

ALLOWED_VIDEO_MIME_TYPES = {
    "video/ogg",       # OGG Vorbis
    "video/webm",      # WebM видео
    "video/mp4"        # MP4
}

ALLOWED_MIME_TYPES = ALLOWED_AUDIO_MIME_TYPES | ALLOWED_VIDEO_MIME_TYPES


async def validate_file(file: UploadFile) -> None:
    """
    Проверяет MIME-тип загруженного файла. Бросает HTTPException в случае невалидного типа.
    """
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {
                file.content_type}. Only audio and specific video files are allowed."
        )


def task_exists(key: str, file_name: str) -> bool:
    """
    Проверяет, существует ли запись с заданным именем файла для данного ключа в Redis.

    :param key: Уникальный ключ пользователя.
    :param file_name: Имя файла.
    :return: True, если запись существует, иначе False.
    """

    existing_tasks = R.lrange(key, 0, -1)

    # Проверяем, если файл с таким же именем уже существует
    for task_json in existing_tasks:
        task_data = loads(task_json)
        if task_data['file_name'] == file_name:
            return True

    return False


async def check_task_existence(token: str, filename: str) -> None:
    """
    Проверяет, существует ли задача для данного токена и имени файла.
    """
    if task_exists(token, filename):
        raise HTTPException(
            status_code=400,
            detail=f"File with name '{
                filename}' already exists for this token."
        )


async def convert_to_wav(audio_file: UploadFile) -> str:
    """
    Конвертация аудиофаил в формат WAV.

    Этот метод принимает аудиофайл в виде объекта UploadFile и возвращает
    имя временного файла wav, сохраненного в папке app/audio.

    Args:
        audio_file (UploadFile): Объект UploadFile с аудиофайлом.

    Returns:
        str: Имя временного wav-файла.

    Raises:
        Exception: В случае возникновения ошибки.   

    """
    # Создание уникального идентификатора
    file_id = str(uuid4())
    file_location = f'app/audio/{file_id}'
    wav_file_location = f'{file_location}.wav'

    try:
        async with aio_open(file_location, 'wb') as f:
            while chunk := await audio_file.read(1024 * 1024):  # Чтение по 1MB
                await f.write(chunk)

        audio = AudioSegment.from_file(file_location)
        audio.export(wav_file_location, format='wav')

    except Exception as e:
        if os.path.exists(file_location):
            os.remove(file_location)
        raise e

    finally:
        if os.path.exists(file_location):
            os.remove(file_location)

    return wav_file_location


def split_audio(audio_file_path: str, max_duration: int = 30 * 1000) -> list:
    """
    Разделяет аудиофайл на части по максимальной длительности.

    Args:
        audio_file_path (str): Путь к аудиофайлу.
        max_duration (int): Максимальная длительность каждой части в миллисекундах (по умолчанию 30 секунд).

    Returns:
        list: Список путей к временным частям аудиофайла.
    """
    audio = AudioSegment.from_file(audio_file_path)
    duration = len(audio)
    chunks = []

    for i in range(0, duration, max_duration):
        chunk = audio[i:i + max_duration]
        chunk_path = f"{audio_file_path}_part_{i // max_duration}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks
