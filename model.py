# model.py
import whisper

def load_model(model_name: str = "base"):
    return whisper.load_model(model_name)
