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
from call_analysis.analysis_strategies.analysis_processor import (
    CallAnalyzer,
    ReportEvaluator,
)
from call_analysis.result_handlers import SheetResultHandler, TranscriptHandler

logger = logging.getLogger(__name__)


def execute():
    logger.info("Starting analysis pipeline...")

    # --- 1. Setup Google Services & Clients ---
    gemini_client = Client()
    scopes = [Scopes.DRIVE]

    service_provider = GoogleServicesProvider(scopes)

    drive_service, gspread_client = service_provider.get_clients()

    spreadsheet = gspread_client.open_by_url(Constants.SHEET_URL)
    worksheet = spreadsheet.sheet1

    # --- 2. Setup Core Components ---
    searcher = FileSearcher(service=drive_service)
    downloader = AudioDownloader(service=drive_service)
    uploader = FileUploader(service=drive_service)
    sheet_editor = GoogleSheetEditor(client=gspread_client, worksheet=worksheet)
    sheet_editor.load_mapping(mapping_path=ConfigFiles.COLUMN_MAPPING)

    # --- 3. Find Audio Files Folder ---
    audio_folder_id = Constants.AUDIOFILES_FOLDER_ID

    if audio_folder_id:
        logger.info(
            f"Using direct folder ID from AUDIOFILES_FOLDER_ID: {audio_folder_id}"
        )
    else:
        logger.warning(
            "AUDIOFILES_FOLDER_ID is not set. Falling back to search by AUDIOFILES_FOLDER_NAME."
        )

        folder_name = Constants.AUDIOFILES_FOLDER_NAME
        if not folder_name:
            logger.error(
                "Process stopped: Neither AUDIOFILES_FOLDER_ID nor AUDIOFILES_FOLDER_NAME environment variables are set."
            )
            return

        audio_folder_id = searcher.get_folder_id(folder_name)

        if not audio_folder_id:
            logger.error(
                f"Process stopped: Folder '{folder_name}' not found on Google Drive."
            )
            return

    # --- 4. List Audio Files ---
    audio_files = searcher.list_files_in_folder(audio_folder_id)

    if not audio_files:
        logger.warning("No files for processing in the folder.")
        return

    logger.info("Building Gemini prompt...")
    prompt = GeminiAnalysisStrategy.build_prompt_from_template(
        criteria_path=ConfigFiles.ANALYSIS_CRITERIA, template_path=GeminiConfig.PROMPT
    )

    # --- 5. Setup Call Analysis Strategy ---
    gemini_strategy = GeminiAnalysisStrategy(
        client=gemini_client, model=GeminiConfig.MODEL, prompt=prompt
    )

    # --- 6. Setup Analyzer (Context) ---
    analyzer = CallAnalyzer(strategy=gemini_strategy, downloader=downloader)

    # --- 7. Run Analysis ---
    processed_calls = analyzer.analyze_files(audio_files)

    if not processed_calls:
        logger.warning("No analysis results were obtained. Process finished.")
        return

    logger.debug(f"Processed calls list: {processed_calls}")

    # --- 8. Run Post-Processing & Evaluation ---
    evaluator = ReportEvaluator(processed_calls)

    evaluated_reports = evaluator.generate_evaluated_reports()

    logger.debug(f"Evaluated reports list: {evaluated_reports}")

    # --- 9. Setup Result Handlers ---
    logger.info("Setting up result handlers...")
    sheet_handler = SheetResultHandler(sheet_editor)

    transcript_handler = TranscriptHandler(
        uploader=uploader,
        local_save_directory=Directories.AUDIOFILES_ROOT,
        drive_folder_id=audio_folder_id,
    )

    # --- 10. Writing results to a table and drive ---

    # 10.1. Save to Google Sheet and color cells
    sheet_handler.save_and_format_reports(
        reports=evaluated_reports, sheet_url=Constants.SHEET_URL
    )

    # 10.2. Save and upload transcripts
    transcript_handler.save_and_upload_transcripts(reports=evaluated_reports)

    logger.info("Whole process successfully finished!")


if __name__ == "__main__":
    configure_logging()
    try:
        logger.info("Application starting...")
        execute()
        logger.info("Application finished successfully.")

    except Exception as e:
        logger.exception("An unhandled exception occurred. Process stopped.")
