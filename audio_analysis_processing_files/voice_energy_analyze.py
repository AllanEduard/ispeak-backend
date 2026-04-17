import numpy as np
import librosa
from typing import Dict, List


# ---------------- CONFIG ----------------

WHISPER_THRESHOLD_DB = -40.0
SHOUT_THRESHOLD_DB = -10.0

LOW_VARIATION_DB = 12.0
MONOTONE_PITCH_STD_THRESHOLD = 20.0  # Hz variation

MIN_ACTIVE_RATIO = 0.10
MIN_FRAMES_FOR_ROBUST_PERCENTILE = 50

DEFAULT_FRAME_LENGTH = 1024
DEFAULT_HOP_LENGTH = 256


# ---------------- GLOBAL ANALYSIS ----------------
def analyze_energy(
    y: np.ndarray,
    sr: int,
    silence_threshold: float = 1e-4,
    frame_length: int = DEFAULT_FRAME_LENGTH,
    hop_length: int = DEFAULT_HOP_LENGTH,
) -> Dict:

    rms_energy = librosa.feature.rms(
        y=y,
        frame_length=frame_length,
        hop_length=hop_length,
    ).squeeze()

    active_ratio = float(np.mean(rms_energy > silence_threshold))

    if active_ratio < MIN_ACTIVE_RATIO:
        return {
            "average_volume_db": -80.0,
            "dynamic_range": 0.0,
            "loudness_status": "Silence",
            "is_low_variation": True,
            "is_monotone": True,
        }

    avg_power = np.mean(rms_energy ** 2)
    average_db = float(10 * np.log10(max(avg_power, 1e-10)))

    if average_db < WHISPER_THRESHOLD_DB:
        loudness_status = "Too quiet (whispering)"
    elif average_db > SHOUT_THRESHOLD_DB:
        loudness_status = "Too loud (shouting)"
    else:
        loudness_status = "Normal volume"

    rms_energy = np.clip(rms_energy, 1e-10, None)
    db_levels = librosa.amplitude_to_db(rms_energy, ref=1.0)

    if len(db_levels) >= 2:
        if len(db_levels) >= MIN_FRAMES_FOR_ROBUST_PERCENTILE:
            p_low, p_high = 5, 95
        else:
            p_low, p_high = 0, 100

        dynamic_range = float(
            np.percentile(db_levels, p_high)
            - np.percentile(db_levels, p_low)
        )
    else:
        dynamic_range = 0.0

    is_low_variation = dynamic_range < LOW_VARIATION_DB

    try:
        f0, voiced_flag, _ = librosa.pyin(
            y,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
        )

        voiced_f0 = f0[voiced_flag]
        pitch_std = float(np.std(voiced_f0)) if len(voiced_f0) > 0 else 0.0
        is_monotone = pitch_std < MONOTONE_PITCH_STD_THRESHOLD

    except Exception:
        pitch_std = 0.0
        is_monotone = True

    return {
        "average_volume_db": round(average_db, 2),
        "dynamic_range": round(dynamic_range, 2),
        "loudness_status": loudness_status,
        "is_low_variation": is_low_variation,
        "pitch_variation_hz": round(pitch_std, 2),
        "is_monotone": is_monotone,
    }


# ---------------- PER-WORD ANALYSIS ----------------

def extract_audio_segment(y, sr, start, end):
    start_sample = int(start * sr)
    end_sample = int(end * sr)
    return y[start_sample:end_sample]


def compute_segment_db(y_segment):
    if len(y_segment) == 0:
        return -80.0

    rms = librosa.feature.rms(y=y_segment).squeeze()
    if len(rms) == 0:
        return -80.0

    avg_power = np.mean(rms ** 2)
    db = 10 * np.log10(max(avg_power, 1e-10))
    return float(db)


def classify_loudness(db):
    if db < WHISPER_THRESHOLD_DB:
        return "whisper"
    elif db > SHOUT_THRESHOLD_DB:
        return "shout"
    else:
        return "normal"


def analyze_per_word(y, sr, whisper_result) -> List[Dict]:
    word_results = []

    for segment in whisper_result.get("segments", []):
        for word_info in segment.get("words", []):
            start = word_info["start"]
            end = word_info["end"]
            word = word_info["word"]

            y_segment = extract_audio_segment(y, sr, start, end)
            db = compute_segment_db(y_segment)
            label = classify_loudness(db)

            word_results.append({
                "word": word,
                "start": round(start, 2),
                "end": round(end, 2),
                "volume_db": round(db, 2),
                "loudness": label
            })

    return word_results


# ---------------- MAIN PIPELINE ----------------

def generate_full_analysis(temp_path: str, model):
    y, sr = librosa.load(temp_path, sr=16000, mono=True)

    result = model.transcribe(
        temp_path,
        word_timestamps=True
    )

    # Global analysis
    energy_analysis = analyze_energy(y, sr)

    # Per-word analysis
    word_analysis = analyze_per_word(y, sr, result)

    return {
        "text": result.get("text", ""),
        "energy": energy_analysis,
        "word_analysis": word_analysis
    }
