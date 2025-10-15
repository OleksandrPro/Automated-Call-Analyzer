from google import genai
from google.genai import types
from .output_schema import config, DialogLine


def transcribe_audio(audio_bytes: bytes):

    client = genai.Client()

    prompt = "Створити повну транскрипцію розмови."
    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3")

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=[prompt, audio_part], config=config
    )

    return response


def parse_responce_text(response):
    dialogues: list[DialogLine] = response.parsed
    return dialogues
