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

    if not TOKEN_PATH.exists():
        print(f"❌ Missing OAuth token file at: {TOKEN_PATH}")
        print("Run 'generate_tokens.py' to generate your YouTube OAuth session.")
        return

    try:
        credentials = Credentials.from_authorized_user_file(str(TOKEN_PATH))
        youtube = build("youtube", "v3", credentials=credentials)

        # 1. Fetch Authenticated Channel Details
        ch_res = youtube.channels().list(part="snippet,statistics", mine=True).execute()
        items = ch_res.get("items", [])
        if not items:
            print("⚠️ No channel associated with this OAuth account.")
            return

        ch = items[0]
        snippet = ch.get("snippet", {})
        stats = ch.get("statistics", {})

        print(f"\n📺 Channel Name:   {snippet.get('title')}")
        print(f"🆔 Channel ID:     {ch.get('id')}")
        print(f"🔗 Custom URL:     https://youtube.com/{snippet.get('customUrl', '')}")
        print(f"👥 Subscribers:    {stats.get('subscriberCount', '0')}")
        print(f"👁️ Total Views:    {stats.get('viewCount', '0')}")
        print(f"🎬 Total Videos:   {stats.get('videoCount', '0')}")

        # 2. Fetch Recent Uploads
        print("\n--------------------------------------------------")
        print(" 📋 Recent 5 Uploads & Privacy Status")
        print("--------------------------------------------------")

        search_res = youtube.search().list(
            forMine=True,
            type="video",
            order="date",
            maxResults=5,
            part="id,snippet",
        ).execute()

        video_ids = [it["id"]["videoId"] for it in search_res.get("items", []) if "videoId" in it.get("id", {})]

        if not video_ids:
            print("No uploaded videos found yet.")
            return

        v_res = youtube.videos().list(id=",".join(video_ids), part="snippet,status").execute()
        for v in v_res.get("items", []):
            v_id = v["id"]
            v_title = v["snippet"]["title"]
            v_status = v["status"]["privacyStatus"]
            is_synthetic = v["status"].get("containsSyntheticMedia", False)

            status_icon = "🟢" if v_status == "public" else ("🟡" if v_status == "unlisted" else "🔒")
            print(f"\n{status_icon} [{v_status.upper()}] {v_title[:60]}")
            print(f"   • Video ID:    {v_id}")
            print(f"   • Short URL:   https://www.youtube.com/shorts/{v_id}")
            print(f"   • Studio Edit: https://studio.youtube.com/video/{v_id}/edit")
            print(f"   • Synthetic:   {is_synthetic}")

            if v_status == "private":
                print(f"   ⚠️ ACTION REQUIRED: Video is currently locked in private mode.")
                print(f"      Open Studio Edit link to publish publicly, or submit Google's YouTube API compliance form.")

        print("\n==================================================")
        print(" ✅ Channel diagnostic complete.")
        print("==================================================")

    except Exception as e:
        print(f"❌ Error during YouTube diagnostic: {e}")


if __name__ == "__main__":
    check_channel_status()
