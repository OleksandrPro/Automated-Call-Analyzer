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


class RGBColor:
    def __init__(self, red: int, green: int, blue: int):
        if not all(value >= 0 and value <= 255 for value in [red, green, blue]):
            raise ValueError("Each value has to be in range of 0 to 255.")
        self.red = red
        self.green = green
        self.blue = blue


class CellBackgroundColors:
    RED = RGBColor(red=225, green=183, blue=183)
    GREEN = RGBColor(red=201, green=225, blue=183)


class TableConfig:
    BOOL_TO_INT_FIELDS = [
        "script_greeting",
        "script_farewell",
        "car_info_body_asked",
        "car_info_year_asked",
        "car_info_mileage_asked",
        "upsale_diagnostics_offered",
        "upsale_previous_work_asked",
    ]
    NEGATIVE_COMMENT = "is_comment_negative"
    CELL_TO_COLOR = "comment"
    TOTAL_SCORE = "total_score"
