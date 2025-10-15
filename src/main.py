from speech_processing.gemini.gemini_transcription import (
    transcribe_audio,
    parse_responce_text,
)
from utils import create_full_path, read_audio_file
from constants import Directories
from google_spreadsheets.test_shreadsheets_access import test_cell_access


def test_function():
    sheet_name = "Звіт прослуханих розмов"
    cell = test_cell_access(sheet_name, "G2")
    print(cell)


def transcribe_file(audiofile_path: str):
    audio_bytes = read_audio_file(audiofile_path)
    response = transcribe_audio(audio_bytes)

    parsed_responce = parse_responce_text(response)
    print(parsed_responce)

    return response


if __name__ == "__main__":
    file_name = "2024-11-13_12-57_0667131186_outgoing.mp3"
    audiofile_path = create_full_path(Directories.AUDIOFILES_ROOT, file_name)

    response = transcribe_file(audiofile_path)

    print(response.text)
