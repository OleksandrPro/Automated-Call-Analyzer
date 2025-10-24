import logging
import json
from google.genai import Client, types
from pydantic import ValidationError
from ..base_strategy import BaseAnalysisStrategy
from call_analysis.analysis_strategies.gemini.output_schema import (
    CallAnalysisResult,
    config,
)
from utils import read_json, read_file, _format_list, configure_logging

configure_logging()
logger = logging.getLogger(__name__)


class GeminiAnalysisStrategy(BaseAnalysisStrategy):
    """
    A concrete strategy implementation that uses the Gemini API
    for transcription and analysis.
    """

    def __init__(self, client: Client, model: str, prompt: str):
        """
        Initializes the Gemini strategy.

        Args:
            client: An authenticated Google Gemini Client.
            model: The specific model name (e.g., 'gemini-1.5-pro').
            prompt: The fully constructed prompt string to be used for analysis.
        """
        self._client = client
        self._model = model
        self._prompt = prompt
        self._api_config = config
        logger.debug("GeminiAnalysisStrategy initialized.")

    @staticmethod
    def build_prompt_from_template(criteria_path: str, template_path: str) -> str:
        """
        (Helper Method) Loads criteria and a prompt template,
        then injects the criteria into the template.
        """
        criteria = read_json(criteria_path)
        prompt_template = read_file(template_path)

        top_works_str = _format_list(criteria["top_works"])
        call_types_str = _format_list(criteria["call_types"])
        call_results_str = _format_list(criteria["call_results"])
        parts_discussed_str = _format_list(criteria["parts_discussed"])

        final_prompt = prompt_template.format(
            top_works_list=top_works_str,
            call_types_list=call_types_str,
            call_results_list=call_results_str,
            parts_discussed_list=parts_discussed_str,
        )
        return final_prompt

    def _transcribe_audio(self, audio_bytes: bytes) -> types.GenerateContentResponse:
        """
        Private method to send the actual request to the Gemini API.
        """
        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3")

        response = self._client.models.generate_content(
            model=self._model,
            contents=[self._prompt, audio_part],
            generation_config=self._api_config,
        )
        return response

    def analyse_call(self, audio_file_data: bytes) -> CallAnalysisResult | None:
        """
        Analyzes the audio, parses the JSON response, and validates it.
        This is the implementation of the abstract method.
        """
        try:
            # 1. Get the raw response from the API
            logger.debug("Sending audio to Gemini API...")
            raw_response = self._transcribe_audio(audio_file_data)

            # 2. Check if the response contains a parsed object (if response_schema is used)
            if hasattr(raw_response, "parsed") and raw_response.parsed:
                call_analysis = raw_response.parsed
                logger.info("Successfully parsed response using 'response_schema'.")
                return call_analysis
            else:
                # If .parsed is empty or not available, try to parse the text manually
                logger.info("Parsing response from raw text...")
                response_dict = json.loads(raw_response.text)
                call_analysis = CallAnalysisResult(**response_dict)
                return call_analysis

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(
                f"   Received response: {getattr(raw_response, 'text', 'no text')[:200]}..."
            )
            return None
        except ValidationError as e:
            logger.error(f"Pydantic validation error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during Gemini analysis: {e}")
            return None
