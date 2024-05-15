from whisperModel import pipe

# Specify the path to your .wav file
wav_file_path = "uploads/16.wav"

# Use the pipeline to transcribe the local audio file
result = pipe(wav_file_path)
print(result["text"])


from transformers import pipeline

# from pyannote.audio import Pipeline

#  Text to Speech
whisper = pipeline('automatic-speech-recognition', model = 'openai/whisper-medium', device = -1)

""" whisper_model = None

def load_models():
    global whisper_model
    if whisper_model is None:
        whisper_model = pipeline('automatic-speech-recognition', model='openai/whisper-medium', device=-1)
 """
# Emotion Recognition
# emotion = pipeline('audio-classification',model='superb/wav2vec2-base-superb-er')
emotion = pipeline("audio-classification", model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition", device = -1)
# Speaker Segementation 
""" segmentation = Pipeline.from_pretrained(
  "pyannote/speaker-diarization-3.0",
  use_auth_token="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") """