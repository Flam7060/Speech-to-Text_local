import os
from json import JSONDecodeError, dumps, loads

import whisper
from celery import Celery
from celery.result import AsyncResult
from redis import Redis, RedisError


from utils import split_audio

celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)


R = Redis(host="redis", port=6379, decode_responses=True, db=0)


@celery_app.task
def transcribe_audio(audio_file_path: str, model_name: str, language: str = None) -> str:
    """
    Выполняет транскрипцию аудиофайла с использованием Whisper, разбивая его на части, если он превышает 30 секунд.

    Args:
        audio_file_path (str): Путь к аудиофайлу.
        model_name (str): Название модели Whisper.
        language (str, optional): Язык аудиофайла. По умолчанию None.

    Returns:
        str: Объединенный текст транскрипции или None в случае ошибки.
    """
    try:
        model = whisper.load_model(model_name)
        audio_chunks = split_audio(audio_file_path)  #

        all_texts = []
        for chunk_path in audio_chunks:
            try:
                result = model.transcribe(
                    chunk_path, language=language) if language else model.transcribe(chunk_path)
                all_texts.append(result['text'])
            except Exception as e:
                print(e)
                raise e
            finally:
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)

        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)

        return ' '.join(all_texts)

    except Exception as e:
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)
        return None


def get_text(task_id: str):
    """
    Возвращает статус задачи транскрипции по идентификатору задачи.
    """
    task_result = AsyncResult(task_id)
    print(task_result.state)
    match task_result.state:
        case 'PENDING':
            return {"status": "Pending"}
        case 'SUCCESS':
            return {"status": "Success", "result": task_result.result}
        case _:
            return {"status": task_result.state}


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
