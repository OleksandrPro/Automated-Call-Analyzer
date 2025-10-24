import logging
from typing import List, Dict, Any

from .base_strategy import BaseAnalysisStrategy
from .gemini.output_schema import CallAnalysisResult
from google_drive.audio_downloader import AudioDownloader
from constants import TableConfig
from utils import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


class ProcessedCall:
    """Container for storing the source file name and its analysis result."""

    def __init__(self, source_file_name: str, analysis: CallAnalysisResult):
        self.source_file_name = source_file_name
        self.analysis = analysis


class CallAnalyzer:
    """
    The "Context" class that uses a strategy to analyze files.
    Its job is to orchestrate the process of getting files
    and running the chosen analysis strategy on them.
    """

    def __init__(
        self,
        strategy: BaseAnalysisStrategy,
        downloader: AudioDownloader,
    ):
        self._strategy = strategy
        self._downloader = downloader
        logger.info(
            f"CallAnalyzer initialized with strategy: {self._strategy.__class__.__name__}"
        )

    def analyze_files(self, audio_files: List[Dict[str, str]]) -> List[ProcessedCall]:
        """
        Downloads and analyzes a list of audio files using the injected strategy.
        """
        processed_results = []
        for file in audio_files:
            file_name = file.get("name", "Unknown")
            file_id = file.get("id", None)

            if not file_id:
                logger.warning(f"Skipping file '{file_name}' - missing 'id'.")
                continue

            logger.info(f"Processing file: {file_name} ({file_id})")

            # 1. Download file
            audio_bytes = self._downloader.download_file_in_memory(file_id)
            if not audio_bytes:
                logger.warning(f"Failed to download {file_name}. Skipping.")
                continue

            # 2. Delegate analysis to the strategy
            logger.info(
                f"Sending file to '{self._strategy.__class__.__name__}' for analysis..."
            )
            call_analysis = self._strategy.analyse_call(audio_bytes)

            # 3. Store result
            if call_analysis:
                processed_call = ProcessedCall(
                    source_file_name=file_name, analysis=call_analysis
                )
                processed_results.append(processed_call)
                logger.info(f"File {file_name} successfully analyzed.")
            else:
                logger.warning(f"Analysis of file {file_name} failed. Skipping.")

        return processed_results


class ReportEvaluator:
    """
    Handles post-analysis processing:
    1. Converts Pydantic models to dictionaries.
    2. Scores and evaluates the results based on business logic.
    """

    def __init__(self, processed_calls: List[ProcessedCall]):
        self._processed_calls = processed_calls
        self._report_dicts = []

    def _transform_models_to_dicts(self):
        """
        Converts the list of ProcessedCall objects to a list of dicts,
        merging the source_file_name with the dumped analysis data.
        """
        self._report_dicts = []

        for call in self._processed_calls:
            analysis_dict = call.analysis.model_dump()
            analysis_dict["source_file_name"] = call.source_file_name
            self._report_dicts.append(analysis_dict)

    def _transform_value(self, key: str, value: Any) -> Any:
        """Transforms a single value for the final report (e.g., bool to 1/0)."""
        if isinstance(value, bool):
            if key in TableConfig.BOOL_TO_INT_FIELDS:
                return 1 if value else 0
            elif key == TableConfig.NEGATIVE_COMMENT:
                return value  # Keep boolean

        if value is None:
            return ""  # Replace None with empty string

        return value

    def _evaluate_reports(self):
        """Iterates over report dicts to score them."""
        for report_dict in self._report_dicts:
            final_score = 0
            for key, value in report_dict.items():
                new_value = self._transform_value(key, value)
                report_dict[key] = new_value

                # Add to score if it's a field we're tracking
                if key in TableConfig.BOOL_TO_INT_FIELDS:
                    final_score += new_value  # new_value is already 1 or 0

            report_dict[TableConfig.TOTAL_SCORE] = final_score

    def generate_evaluated_reports(self) -> List[Dict[str, Any]]:
        """
        Public method to run the entire post-processing pipeline.
        """
        logger.info(
            f"Starting post-processing for {len(self._processed_calls)} reports..."
        )

        # 1. Pydantic -> Dict
        self._transform_models_to_dicts()

        # 2. Score dicts
        self._evaluate_reports()

        logger.info("Post-processing and evaluation complete.")
        return self._report_dicts
