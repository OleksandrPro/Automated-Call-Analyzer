import logging
from google.genai import Client

from utils import configure_logging
from constants import Scopes, Constants, ConfigFiles, GeminiConfig, Directories
from google_services import GoogleServicesProvider
from excel_table.google_spreadsheets.editor import GoogleSheetEditor
from google_drive.audio_downloader import AudioDownloader
from google_drive.file_searcher import FileSearcher
from google_drive.file_uploader import FileUploader
from call_analysis.analysis_strategies.gemini.gemini_strategy import (
    GeminiAnalysisStrategy,
)
from call_analysis.analysis_strategies.mock_strategy import MockAnalysisStrategy
from call_analysis.analysis_strategies.analysis_processor import (
    CallAnalyzer,
    ReportEvaluator,
)
from call_analysis.result_handlers import SheetResultHandler, TranscriptHandler

logger = logging.getLogger(__name__)


def execute():
    logger.info("Starting analysis pipeline...")
    gemini_client = Client()
    scopes = [Scopes.DRIVE]

    service_provider = GoogleServicesProvider(scopes)

    drive_service, gspread_client = service_provider.get_clients()

    spreadsheet = gspread_client.open_by_url(Constants.SHEET_URL)
    worksheet = spreadsheet.sheet1

    searcher = FileSearcher(service=drive_service)
    downloader = AudioDownloader(service=drive_service)
    uploader = FileUploader(service=drive_service)
    sheet_editor = GoogleSheetEditor(client=gspread_client, worksheet=worksheet)
    sheet_editor.load_mapping(mapping_path=ConfigFiles.COLUMN_MAPPING)

    folder_id = searcher.get_folder_id(Constants.TARGET_FOLDER_NAME)
    if not folder_id:
        logger.error(
            f"Process stopped: folder '{Constants.TARGET_FOLDER_NAME}' not found."
        )
        return

    audio_files = searcher.list_files_in_folder(folder_id)

    # --- 2.5 My mock for the test ---
    logger.debug("--- Starting mock file filter ---")
    result_audio_files = []
    target_file_name_1 = "2024-11-13_12-57_0667131186_outgoing.mp3"
    target_file_name_2 = "2025-07-14_14-48_0974747746_incoming.mp3"
    mocked_audio_files = [target_file_name_1, target_file_name_2]
    for audio_data in audio_files:
        audio_name = audio_data.get("name")
        logger.debug(f"Mock filter: checking file {audio_name}")
        if audio_name in mocked_audio_files:
            result_audio_files.append(audio_data)

    audio_files = result_audio_files
    logger.debug(f"--- Mock filter finished. Using {len(audio_files)} files. ---")
    # --- Mock end ---

    if not audio_files:
        logger.warning("No files for processing in the folder.")
        return

    logger.info("Building Gemini prompt...")
    prompt = GeminiAnalysisStrategy.build_prompt_from_template(
        criteria_path=ConfigFiles.ANALYSIS_CRITERIA, template_path=GeminiConfig.PROMPT
    )

    # --- 3. Setup Analysis Strategy ---
    gemini_strategy = GeminiAnalysisStrategy(
        client=gemini_client, model=GeminiConfig.MODEL, prompt=prompt
    )

    mock_strategy = MockAnalysisStrategy()

    # --- 4. Setup Analyzer (Context) ---
    # analyzer = CallAnalyzer(strategy=gemini_strategy, downloader=downloader)
    logger.info("Using MockAnalysisStrategy for analysis.")
    analyzer = CallAnalyzer(strategy=mock_strategy, downloader=downloader)

    # --- 5. Run Analysis ---
    processed_calls = analyzer.analyze_files(audio_files)

    if not processed_calls:
        logger.warning("No analysis results were obtained. Process finished.")
        return

    logger.debug(f"Processed calls list: {processed_calls}")

    # --- 6. Run Post-Processing & Evaluation ---
    evaluator = ReportEvaluator(processed_calls)

    evaluated_reports = evaluator.generate_evaluated_reports()

    logger.debug(f"Evaluated reports list: {evaluated_reports}")

    # --- 7. Setup Result Handlers ---
    logger.info("Setting up result handlers...")
    sheet_handler = SheetResultHandler(sheet_editor)

    transcript_handler = TranscriptHandler(
        uploader=uploader,
        local_save_directory=Directories.AUDIOFILES_ROOT,
        drive_folder_id=folder_id,
    )

    # --- 8. Writing results to a table and cloud ---

    # 8.1. Save to Google Sheet and color cells
    sheet_handler.save_and_format_reports(
        reports=evaluated_reports, sheet_url=Constants.SHEET_URL
    )

    # 8.2. Save and upload transcripts
    transcript_handler.save_and_upload_transcripts(reports=evaluated_reports)

    logger.info("Whole process successfully finished!")


if __name__ == "__main__":
    configure_logging()
    execute()
