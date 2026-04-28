import sys
import os
from typing import Any, Dict, List
import librosa

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from model import load_model
from audio_analysis_processing_files.voice_pacing_calculation import calculate_pacing
from whisper_service import _compute_pacing_score


def test_pacing_analysis():
    audio_path = r"C:\Users\ALLAN\AppData\Local\Temp\myapp_uploads\Recording.m4a"

    model = load_model("base")
    y, sr = librosa.load(audio_path, sr=16000, mono=True)
    transcription = model.transcribe(audio_path, word_timestamps=True, language="en")

    segments: List[Dict[str, Any]] = transcription.get("segments", [])
    audio_duration = transcription.get("duration")
    if not audio_duration:
        audio_duration = librosa.get_duration(y=y, sr=sr)
        print("Warning: duration missing from Whisper, falling back to librosa")

    pacing_stats = calculate_pacing(segments, audio_duration)
    pacing_score = _compute_pacing_score(pacing_stats)

    from pprint import pprint
    print("=== Pacing Stats ===")
    pprint(pacing_stats)
    print("=== Pacing Score ===")
    print(pacing_score)


test_pacing_analysis()