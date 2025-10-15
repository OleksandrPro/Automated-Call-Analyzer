from enum import Enum
from pydantic import BaseModel


class SpeakerTypes(Enum):
    CLIENT = "Клієнт"
    MANAGER = "Менеджер"


class DialogLine(BaseModel):
    speaker: SpeakerTypes
    text: str


config = {
    "response_mime_type": "application/json",
    "response_schema": list[DialogLine],
}
