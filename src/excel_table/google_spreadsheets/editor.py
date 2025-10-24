import logging
import json
from call_analysis.analysis_strategies.gemini.output_schema import CallAnalysisResult
from typing import Optional, Any
from gspread.client import Client
from gspread.utils import column_letter_to_index
import gspread_formatting as gsf
from gspread.worksheet import Worksheet
from constants import ConfigFiles
from utils import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


class GoogleSheetEditor:
    def __init__(self, client: Client, worksheet: Worksheet):
        self.client = client
        self.mapping = {}
        self.worksheet = worksheet
        logger.info("Authenticated with Google Sheets.")

    def load_mapping(self, mapping_path: str = ConfigFiles.COLUMN_MAPPING):
        with open(mapping_path, "r", encoding="utf-8") as f:
            self.mapping = json.load(f)
        logger.info(f"Column mapping loaded from {mapping_path}.")

    def prepare_row_data(self, data: CallAnalysisResult) -> list:
        """
        **THIS IS AN AUXILIARY FUNCTION - THE BRAIN OF THE CLASS.**
        Converts a Pydantic object into a simple list, ready to be written to a table row.
        """
        if not self.mapping:
            raise ValueError(
                "Column map is not loaded. Call load_mapping() before writing."
            )

        # 1. Find the rightmost column from the map (e.g., 'U') to create a row of the correct length.
        max_col_num = 0
        for col_letter in self.mapping.values():
            col_num = column_letter_to_index(col_letter)
            if col_num > max_col_num:
                max_col_num = col_num

        # 2. Create an empty row (a list of empty strings) of the required length.
        row = [""] * max_col_num

        # 3. Fill this row with data from the Pydantic object.
        for field, col_letter in self.mapping.items():
            # Get the column index (A=0, B=1, ...)
            col_index = column_letter_to_index(col_letter) - 1
            # Get the field value from the Pydantic object (e.g., data.call_type)
            value = getattr(data, field, "")

            # 4. Convert the value to a string suitable for the cell.
            if isinstance(value, bool):
                row[col_index] = "1" if value else "0"
            elif isinstance(value, list):
                row[col_index] = ", ".join(map(str, value))
            elif value is None:
                row[col_index] = ""
            else:
                row[col_index] = str(value)

        return row

    def _prepare_row_data(self, data: dict[str, Any]) -> list:
        """
        [UPDATED] Accepts a dictionary (Dict) and converts it into a list (list),
        ready to be written to a table row according to the mapping.
        """
        if not self.mapping:
            raise ValueError(
                "Column map is not loaded. Call load_mapping() before writing."
            )

        # 1. Find the rightmost column from the map.
        max_col_num = 0
        for col_letter in self.mapping.values():
            col_num = column_letter_to_index(col_letter)
            if col_num > max_col_num:
                max_col_num = col_num

        # 2. Create an empty row of the required length.
        row = [""] * max_col_num

        # 3. Fill the row with data from the dictionary.
        for field, col_letter in self.mapping.items():
            # Get the column index
            col_index = column_letter_to_index(col_letter) - 1
            # Get the field value from the dictionary.
            value = data.get(field)

            # 4. Convert the value to a string suitable for the cell.
            if isinstance(value, bool):
                row[col_index] = "1" if value else "0"
            elif isinstance(value, list):
                row[col_index] = ", ".join(map(str, value))
            elif value is None:
                row[col_index] = ""
            else:
                row[col_index] = str(value)

        return row

    def write_rows(
        self,
        sheet_url: str,
        rows_to_add: list[list[str]],
        sheet_name: Optional[str] = None,
    ):
        logger.debug("Using 'append_rows' method.")
        logger.debug(f"Rows to add: {rows_to_add}")
        try:
            response = self.worksheet.append_rows(rows_to_add)
            logger.debug(f"Rows addition response: {response}")

            logger.info(f"All of the rows have been written successfully.")
            return response
        except Exception as e:
            logger.error(f" (write_rows) An error occurred: {e}")
            return None

    def color_cell(self, row: int, col_letter: str, red: int, green: int, blue: int):
        cell_range = f"{col_letter}{row}"
        self._color_cell_background(cell_range, red, green, blue)

    def _color_cell_background(self, cell_range: str, red: int, green: int, blue: int):
        # 1. Create a color object, converting 0-255 to 0.0-1.0
        bg_color = gsf.color(red / 255.0, green / 255.0, blue / 255.0)

        fmt = gsf.cellFormat(backgroundColor=bg_color)

        gsf.format_cell_range(self.worksheet, cell_range, fmt)
