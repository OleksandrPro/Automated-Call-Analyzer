import logging
from .base_strategy import BaseAnalysisStrategy
from call_analysis.analysis_strategies.gemini.output_schema import (
    DialogLine,
    SpeakerTypes,
    CallAnalysisResult,
)
from utils import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


class MockAnalysisStrategy(BaseAnalysisStrategy):
    def analyse_call(self, audio_file_data: bytes) -> CallAnalysisResult | None:
        logger.info("--- Using MOCK Analysis Strategy ---")
        return self._return_call_analysis()

    def _return_call_analysis(self):

        call_analysis = CallAnalysisResult(
            transcript=[
                DialogLine(
                    speaker=SpeakerTypes.CLIENT,
                    text="Client line",
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
