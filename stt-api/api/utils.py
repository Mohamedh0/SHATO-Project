import io
import uuid
import logging
import whisper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Load Whisper model once at startup
model = whisper.load_model("tiny")

def transcribe_audio(audio_data: bytes) -> tuple[str, str]:
    """
    Transcribe audio bytes (WAV/MP3/etc.) into text using OpenAI Whisper.
    Returns (id_correlation, transcription).
    """
    try:
        # Generate a correlation ID for tracking
        id_correlation = str(uuid.uuid4())

        # Save bytes to a temporary in-memory buffer
        with io.BytesIO(audio_data) as audio_file:
            temp_path = f"/tmp/{id_correlation}.wav"
            with open(temp_path, "wb") as f:
                f.write(audio_file.read())

        # Transcribe
        logging.info(f"[{id_correlation}] Starting transcription")
        result = model.transcribe(temp_path)
        text = result.get("text", "").strip()

        logging.info(f"[{id_correlation}] Transcription completed: {text}")

        return id_correlation, text

    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        raise ValueError(f"Error processing audio: {str(e)}")
