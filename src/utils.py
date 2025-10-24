import os
import sys
import logging
from logging import _Level
import json
import re
from typing import Optional, Tuple


def configure_logging(logging_level: _Level = logging.INFO):
    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def create_full_path(directory: str, file_name: str):
    return os.path.join(directory, file_name)


def read_audio_file(audiofile_path: str):
    with open(audiofile_path, "rb") as f:
        audio_bytes = f.read()
        return audio_bytes


def _format_list(items: list[str]):
    result_str = "\n".join([f"{item}" for item in items])
    return result_str


def read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        result = json.load(f)
    return result


def read_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        result = f.read()
    return result


def write_json_file(input_data: list[dict], output_file_path: str):
    with open(output_file_path, "w", encoding="utf-8") as final:
        json.dump(
            input_data,
            final,
            indent=2,
            default=lambda x: list(x) if isinstance(x, tuple) else str(x),
            ensure_ascii=False,
        )


def add_new_key(dictionary: dict, key: str, value=None):

    if key in dictionary:
        print(
            f"Warning: Key '{key}' already exists in the dictionary. Value not changed."
        )
    else:
        dictionary[key] = value
        print(f"Key '{key}' successfully added with value {value}.")

    return dictionary


def add_new_key_to_dicts(dictionaries: list[dict], key: str, value=None):
    updated_dicts = []
    for dictionaty in dictionaries:
        new_dict = add_new_key(dictionaty, key)
        updated_dicts.append(new_dict)

    return updated_dicts


def get_start_end_row(updated_range: str) -> Optional[Tuple[int, int]]:
    """
    Args:
        updated_range (str): example - "'Sheet1'!A9:V10".

    Returns:
        (start_row, end_row) or None.
    """

    range_part = updated_range.split("!")[-1]

    match = re.search(r"[A-Z]+(\d+):[A-Z]+(\d+)", range_part)

    if match:
        start_row = int(match.group(1))
        end_row = int(match.group(2))

        return start_row, end_row
    else:
        single_row_match = re.search(r"[A-Z]+(\d+)$", range_part)
        if single_row_match:
            start_row = int(single_row_match.group(1))
            end_row = start_row
            return start_row, end_row

    print(f"Parse error: Couldn't find rown numbers in '{updated_range}'.")
    return None
