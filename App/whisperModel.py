import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset
import re

# Device and data type configuration
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# Load the model and set up the processor
model_id = "openai/whisper-large-v3"
translator_model_id = "Helsinki-NLP/opus-mt-hi-en"
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

translator = pipeline(
    "translation",
    model=translator_model_id,
    tokenizer=translator_model_id,
    device=device
)


processor = AutoProcessor.from_pretrained(model_id)

# Create a pipeline for ASR tasks
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=30,
    batch_size=16,
    return_timestamps=True,
    torch_dtype=torch_dtype,
    device=device,
)

# Define a function for language detection
def detect_language(text):
    if re.search(r'[a-zA-Z]', text):
        return "English"
    else:
        return "Hindi"

# Device and data type configuration
classifier = pipeline("sentiment-analysis", model="michellejieli/emotion_text_classifier")


def detect(data):
    # Transcribe the audio file
    transcription = pipe(data)['text']

    # Detect the language of transcription
    language = detect_language(transcription)

    if language == "English":
        print(transcription)
        return transcription
    else:
        print(transcription)
        english_translation = translator(transcription)
        print(english_translation)
        return english_translation