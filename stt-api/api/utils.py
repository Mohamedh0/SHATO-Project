import torch
import torchaudio
import io
from transformers import WhisperProcessor, WhisperForConditionalGeneration

device = "cuda" if torch.cuda.is_available() else "cpu"

# load model + processor
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny").to(device)
processor = WhisperProcessor.from_pretrained("openai/whisper-tiny")

def transcribe_audio(audio_data: bytes) -> str:
    """
    Transcribe audio bytes (WAV/MP3) into text using Hugging Face Whisper.
    """
    try:
        with io.BytesIO(audio_data) as audio_file:
            # Load waveform
            waveform, sample_rate = torchaudio.load(audio_file)

            # Convert to mono if stereo
            if waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0, keepdim=True)

            # Resample to 16kHz (Whisper requirement)
            if sample_rate != 16000:
                resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                waveform = resampler(waveform)

            # Ensure float32 dtype
            waveform = waveform.to(torch.float32)

            # Whisper expects shape: (samples,)
            input_features = processor(
                waveform.squeeze(0),
                sampling_rate=16000,
                return_tensors="pt"
            ).input_features.to(device)

            # Generate transcription
            predicted_ids = model.generate(input_features)
            transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

            return transcription

    except Exception as e:
        raise ValueError(f"Error processing audio: {str(e)}")
