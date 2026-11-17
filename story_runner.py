"""
Cinematic Story-to-Shorts Pipeline Runner (Autonomous AI Video Engine).
Supports:
1. Lightning Native Engine (Default on workstation: 20s hardware render, 0% CPU strain)
2. Remotion Chromium Engine (For Cloud / GitHub Actions / Cloud Run with 16GB RAM)
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
VIDEO_APP_DIR = BASE_DIR / "video-app"
PUBLIC_AUDIO_DIR = VIDEO_APP_DIR / "public" / "audio"
PUBLIC_IMAGES_DIR = VIDEO_APP_DIR / "public" / "images"
PUBLIC_SFX_DIR = VIDEO_APP_DIR / "public" / "sfx"
DATA_JSON_PATH = VIDEO_APP_DIR / "src" / "storyData.json"
OUTPUT_DIR = VIDEO_APP_DIR / "out"

from story_pipeline.story_extractor import (
    extract_next_story_slice,
    load_history,
    save_history,
)
from story_pipeline.narrative_engine import generate_cinematic_story
from story_pipeline.scene_audio_builder import build_scene_audios_sync
from story_pipeline.sfx_generator import generate_all_sfx
from story_pipeline.image_generator import generate_scene_image
from story_pipeline.fast_video_engine import render_fast_story_video
from story_pipeline.thumbnail_generator import generate_high_ctr_thumbnail
from audio_generator import generate_music_for_genre
from main import upload_to_youtube, upload_to_instagram

RENDER_ENGINE = os.getenv("RENDER_ENGINE", "fast")  # 'fast' (native ~20s) or 'remotion' (Chromium)
MAX_RENDER_RETRIES = 2
RENDER_TIMEOUT_SECONDS = 600


def render_with_remotion(cmd: list, cwd: str, out_file: Path) -> bool:
    """Executes Remotion video render with breakout logic."""
    for attempt in range(1, MAX_RENDER_RETRIES + 1):
        print(f"\n🎬 [Attempt {attempt}/{MAX_RENDER_RETRIES}] Rendering Remotion composition...")
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                timeout=RENDER_TIMEOUT_SECONDS,
                check=False,
            )

            if result.returncode == 0 and out_file.exists() and out_file.stat().st_size > 100_000:
                print(f"✅ Render succeeded on attempt {attempt}!")
                return True
            else:
                print(f"⚠️ Render failed with exit code: {result.returncode}")

        except subprocess.TimeoutExpired:
            print(f"⏱️ TIMEOUT: Rendering exceeded {RENDER_TIMEOUT_SECONDS}s.")
            if out_file.exists():
                out_file.unlink(missing_ok=True)
        except Exception as e:
            print(f"⚠️ Unexpected render exception: {e}")

        if attempt < MAX_RENDER_RETRIES:
            time.sleep(5)

    return False


def process_next_story() -> dict:
    print("\n=======================================================")
    print(" 📖 Starting 8-Hour Story-to-Shorts Production Pipeline ")
    print("=======================================================")

    # Step 1: Ingest next chapter
    story_slice = extract_next_story_slice()
    if not story_slice:
        print("⚠️ No new story chapters found in 'books/'. Waiting for next upload.")
        return {"status": "NO_NEW_STORIES"}

    chapter_title = story_slice.get("chapter_title") or story_slice.get("episode_title") or "Episode"
    chapter_id = story_slice.get("chapter_id") or story_slice.get("episode_id") or f"{story_slice['book_name']}::{chapter_title}"
    book_name = story_slice["book_name"]
    ep_num = story_slice["episode_number"]
    raw_scenes = story_slice.get("scenes_raw", [])

    print(f"📖 Selected Chapter: {chapter_title} from {book_name}")

    # Step 2: Write gripping narrative script (5 high-retention cinematic beats)
    print("\n🎭 Crafting multi-speaker cinematic storytelling script...")
    clean_book_name = (
        book_name.replace(".epub", "")
        .replace(".pdf", "")
        .replace(".txt", "")
        .replace("Various_", "")
        .replace("_", " ")
    )
    script_data = generate_cinematic_story(clean_book_name, chapter_title, raw_scenes, ep_num)
    genre = script_data.get("genre", "Children Adventure / Energetic")

    # Step 3: Verify or Generate SFX Foley Suite
    if not (PUBLIC_SFX_DIR / "whoosh.wav").exists():
        print("🔊 Synthesizing Foley SFX Suite...")
        generate_all_sfx()

    # Step 4: Verify Artwork or Fallback to AI Image Generator
    PUBLIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    for scene in script_data["scenes"]:
        img_url = scene.get("image_url")
        if not img_url or not (VIDEO_APP_DIR / "public" / img_url).exists():
            s_num = scene["scene_number"]
            gen_img_file = PUBLIC_IMAGES_DIR / f"ai_gen_scene_{s_num}.jpg"
            if not gen_img_file.exists():
                print(f"🎨 Generating AI illustration for Scene #{s_num}: '{scene['title']}'...")
                generate_scene_image(scene["narration"], gen_img_file)
            scene["image_url"] = f"images/{gen_img_file.name}"

    # Step 5: Multi-Speaker Voiceover & Word-by-Word Karaoke Sync
    PUBLIC_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    print("\n🎙️ Generating multi-speaker voiceovers and word karaoke synchronization...")
    try:
        script_data["scenes"] = build_scene_audios_sync(script_data["scenes"])
    except Exception as e:
        print(f"⚠️ Voiceover generation failed: {e}. Breaking out cleanly.")
        return {"status": "VOICEOVER_FAILED", "error": str(e)}

    # Step 6: Generate genre-tailored background music (60s)
    bg_music_path = PUBLIC_AUDIO_DIR / "story_bg.wav"
    print(f"\n🎵 Generating background music for genre '{genre}'...")
    generate_music_for_genre(genre, bg_music_path, duration=60.0)

    # Step 7: Save composition data
    with open(DATA_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2)
    print(f"💾 Updated story composition data in: {DATA_JSON_PATH}")

    # Step 8: Render 60-Second Video (Fast Native Engine or Remotion)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_mp4 = OUTPUT_DIR / f"story_episode_{ep_num}.mp4"

    render_success = False
    if RENDER_ENGINE == "fast":
        try:
            render_fast_story_video(script_data, out_mp4)
            render_success = out_mp4.exists() and out_mp4.stat().st_size > 100_000
        except Exception as e:
            print(f"⚠️ Lightning render encountered issue ({e}). Falling back to Remotion...")

    if not render_success:
        print(f"\n🎬 Rendering via Remotion composition (Timeout: {RENDER_TIMEOUT_SECONDS}s)...")
        cmd = [
            "npx",
            "remotion",
            "render",
            "src/index.ts",
            "StoryVideo",
            str(out_mp4),
        ]
        render_success = render_with_remotion(cmd, str(VIDEO_APP_DIR), out_mp4)

    if not render_success:
        print("❌ Video rendering failed. Breaking out.")
        return {"status": "RENDER_FAILED"}

    print(f"\n✅ Video successfully exported to: {out_mp4}")

    # Step 9: Automatic High-CTR Thumbnail Generation
    print("\n📸 Generating High-CTR Thumbnail...")
    thumb_path = generate_high_ctr_thumbnail(ep_num, script_data.get("hook_headline", "WATCH NOW!"), video_path=out_mp4)

    # Step 10: Automated Uploads
    yt_title = f"{clean_book_name}: {chapter_title} (Ep {ep_num}) #shorts"
    full_text = " ".join([s["narration"] for s in script_data["scenes"]])
    yt_desc = f"Listen to Episode {ep_num} of {clean_book_name}! Subscribe for new episodes every 8 hours.\n\n{full_text}"
    yt_tags = ["story", "audiobook", "shorts", "kids", "animation", "lion", "viral"]

    ig_caption = f"✨ Episode {ep_num}: {chapter_title}\n\n{script_data['hook_headline']}\n\nNew episode drops every 8 hours! Follow for more. 📖🦁 #storytime #audiobook #reels #animation #kids"

    print("\n📤 Publishing to social platforms...")
    yt_res = upload_to_youtube(str(out_mp4), yt_title, yt_desc, yt_tags)
    print(f"YouTube: {yt_res}")

    ig_res = upload_to_instagram(str(out_mp4), ig_caption)
    print(f"Instagram: {ig_res}")

    # Step 11: Update history
    history = load_history()
    processed_list = history.get("processed_chapters", [])
    processed_list.append(chapter_id)
    history["processed_chapters"] = processed_list
    history["episode_count"] = ep_num
    history["last_book"] = book_name
    save_history(history)

    print(f"\n🎉 Episode #{ep_num} production & publishing completed!")
    return {
        "status": "SUCCESS",
        "episode": ep_num,
        "video_path": str(out_mp4),
        "thumbnail_path": str(thumb_path),
        "chapter": chapter_title,
    }


if __name__ == "__main__":
    process_next_story()
