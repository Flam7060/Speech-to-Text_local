from aiofiles import open as aio_open
import uuid
import whisper
from pydub import AudioSegment
from uuid import uuid4
from fastapi import UploadFile
import os
from celery import Celery
from celery.result import AsyncResult
from redis import Redis, RedisError
from json import JSONDecodeError, dumps, loads

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

R = Redis(host="localhost", port=6379, decode_responses=True, db=0)


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
    file_id = str(uuid.uuid4())
    file_location = f'app/audio/{file_id}'
    wav_file_location = f'{file_location}.wav'

    try:
        contents = await audio_file.read()
        #  GPT посоветовал использовать aiofiles для асинхронного открытия файла
        async with aio_open(file_location, 'wb') as f:
            await f.write(contents)

        # Конвертация в wav
        audio = AudioSegment.from_file(file_location)
        audio.export(wav_file_location, format='wav')

    except Exception as e:
        if os.path.exists(file_location):
            # os.remove(file_location)
            pass
        raise e

    finally:
        if os.path.exists(file_location):
            pass
            # os.remove(file_location)

    return wav_file_location


@celery_app.task
def transcribe_audio(audio_file_path: str, model_name: str, language: str = None) -> str:
    try:
        model = whisper.load_model(model_name)

        if language:
            result = model.transcribe(audio_file_path, language=language)
        else:
            result = model.transcribe(audio_file_path)

        os.remove(audio_file_path)
        return result['text']
    except Exception as e:
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)
        return None


def get_text(task_id: str):
    task_result = AsyncResult(task_id)
    print(task_result.state)
    if task_result.state == 'PENDING':
        return {"status": "Pending"}
    elif task_result.state == 'SUCCESS':
        return {"status": "Success", "result": task_result.result}
    else:
        return {"status": task_result.state}


def task_exists(key: str, file_name: str) -> bool:
    """
    Проверяет, существует ли запись с заданным именем файла для данного ключа в Redis.

    :param key: Уникальный ключ пользователя.
    :param file_name: Имя файла.
    :return: True, если запись существует, иначе False.
    """
    # Получаем все элементы списка по ключу
    existing_tasks = R.lrange(key, 0, -1)

    # Проверяем, если файл с таким же именем уже существует
    for task_json in existing_tasks:
        task_data = loads(task_json)
        if task_data['file_name'] == file_name:
            return True  # Если файл существует, возвращаем True

    return False  # Если файл не существует, возвращаем False


async def get_history(key: str) -> list:
    """
    Возвращает все задачи пользователя с заданным ключом в Redis.

    :param key: Уникальный ключ пользователя.
    :return: Список задач.
    """
    try:
        tasks = R.lrange(key, 0, -1)
        print(tasks)

        # Проверяем, что tasks не пустой
        if not tasks:
            return []

        # Попытка десериализовать задачи
        return [loads(task) for task in tasks]

    except JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")
        return []
    except RedisError as e:
        print(f"Ошибка работы с Redis: {e}")
        return []


def add_task(key: str, file_name: str, task_id: str):
    """
    Добавляет запись задачи в Redis.

    :param key: Уникальный ключ пользователя.
    :param file_name: Имя файла.
    :param task_id: Идентификатор задачи.
    """
    data = dumps({'file_name': file_name, 'task_id': task_id})
    R.rpush(f'tasks_{key}', data)
    R.expire(key, 24 * 60 * 60)
