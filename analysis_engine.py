# ============================================================
# File: analysis_engine.py
# Wires the Streamlit UI to the real Module 1/2/3 engines:
#   speech_to_text.py   -> transcribe_audio()
#   semantic_engine.py  -> evaluate_understanding()
#   audio_features.py   -> analyze_audio()
# Replaces the old fabricated "analyze_audio_file_dynamically".
# ============================================================

import os
import tempfile
import logging
from typing import Dict, Any

import streamlit as st

from speech_to_text import transcribe_audio
from semantic_engine import evaluate_understanding
from audio_features import analyze_audio
from config import REFERENCE_CONCEPT_TEXT

logger = logging.getLogger("analysis_engine")

# Weights for combining the three sub-scores into one final score (0-100).
# similarity carries the most weight since "understanding" is the core goal;
# fluency and confidence are secondary delivery signals.
WEIGHT_SIMILARITY = 0.5
WEIGHT_FLUENCY = 0.3
WEIGHT_CONFIDENCE = 0.2


class AnalysisPipelineError(Exception):
    """Raised when the end-to-end analysis pipeline cannot produce a result."""
    pass


@st.cache_resource(show_spinner=False)
def _warm_models():
    """
    Triggers model loading once per Streamlit server process instead of
    once per uploaded file. transcribe_audio/evaluate_understanding already
    cache their own singleton engines internally, so this just forces that
    caching to happen the first time the app starts handling requests.
    """
    return True


def _save_uploaded_file(uploaded_file) -> str:
    """Streamlit's UploadedFile isn't a real path; Whisper/librosa need one on disk."""
    suffix = os.path.splitext(uploaded_file.name)[1].lower() or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name


def _classify_final_level(final_score: int) -> str:
    if final_score >= 80:
        return "Strong Understanding"
    elif final_score >= 50:
        return "Moderate Understanding"
    else:
        return "Poor Understanding"


def run_real_analysis(uploaded_file, reference_text: str = REFERENCE_CONCEPT_TEXT) -> Dict[str, Any]:
    """
    Runs the full pipeline on a single uploaded audio file and returns a
    metrics dict shaped exactly like the one the UI/PDF code already expects:
    transcript, semantic_similarity, filler_word_ratio, pause_ratio,
    confidence, final_score, understanding_level (+ feedback, extras).
    """
    _warm_models()
    temp_path = _save_uploaded_file(uploaded_file)

    try:
        # --- Module 1: Speech-to-Text -----------------------------------
        stt_result = transcribe_audio(temp_path)
        transcript = (stt_result.get("transcript") or "").strip()

        if stt_result.get("error"):
            raise AnalysisPipelineError(f"Transcription failed: {stt_result['error']}")
        if not transcript:
            raise AnalysisPipelineError(
                "No speech was detected in this recording. Please upload a clearer audio file."
            )

        # --- Module 2: Semantic Similarity -------------------------------
        semantic_result = evaluate_understanding(reference_text, transcript)
        if semantic_result.get("level") == "Error":
            raise AnalysisPipelineError(f"Semantic evaluation failed: {semantic_result['feedback']}")

        # --- Module 3: Audio Feature / Fluency Extraction -----------------
        audio_result = analyze_audio(temp_path, transcript)
        if audio_result.get("error"):
            raise AnalysisPipelineError(f"Audio feature extraction failed: {audio_result['error']}")

        similarity_pct = semantic_result["similarity"]          # 0-100
        fluency_score = audio_result["fluency_score"]            # 0-100
        confidence_score = audio_result["confidence_score"]      # 0-100

        final_score_num = round(
            WEIGHT_SIMILARITY * similarity_pct
            + WEIGHT_FLUENCY * fluency_score
            + WEIGHT_CONFIDENCE * confidence_score
        )
        final_score_num = min(max(final_score_num, 0), 100)

        word_count = len(transcript.split())
        filler_ratio = round(audio_result["filler_count"] / word_count, 3) if word_count else 0.0

        return {
            "transcript": transcript,
            "semantic_similarity": similarity_pct,
            "filler_word_ratio": filler_ratio,
            "pause_ratio": audio_result["pause_ratio"],
            "confidence": confidence_score,
            "final_score": f"{final_score_num}/100",
            "understanding_level": _classify_final_level(final_score_num),
            # Extra fields available to the UI/PDF if you want to show more detail:
            "feedback": semantic_result["feedback"],
            "speaking_rate": audio_result["speaking_rate"],
            "filler_count": audio_result["filler_count"],
            "fluency_score": fluency_score,
            "duration": audio_result["duration"],
            "language": stt_result.get("language", "unknown"),
        }

    except AnalysisPipelineError:
        raise
    except Exception as exc:
        logger.exception("Unexpected failure in analysis pipeline")
        raise AnalysisPipelineError(f"Unexpected error during analysis: {exc}") from exc

    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass
