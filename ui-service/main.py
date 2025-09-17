import gradio as gr
import requests
import base64
import uuid
import os

import gradio_client.utils as gu

# --- PATCH for Gradio's JSON Schema bug ---
_original_json_schema_to_python_type = gu._json_schema_to_python_type

def _patched_json_schema_to_python_type(schema, defs=None):
    if isinstance(schema, bool):  # Fix: handle True/False schema
        return "dict[str, any]" if schema else "dict[str, None]"
    return _original_json_schema_to_python_type(schema, defs)

gu._json_schema_to_python_type = _patched_json_schema_to_python_type

# Orchestrator API URL
ORCHESTRATOR_URL = os.getenv(
    "ORCHESTRATOR_URL",
    "ORCHESTRATOR_URL=http://orchestrator:8500/voice_flow"  
)


def process_audio(file_path):
    """
    Sends the recorded/uploaded audio to the Orchestrator API
    and returns transcription text and/or TTS audio.
    """
    if not file_path:
        return "⚠️ Please upload or record an audio file first.", None

    try:
        with open(file_path, "rb") as f:
            files = {"audio": ("input_audio.wav", f, "audio/wav")}
            headers = {"id_correlation": str(uuid.uuid4())}

            resp = requests.post(ORCHESTRATOR_URL, files=files, headers=headers)

        if not resp.ok:
            return f"❌ Error {resp.status_code}: {resp.text}", None

        try:
            data = resp.json()
        except ValueError:
            return "❌ Invalid JSON response from Orchestrator", None

        # --- Extract pipeline outputs ---
        transcription = None
        tts_audio_path = None

        # STT
        if "stt" in data and "text" in data["stt"]:
            transcription = data["stt"]["text"]

        # TTS audio
        if "tts" in data and "audio_base64" in data["tts"]:
            audio_bytes = base64.b64decode(data["tts"]["audio_base64"])
            tts_audio_path = "tts_output.wav"
            with open(tts_audio_path, "wb") as out_f:
                out_f.write(audio_bytes)

        return transcription or "⚠️ No transcription available", tts_audio_path

    except Exception as e:
        return f"❌ Connection error: {e}", None


# --- Build Gradio Interface ---
with gr.Blocks() as demo:
    gr.Markdown("## 🎙️ SHATO Robot")
    gr.Markdown("Upload or record your **voice command** and let SHATO process it end-to-end.")

    with gr.Row():
        audio_input = gr.Audio(
            sources=["microphone", "upload"],
            type="filepath",
            label="🎤 Record or Upload Audio"
        )

    with gr.Row():
        trans_output = gr.Textbox(label="📝 Transcription")
        tts_output = gr.Audio(label="🔊 TTS Output", type="filepath")

    submit_btn = gr.Button("🚀 Send to Orchestrator")

    submit_btn.click(
        fn=process_audio,
        inputs=audio_input,
        outputs=[trans_output, tts_output]
    )


# Launch the app
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_api=False,
        inbrowser=False
    )
