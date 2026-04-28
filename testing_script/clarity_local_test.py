import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from typing import List, Dict, Any
import statistics
import logging
from model import load_model
from audio_analysis_processing_files.clarity_analysis_module.voice_clarity_detection import analyze_clarity

def test_clarity_analysis():
    audio_path = r"C:\Users\ALLAN\AppData\Local\Temp\myapp_uploads\Recording.m4a"

    model = load_model("base")
    transcription = model.transcribe(audio_path, word_timestamps=True, language="en")
    
    word_segments: List[Dict[str, Any]] = transcription.get("segments", [])
    clarity_result = analyze_clarity(word_segments)

    from pprint import pprint
    print("=== Clarity Analysis Result ===")
    pprint(clarity_result)

test_clarity_analysis()