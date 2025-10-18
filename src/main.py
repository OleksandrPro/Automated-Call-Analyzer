from google.genai import Client
from call_analysis.gemini.gemini_transcription import transcribe_audio
from utils import (
    create_full_path,
    read_audio_file,
    build_prompt_from_template,
    add_new_key_to_dicts,
)
from constants import Directories, GeminiConfig, ConfigFiles, Constants, Scopes
from call_analysis.gemini.output_schema import CallAnalysisResult
from google_drive.audio_downloader import AudioDownloader
from google_drive.file_searcher import FileSearcher
from google_drive.components_creator import ComponentCreator
from google_drive.file_uploader import FileUploader

from excel_table.google_spreadsheets.writer import GoogleSheetWriter
from excel_table.utils import (
    create_transcription_string,
    prepare_row_data,
    transform_list_of_pydantic_models,
)

from google_clients import setup_google_clients

from main_processor import (
    analyze_audio_files,
    save_transcripts_locally,
    write_results_to_sheet,
    upload_transcripts_to_drive,
    prepare_reports_for_writing,
)


def transcribe_file(client: Client, prompt: str, audiofile_path: str):
    audio_bytes = read_audio_file(audiofile_path)
    response = transcribe_audio(client, prompt, audio_bytes)

    return response


def test_prompt_build():
    criteria_path = ConfigFiles.ANALYSIS_CRITERIA
    template_path = GeminiConfig.PROMPT
    return build_prompt_from_template(criteria_path, template_path)


def execute():
    client = Client()

    file_name = "2024-11-13_12-57_0667131186_outgoing.mp3"
    file_2 = "2025-07-14_17-18_0937828077_incoming.mp3"
    audiofile_path = create_full_path(Directories.AUDIOFILES_ROOT, file_2)

    prompt = test_prompt_build()
    print(prompt)

    response = transcribe_file(client, prompt, audiofile_path)

    print(f"response: {response}")
    print(60 * "-")
    print(response.text)
    print(response.json())

    call_analysis = CallAnalysisResult(response.json())
    print(call_analysis)


def run_full_process():
    """
    Main function that executes the entire process from start to finish.
    """
    gemini_client = Client()
    scopes = [Scopes.DRIVE]
    drive_service, gspread_client = setup_google_clients(scopes)

    # --- 1. Creating objects for working with the API ---
    searcher = FileSearcher(service=drive_service)
    downloader = AudioDownloader(service=drive_service)
    uploader = FileUploader(service=drive_service)
    sheet_writer = GoogleSheetWriter(client=gspread_client)
    sheet_writer.load_mapping(mapping_path=ConfigFiles.COLUMN_MAPPING)

    # --- 2. Getting files from Google Drive ---
    folder_id = searcher.get_folder_id(Constants.TARGET_FOLDER_NAME)
    if not folder_id:
        print(
            f"Process stopped: folder '{Constants.TARGET_FOLDER_NAME}' not found."
        )  # Роботу зупинено: папка '{Constants.TARGET_FOLDER_NAME}' не знайдена.
        return

    audio_files = searcher.list_files_in_folder(folder_id)

    # --- 2.5 My mock for the test ---
    target_file_name = "2024-11-13_12-57_0667131186_outgoing.mp3"
    # target_file_name = "2025-07-14_14-48_0974747746_incoming.mp3"
    found = None
    for audio_data in audio_files:
        if audio_data.get("name") == target_file_name:
            found = audio_data
            break

    if found:
        audio_files = [found]
    else:
        audio_files = []

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
        print(
            "No analysis results were obtained. Process finished."
        )  # Не було отримано жодного результату аналізу. Роботу завершено.
        return

    analysis_reports = [x.analysis for x in analysis_results]
    analysis_report_dicts = transform_list_of_pydantic_models(analysis_reports)
    print(analysis_report_dicts)

    analysis_report_dicts = add_new_key_to_dicts(analysis_report_dicts, "total_score")

    # updated_report = evaluate_dict_responce(analysis_report_dicts)

    # rows_to_add = prepare_reports_for_writing(analysis_report_dicts)

    # --- 4. Writing results to a table ---
    # write_results_to_sheet(sheet_writer, Constants.SHEET_URL, rows_to_add)
    write_results_to_sheet(sheet_writer, Constants.SHEET_URL, analysis_report_dicts)

    # --- 5. Saving and loading transcriptions (optional) ---
    saved_paths = save_transcripts_locally(
        analysis_results, Directories.AUDIOFILES_ROOT
    )
    upload_transcripts_to_drive(uploader, saved_paths, folder_id)
    # WORKING VERSION
    print(
        "\nWhole process successfully finished!"
    )  # Whole process successfully finished!


if __name__ == "__main__":
    run_full_process()
