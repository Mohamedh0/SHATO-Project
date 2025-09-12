import torch
import torchaudio
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import io

device = 'cuda' if torch.cuda.is_available() else 'cpu'

model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny").to(device)
processor = WhisperProcessor.from_pretrained("openai/whisper-tiny")

def transcribe_audio(audio_data: bytes) -> str:
    """
    Transcribe audio bytes from a WAV or MP3 file to text using Whisper.
    """
    try:
        # Create a new BytesIO object for loading
        with io.BytesIO(audio_data) as audio_file:
            # Load audio and let torchaudio auto-detect the format
            waveform, sample_rate = torchaudio.load(audio_file)
            
            # Convert to mono by averaging channels if stereo
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            
            # Resample to 16kHz if necessary (Whisper expects 16000 Hz)
            if sample_rate != 16000:
                resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                waveform = resampler(waveform)
            
            # Process audio with Whisper processor
            input_features = processor(waveform.squeeze(0), sampling_rate=16000, return_tensors="pt").input_features.to(device)
            
            # Generate transcription
            predicted_ids = model.generate(input_features)
            transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            
            return transcription
    except Exception as e:
        raise ValueError(f"Error processing audio: {str(e)}")