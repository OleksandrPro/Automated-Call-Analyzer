import os
from google.genai import Client
from typing import List, Dict, Any
from dataclasses import dataclass
from call_analysis.gemini.output_schema import CallAnalysisResult
from call_analysis.gemini.gemini_transcription import transcribe_audio
from google_drive.audio_downloader import AudioDownloader
from google_drive.file_uploader import FileUploader
from excel_table.google_spreadsheets.editor import GoogleSheetEditor
from excel_table.utils import edit_transcription_view
from utils import create_full_path, read_audio_file, write_json_file, get_start_end_row
from call_analysis.gemini.gemini_transcription import analyze_audio_with_gemini
from constants import TableConfig, CellBackgroundColors, RGBColor
from gspread.utils import column_letter_to_index


@dataclass
class ProcessedCall:
    """Container for storing the source file name and its analysis result."""

    source_file_name: str
    analysis: CallAnalysisResult


def transcribe_file(client: Client, prompt: str, audiofile_path: str):
    audio_bytes = read_audio_file(audiofile_path)
    response = transcribe_audio(client, prompt, audio_bytes)

    return response


def return_call_analysis():
    from call_analysis.gemini.output_schema import DialogLine, SpeakerTypes

    call_analysis = CallAnalysisResult(
        transcript=[
            DialogLine(
                speaker=SpeakerTypes.CLIENT,
                text="Transcription for {file['name']}",
            ),
            DialogLine(
                speaker=SpeakerTypes.MANAGER,
                text="Manager line",
            ),
        ],
        call_type="Test",
        manager_name="Test",
        script_greeting=True,
        script_farewell=True,
        car_info_body_asked=False,
        car_info_year_asked=True,
        car_info_mileage_asked=True,
        upsale_diagnostics_offered=False,
        upsale_previous_work_asked=False,
        service_booking_date="2025-10-16",
        top_works_mentioned=["Test", "Not Test"],
        parts_discussed=None,
        call_result="Test",
        comment="Comment for {file['name']}",
        is_comment_negative=True,
    )

    return call_analysis


# --- Mockup for testing ---
# call_analysis = return_call_analysis()
# --- End of Mockup ---


def analyze_audio_files(
    gemini_client: Client,
    gemini_model: str,
    prompt: str,
    downloader: AudioDownloader,
    audio_files: List[dict],
) -> List[ProcessedCall]:
    """
    Downloads and analyzes a list of audio files.
    """
    processed_results = []
    for file in audio_files:
        print(f"\nProcessing file: {file['name']} ({file['id']})")
        audio_bytes = downloader.download_file_in_memory(file["id"])

        if not audio_bytes:
            # ... (TODO)
            continue

        print("Sending file to Gemini for analysis...")

        # call_analysis = analyze_audio_with_gemini(gemini_client, gemini_model, prompt, audio_bytes)

        # MOCKUP for tests
        call_analysis = return_call_analysis()

        print(call_analysis)

        # Check that the analysis was successful
        if call_analysis:
            processed_call = ProcessedCall(
                source_file_name=file["name"], analysis=call_analysis
            )
            processed_results.append(processed_call)
            print(f"File {file['name']} successfully analyzed.")
        else:
            print(f"Analysis of file {file['name']} failed. Skipping.")

    return processed_results


def save_transcripts_locally(
    processed_calls: List[ProcessedCall], directory: str
) -> List[str]:
    """
    Saves the transcriptions, using the source audio file name.
    """
    saved_files = []
    print("\nSaving transcriptions to local files...")
    for item in processed_calls:
        base_name, _ = os.path.splitext(
            item.source_file_name
        )  # Remove the .mp3 extension
        file_name = f"{base_name}_transcript.json"
        file_path = create_full_path(directory, file_name)

        transcript_content = [line.model_dump() for line in item.analysis.transcript]

        write_json_file(transcript_content, file_path)
        saved_files.append(file_path)

    print(f"Saved {len(saved_files)} transcription files.")
    return saved_files


def prepare_transcription_for_saving(analysis_results: List[CallAnalysisResult]):
    pass


def prepare_reports_for_writing(
    writer: GoogleSheetEditor, analysis_reports_dicts: List[Dict[str, Any]]
) -> List[List[str]]:
    rows_to_add = []

    for report_dict in analysis_reports_dicts:
        print(report_dict)
        edit_transcription_view(report_dict)
        prepared_row = writer._prepare_row_data(report_dict)
        rows_to_add.append(prepared_row)

    return rows_to_add


def write_results_to_sheet_1(
    writer: GoogleSheetEditor, sheet_url: str, rows_to_add: List
):
    """
    Writes analysis results to a Google Sheet.
    """
    print("\nWriting results to Google Sheet...")
    writer.write_rows(sheet_url=sheet_url, rows_to_add=rows_to_add)
    print("All results successfully written.")


def prepare_analysis_for_batch_writing(
    writer: GoogleSheetEditor,
    analysis_reports: List[CallAnalysisResult | Dict[str, Any]],
) -> List[List[str]]:
    """
    Accepts a list of analysis results (Pydantic or Dict)
    and converts them into a list of lists (list[list[str]]) for batch writing.
    """
    rows_to_add = []

    for report in analysis_reports:
        # Convert Pydantic model to dictionary, if necessary
        if isinstance(report, CallAnalysisResult):
            report_dict = report.model_dump()
        else:
            report_dict = report

        # Use the writer's internal data preparation method
        try:
            prepared_row = writer._prepare_row_data(report_dict)
            rows_to_add.append(prepared_row)
        except Exception as e:
            print(
                f"Error preparing data for report {report_dict.get('manager_name', 'Unknown')}: {e}. Row skipped."
            )
            continue

    return rows_to_add


def write_results_to_sheet(
    writer: GoogleSheetEditor,
    sheet_url: str,
    analysis_reports_dicts: List[Dict[str, Any]],
):
    """
    Accepts a list of dictionaries (Dict) with analysis results and writes them to a Google Sheet.
    """
    print("\nWriting results to Google Sheet...")

    if not analysis_reports_dicts:
        print("No data to write to the table.")
        return

    # 1. Prepare data for batch writing
    rows_to_add = prepare_reports_for_writing(writer, analysis_reports_dicts)

    # 2. Use batch writing
    response = writer.write_rows(sheet_url=sheet_url, rows_to_add=rows_to_add)

    print(f"Successfully wrote {len(rows_to_add)} rows to the table.")
    return response


def color_cells(editor: GoogleSheetEditor, response: dict, analysis_report_dicts):
    updated_range = response.get("updates", {}).get("updatedRange")

    if not updated_range:
        print("Error: Response doesn't contain key 'updatedRange'.")
        return None

    start_row, end_row = get_start_end_row(updated_range)

    rows = range(start_row, end_row + 1)
    if start_row == end_row:
        print("'rows' is empty. start_row: %s, end_row: %s", start_row, end_row)
        return

    color_sequence: list[RGBColor] = []
    for report in analysis_report_dicts:
        is_comment_negative = report.get(TableConfig.NEGATIVE_COMMENT)
        color = (
            CellBackgroundColors.RED
            if is_comment_negative
            else CellBackgroundColors.GREEN
        )
        color_sequence.append(color)

    col_letter = editor.mapping.get(TableConfig.CELL_TO_COLOR)

    for index, color in enumerate(color_sequence):
        row = rows[index]
        editor.color_cell(row, col_letter, color.red, color.green, color.blue)


def upload_transcripts_to_drive(
    uploader: FileUploader, file_paths: List[str], folder_id: str
):
    """
    Uploads local transcription files to the specified Google Drive folder.
    """
    print(f"\nUploading transcription files to folder '{folder_id}' on Google Drive...")
    uploader.upload_multiple_files(local_file_paths=file_paths, folder_id=folder_id)
