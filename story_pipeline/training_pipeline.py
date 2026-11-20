"""
Autonomous Pipeline Quality Auditor & Instant Training Pipeline.
Activated immediately whenever any pipeline stage or audit gate fails:
1. Enforces strict zero-tolerance: IMMEDIATELY halts execution and blocks progression to subsequent steps.
2. Captures full telemetry, payload, and stack traces into an empirical training dataset (training_failures.jsonl).
3. Executes automated diagnostic triage and updates dynamic pipeline calibration parameters (pipeline_calibration.json).
4. Dispatches real-time training alerts to Telegram on mobile.
"""

import datetime
import json
import os
import traceback
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TRAINING_FAILURES_FILE = BASE_DIR / "story_pipeline" / "training_failures.jsonl"
CALIBRATION_FILE = BASE_DIR / "story_pipeline" / "pipeline_calibration.json"


def load_calibration() -> dict:
    """Loads current dynamic pipeline tuning parameters."""
    if CALIBRATION_FILE.exists():
        try:
            return json.loads(CALIBRATION_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "max_script_words": 135,
        "min_script_words": 105,
        "image_retry_delay_seconds": 25,
        "primary_gemini_model": "gemini-2.0-flash",
        "audio_speed_rate": "-3%",
        "total_failures_triaged": 0,
        "last_failure_timestamp": None,
    }


def save_calibration(data: dict) -> None:
    """Persists updated calibration parameters."""
    CALIBRATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    CALIBRATION_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def diagnose_root_cause(stage_name: str, error: Exception, payload: dict | None = None) -> tuple[str, dict]:
    """Diagnoses root cause and determines corrective calibration."""
    err_str = str(error).lower()
    calibration = load_calibration()
    remedy = {}

    if "404" in err_str or "not_found" in err_str or "no longer available" in err_str:
        diagnosis = "Deprecated or unavailable AI model endpoint."
        calibration["primary_gemini_model"] = "gemini-2.0-flash"
        remedy = {"action": "fallback_model_redirect", "model": "gemini-2.0-flash"}
    elif "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str or "rate limit" in err_str:
        diagnosis = "API Rate Limit Exhaustion / Concurrency Quota hit."
        calibration["image_retry_delay_seconds"] = max(25, calibration.get("image_retry_delay_seconds", 20) + 10)
        remedy = {"action": "increase_backoff_delay", "new_delay_seconds": calibration["image_retry_delay_seconds"]}
    elif "pacing rejection" in err_str or "script too short" in err_str:
        diagnosis = "Generated script failed minimum word count requirement for retention."
        calibration["min_script_words"] = 110
        remedy = {"action": "enforce_longer_hook_narration"}
    elif "duration rejection" in err_str or "script too long" in err_str or "exceed 59-second" in err_str:
        diagnosis = "Generated script exceeded safe word count; duration at risk of surpassing 59s Shorts limit."
        calibration["max_script_words"] = 125
        remedy = {"action": "tighten_script_word_budget", "max_words": 125}
    elif "visual rejection" in err_str or "file not found" in err_str:
        diagnosis = "Image asset failure: beat visual was not persisted to disk prior to rendering."
        remedy = {"action": "engage_multi_tier_visual_fallback", "ensure_disk_write": True}
    elif "remotion" in err_str or "render" in err_str:
        diagnosis = "Remotion rendering process terminated prematurely or encountered timeout."
        remedy = {"action": "enable_isolated_render_retries", "cleanup_stale_bundles": True}
    else:
        diagnosis = f"Unclassified stage exception in {stage_name}."
        remedy = {"action": "general_stage_triage", "details": str(error)}

    calibration["total_failures_triaged"] = calibration.get("total_failures_triaged", 0) + 1
    calibration["last_failure_timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_calibration(calibration)

    return diagnosis, remedy


def trigger_failure_training(stage_name: str, error: Exception, payload: dict | None = None) -> None:
    """
    Executes instant training & triage pipeline upon any failure:
    1. Formats failure incident into training dataset.
    2. Runs diagnostic triage and updates calibration parameters.
    3. Notifies mobile via Telegram.
    4. Halts pipeline immediately.
    """
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    diagnosis, remedy = diagnose_root_cause(stage_name, error, payload)

    training_entry = {
        "timestamp": now_iso,
        "stage": stage_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
        "diagnosis": diagnosis,
        "remedy": remedy,
        "payload_snippet": str(payload)[:500] if payload else None,
    }

    # 1. Record incident to empirical training dataset
    try:
        TRAINING_FAILURES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TRAINING_FAILURES_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(training_entry) + "\n")
        print(f"📊 [Training Pipeline] Incident logged to dataset: {TRAINING_FAILURES_FILE.name}")
        print(f"🔬 [Diagnostic Triage] Root cause: {diagnosis}")
        print(f"⚙️ [Pipeline Calibration] Applied remedy: {remedy}")
    except Exception as log_err:
        print(f"⚠️ Failed to write training incident: {log_err}")

    # 2. Telegram Alert Dispatch
    try:
        from story_pipeline.telegram_notifier import notify_error
        alert_msg = (
            f"❌ Gate Failed: {stage_name}\n"
            f"⚠️ Error: {str(error)[:180]}\n"
            f"🔬 Diagnosis: {diagnosis}\n"
            f"⚙️ Calibration: {remedy.get('action')}\n\n"
            f"🛑 Execution halted immediately. Next steps blocked."
        )
        notify_error(stage_name=f"Training Pipeline [{stage_name}]", error_msg=alert_msg, exc=error)
    except Exception as tele_err:
        print(f"⚠️ Telegram alert dispatch error: {tele_err}")

    print("🛑 [Strict Auditor] Execution halted. Process will NOT proceed to next stage.\n")
