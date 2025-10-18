import os
import json


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


def build_prompt_from_template(criteria_path: str, template_path: str) -> str:
    """
    Loads criteria from a JSON file and a prompt from a text file,
    then injects the criteria into the prompt template.
    """

    criteria = read_json(criteria_path)
    prompt_template = read_file(template_path)

    # 3. Format the lists from the criteria into simple text strings
    top_works_str = _format_list(criteria["top_works"])
    call_types_str = _format_list(criteria["call_types"])
    call_results_str = _format_list(criteria["call_results"])
    parts_discussed_str = _format_list(criteria["parts_discussed"])

    # 4. Use an f-string to inject the formatted strings into the template
    final_prompt = prompt_template.format(
        top_works_list=top_works_str,
        call_types_list=call_types_str,
        call_results_list=call_results_str,
        parts_discussed_list=parts_discussed_str,
    )

    return final_prompt


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


def evaluate_dict_responce(analysis_report_dict: dict):
    pass
