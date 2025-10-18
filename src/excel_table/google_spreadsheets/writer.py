import gspread
import json
from call_analysis.gemini.output_schema import CallAnalysisResult
from typing import List, Optional, Any, Dict
from gspread.client import Client
from gspread.utils import column_letter_to_index


class GoogleSheetWriter:
    def __init__(self, client: Client):
        self.client = client
        self.mapping = {}
        print("Authenticated with Google Sheets.")

    def load_mapping(self, mapping_path: str = "column_mapping.json"):
        with open(mapping_path, "r", encoding="utf-8") as f:
            self.mapping = json.load(f)
        print(f"Column mapping loaded from {mapping_path}.")

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
        # For example, if max_col_num = 21 (for 'U'), it will create ['', '', ..., ''] (21 elements).
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
            # Get the field value from the dictionary. Use .get() to avoid errors
            # if the field is not in the dictionary.
            value = data.get(field)

            # 4. Convert the value to a string suitable for the cell.
            if isinstance(value, bool):
                row[col_index] = "1" if value else "0"
            elif isinstance(value, list):
                # For a list, join elements with a comma
                row[col_index] = ", ".join(map(str, value))
            elif value is None:
                row[col_index] = ""
            else:
                row[col_index] = str(value)

        return row

    def write_row(
        self,
        sheet_url: str,
        data: CallAnalysisResult | Dict[str, Any],
        sheet_name: Optional[str] = None,
    ):
        """
        [MODIFIED] - Accepts either Pydantic or Dict. Internally converts Pydantic to dict
        to use _prepare_row_data.
        """
        if isinstance(data, CallAnalysisResult):
            # Convert the Pydantic model to a dictionary for unification
            data_dict = data.model_dump()
        else:
            data_dict = data

        try:
            prepared_row = self._prepare_row_data(data_dict)

            spreadsheet = self.client.open_by_url(sheet_url)
            worksheet = (
                spreadsheet.worksheet(sheet_name) if sheet_name else spreadsheet.sheet1
            )
            worksheet.append_row(prepared_row)

            print(f"Successfully added a new row to sheet '{worksheet.title}'.")
            return True

        except Exception as e:
            print(f"An error occurred while writing to the table: {e}")
            return False

    def write_rows(
        self,
        sheet_url: str,
        rows_to_add: list[list[str]],
        sheet_name: Optional[str] = None,
    ):
        print(f"rows_to_add: {rows_to_add}")
        try:
            spreadsheet = self.client.open_by_url(sheet_url)

            if sheet_name:
                worksheet = spreadsheet.worksheet(sheet_name)
            else:
                worksheet = spreadsheet.sheet1

            for row in rows_to_add:
                print(f"row: {row}")
                worksheet.append_row(row)
                print(f"Successfully wrote a new row to worksheet '{worksheet.title}'.")

            print(f"All of the rows have been written successfully.")
            return True
        except Exception as e:
            print(f" (write_rows) An error occurred: {e}")
            return False
