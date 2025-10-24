import logging
import os
from typing import List, Dict, Any

from excel_table.google_spreadsheets.editor import GoogleSheetEditor
from google_drive.file_uploader import FileUploader
from constants import TableConfig, CellBackgroundColors
from utils import (
    write_json_file,
    create_full_path,
    get_start_end_row,
    configure_logging,
)

configure_logging()
logger = logging.getLogger(__name__)


class SheetResultHandler:
    """
    Handles all operations related to writing and formatting
    results in a Google Sheet.
    """

    def __init__(self, editor: GoogleSheetEditor):
        """
        Initializes the handler with an existing GoogleSheetEditor instance.
        """
        self._editor = editor
        if not self._editor.mapping:
            logger.warning(
                "GoogleSheetEditor has no mapping loaded. Call load_mapping()."
            )

    def _create_transcription_string(self, dialogue_lines: List[Dict]) -> str:
        """
        Creates a formatted string from transcript dialogue lines.
        """
        if not dialogue_lines:
            return "Transcription is missing."

        formatted_lines = [
            f"{line.get('speaker', 'Unknown')}: {line.get('text', '')}"
            for line in dialogue_lines
        ]
        return "\n".join(formatted_lines)

    def _prepare_reports_for_writing(
        self, analysis_reports_dicts: List[Dict[str, Any]]
    ) -> List[List[str]]:
        """
        Converts a list of report dicts into a list of rows for the sheet.
        """
        rows_to_add = []
        for report_dict in analysis_reports_dicts:
            # IMPORTANT: We create a copy to avoid modifying the original dict,
            # which is needed by TranscriptHandler.
            report_copy = report_dict.copy()

            # Format transcription for sheet view
            transcript_str = self._create_transcription_string(
                report_copy.get("transcript", [])
            )
            report_copy.pop("transcript", None)  # Remove original list
            report_copy["transcription"] = transcript_str  # Add formatted string

            # Use the editor's internal logic to map dict keys to row cells
            prepared_row = self._editor._prepare_row_data(report_copy)
            rows_to_add.append(prepared_row)

        return rows_to_add

    def _color_report_cells(
        self, write_response: dict, analysis_reports_dicts: List[Dict[str, Any]]
    ):
        """
        Colors cells based on the analysis results (e.g., negative comments).
        """
        updated_range = write_response.get("updates", {}).get("updatedRange")
        if not updated_range:
            logger.error(
                "Response doesn't contain 'updatedRange'. Skipping cell coloring."
            )
            return

        start_row, end_row = get_start_end_row(updated_range)
        if start_row > end_row:
            logger.error(
                f"Invalid row range. start: {start_row}, end: {end_row}. Skipping cell coloring."
            )
            return

        rows_to_color = range(start_row, end_row + 1)

        # Build a list of colors based on the reports
        color_sequence = []
        for report in analysis_reports_dicts:
            is_negative = report.get(TableConfig.NEGATIVE_COMMENT, False)
            color = (
                CellBackgroundColors.RED if is_negative else CellBackgroundColors.GREEN
            )
            color_sequence.append(color)

        # Get the column to color from the editor's mapping
        col_letter = self._editor.mapping.get(TableConfig.CELL_TO_COLOR)
        if not col_letter:
            logger.error(
                f"'{TableConfig.CELL_TO_COLOR}' not in mapping. Skipping cell coloring."
            )
            return

        # Apply coloring
        logger.info(
            f"Applying cell formatting to range {col_letter}{start_row}:{col_letter}{end_row}..."
        )
        for index, color in enumerate(color_sequence):
            row = rows_to_color[index]
            self._editor.color_cell(row, col_letter, color.red, color.green, color.blue)

    def save_and_format_reports(self, reports: List[Dict[str, Any]], sheet_url: str):
        """
        Main public method.
        Writes all reports to the sheet and then colors the cells.
        """
        if not reports:
            logger.warning("No reports to write to Google Sheet.")
            return

        logger.info("Preparing reports for Google Sheet...")
        # 1. Prepare data for batch writing
        rows_to_add = self._prepare_reports_for_writing(reports)

        # 2. Use batch writing
        logger.info("Writing reports to Google Sheet...")
        response = self._editor.write_rows(sheet_url=sheet_url, rows_to_add=rows_to_add)

        if not response:
            logger.error("Failed to write rows. Aborting cell coloring.")
            return

        logger.info(f"Successfully wrote {len(rows_to_add)} rows.")

        # 3. Color cells
        self._color_report_cells(response, reports)
        logger.info("Cell coloring applied.")


class TranscriptHandler:
    """
    Handles saving transcriptions locally and uploading them
    to a cloud storage (like Google Drive).
    """

    def __init__(
        self,
        uploader: FileUploader,
        local_save_directory: str,
        drive_folder_id: str,
    ):
        self._uploader = uploader
        self._local_dir = local_save_directory
        self._drive_folder_id = drive_folder_id
        os.makedirs(self._local_dir, exist_ok=True)  # Ensure directory exists

    def _get_local_filepath(self, source_file_name: str) -> str:
        """
        Generates a .json file path for a transcript.
        """
        base_name, _ = os.path.splitext(source_file_name)
        file_name = f"{base_name}_transcript.json"
        return create_full_path(self._local_dir, file_name)

    def save_and_upload_transcripts(self, reports: List[Dict[str, Any]]):
        """
        Main public method.
        Saves transcripts locally, then uploads them to Google Drive.

        **Assumption**: Each dict in 'reports' contains:
        - 'source_file_name' (str): The original audio file name.
        - 'transcript' (List[dict]): The original transcript data.
        """
        logger.info("Processing transcript files...")
        saved_file_paths = []

        # 1. Save all transcripts locally
        for report in reports:
            logger.debug(
                f"Processing report for transcript: {report.get('source_file_name')}"
            )
            source_name = report.get("source_file_name")
            transcript_content = report.get("transcript")

            if not source_name or not transcript_content:
                logger.warning(
                    "Skipping transcript save for a report - missing 'source_file_name' or 'transcript' key."
                )
                continue

            # Get local file path
            file_path = self._get_local_filepath(source_name)

            # Write JSON data
            try:
                write_json_file(transcript_content, file_path)
                saved_file_paths.append(file_path)
            except Exception as e:
                logger.error(f"Error saving local transcript '{file_path}': {e}")

        logger.info(f"Saved {len(saved_file_paths)} transcript files locally.")

        # 2. Upload all saved files to Google Drive
        if saved_file_paths:
            logger.info(
                f"Uploading {len(saved_file_paths)} transcripts to Google Drive folder '{self._drive_folder_id}'..."
            )
            self._uploader.upload_multiple_files(
                local_file_paths=saved_file_paths, folder_id=self._drive_folder_id
            )
        else:
            logger.info("No local transcript files to upload.")
