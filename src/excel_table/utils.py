from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from call_analysis.gemini.output_schema import CallAnalysisResult
from gspread.utils import column_letter_to_index
from constants import TableConfig


def create_transcription_string(dialogue_lines: List[Dict]) -> str:

    # Safely get the list of transcript lines.
    # If the key doesn't exist, it returns an empty list.
    # dialogue_lines: List[Dict] = analysis_data.get("transcript", [])
    if not dialogue_lines:
        return "Transcription is missing."

    # Use a list comprehension to format each line and then join them with newlines.
    formatted_lines = [
        f"{line.get('speaker', 'Невідомо')}: {line.get('text', '')}"
        for line in dialogue_lines
    ]

    return "\n".join(formatted_lines)


def edit_transcription_view(gemini_responce: dict) -> dict:
    transcription_string = create_transcription_string(
        gemini_responce.get("transcript")
    )

    gemini_responce.pop("transcript")
    gemini_responce["transcription"] = transcription_string


def transform_responce_values_to_report_content(key: str, value: Any) -> str:
    if isinstance(value, bool):
        if key in TableConfig.BOOL_TO_INT_FIELDS:
            result = 1 if value else 0
            return result
        elif key == TableConfig.NEGATIVE_COMMENT:
            return value
    # elif isinstance(value, list):
    #    return ", ".join(map(str, value))
    elif value is None:
        return ""
    elif isinstance(value, int):
        return str(value)
    # else:
    #    return str(value)
    return value


def return_dict_from_pydantic_model(model: BaseModel):
    return model.model_dump()


def transform_list_of_pydantic_models(models: list[BaseModel]):
    result = [return_dict_from_pydantic_model(x) for x in models]
    return result


def transform_responce_values_to_report_content_1(key: str, value: Any) -> str:
    if isinstance(value, bool):
        if key in TableConfig.BOOL_TO_INT_FIELDS:
            result = 1 if value else 0
            return result
        elif key == TableConfig.NEGATIVE_COMMENT:
            return value
    elif isinstance(value, list):
        return ", ".join(map(str, value))
    elif value is None:
        return ""
    else:
        return str(value)


def evaluate_dict_responce(analysis_report_dict: dict):
    final_score = 0
    for key, value in analysis_report_dict.items():
        new_value = transform_responce_values_to_report_content(key, value)
        analysis_report_dict[key] = new_value

        if key in TableConfig.BOOL_TO_INT_FIELDS:
            final_score += new_value

    analysis_report_dict[TableConfig.TOTAL_SCORE] = final_score


def evaluate_dict_responces(analysis_report_dicts: list[dict]):
    result = [evaluate_dict_responce(item) for item in analysis_report_dicts]
