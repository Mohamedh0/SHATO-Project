import gradio as gr
import requests
import base64
import tempfile
import os

# Orchestrator API URL
ORCHESTRATOR_URL = "http://localhost:9000/orchestrator"

def pipeline(audio_file):
    """
    Send recorded audio to the Orchestrator, handle both transcription (text) 
    and TTS response (audio).
    """
    if audio_file is None:
        return "No audio recorded.", None

    try:
        # Send the file multipart/form-data
        with open(audio_file, "rb") as f:
            files = {"audio": f}
            response = requests.post(ORCHESTRATOR_URL, files=files)

        if response.status_code == 200:
            data = response.json()

            # Case 1: Orchestrator returns text only
            if "text" in data and "audio_base64" not in data:
                return data["text"], None

            # Case 2: Orchestrator returns TTS response with audio
            if "audio_base64" in data:
                audio_bytes = base64.b64decode(data["audio_base64"])

                # Save to temp wav file
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                tmp_file.write(audio_bytes)
                tmp_file.close()

                return "Audio generated successfully.", tmp_file.name

            return "Unexpected response format.", None
        else:
            return f"Error: {response.status_code} - {response.text}", None

    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the orchestrator API.", None

# Gradio UI
with gr.Blocks() as app:
    gr.Markdown("## 🎤 Voice Input → Orchestrator")

    with gr.Row():
        audio_input = gr.Audio(
            sources=["microphone"], type="filepath", label="Record your voice"
        )

    record_btn = gr.Button("Send to Orchestrator")

    with gr.Row():
        text_output = gr.Textbox(label="Transcription / Status")
        audio_output = gr.Audio(label="TTS Output", type="filepath")

    record_btn.click(
        fn=pipeline,
        inputs=audio_input,
        outputs=[text_output, audio_output]
    )

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
