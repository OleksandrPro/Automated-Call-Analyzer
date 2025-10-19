from google.genai import Client
from utils import (
    build_prompt_from_template,
    add_new_key_to_dicts,
)
from constants import Directories, GeminiConfig, ConfigFiles, Constants, Scopes
from call_analysis.gemini.output_schema import CallAnalysisResult
from google_drive.audio_downloader import AudioDownloader
from google_drive.file_searcher import FileSearcher
from google_drive.components_creator import ComponentCreator
from google_drive.file_uploader import FileUploader

from src.excel_table.google_spreadsheets.editor import GoogleSheetEditor
from excel_table.utils import transform_list_of_pydantic_models, evaluate_dict_responces

from google_clients import setup_google_clients

from main_processor import (
    analyze_audio_files,
    save_transcripts_locally,
    write_results_to_sheet,
    upload_transcripts_to_drive,
    prepare_reports_for_writing,
    color_cells,
)


def run_full_process():
    """
    Main function that executes the entire process from start to finish.
    """
    gemini_client = Client()
    scopes = [Scopes.DRIVE]
    drive_service, gspread_client = setup_google_clients(scopes)

    spreadsheet = gspread_client.open_by_url(Constants.SHEET_URL)
    # worksheet = spreadsheet.worksheet(sheet_name) if sheet_name else spreadsheet.sheet1
    worksheet = spreadsheet.sheet1

    # --- 1. Creating objects for working with the API ---
    searcher = FileSearcher(service=drive_service)
    downloader = AudioDownloader(service=drive_service)
    uploader = FileUploader(service=drive_service)
    sheet_editor = GoogleSheetEditor(client=gspread_client, worksheet=worksheet)
    sheet_editor.load_mapping(mapping_path=ConfigFiles.COLUMN_MAPPING)

    # --- 2. Getting files from Google Drive ---
    folder_id = searcher.get_folder_id(Constants.TARGET_FOLDER_NAME)
    if not folder_id:
        print(f"Process stopped: folder '{Constants.TARGET_FOLDER_NAME}' not found.")
        return

    audio_files = searcher.list_files_in_folder(folder_id)

    # --- 2.5 My mock for the test ---
    result_audio_files = []
    target_file_name_1 = "2024-11-13_12-57_0667131186_outgoing.mp3"
    target_file_name_2 = "2025-07-14_14-48_0974747746_incoming.mp3"
    mocked_audio_files = [target_file_name_1, target_file_name_2]
    for audio_data in audio_files:
        audio_name = audio_data.get("name")
        print(audio_name)
        if audio_name in mocked_audio_files:
            result_audio_files.append(audio_data)

    audio_files = result_audio_files
    # --- Mock end ---

    if not audio_files:
        print("No files for processing in the folder.")
        return

    # --- 3. Analyzing files ---
    prompt = build_prompt_from_template(
        criteria_path=ConfigFiles.ANALYSIS_CRITERIA, template_path=GeminiConfig.PROMPT
    )
    gemini_model = GeminiConfig.MODEL
    analysis_results = analyze_audio_files(
        gemini_client, gemini_model, prompt, downloader, audio_files
    )

    if not analysis_results:
        print("No analysis results were obtained. Process finished.")
        return

    analysis_reports = [x.analysis for x in analysis_results]
    analysis_report_dicts = transform_list_of_pydantic_models(analysis_reports)

    analysis_report_dicts = add_new_key_to_dicts(analysis_report_dicts, "total_score")

    evaluate_dict_responces(analysis_report_dicts)

    # rows_to_add = prepare_reports_for_writing(analysis_report_dicts)

    # --- 4. Writing results to a table ---
    response = write_results_to_sheet(
        sheet_editor, Constants.SHEET_URL, analysis_report_dicts
    )

    color_cells(sheet_editor, response, analysis_report_dicts)

    # --- 5. Saving and loading transcriptions (optional) ---
    saved_paths = save_transcripts_locally(
        analysis_results, Directories.AUDIOFILES_ROOT
    )
    upload_transcripts_to_drive(uploader, saved_paths, folder_id)

    print("\nWhole process successfully finished!")


if __name__ == "__main__":
    run_full_process()
