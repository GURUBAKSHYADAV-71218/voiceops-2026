
import os
from pathlib import Path
from dotenv import load_dotenv
from gnani.stt import GnaniSTTClient
from gnani.tts import GnaniTTSClient

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def transcribe_audio(audio_path: str, language_code: str = "en-IN") -> str:
    """Convert one customer audio file to text using Gnani STT."""
    stt = GnaniSTTClient()
    result = stt.transcribe(
        audio_path,
        language_code=language_code,
    )
    return result.get("transcript", "").strip()


def synthesize_reply(
    text: str,
    output_path: str,
    language: str = "en-IN",
) -> str:
    """Save the agent's spoken reply using Gnani TTS."""
    tts = GnaniTTSClient()
    tts.synthesize(
        text,
        voice="Kaveri",
        model="timbre-v2.5",
        language=language,
        output_file=output_path,
    )
    return output_path
