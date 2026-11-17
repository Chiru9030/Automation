"""
Telegram Mobile Notifier for Autonomous Video Pipeline.
Delivers real-time notifications, upload logs, error alerts, and video previews directly to your mobile phone:
1. Success: Formatted status report + direct YouTube link + attached 1080x1920 MP4 preview (with protected content).
2. Fallback: Alerts when an engine switches from cloud to native fallback.
3. Error: Immediate failure alert with stage diagnosis and traceback.
"""

import os
import traceback
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def get_telegram_creds() -> tuple[str | None, str | None]:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if bot_token:
        bot_token = bot_token.strip().strip("'").strip('"')
    if chat_id:
        chat_id = chat_id.strip().strip("'").strip('"')
    return bot_token, chat_id


def send_telegram_message(text: str, parse_mode: str | None = "HTML") -> bool:
    """Sends a text message to your mobile Telegram chat with automatic fallback."""
    bot_token, chat_id = get_telegram_creds()
    if not bot_token or not chat_id:
        print("⚠️ Telegram skipped: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing in environment.")
        return False

    try:
        import requests

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": False,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode

        res = requests.post(url, json=payload, timeout=20)
        if res.status_code == 200:
            print("✅ Telegram notification delivered successfully!")
            return True
        else:
            print(f"⚠️ Telegram API error ({res.status_code}): {res.text}")
            # If HTML parsing failed, retry as plain text
            if parse_mode:
                print("🔄 Retrying Telegram message in plain text format...")
                payload.pop("parse_mode", None)
                # Strip HTML tags simply
                clean_text = text.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "").replace("<code>", "").replace("</code>", "")
                payload["text"] = clean_text
                res2 = requests.post(url, json=payload, timeout=20)
                if res2.status_code == 200:
                    print("✅ Telegram notification delivered (plain text fallback)!")
                    return True
                else:
                    print(f"⚠️ Telegram retry error ({res2.status_code}): {res2.text}")
            return False
    except Exception as e:
        print(f"⚠️ Telegram message dispatch error: {e}")
        return False


def send_telegram_video(
    video_path: Path, caption: str, protect_content: bool = True
) -> bool:
    """Sends the rendered vertical video preview directly to your phone."""
    bot_token, chat_id = get_telegram_creds()
    if not bot_token or not chat_id:
        return False

    if not video_path.exists():
        print(f"⚠️ Video file missing for Telegram send: {video_path}")
        return False

    file_size_mb = video_path.stat().st_size / 1_000_000
    if file_size_mb > 49.0:
        print(f"ℹ️ Video size ({file_size_mb:.1f}MB) exceeds Telegram's 50MB direct bot limit.")
        return False

    try:
        import requests

        url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
        data = {
            "chat_id": chat_id,
            "caption": caption[:1000],
            "supports_streaming": True,
            "protect_content": protect_content,
        }
        with open(video_path, "rb") as vf:
            files = {"video": vf}
            res = requests.post(url, data=data, files=files, timeout=180)
            if res.status_code == 200:
                print("✅ Telegram video preview delivered successfully!")
                return True
            else:
                print(f"⚠️ Telegram video upload error ({res.status_code}): {res.text}")
                return False
    except Exception as e:
        print(f"⚠️ Telegram video dispatch error: {e}")
        return False


def notify_success(
    episode_num: int,
    title: str,
    duration: float,
    size_mb: float,
    youtube_res: str,
    video_path: Path | None = None,
) -> bool:
    """Sends celebratory success card + YouTube link + attached video to mobile."""
    # Extract video ID or link
    yt_link = "N/A"
    if "Video ID:" in youtube_res:
        vid_id = youtube_res.split("Video ID:")[-1].strip()
        yt_link = f"https://youtube.com/shorts/{vid_id}"

    msg = (
        f"🎬 <b>Episode #{episode_num} Published Successfully!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 <b>Topic:</b> {title}\n"
        f"⏱️ <b>Duration:</b> {duration:.2f}s\n"
        f"📦 <b>Size:</b> {size_mb:.1f} MB\n"
        f"✅ <b>Auditor Gate:</b> 5/5 Certified (1080x1920 @ 30fps)\n"
        f"🔊 <b>Voice:</b> Single Narrator (Crazy Bass Boost)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <b>Watch Live:</b> {yt_link}\n"
    )

    # 1. Always deliver the status text report first
    print("📱 Sending mobile status report via Telegram...")
    sent_text = send_telegram_message(msg)

    # 2. Then attempt to deliver the video file preview
    if video_path and video_path.exists():
        print("📱 Sending mobile video preview via Telegram...")
        send_telegram_video(video_path, caption=f"🎬 Ep #{episode_num}: {title}", protect_content=True)

    return sent_text


def notify_fallback(stage_name: str, details: str) -> bool:
    """Sends a warning alert when an engine switches to a safe fallback."""
    msg = (
        f"⚠️ <b>Pipeline Fallback Triggered</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚙️ <b>Stage:</b> {stage_name}\n"
        f"📝 <b>Details:</b> {details}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"ℹ️ <i>Automated fallback completed. Pipeline continuing seamlessly.</i>"
    )
    return send_telegram_message(msg)


def notify_error(stage_name: str, error_msg: str, exc: Exception | None = None) -> bool:
    """Sends an urgent alert when a pipeline step or auditor rejects an output."""
    tb = ""
    if exc:
        tb = f"\n<pre>{traceback.format_exc()[-400:]}</pre>"

    msg = (
        f"🚨 <b>Pipeline Alert: Failure in {stage_name}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"❌ <b>Error:</b> {error_msg}\n"
        f"{tb}"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔄 <i>Check GitHub Actions log for full diagnostic.</i>"
    )
    print(f"📱 Dispatching error alert to mobile via Telegram...")
    return send_telegram_message(msg)
