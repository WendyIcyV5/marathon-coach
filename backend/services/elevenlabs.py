"""
elevenlabs.py

Handles all interactions with the ElevenLabs API.
Generates voice audio from coaching feedback and training briefings.
"""

import os
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from dotenv import load_dotenv

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))


def generate_voice(text: str, filename: str = "coaching.mp3") -> str:
    audio = client.text_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb", text=text, model_id="eleven_monolingual_v1"
    )

    output_path = f"audio/{filename}"
    os.makedirs("audio", exist_ok=True)
    save(audio, output_path)

    return output_path
