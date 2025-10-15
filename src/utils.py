import os
from constants import Directories


def create_full_path(directory: Directories, file_name: str):
    return os.path.join(directory, file_name)


def read_audio_file(audiofile_path: str):
    with open(audiofile_path, "rb") as f:
        audio_bytes = f.read()
        return audio_bytes
