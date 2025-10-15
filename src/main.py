from speech_processing.gemini.gemini_transcription import (
    transcribe_audio,
    parse_responce_text,
)
from utils import create_full_path, read_audio_file, build_prompt_from_template
from constants import Directories, GeminiConfig, ConfigFiles


def transcribe_file(prompt: str, audiofile_path: str):
    audio_bytes = read_audio_file(audiofile_path)
    response = transcribe_audio(prompt, audio_bytes)

    parsed_responce = parse_responce_text(response)
    print(parsed_responce)

    return response


def test_prompt_build():
    criteria_path = ConfigFiles.ANALYSIS_CRITERIA
    template_path = GeminiConfig.PROMPT
    return build_prompt_from_template(criteria_path, template_path)


def execute():
    file_name = "2024-11-13_12-57_0667131186_outgoing.mp3"
    file_2 = "2025-07-14_17-18_0937828077_incoming.mp3"
    audiofile_path = create_full_path(Directories.AUDIOFILES_ROOT, file_2)

    prompt = test_prompt_build()
    print(prompt)

    response = transcribe_file(prompt, audiofile_path)

    print(f"response: {response}")
    print(60 * "-")
    print(response.text)


if __name__ == "__main__":
    execute()
