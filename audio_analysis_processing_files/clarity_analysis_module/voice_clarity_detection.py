from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any
import statistics
import logging

logger = logging.getLogger(__name__)

# Configuration

@dataclass
class PronunciationConfig:
    min_confidence: float = 0.75
    min_word_duration: float = 0.08
    max_word_duration: float = 1.2

    confidence_weight: float = 0.7
    duration_weight: float = 0.3


DEFAULT_CONFIG = PronunciationConfig()


SCORE_THRESHOLDS = [
    (85, "Excellent pronunciation"),
    (70, "Good pronunciation with minor issues"),
    (50, "Noticeable pronunciation problems"),
    (0,  "Pronunciation needs improvement"),
]

# Helpers

def _normalize_weights(cfg: PronunciationConfig) -> tuple[float, float]:
    total = cfg.confidence_weight + cfg.duration_weight

    if total <= 0:
        raise ValueError("Invalid scoring weights")

    return (
        cfg.confidence_weight / total,
        cfg.duration_weight / total,
    )


def _safe_confidence(value: Any) -> float:
    """Safely parse and clamp confidence."""
    try:
        conf = float(value)
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, min(conf, 1.0))


def _duration_score(duration: float, cfg: PronunciationConfig) -> float:
    """
    Smooth duration scoring (0–1).

    - Linear ramp for short words
    - Gentle decay for overly long words
    """

    if duration <= 0:
        return 0.0

    if duration < cfg.min_word_duration:
        # Linear ramp-up
        return duration / cfg.min_word_duration

    if duration > cfg.max_word_duration:
        excess = duration - cfg.max_word_duration
        penalty = excess / cfg.max_word_duration
        return max(0.5, 1.0 - penalty)

    return 1.0


def _feedback_message(score: int) -> str:
    return next(
        msg for threshold, msg in SCORE_THRESHOLDS
        if score >= threshold
    )


# Main Analysis

def analyze_pronunciation(
    word_segments: List[Dict[str, Any]],
    config: PronunciationConfig = DEFAULT_CONFIG
) -> Dict[str, Any]:
    """
    Compute pronunciation quality score (0–100).

    Expected word format:
        {
            "text": str,
            "start": float,
            "end": float,
            "confidence": float
        }
    """

    if not word_segments:
        return {
            "pronunciation_score": 0,
            "problematic_words": [],
            "message": "No speech detected"
        }

    conf_w, dur_w = _normalize_weights(config)

    scores: List[float] = []
    problematic_words: List[Dict[str, Any]] = []

    for word in word_segments:

        text = str(word.get("text", "")).strip()
        start = word.get("start")
        end = word.get("end")

        if not text:
            continue

        # ---- timestamp validation ----
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            logger.warning("Invalid timestamps for word: %s", text)
            continue

        if end < start:
            logger.warning("Inverted timestamps for word: %s", text)
            duration = 0.0
            inverted = True
        else:
            duration = end - start
            inverted = False

        confidence = _safe_confidence(word.get("confidence"))

        dur_score = _duration_score(duration, config)

        word_score = (
            conf_w * confidence +
            dur_w * dur_score
        )

        scores.append(word_score)

        # ---- issue diagnostics ----
        issues = []

        if confidence < config.min_confidence:
            issues.append("low confidence")

        if dur_score < 0.95:
            issues.append("unusual duration")

        if inverted:
            issues.append("invalid timestamps")

        if issues:
            problematic_words.append({
                "word": text,
                "confidence": round(confidence, 2),
                "duration": round(duration, 2),
                "issue": ", ".join(issues),
            })

    if not scores:
        return {
            "pronunciation_score": 0,
            "problematic_words": [],
            "message": "No valid words analyzed"
        }

    final_score = round(statistics.mean(scores) * 100)

    return {
        "pronunciation_score": final_score,
        "problematic_words": problematic_words,
        "message": _feedback_message(final_score),
    }

