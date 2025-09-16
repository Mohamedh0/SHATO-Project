import streamlit as st
import requests  # To send voice to the orchestrator
import io  # For handling audio bytes

st.title("SHATO Robot Controller")
st.write("Press the mic button below to record a command, like 'Rotate 90 degrees clockwise'.")

# Record button using your computer's mic
audio = st.experimental_audio_input("Record Your Command")

if audio:
    st.write("Sending your voice to SHATO...")
    # Pack the audio and send to the orchestrator service (it will handle STT, LLM, etc.)
    files = {'audio': ('command.wav', io.BytesIO(audio.getvalue()), 'audio/wav')}
    try:
        response = requests.post("http://orchestrator-api:8000/process", files=files)
        if response.status_code == 200:
            # Play the spoken reply from TTS
            st.audio(response.content, format='audio/wav')
            # Show the text response too
            st.write("Robot says: " + response.text)
        else:
            st.error("Something went wrong: " + response.text)
    except Exception as e:
        st.error("Error: " + str(e))