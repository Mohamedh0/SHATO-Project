# Orchestrator Service

A service that orchestrates voice-to-command processing, including speech-to-text (STT), LLM inference, validation, and text-to-speech (TTS) generation.

---

## Usage Instructions

### 1. Run the Service

Start the orchestrator service using uvicorn:

uvicorn main:app --reload --port 8500

---

### 2. Test Endpoints

#### Health Check

Visit this URL in your browser:

http://localhost:8500

Expected Response:

{
  "message": "Orchestrator service is running"
}

#### Voice Flow Endpoint (via Postman or cURL)

Process a voice command through the full pipeline: STT → LLM → Validator → TTS.

- Method: POST
- URL: http://localhost:8500/voice_flow
- Body: form-data
  - Key: audio
  - Type: File
  - Value: Select a .wav file (e.g., sample.wav)

Example cURL command:

curl -X POST \
  http://localhost:8500/voice_flow \
  -F "audio=@sample.wav"

Expected Response:

{
  "stt": {
    "text": "transcribed text here"
  },
  "llm": {
    "command": "inferred_command",
    "command_params": {}
  },
  "validator": {
    "validation_result": "valid"
  },
  "tts": {
    "audio_base64": "base64_encoded_audio"
  }
}

Note: The "audio_base64" field contains the generated TTS audio encoded in Base64. Decode and play it as needed.
