import json
from google.genai import Client, types
from pydantic import ValidationError
from call_analysis.gemini.output_schema import (
    CallAnalysisResult,
    config,
)


def transcribe_audio(client: Client, model: str, prompt: str, audio_bytes: bytes):
    """
    Your existing function that sends a request to the Gemini API.
    """
    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3")

    response = client.models.generate_content(
        model=model,
        contents=[prompt, audio_part],
        config=config,
    )
    print(f"gemini responce: {response}")
    return response


def analyze_audio_with_gemini(
    client: Client, model: str, prompt: str, audio_bytes: bytes
) -> CallAnalysisResult | None:
    """
    Analyzes the audio, parses the JSON response, and validates it into a Pydantic model.
    This is a wrapper function that combines transcription and parsing.
    """
    try:
        # 1. Get the raw response from the API
        raw_response = transcribe_audio(client, model, prompt, audio_bytes)

        # 2. Check if the response contains a parsed object (if response_schema is used)
        if raw_response.parsed:
            call_analysis = raw_response.parsed
            return call_analysis
        else:
            # If .parsed is empty, try to parse the text manually
            response_dict = json.loads(raw_response.text)
            call_analysis = CallAnalysisResult(**response_dict)
            return call_analysis

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(
            f"   Received response: {getattr(raw_response, 'text', 'no text')[:200]}..."
        )
        return None
    except ValidationError as e:
        print(f"Pydantic validation error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during analysis in Gemini: {e}")
        return None
