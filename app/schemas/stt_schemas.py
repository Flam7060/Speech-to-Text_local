from pydantic import BaseModel, Field
from typing import Optional



from pydantic import BaseModel, Field
from typing import Optional



class TranscriptionRequestParams(BaseModel):
    token: str = Field(..., description="Уникальный токен пользователя для идентификации запросов.")
    model: str = Field(..., 
        description="Чем больше модель, тем дольше обрабатывается аудиофайл. Возможные модели: 'tiny', 'base', 'small', 'medium'.",
        enum=["tiny", "base", "small", "medium"],
        example="small"  # Пример модели
    )
    language: Optional[str] = Field(
        None,
        description="Правильный выбор языка ускоряет процесс обработки аудиофайла.",
        enum=["ru", "en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko"],
        example="en"  # Пример языка
    )

