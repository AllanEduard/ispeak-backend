<<<<<<< HEAD
##########################################################
# THIS IS NOT NEEDED. INTENDED ONLY FOR TESTING MODULES. #
#########################################################




import json
import librosa
from audio_analysis_processing_files.voice_energy_analyze import analyze_energy
from audio_analysis_processing_files.voice_pacing_calculation import calculate_pacing
from audio_analysis_processing_files.clarity_analysis_module.voice_clarity_detection import analyze_pronunciation
from whisper_service import _compute_energy_score, _compute_overall_score, _compute_pacing_score, generate_full_analysis
import whisper


AUDIO_PATH = r"C:\Users\ALLAN\AppData\Local\Temp\myapp_uploads\temporary_audio.mp3" 

# ---------- ENERGY ----------
print("\n--- Testing Energy Module ---")
y, sr = librosa.load(AUDIO_PATH, sr=16000, mono=True)
energy_result = analyze_energy(y, sr)
score_energy = _compute_energy_score(energy_result)
print(json.dumps(energy_result, indent=2))
print(f"Loudness Status: {energy_result.get('loudness_status')}")
print(f"Energy Score: {score_energy}")

# ---------- PACING ----------
print("\n--- Testing Pacing Module ---")
model = whisper.load_model("small")  # instead of "base"
transcription = model.transcribe(AUDIO_PATH, word_timestamps=True)
segments = transcription.get("segments", [])

# whisper doesn't return "duration" directly — calculate it from the audio
audio_duration = librosa.get_duration(path=AUDIO_PATH)
pacing_result = calculate_pacing(segments, audio_duration)
score_pacing = _compute_pacing_score(pacing_result)
print(json.dumps(pacing_result, indent=2))
print(f"Pacing Status: {pacing_result.get('pacing_status')}")
print(f"Pacing Score: {score_pacing}")

# ---------- PRONUNCIATION ----------
print("\n--- Testing Pronunciation Module ---")
word_segments = [
    {
        "text": word.get("word", ""),
        "start": word.get("start"),
        "end": word.get("end"),
        "confidence": word.get("probability", 0.0),  # whisper uses "probability"
    }
    for seg in segments
    for word in seg.get("words", [])
]
print("word segments found:", len(word_segments))

pronunciation_result = analyze_pronunciation(word_segments)
print(json.dumps(pronunciation_result, indent=2))
print(f"Clarity Score: {pronunciation_result.get('pronunciation_score')}")

# ---------- OVERALL SCORE ----------
print("\n--- Testing Overall Score Calculation ---")
overall_score = _compute_overall_score(score_pacing, pronunciation_result.get("pronunciation_score", 0), score_energy)
print(f"Overall Score: {overall_score}")
=======
#######################
# THIS IS NOT NEEDED #
#######################




import json
import librosa
from audio_analysis_processing_files.voice_energy_analyze import analyze_energy
from audio_analysis_processing_files.voice_pacing_calculation import calculate_pacing
from audio_analysis_processing_files.clarity_analysis_module.voice_clarity_detection import analyze_pronunciation
import whisper


AUDIO_PATH = r"C:\Users\ALLAN\AppData\Local\Temp\myapp_uploads\temporary_audio.mp3" 

# ---------- ENERGY ----------
print("\n--- Testing Energy Module ---")
y, sr = librosa.load(AUDIO_PATH, sr=16000, mono=True)
energy_result = analyze_energy(y, sr)
print(json.dumps(energy_result, indent=2))

# ---------- PACING ----------
print("\n--- Testing Pacing Module ---")
model = whisper.load_model("small")  # instead of "base"
transcription = model.transcribe(AUDIO_PATH, word_timestamps=True)
segments = transcription.get("segments", [])

# whisper doesn't return "duration" directly — calculate it from the audio
audio_duration = librosa.get_duration(path=AUDIO_PATH)

pacing_result = calculate_pacing(segments, audio_duration)
print(json.dumps(pacing_result, indent=2))

# ---------- PRONUNCIATION ----------
print("\n--- Testing Pronunciation Module ---")
word_segments = [
    {
        "text": word.get("word", ""),
        "start": word.get("start"),
        "end": word.get("end"),
        "confidence": word.get("probability", 0.0),  # whisper uses "probability"
    }
    for seg in segments
    for word in seg.get("words", [])
]
print("word segments found:", len(word_segments))

pronunciation_result = analyze_pronunciation(word_segments)
print(json.dumps(pronunciation_result, indent=2))
>>>>>>> 00555d3f5feaa893f974aefee632b8654d1d0732
