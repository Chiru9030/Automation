import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from google.antigravity import Agent, LocalAgentConfig
from google.antigravity.hooks import policy
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from instagrapi import Client

BASE_DIR = Path(__file__).resolve().parent
VIDEO_APP_DIR = BASE_DIR / "video-app"


def upload_to_youtube(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    thumbnail_path: str | None = None,
    privacy_status: str | None = None,
) -> str:
    """Uploads a rendered MP4 video to YouTube and returns the Video ID.

    Args:
        video_path: Absolute or relative path to the MP4 file.
        title: Title of the video.
        description: Description of the video.
        tags: List of keywords/tags for the video.
        thumbnail_path: Optional path to custom high-CTR thumbnail JPG.
        privacy_status: 'private', 'unlisted', or 'public' (defaults to YOUTUBE_PRIVACY_STATUS or 'private').
    """
    token_path = BASE_DIR / "youtube_tokens.json"
    if not token_path.exists():
        return (
            f"[MOCK UPLOAD] YouTube upload skipped: '{token_path}' not found. "
            f"Run 'generate_tokens.py' to generate your OAuth token."
        )

    credentials = Credentials.from_authorized_user_file(str(token_path))
    youtube = build("youtube", "v3", credentials=credentials)

    chosen_privacy = privacy_status or os.getenv("YOUTUBE_PRIVACY_STATUS", "private")

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "28",  # Science & Technology
        },
        "status": {
            "privacyStatus": chosen_privacy,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,  # YouTube 2025/2026 AI disclosure compliance
        },
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)
    response = request.execute()
    video_id = response.get("id")

    # Set custom high-CTR thumbnail if provided
    if video_id and thumbnail_path and Path(thumbnail_path).exists():
        try:
            thumb_media = MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
            youtube.thumbnails().set(videoId=video_id, media_body=thumb_media).execute()
            print(f"📸 Custom High-CTR Thumbnail applied to YouTube Short: {Path(thumbnail_path).name}")
        except Exception as e_thumb:
            print(f"Notice: Custom thumbnail set note ({e_thumb})")

    # Post engagement booster comment
    if video_id:
        try:
            comment_body = {
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": "Would you survive this scenario? Drop your theory in the comments! 👇 Subscribe for daily curiosity drops! 🚀"
                        }
                    }
                }
            }
            youtube.commentThreads().insert(part="snippet", body=comment_body).execute()
            print("💬 Automatically posted engagement comment on YouTube Short!")
        except Exception as e_comm:
            print(f"Notice: Auto-comment note ({e_comm})")

    return f"Successfully uploaded to YouTube! Video ID: {video_id} (Privacy: {chosen_privacy}, SyntheticMedia: True)"


def upload_to_instagram(video_path: str, caption: str) -> str:
    """Uploads a rendered MP4 video to Instagram Reels and returns the Media ID.

    Args:
        video_path: Absolute or relative path to the MP4 file.
        caption: Caption text including viral hashtags.
    """
    session_path = BASE_DIR / "instagram_session.json"
    if not session_path.exists():
        return (
            f"[MOCK UPLOAD] Instagram upload skipped: '{session_path}' not found. "
            f"Run 'generate_tokens.py' to generate your session."
        )

    cl = Client()
    cl.load_settings(str(session_path))
    media = cl.clip_upload(video_path, caption)
    return f"Successfully uploaded to Instagram! Media ID: {media.pk}"


pipeline_prompt = f"""
You are an automated video creation and publishing pipeline.

Execute the following steps:
1. Examine the Remotion project in '{VIDEO_APP_DIR}' and review the composition in 'src/SpaceFacts.tsx'.
2. Use terminal commands inside '{VIDEO_APP_DIR}' to render the video:
   Run: npx remotion render src/index.ts SpaceFacts out/space_facts.mp4
3. Verify that the MP4 output file exists at '{VIDEO_APP_DIR}/out/space_facts.mp4'.
4. Call the 'upload_to_youtube' tool with:
   - video_path: '{VIDEO_APP_DIR}/out/space_facts.mp4'
   - title: '3 Mind-Blowing Facts About Space That Will Shock You! 🌌 #shorts'
   - description: 'Explore 3 cosmic secrets about Venus, the cosmic ocean, and neutron stars. Subscribe for daily universe facts!'
   - tags: ['space', 'universe', 'cosmic', 'astronomy', 'science', 'facts', 'shorts']
5. Call the 'upload_to_instagram' tool with:
   - video_path: '{VIDEO_APP_DIR}/out/space_facts.mp4'
   - caption: '3 Space facts that sound fake but are 100% true! 🤯🚀 Which one surprised you most? #space #astronomy #universe #cosmic #science #reels'
6. Return a summary of the executed steps and upload statuses.
"""


async def main():
    print("==================================================")
    print(" Antigravity Autonomous Video Automation Pipeline ")
    print("==================================================")

    skill_path = str(BASE_DIR / ".agents" / "skills" / "remotion-best-practices")

    # Configure the Antigravity Agent
    config = LocalAgentConfig(
        model="gemini-3.8-flash",
        workspaces=[str(BASE_DIR)],
        skills_paths=[skill_path],
        tools=[
            upload_to_youtube,
            upload_to_instagram,
        ],
        policies=[policy.allow_all()],
    )

    async with Agent(config=config) as agent:
        response = await agent.chat(pipeline_prompt)
        print("\n=== Agent Execution Output ===")
        print(await response.text())


if __name__ == "__main__":
    asyncio.run(main())

