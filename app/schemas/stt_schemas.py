
from fastapi import Query
from typing import Optional
from pydantic import BaseModel


class TranscriptionRequestParams(BaseModel):
    token: str = Query(...,
                       description="Уникальный токен пользователя для идентификации запросов.")
    model: str = Query(
        ...,
        enum=["tiny", "base", "small", "medium"],
        description="Чем больше модель, тем дольше обрабатывается аудиофайл."
    )
    language: Optional[str] = Query(
        None,
        enum=["ru", "en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko"],
        description="Правильный выбор языка ускоряет процесс обработки аудиофайла."
    )
