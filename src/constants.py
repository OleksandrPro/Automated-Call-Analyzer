import os
from dotenv import load_dotenv
from utils import create_full_path


load_dotenv()


class Directories:
    ROOT = os.path.dirname(os.path.abspath(__file__))

    PROJECT_ROOT = os.path.dirname(ROOT)

    APP_DATA = os.path.join(PROJECT_ROOT, "app_data")

    AUDIOFILES_ROOT = os.path.join(APP_DATA, "audiofiles")

    GEMINI_ROOT = os.path.join(ROOT, "call_analysis", "gemini")


class ConfigFiles:
    CREDENTIALS = create_full_path(Directories.PROJECT_ROOT, "credentials.json")

    ANALYSIS_CRITERIA = create_full_path(Directories.APP_DATA, "analysis_criteria.json")

    COLUMN_MAPPING = create_full_path(Directories.APP_DATA, "columns_map.json")

    CLIENT_SECRET_FILE = create_full_path(
        Directories.PROJECT_ROOT, "client_secret.json"
    )

    TOKEN_FILE = create_full_path(Directories.PROJECT_ROOT, "token.json")


class GeminiConfig:
    PROMPT = create_full_path(Directories.GEMINI_ROOT, "prompt_template.txt")
    MODEL = os.getenv("GEMINI_MODEL")


class Constants:
    TARGET_FOLDER_NAME = os.getenv("GOOGLE_DRIVE_CALLS_FOLDER_NAME")
    SHEET_URL = os.getenv("TABLE_URL")


class Scopes:
    DRIVE = "https://www.googleapis.com/auth/drive"
