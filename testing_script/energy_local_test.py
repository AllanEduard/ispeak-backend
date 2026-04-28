import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import librosa
from model import load_model
from audio_analysis_processing_files.voice_energy_analyze import analyze_energy
from whisper_service import _compute_energy_score

audio_path = r"C:\Users\ALLAN\AppData\Local\Temp\myapp_uploads\Recording.m4a"
model = load_model("base")

def test_energy_analysis():
    y, sr = librosa.load(audio_path, sr=16000, mono=True)
    energy_stats = analyze_energy(y, sr)
    energy_score = _compute_energy_score(energy_stats)

    from pprint import pprint
    print("=== Energy Stats ===")
    pprint(energy_stats)
    print("=== Energy Score ===")
    print(energy_score)

test_energy_analysis()