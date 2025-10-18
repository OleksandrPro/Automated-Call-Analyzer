from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from call_analysis.gemini.output_schema import CallAnalysisResult
from gspread.utils import column_letter_to_index


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


def create_row_content(gemini_responce: dict) -> dict:
    transcription_string = create_transcription_string(
        gemini_responce.get("transcript")
    )

    row_dict = gemini_responce.pop("transcript")
    row_dict["transcription"] = transcription_string

    return row_dict


def _transform_responce_values_to_cell_content(value: Any) -> str:
    if isinstance(value, bool):
        result = "1" if value else "0"
        return result
    elif isinstance(value, list):
        return ", ".join(map(str, value))
    elif value is None:
        return ""
    else:
        return str(value)


def return_dict_from_pydantic_model(model: BaseModel):
    return model.model_dump()


def transform_list_of_pydantic_models(models: list[BaseModel]):
    result = [return_dict_from_pydantic_model(x) for x in models]
    return result


def prepare_row_data(self, gemini_responce: dict) -> list:
    data = create_row_content(gemini_responce)

    # Determine the maximum column number to create a row of the required length
    max_col_num = 0
    for col_letter in self.mapping.values():
        col_num = column_letter_to_index(col_letter)
        if col_num > max_col_num:
            max_col_num = col_num

    # Create an empty row (list) of the required length
    row = [""] * max_col_num

    # Fill the row with data from the Pydantic object
    for field, col_letter in self.mapping.items():
        col_index = column_letter_to_index(col_letter) - 1
        value = getattr(data, field, "")

        # Convert various data types to strings for writing to the cell
        row[col_index] = _transform_responce_values_to_cell_content(value)

    return row
