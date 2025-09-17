# Orchestrator Service

A service that orchestrates voice-to-command processing, including speech-to-text (STT), LLM inference, validation, and text-to-speech (TTS) generation.

---

## Usage Instructions

### 1. Run the Service

Start the orchestrator service using `uvicorn`:

```bash
uvicorn main:app --reload --port 8500

2. Test Endpoints
Health Check
Visit this URL in your browser to verify the service is running:



1
http://localhost:8500
Expected Response:

json


1
2
3
⌄
{
  "message": "Orchestrator service is running"
}
Voice Flow Endpoint (via Postman or cURL)
Process a voice command through the full pipeline: STT → LLM → Validator → TTS.

Method: POST
URL: http://localhost:8500/voice_flow
Body: form-data
audio
File
Select a
.wav
file (e.g.,
sample.wav
)

Example cURL:

bash


1
2
3
curl -X POST \
  http://localhost:8500/voice_flow \
  -F "audio=@sample.wav"
Expected Response:

json


1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
⌄
⌄
⌄
⌄
⌄
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
The audio_base64 field contains the generated TTS audio encoded in Base64. Decode and play it as needed. 
