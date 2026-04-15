<<<<<<< HEAD
from typing import List, Dict
import re
import logging


logger = logging.getLogger(__name__)


def calculate_pacing(
    whisper_segments: List[Dict],
    audio_duration_seconds: float,
    slow: int = 110,
    fast: int = 160,
    pause_threshold: float = 0.85,
    timing_jitter: float = 0.15,
) -> Dict:

    if audio_duration_seconds <= 0:
        raise ValueError("Invalid audio duration")

    if not whisper_segments:
        return {
            "wpm": 0.0,
            "articulation_rate": 0.0,
            "pacing_status": "No speech detected",
            "total_pause_seconds": 0.0,
        }

    required_keys = {"start", "end", "text"}
    for i, seg in enumerate(whisper_segments):
        if not required_keys <= seg.keys():
            raise ValueError(f"Malformed segment at index {i}")

    # ---------- WORD COUNT ----------
    total_words = 0
    total_pause_time = 0.0
    speaking_time = 0.0

    for i, segment in enumerate(whisper_segments):

        duration = max(0.0, segment["end"] - segment["start"])
        speaking_time += duration

        words = re.findall(r"[\w'-]+", segment["text"], re.UNICODE)
        total_words += len(words)

        # ---------- PAUSE DETECTION ----------
        if i > 0:
            previous = whisper_segments[i - 1]

            raw_pause = segment["start"] - previous["end"]
            perceived_pause = max(0.0, raw_pause - timing_jitter)

            # Option A — count full pause duration
            if perceived_pause > pause_threshold:
                total_pause_time += perceived_pause

    if speaking_time <= 0:
        return {
            "wpm": 0.0,
            "articulation_rate": 0.0,
            "pacing_status": "Insufficient speech",
            "total_pause_seconds": round(total_pause_time, 2),
        }

    # ---------- SPEED METRICS ----------
    real_minutes = audio_duration_seconds / 60.0
    speaking_minutes = speaking_time / 60.0

    wpm = total_words / real_minutes
    articulation_rate = total_words / speaking_minutes

    # ---------- PACING CLASSIFICATION ----------
    pacing_status = (
        "Slow pacing" if wpm < slow
        else "Fast pacing" if wpm > fast
        else "Excellent pacing"
    )

    # ---------- SANITY CHECK ----------
    if speaking_time > audio_duration_seconds * 1.05:
        logger.warning("Speaking time exceeds audio duration")

    return {
        "wpm": round(wpm, 1),
        "articulation_rate": round(articulation_rate, 1),
        "pacing_status": pacing_status,
        "total_pause_seconds": round(total_pause_time, 2),
    }

if __name__ == "__main__":
    segments = [
        {"start": 0.0, "end": 3.0, "text": "Hello this is a test"},
        {"start": 3.5, "end": 6.0, "text": "of the pacing function"},
        {"start": 7.2, "end": 10.0, "text": "with some pauses in between"},
    ]
    audio_duration = 10.0
    result = calculate_pacing(segments, audio_duration)
=======
from typing import List, Dict
import re
import logging


logger = logging.getLogger(__name__)


def calculate_pacing(
    whisper_segments: List[Dict],
    audio_duration_seconds: float,
    slow: int = 110,
    fast: int = 160,
    pause_threshold: float = 0.85,
    timing_jitter: float = 0.15,
) -> Dict:

    if audio_duration_seconds <= 0:
        raise ValueError("Invalid audio duration")

    if not whisper_segments:
        return {
            "wpm": 0.0,
            "articulation_rate": 0.0,
            "pacing_status": "No speech detected",
            "total_pause_seconds": 0.0,
        }

    required_keys = {"start", "end", "text"}
    for i, seg in enumerate(whisper_segments):
        if not required_keys <= seg.keys():
            raise ValueError(f"Malformed segment at index {i}")

    # ---------- WORD COUNT ----------
    total_words = 0
    total_pause_time = 0.0
    speaking_time = 0.0

    for i, segment in enumerate(whisper_segments):

        duration = max(0.0, segment["end"] - segment["start"])
        speaking_time += duration

        words = re.findall(r"[\w'-]+", segment["text"], re.UNICODE)
        total_words += len(words)

        # ---------- PAUSE DETECTION ----------
        if i > 0:
            previous = whisper_segments[i - 1]

            raw_pause = segment["start"] - previous["end"]
            perceived_pause = max(0.0, raw_pause - timing_jitter)

            # Option A — count full pause duration
            if perceived_pause > pause_threshold:
                total_pause_time += perceived_pause

    if speaking_time <= 0:
        return {
            "wpm": 0.0,
            "articulation_rate": 0.0,
            "pacing_status": "Insufficient speech",
            "total_pause_seconds": round(total_pause_time, 2),
        }

    # ---------- SPEED METRICS ----------
    real_minutes = audio_duration_seconds / 60.0
    speaking_minutes = speaking_time / 60.0

    wpm = total_words / real_minutes
    articulation_rate = total_words / speaking_minutes

    # ---------- PACING CLASSIFICATION ----------
    pacing_status = (
        "Slow pacing" if wpm < slow
        else "Fast pacing" if wpm > fast
        else "Excellent pacing"
    )

    # ---------- SANITY CHECK ----------
    if speaking_time > audio_duration_seconds * 1.05:
        logger.warning("Speaking time exceeds audio duration")

    return {
        "wpm": round(wpm, 1),
        "articulation_rate": round(articulation_rate, 1),
        "pacing_status": pacing_status,
        "total_pause_seconds": round(total_pause_time, 2),
    }

if __name__ == "__main__":
    segments = [
        {"start": 0.0, "end": 3.0, "text": "Hello this is a test"},
        {"start": 3.5, "end": 6.0, "text": "of the pacing function"},
        {"start": 7.2, "end": 10.0, "text": "with some pauses in between"},
    ]
    audio_duration = 10.0
    result = calculate_pacing(segments, audio_duration)
>>>>>>> 00555d3f5feaa893f974aefee632b8654d1d0732
    print(result)