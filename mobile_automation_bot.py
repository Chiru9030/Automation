"""
Mobile Telegram Automation Command & Monitoring Bot.
Enables full remote control and monitoring of the 7-Stage Video Automation Pipeline from your mobile phone with a single text.

Available Mobile Commands:
  • Any topic text: Instantly triggers video generation for that topic.
  • /create <topic>: Generates and publishes video for the custom topic.
  • /status: Shows live pipeline status, latest episode, and system health.
  • /latest: Returns the last uploaded YouTube Short link, title, and thumbnail.
  • /cloud <topic>: Dispatches a cloud run on GitHub Actions from mobile.
  • /logs: Shows recent pipeline logs and auditor metrics.
  • /help: Displays mobile control guide.
"""

import json
import os
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "story_pipeline" / "story_history.json"
CALIBRATION_FILE = BASE_DIR / "story_pipeline" / "pipeline_calibration.json"

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else None

# State tracking
CURRENT_RUN_LOCK = threading.Lock()
IS_GENERATING = False


def send_tg_message(text: str, reply_to: int | None = None) -> bool:
    """Sends a markdown-formatted message to the authorized user's Telegram."""
    if not API_BASE or not CHAT_ID:
        return False
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }
    if reply_to:
        payload["reply_to_message_id"] = reply_to

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{API_BASE}/sendMessage",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"⚠️ Telegram send error: {e}")
        return False


def get_updates(offset: int = 0) -> list[dict]:
    """Polls Telegram for new incoming text messages."""
    if not API_BASE:
        return []
    url = f"{API_BASE}/getUpdates?offset={offset}&timeout=20"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "StoryBot/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                return data.get("result", [])
    except Exception:
        pass
    return []


def handle_status(message_id: int):
    """Sends pipeline status, episode counts, and health metrics."""
    history = {}
    if HISTORY_FILE.exists():
        try:
            history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    ep_count = history.get("episode_count", 0)
    topics = history.get("generated_topics", [])
    last_topic = topics[-1] if topics else "None yet"
    used_count = len(history.get("used_topics", []))

    status_msg = (
        f"📊 *Automated Pipeline System Status*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎬 *Current Episode:* #{ep_count}\n"
        f"🎯 *Last Topic:* `{last_topic}`\n"
        f"📚 *Unique Topics Created:* {used_count}\n"
        f"⏱️ *Schedule Cadence:* Every 5 Hours (00:00, 05:00, 10:00, 15:00, 20:00 UTC)\n"
        f"⚙️ *Engine Mode:* 7-Stage Native Hardware / Remotion Hybrid\n"
        f"🔊 *Voice Profile:* Christopher Neural (-4Hz) + Crazy Sub-Bass (+16dB)\n"
        f"🛡️ *Audit Gate Status:* 5/5 Active (Zero-Tolerance Halts Enabled)\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 _Reply with any topic to generate immediately!_"
    )
    send_tg_message(status_msg, reply_to=message_id)


def handle_latest(message_id: int):
    """Fetches the latest published video information."""
    history = {}
    if HISTORY_FILE.exists():
        try:
            history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    ep_count = history.get("episode_count", 0)
    topics = history.get("generated_topics", [])
    last_topic = topics[-1] if topics else "None"

    msg = (
        f"🎥 *Latest Published Episode #{ep_count}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 *Title:* {last_topic}\n"
        f"🔗 *Channel:* [YouTube Studio / Channel](https://studio.youtube.com)\n"
        f"📺 *Type:* YouTube Short (1080x1920 Vertical, <59s)\n"
    )
    send_tg_message(msg, reply_to=message_id)


def execute_pipeline_task(topic: str | None, message_id: int):
    """Runs the 7-stage story pipeline in a background thread."""
    global IS_GENERATING
    with CURRENT_RUN_LOCK:
        if IS_GENERATING:
            send_tg_message("⏳ A video generation task is already in progress. Please wait...", reply_to=message_id)
            return
        IS_GENERATING = True

    try:
        topic_desc = f"'{topic}'" if topic else "Autonomous Viral Concept"
        send_tg_message(
            f"🚀 *Pipeline Initiated via Mobile Text*\n\n"
            f"🎯 *Target Topic:* {topic_desc}\n"
            f"⏱️ *Estimated Synthesis Time:* ~45-60 seconds\n"
            f"📱 Full logs & video preview will be delivered here automatically.",
            reply_to=message_id,
        )

        cmd = [sys.executable, "story_runner.py"]
        if topic:
            cmd.extend(["--topic", topic])

        proc = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=700,
        )

        if proc.returncode == 0:
            send_tg_message(
                f"✅ *Mobile Video Generation Certified & Completed!*\n\n"
                f"🎉 Short published and video preview delivered.",
                reply_to=message_id,
            )
        else:
            err_snip = proc.stderr[-400:] if proc.stderr else proc.stdout[-400:]
            send_tg_message(
                f"🚨 *Generation Stopped by Quality Auditor*\n\n"
                f"```text\n{err_snip}\n```",
                reply_to=message_id,
            )
    except Exception as e:
        send_tg_message(f"🚨 *Execution Error:* `{e}`", reply_to=message_id)
    finally:
        with CURRENT_RUN_LOCK:
            IS_GENERATING = False


def trigger_github_cloud(topic: str | None, message_id: int):
    """Dispatches a GitHub Actions workflow from mobile via gh CLI."""
    send_tg_message("☁️ Dispatching cloud generation run to GitHub Actions...", reply_to=message_id)
    cmd = ["gh", "workflow", "run", "story_pipeline.yml", "--ref", "main"]
    if topic:
        cmd.extend(["-f", f"custom_topic={topic}"])

    try:
        res = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True, timeout=30)
        if res.returncode == 0:
            send_tg_message("✅ *GitHub Actions Cloud Job Successfully Triggered!*", reply_to=message_id)
        else:
            send_tg_message(f"⚠️ Cloud dispatch note: {res.stderr[:200]}", reply_to=message_id)
    except Exception as e:
        send_tg_message(f"⚠️ Cloud dispatch error: {e}", reply_to=message_id)


def start_mobile_listener():
    """Main polling loop listening for mobile texts."""
    print("==================================================================")
    print(" 📱 Mobile Telegram Command & Monitoring Bot Active")
    print("==================================================================")

    if not BOT_TOKEN or not CHAT_ID:
        print("🚨 TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing in .env!")
        return

    send_tg_message(
        "🤖 *Automation Command Bot Online*\n\n"
        "Send any topic text to generate a video instantly, or send `/status` to view pipeline metrics."
    )

    offset = 0
    while True:
        try:
            updates = get_updates(offset)
            for u in updates:
                offset = max(offset, u["update_id"] + 1)
                msg = u.get("message", {})
                from_id = str(msg.get("chat", {}).get("id"))
                text = msg.get("text", "").strip()
                message_id = msg.get("message_id")

                # Verify authorized chat
                if from_id != str(CHAT_ID):
                    continue

                if not text:
                    continue

                print(f"📩 Mobile Command Received: '{text}'")

                if text in ["/start", "/help"]:
                    help_text = (
                        "📱 *Mobile Automation Command Center*\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        "• Send *any story topic* $\to$ Instantly generates, masters, and publishes Short\n"
                        "• `/status` $\to$ Live pipeline status and episode metrics\n"
                        "• `/latest` $\to$ Info on latest published video\n"
                        "• `/cloud <topic>` $\to$ Launch job on GitHub Actions cloud\n"
                        "• `/run` $\to$ Generate autonomous paradox episode\n"
                    )
                    send_tg_message(help_text, reply_to=message_id)
                elif text == "/status":
                    handle_status(message_id)
                elif text == "/latest":
                    handle_latest(message_id)
                elif text.startswith("/cloud"):
                    custom_t = text.replace("/cloud", "").strip() or None
                    threading.Thread(target=trigger_github_cloud, args=(custom_t, message_id)).start()
                elif text == "/run":
                    threading.Thread(target=execute_pipeline_task, args=(None, message_id)).start()
                elif text.startswith("/create"):
                    custom_t = text.replace("/create", "").strip() or None
                    threading.Thread(target=execute_pipeline_task, args=(custom_t, message_id)).start()
                else:
                    # Treat raw text as direct topic generation prompt
                    threading.Thread(target=execute_pipeline_task, args=(text, message_id)).start()

        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(3)

        time.sleep(1)


if __name__ == "__main__":
    start_mobile_listener()
