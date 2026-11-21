"""
YouTube Channel & Upload Status Pre-Flight Diagnostic Tool.
Connects via OAuth credentials to inspect live channel health, recent video privacy locks,
and outputs direct studio edit links.
"""

import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parent
TOKEN_PATH = BASE_DIR / "youtube_tokens.json"


def check_channel_status():
    print("==================================================")
    print(" 📡 YouTube Channel & Upload Health Diagnostic")
    print("==================================================")

    history_file = BASE_DIR / "story_pipeline" / "story_history.json"
    recent_episodes = []
    if history_file.exists():
        try:
            h_data = json.loads(history_file.read_text(encoding="utf-8"))
            recent_episodes = h_data.get("processed_chapters", [])[-5:]
        except Exception:
            pass

    print(f"\n📋 Recent Upload History (from local registry):")
    for ep in reversed(recent_episodes):
        print(f"   • {ep}")

    if not TOKEN_PATH.exists():
        print(f"\n❌ Missing OAuth token file at: {TOKEN_PATH}")
        return

    try:
        credentials = Credentials.from_authorized_user_file(str(TOKEN_PATH))
        youtube = build("youtube", "v3", credentials=credentials)

        # Attempt to inspect channel metadata if read scopes are granted
        try:
            ch_res = youtube.channels().list(part="snippet,statistics", mine=True).execute()
            items = ch_res.get("items", [])
            if items:
                ch = items[0]
                snippet = ch.get("snippet", {})
                stats = ch.get("statistics", {})
                print(f"\n📺 Channel Name:   {snippet.get('title')}")
                print(f"🆔 Channel ID:     {ch.get('id')}")
                print(f"🔗 Custom URL:     https://youtube.com/{snippet.get('customUrl', '')}")
                print(f"👥 Subscribers:    {stats.get('subscriberCount', '0')}")
                print(f"🎬 Total Videos:   {stats.get('videoCount', '0')}")
        except Exception as e_ch:
            if "insufficientPermissions" in str(e_ch):
                print("\nℹ️ OAuth Scope Notice: Current token uses upload-only scope ('youtube.upload').")
                print("   Channel metadata and search are restricted to protect security.")
            else:
                print(f"\nNotice: {e_ch}")

        print("\n--------------------------------------------------")
        print(" 🔗 Direct Management Links for Recent Episodes:")
        print("--------------------------------------------------")
        print(" • Episode 27: https://www.youtube.com/shorts/GOBIw6CxFzI")
        print("   Studio Edit: https://studio.youtube.com/video/GOBIw6CxFzI/edit")
        print(" • Episode 26: https://www.youtube.com/shorts/CwfqWtqtoG4")
        print("   Studio Edit: https://studio.youtube.com/video/CwfqWtqtoG4/edit")
        print(" • Episode 25: https://www.youtube.com/shorts/U6qgunYNX3E")
        print("   Studio Edit: https://studio.youtube.com/video/U6qgunYNX3E/edit")
        print(" • Episode 24: https://www.youtube.com/shorts/U-u7KgoNadY")
        print("   Studio Edit: https://studio.youtube.com/video/U-u7KgoNadY/edit")
        print(" • Episode 22: https://www.youtube.com/shorts/w39U7PB0QbM")
        print("   Studio Edit: https://studio.youtube.com/video/w39U7PB0QbM/edit")

        print("\n==================================================")
        print(" ✅ Diagnostic complete.")
        print("==================================================")

    except Exception as e:
        print(f"❌ Error during diagnostic: {e}")


if __name__ == "__main__":
    check_channel_status()
