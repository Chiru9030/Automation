"""
Autonomous Dynamic Story-to-Shorts Pipeline Runner (7-Stage Viral Production Engine).
Runs continuously on a 5-hour schedule or 1-click cloud trigger without manual book uploads:
1. Stage 1: Unique Viral Curiosity Topic Generator ("What If", Paradoxes, Shocking Science).
2. Stage 2: Hook-Driven 59-Second Narrative Script Engine (Retention hooks every 10 seconds).
   -> Auditor Gate 1: Narrative structure, pacing, word count verification.
3. Stage 3: High-Definition 3D Pixar & CGI Image Generator (Imagen 3 / Pollinations Free Tier).
   -> Auditor Gate 2: Resolution & image asset integrity verification.
4. Stage 4 & 5: Multi-Speaker Neural Voiceover & Exact Frame-Accurate Timing Engine.
   -> Auditor Gate 3: Neural audio alignment & strict <59s duration verification.
5. Stage 6: Kinetic Subtitle & Typography Engine (Submagic / Hormozi discrete word highlighting).
   -> Auditor Gate 4: Frame-accurate ASS event verification.
6. Stage 7 & Render: Native Hardware-Accelerated Video Synthesis with multi-track audio mix.
   -> Auditor Gate 5: Deep ffprobe quality certification (1080x1920, <59s, AAC audio).
7. High-CTR Thumbnail Generation & Social Publishing (YouTube Shorts & Instagram Reels).
8. Perpetual History Tracking.
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
PUBLIC_DIR = VIDEO_APP_DIR / "public"
PUBLIC_AUDIO_DIR = PUBLIC_DIR / "audio"
PUBLIC_IMAGES_DIR = PUBLIC_DIR / "images"
PUBLIC_SFX_DIR = PUBLIC_DIR / "sfx"
DATA_JSON_PATH = VIDEO_APP_DIR / "src" / "storyData.json"
OUTPUT_DIR = VIDEO_APP_DIR / "out"

from story_pipeline.story_extractor import (
    extract_next_story_slice,
    load_history,
    save_history,
)
from story_pipeline.viral_topic_engine import generate_unique_viral_topic
from story_pipeline.viral_script_engine import generate_viral_script
from story_pipeline.hd_image_engine import generate_all_beat_images
from story_pipeline.neural_audio_engine import build_audio_and_timings_sync
from story_pipeline.kinetic_subtitle_engine import compile_kinetic_subtitles
from story_pipeline.strict_pipeline_auditor import (
    audit_story_script,
    audit_scientific_factuality,
    audit_visual_assets,
    audit_audio_sync,
    audit_subtitles_file,
    audit_final_rendered_video,
    QualityAuditError,
)
from story_pipeline.sfx_generator import generate_all_sfx
from story_pipeline.fast_video_engine import render_fast_story_video
from story_pipeline.thumbnail_generator import generate_high_ctr_thumbnail
from story_pipeline.telegram_notifier import (
    notify_success,
    notify_error,
    notify_fallback,
    notify_zero_upload_blocked,
    notify_audit_rejection,
    RUN_TRACKER,
)
from story_pipeline.training_pipeline import trigger_failure_training
from audio_generator import generate_music_for_genre
from main import upload_to_youtube, upload_to_instagram

USE_DYNAMIC_TOPICS = os.getenv("USE_DYNAMIC_TOPICS", "true").lower() == "true"
RENDER_ENGINE = os.getenv("RENDER_ENGINE", "fast")
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


PIPELINE_VERSION = "v1.6.0"

def process_next_story(custom_topic: str | None = None, publish: bool = True) -> dict:
    RUN_TRACKER.reset()
    print("\n==================================================================")
    print(f" 🚀 Autonomous 7-Stage Viral Story Video Pipeline ({PIPELINE_VERSION}) Initiated")
    print("==================================================================")

    current_stage = "Stage 1: Dynamic Viral Topic Generator"
    try:
        # -------------------------------------------------------------
        # STAGE 1: Dynamic Viral Topic Generator or Custom User Topic
        # -------------------------------------------------------------
        custom_override = custom_topic or os.getenv("CUSTOM_TOPIC")
        if custom_override and custom_override.strip():
            print(f"\n💡 [Custom User Topic Mode] Generating video for: '{custom_override.strip()}'")
            history = load_history()
            ep_num = history.get("episode_count", 0) + 1
            topic_data = {
                "topic": custom_override.strip(),
                "hook_premise": f"The shocking reality of {custom_override.strip()}",
                "category": "Mind-Blowing Stories & Science",
                "style": "3D Pixar animation Unreal Engine 5",
                "episode": ep_num,
            }
        else:
            print("\n💡 [Stage 1/7] Generating unique viral high-curiosity topic...")
            topic_data = generate_unique_viral_topic()

        ep_num = topic_data.get("episode", 1)
        chapter_title = topic_data.get("topic", f"Episode {ep_num}")
        genre = topic_data.get("category", "Science & Mind-Blowing Facts")
        clean_book_name = chapter_title
        chapter_id = f"dynamic::{chapter_title}::Ep{ep_num}"
        book_name = "Dynamic Viral Curiosity Universe"

        print(f"🎯 Target Concept: '{chapter_title}'")
        print(f"   Category: {genre} | Visual Style: {topic_data.get('style', '3D Pixar')}")

        # -------------------------------------------------------------
        # STAGE 2: 59-Second Hook-Driven Narrative Script Engine & Gate 1 Auditor
        # -------------------------------------------------------------
        current_stage = "Stage 2: 59-Second Narrative Script Engine"
        print("\n✍️ [Stage 2/7] Generating 5-beat retention script with hooks every 10 seconds...")
        script_data = None
        for script_attempt in range(1, 4):
            try:
                script_data = generate_viral_script(topic_data)
                script_data["episode"] = ep_num
                script_data["genre"] = genre
                script_data["title"] = chapter_title
                audit_story_script(script_data)
                audit_scientific_factuality(script_data)
                break
            except QualityAuditError as s_err:
                print(f"⚠️ [Gate 1 Rejection] Script attempt {script_attempt}/3 failed: {s_err}")
                notify_audit_rejection(
                    gate_name="Gate 1: Story Script & Hook",
                    item_name=f"Episode #{ep_num} Script",
                    reason=str(s_err),
                    attempt=script_attempt,
                    max_attempts=3,
                    action="Regenerating script with amplified psychological curiosity hooks...",
                )
                if script_attempt == 3:
                    raise

        # Alias beats to scenes for backwards compatibility
        beats = script_data["beats"]
        for b in beats:
            b["scene_number"] = b["beat_number"]
            b["title"] = b.get("hook_trigger", f"Beat #{b['beat_number']}")
        script_data["scenes"] = beats

        # -------------------------------------------------------------
        # Foley SFX Verification
        # -------------------------------------------------------------
        current_stage = "Foley SFX Engine"
        PUBLIC_SFX_DIR.mkdir(parents=True, exist_ok=True)
        if not (PUBLIC_SFX_DIR / "whoosh.wav").exists():
            print("🔊 Synthesizing Foley SFX Suite...")
            generate_all_sfx()

        # -------------------------------------------------------------
        # STAGE 3: High-Definition 3D Pixar & CGI Image Generator
        # -------------------------------------------------------------
        current_stage = "Stage 3: 3D Pixar Visual Engine"
        print(f"\n🎨 [Stage 3/7] Generating enhanced 3D Pixar visuals for all {len(beats)} beats...")
        PUBLIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        generate_all_beat_images(beats, ep_num)

        # Gate 2: Visual Assets Quality Audit
        current_stage = "Gate 2: Visual Assets Quality Audit"
        audit_visual_assets(beats, PUBLIC_DIR)

        # -------------------------------------------------------------
        # STAGE 4 & 5: Neural Audio & Exact Word Synchronization
        # -------------------------------------------------------------
        current_stage = "Stage 4 & 5: Neural Audio & Exact Word Boundaries"
        print("\n🎙️ [Stage 4 & 5/7] Synthesizing multi-speaker neural voiceovers & word boundaries...")
        PUBLIC_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        beats = build_audio_and_timings_sync(beats)
        script_data["beats"] = beats
        script_data["scenes"] = beats

        # Gate 3: Audio Sync & Duration Quality Audit (<58.5s)
        current_stage = "Gate 3: Audio Sync & Duration Audit"
        audit_audio_sync(beats, PUBLIC_DIR)

        # -------------------------------------------------------------
        # STAGE 6: Kinetic Subtitles & Typography Compilation
        # -------------------------------------------------------------
        current_stage = "Stage 6: Kinetic Subtitles Compilation"
        print("\n✨ [Stage 6/7] Compiling discrete kinetic karaoke subtitles (safe lower-third)...")
        ass_path = OUTPUT_DIR / "fast_render_tmp" / "subtitles.ass"
        compile_kinetic_subtitles(beats, ass_path)
        from story_pipeline.hud_overlay_engine import append_hud_and_progress_to_ass
        append_hud_and_progress_to_ass(ass_path, category=genre, total_duration=58.0)

        # Gate 4: Subtitles Verification Audit
        current_stage = "Gate 4: Subtitles Verification Audit"
        audit_subtitles_file(ass_path)

        # Generate genre-tailored sound design & dynamic 3-act audio arc (58.0s)
        current_stage = "Audio Mixing & BGM Engine"
        print(f"🎵 Generating dynamic sound design & 3-act audio arc for '{genre}' (58.0s)...")
        generate_all_sfx(category=genre)

        # Save complete story data
        with open(DATA_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(script_data, f, indent=2)

        # -------------------------------------------------------------
        # STAGE 7 & RENDER: Native Hardware-Accelerated Video Engine
        # -------------------------------------------------------------
        current_stage = "Stage 6 & Render: Native Video Synthesis"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out_mp4 = OUTPUT_DIR / f"story_episode_{ep_num}.mp4"

        render_success = False
        if RENDER_ENGINE == "fast":
            try:
                render_fast_story_video(script_data, out_mp4)
                render_success = out_mp4.exists() and out_mp4.stat().st_size > 100_000
            except Exception as e:
                print(f"⚠️ Lightning render issue ({e}). Falling back to Remotion...")

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
            raise RuntimeError("Video rendering failed across all engines.")

        # -------------------------------------------------------------
        # Gate 5: Zero-Upload Safety Guard & Comprehensive Multi-Pillar Audit
        # -------------------------------------------------------------
        current_stage = "Gate 5: Zero-Upload Pre-Flight Safety Certification"
        print("\n🛡️ [Zero-Upload Safety Guard] Running comprehensive pre-flight verification...")
        try:
            cert = audit_final_rendered_video(out_mp4, ass_path=ass_path)
        except Exception as audit_err:
            print(f"🛑 [ZERO-UPLOAD SAFETY HALT] Pre-upload verification rejected video: {audit_err}")
            notify_zero_upload_blocked(
                episode_num=ep_num,
                title=chapter_title,
                reason=str(audit_err)
            )
            raise audit_err

        # -------------------------------------------------------------
        # High-CTR Thumbnail Generation
        # -------------------------------------------------------------
        current_stage = "Thumbnail Generation"
        print("\n📸 Generating High-CTR A/B/C Thumbnail Suite...")
        hook_hl = script_data.get("hook_headline", "WHAT HAPPENS NEXT?!")
        from story_pipeline.thumbnail_generator import generate_abc_thumbnail_suite
        thumb_suite = generate_abc_thumbnail_suite(ep_num, hook_hl, category=genre, video_path=out_mp4)
        thumb_path = thumb_suite["variant_a"]

        # -------------------------------------------------------------
        # TikTok & Instagram Swipeable Carousel Generation (Item 19)
        # -------------------------------------------------------------
        try:
            from story_pipeline.carousel_generator import generate_swipeable_carousel
            generate_swipeable_carousel(script_data, ep_num)
        except Exception as e_car:
            print(f"Notice: Carousel generation skipped ({e_car})")

        # -------------------------------------------------------------
        # Automated Long-Form Master Documentary Compilation (Item 16)
        # -------------------------------------------------------------
        if ep_num % 5 == 0:
            print(f"\n🎥 [Milestone Reached: Ep #{ep_num}] Triggering Automated 16:9 Long-Form Compilation...")
            try:
                from story_pipeline.longform_compiler import compile_longform_documentary
                doc_path = compile_longform_documentary(min_episodes=5, custom_title=f"Curiosity Universe Anthology (Episodes {ep_num-4}-{ep_num})")
                if doc_path:
                    print(f"✅ Master 16:9 Documentary compiled: {doc_path.name}")
            except Exception as e_doc:
                print(f"Notice: Longform compilation skipped ({e_doc})")

        # -------------------------------------------------------------
        # Automated Social Media Publishing (Skipped if publish=False)
        # -------------------------------------------------------------
        current_stage = "Stage 7: Multi-Platform Publishing"
        yt_title = f"{chapter_title} (Ep {ep_num}) #shorts"
        full_text = " ".join([b["narration"] for b in beats])

        branch = script_data.get("branching_decision", {})
        branch_text = ""
        if branch:
            branch_text = f"\n\n❓ DECIDE NEXT EPISODE:\n🅰️ {branch.get('choice_a')}\n🅱️ {branch.get('choice_b')}\n{branch.get('vote_callout')}\n"

        yt_desc = f"{chapter_title}\n\nEpisode {ep_num}\n\n{full_text}{branch_text}\n\nSubscribe for new episodes every 5 hours! #shorts #viral #story"
        yt_tags = ["shorts", "viral", "facts", "whatif", "animation", "science", "story"]

        ig_caption = f"🚨 {chapter_title} (Part {ep_num})\n\n{hook_hl}{branch_text}\n\nFollow for more episodes every 5 hours! 🎬✨ #reels #viral #explorepage #animation #whatif"

        if publish:
            print("\n📤 Publishing to social platforms...")
            yt_res = upload_to_youtube(str(out_mp4), yt_title, yt_desc, yt_tags)
            print(f"YouTube: {yt_res}")

            ig_res = upload_to_instagram(str(out_mp4), ig_caption)
            print(f"Instagram: {ig_res}")
        else:
            print("\n🧪 [Sample Mode Active] Video rendered & certified locally. Social publishing skipped.")
            yt_res = "[LOCAL SAMPLE] Video generated locally, upload skipped."
            ig_res = "[LOCAL SAMPLE] Video generated locally, upload skipped."

        # -------------------------------------------------------------
        # Perpetual History Tracking Update
        # -------------------------------------------------------------
        history = load_history()
        processed_list = history.get("processed_chapters", [])
        processed_list.append(chapter_id)
        history["processed_chapters"] = processed_list
        history["episode_count"] = ep_num
        history["last_book"] = book_name
        topics = history.get("generated_topics", [])
        topics.append(chapter_title)
        history["used_topics"] = list(set(history.get("used_topics", []) + [chapter_title]))
        save_history(history)

        # -------------------------------------------------------------
        # Real-Time Mobile Dispatch (Video Preview + Live Link + Logs)
        # -------------------------------------------------------------
        notify_success(
            episode_num=ep_num,
            title=chapter_title,
            duration=cert["duration"],
            size_mb=cert["size_mb"],
            youtube_res=yt_res,
            video_path=out_mp4,
        )

        print("\n==================================================================")
        print(f" 🎉 Episode #{ep_num} 100% Certified & Published!")
        print(f"   • Video: {out_mp4.name} ({cert['duration']:.2f}s, {cert['size_mb']} MB)")
        print(f"   • Thumbnail: {Path(thumb_path).name}")
        print("==================================================================")

        return {
            "status": "SUCCESS",
            "episode": ep_num,
            "video_path": str(out_mp4),
            "thumbnail_path": str(thumb_path),
            "chapter": chapter_title,
            "duration": cert["duration"],
        }
    except Exception as e:
        print(f"\n🚨 [CRITICAL AUDIT HALT] Pipeline rejected at: [{current_stage}]")
        print(f"   Reason: {e}")
        trigger_failure_training(stage_name=current_stage, error=e)
        raise


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous Story Video Pipeline")
    parser.add_argument("--topic", type=str, default="", help="Custom topic or story prompt to render immediately")
    parser.add_argument("--sample", action="store_true", help="Generate sample video locally without publishing")
    parser.add_argument("--no-upload", action="store_true", help="Skip uploading to YouTube/Instagram")
    parser.add_argument("--documentary", action="store_true", help="Compile past episodes into a 16:9 master documentary")
    args = parser.parse_args()

    if args.documentary:
        from story_pipeline.longform_compiler import compile_longform_documentary
        res = compile_longform_documentary(min_episodes=2)
        if res:
            print(f"🎉 16:9 Master Documentary compiled successfully: {res}")
        else:
            print("⚠️ Not enough episodes available to compile documentary.")
        sys.exit(0)

    should_publish = not (
        args.sample
        or args.no_upload
        or os.getenv("SAMPLE_MODE", "false").lower() in ("true", "1", "yes")
    )

    try:
        process_next_story(
            custom_topic=args.topic if args.topic else None,
            publish=should_publish,
        )
    except Exception as e:
        print(f"🚨 Pipeline Fatal Error: {e}")
        notify_error(stage_name="Autonomous Story Pipeline", error_msg=str(e), exc=e)
        sys.exit(1)
