import gradio as gr
import requests

# Orchestrator API URL
ORCHESTRATOR_URL = "http://localhost:9000/orchestrator"

def pipeline(audio_file):
    """
    Send recorded audio to the Orchestrator and return the transcription text.
    """
    if audio_file is None:
        return "No audio recorded."

    try:
        # Send the file multipart/form-data
        with open(audio_file, "rb") as f:
            files = {"audio": f}
            response = requests.post(ORCHESTRATOR_URL, files=files)

        if response.status_code == 200:
            data = response.json()
            return data.get("text", "No transcription found in response.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the orchestrator API. Please ensure it’s running at http://localhost:9000/orchestrator."

# Gradio UI
with gr.Blocks() as app:
    gr.Markdown("## 🎤 Voice Input → Orchestrator")

    with gr.Row():
        audio_input = gr.Audio(
            sources=["microphone"], type="filepath", label="Record your voice"
        )

    record_btn = gr.Button("Send to Orchestrator")

    record_btn.click(
        fn=pipeline,
        inputs=audio_input,
    )

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)