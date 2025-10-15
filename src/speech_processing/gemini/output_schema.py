from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional


class SpeakerTypes(Enum):
    CLIENT = "Клієнт"
    MANAGER = "Менеджер"


class DialogLine(BaseModel):
    speaker: SpeakerTypes
    text: str


class CallAnalysisResult(BaseModel):
    """Повний результат аналізу телефонного дзвінка."""

    transcript: List[DialogLine] = Field(description="Повна транскрипція розмови.")

    call_type: str = Field(
        description="Тип звернення: Консультація, Запис на сервіс, Уточнення, Скарга, Відмова."
    )
    manager_name: Optional[str] = Field(
        description="Ім'я менеджера, якщо він представився."
    )

    script_greeting: bool = Field(
        description="True, якщо менеджер привітався і представився."
    )
    script_farewell: bool = Field(
        description="True, якщо менеджер коректно попрощався."
    )

    car_info_body_asked: bool = Field(
        description="True, якщо менеджер запитав про кузов автомобіля."
    )
    car_info_year_asked: bool = Field(
        description="True, якщо менеджер запитав про рік випуску автомобіля."
    )
    car_info_mileage_asked: bool = Field(
        description="True, якщо менеджер запитав про пробіг."
    )

    upsale_diagnostics_offered: bool = Field(
        description="True, якщо менеджер запропонував комплексну діагностику."
    )
    upsale_previous_work_asked: bool = Field(
        description="True, якщо менеджер питав про попередні роботи."
    )

    service_booking_date: Optional[str] = Field(
        description="Дата та час запису на сервіс, або null, якщо запису не було."
    )

    top_works_mentioned: List[str] = Field(
        description="Список послуг з топ-100, які обговорювались."
    )

    parts_discussed: Optional[str] = Field(
        description="Чиї запчастини будуть використовуватися: клієнта чи наші."
    )

    call_result: str = Field(
        description="Результат дзвінка: Запис створено, Клієнт відмовився, Надано консультацію."
    )

    comment: str = Field(
        description="Загальний коментар по дзвінку. Оцінка роботи менеджера."
    )
    is_comment_negative: bool = Field(
        description="True, якщо менеджер погано провів розмову (для виділення червоним)."
    )


config = {
    "response_mime_type": "application/json",
    "response_schema": CallAnalysisResult,
}
