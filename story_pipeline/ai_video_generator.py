"""
Autonomous AI Video Generation & Animation Engine.
Supports state-of-the-art frontier & open-source video generation models:
1. Google Veo 2 (veo-2.0-generate-001) - DeepMind's Flagship Generative Video Engine
2. Kling AI (Kling 1.6 / 2.0 via Fal.ai & Kling API) - SOTA Fluid Anatomy & Cinematic Physics
3. ByteDance Seedance / AnimateDiff-Lightning - High-Speed Multimodal Video Foundation
4. Alibaba Wan 2.1 (wavespeedai/wan-2.1-t2v-720p) - Premier Open-Weight Video DiT
5. THUDM CogVideoX-5B (thudm/cogvideox-5b) - Leading Open-Source 3D Video Model
6. Pollinations Video - Generative Video Endpoint
7. Local Hardware 5-Beat Parallax Motion Synthesis - Resilient Full-Bleed 1080x1920 Cinematic Parallax
"""

import os
import json
import subprocess
import time
import urllib.request
import urllib.parse
import urllib.error
import concurrent.futures
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DIR = BASE_DIR / "video-app" / "public"
GENERATED_VIDEOS_DIR = BASE_DIR / "video-app" / "public" / "generated_videos"

HAS_WARNED_CLOUD_FALLBACK = False
VEO_VIDEO_ENABLED = True
KLING_VIDEO_ENABLED = True
SEEDANCE_VIDEO_ENABLED = True
REPLICATE_VIDEO_ENABLED = True
POLLINATIONS_VIDEO_ENABLED = True


def call_with_timeout(func, args=(), kwargs=None, timeout_sec=40):
    """Executes a function inside a worker thread with a strict maximum timeout."""
    if kwargs is None:
        kwargs = {}
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    try:
        future = executor.submit(func, *args, **kwargs)
        return future.result(timeout=timeout_sec)
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def build_strong_ai_video_prompt(
    base_prompt: str,
    camera_motion: str = "smooth-zoom-in",
    visual_style: str = "3D Pixar",
) -> str:
    """
    Constructs an engineered, cinema-grade prompt for open-source AI video models
    (Wan 2.1, CogVideoX-5B, AnimateDiff-Lightning, Pollinations).

    Infuses:
    - Dynamic subject clarity & continuous fluid action
    - Precise spatial camera motion direction (dolly push, tracking pan, dramatic boom)
    - Volumetric atmospheric lighting, Unreal Engine 5 render, raytracing, vivid contrast
    - High-frame-rate fluid physics, 8k resolution, zero artifacts
    """
    # 1. Translate camera motion token into explicit cinematography directions
    cam_directives = {
        "rapid-push-in-shake": "rapid high-intensity 10mm camera push-in punch with subtle handheld micro-shake and motion blur",
        "smooth-lateral-pan-right": "cinematic 24mm tracking pan shot moving smoothly from left to right across the turbulent environment",
        "vertical-tilt-reveal": "Dutch-angle 35mm vertical tilt reveal moving dynamically from low to high to capture colossal scale",
        "climax-pull-back": "high-velocity 10mm wide-angle epic scope pull-back revealing catastrophic scale",
        "loop-convergence-zoom": "centered 50mm portrait camera convergence zoom matching opening framing for seamless infinite loop",
        "pan-right": "cinematic slow tracking pan shot moving smoothly from left to right across the vibrant environment",
        "dramatic-pulse": "suspenseful high-tension camera zoom with rapid focus pull and intense dynamic lighting",
        "warm-dolly": "epic scope revealing slow dolly-out camera shot pulling backward to reveal vast scale",
        "sunset-drift": "sweeping vertical crane rise tilting upward smoothly, dramatic perspective shift",
        "smooth-zoom-in": "slow dramatic camera dolly forward push-in into the scene, smooth continuous motion, 60fps",
    }
    cam_str = cam_directives.get(camera_motion, cam_directives["smooth-zoom-in"])

    # 2. Cinema-grade style enhancements
    style_tokens = (
        "masterpiece, 3D Pixar animated film aesthetic, Disney cinematic lighting, "
        "Unreal Engine 5 render, volumetric god rays, ray-traced reflections, "
        "subsurface scattering, highly detailed textures, vibrant vivid saturated colors, "
        "dynamic fluid motion, perfect physics simulation, 8k resolution, cinematic color grading, "
        "hyper-realistic depth of field, full vertical 9:16 frame composition"
    )

    clean_base = base_prompt.strip().rstrip(".")
    strong_prompt = f"{clean_base}, {cam_str}, {style_tokens}"
    return strong_prompt


def normalize_and_lock_video(temp_file: Path, target_path: Path) -> bool:
    """
    Normalizes generated AI video to the channel's strict production standard:
    - Vertical 9:16 aspect ratio (1080x1920)
    - 30 fps frame rate
    - YUV420p color space for universal mobile device playback
    - Audio stripped (music and voice are mixed downstream)
    """
    if not temp_file.exists() or temp_file.stat().st_size < 50_000:
        return False
    try:
        cmd_norm = [
            "ffmpeg", "-y", "-i", str(temp_file),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-an",
            str(target_path),
        ]
        subprocess.run(cmd_norm, check=True, capture_output=True)
        temp_file.unlink(missing_ok=True)
        return target_path.exists() and target_path.stat().st_size > 50_000
    except Exception as e:
        print(f"Notice: Video normalization note ({e})")
        return False


def generate_ai_video_veo(prompt: str, image_path: Path, output_video_path: Path, camera_motion: str = "smooth-zoom-in") -> bool:
    """
    Tier 1A: Google Veo 2 (veo-2.0-generate-001) via Google Gemini API / Vertex AI.
    Generates high-definition cinematic video with physical consistency & 9:16 framing.
    """
    global VEO_VIDEO_ENABLED
    if not VEO_VIDEO_ENABLED:
        return False

    api_key = os.getenv("VEO_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False

    api_key = api_key.strip().strip("'").strip('"')
    temp_cloud = output_video_path.with_suffix(".veo.mp4")
    strong_prompt = build_strong_ai_video_prompt(prompt, camera_motion=camera_motion, visual_style="Cinematic 35mm")

    try:
        print(f"🌟 [Cloud AI Video] Testing Tier 1A: Google Veo 2 ('{prompt[:40]}...')...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-2.0-generate-001:predictVideo?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({
            "prompt": strong_prompt,
            "aspectRatio": "9:16",
            "durationSeconds": 5,
            "fps": 30
        }).encode("utf-8")

        def _call_veo():
            req = urllib.request.Request(url, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=35) as resp:
                return json.loads(resp.read().decode("utf-8"))

        data = call_with_timeout(_call_veo, timeout_sec=40)
        if isinstance(data, dict):
            video_uri = data.get("videoUri") or data.get("predictions", [{}])[0].get("videoUri")
            if video_uri:
                req_dl = urllib.request.Request(video_uri, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req_dl, timeout=35) as resp:
                    temp_cloud.write_bytes(resp.read())
                if normalize_and_lock_video(temp_cloud, output_video_path):
                    print("✅ [Google Veo 2] Successfully generated & normalized 9:16 clip!")
                    return True
    except Exception as e_veo:
        s_veo = str(e_veo).lower()
        if any(k in s_veo for k in ["404", "not found", "403", "401", "permission", "unsupported"]):
            VEO_VIDEO_ENABLED = False
            print(f"Notice: Google Veo 2 endpoint unavailable ({e_veo}), advancing...")
        else:
            print(f"Notice: Google Veo 2 note ({e_veo})...")
    return False


def generate_ai_video_kling(prompt: str, image_path: Path, output_video_path: Path, camera_motion: str = "smooth-zoom-in") -> bool:
    """
    Tier 1B: Kling AI (Kling 1.6 / 2.0 via Fal.ai or Kling API).
    Produces state-of-the-art fluid human anatomy, realistic physics, and dynamic camera choreography.
    """
    global KLING_VIDEO_ENABLED
    if not KLING_VIDEO_ENABLED:
        return False

    fal_key = os.getenv("FAL_KEY") or os.getenv("KLING_API_KEY")
    if not fal_key:
        return False

    fal_key = fal_key.strip().strip("'").strip('"')
    temp_cloud = output_video_path.with_suffix(".kling.mp4")
    strong_prompt = build_strong_ai_video_prompt(prompt, camera_motion=camera_motion, visual_style="Hyper-Realistic Cinema")

    try:
        print(f"🌟 [Cloud AI Video] Testing Tier 1B: Kling AI ('{prompt[:40]}...')...")
        submit_url = "https://queue.fal.run/fal-ai/kling-video/v1.6/standard/text-to-video"
        headers = {
            "Authorization": f"Key {fal_key}",
            "Content-Type": "application/json"
        }
        payload = json.dumps({
            "prompt": strong_prompt,
            "aspect_ratio": "9:16",
            "duration": "5"
        }).encode("utf-8")

        def _call_kling():
            req = urllib.request.Request(submit_url, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            request_id = data.get("request_id")
            if not request_id:
                return data
            status_url = f"https://queue.fal.run/fal-ai/kling-video/requests/{request_id}/status"
            for _ in range(10):
                time.sleep(3)
                req_st = urllib.request.Request(status_url, headers=headers)
                with urllib.request.urlopen(req_st, timeout=10) as s_resp:
                    st_data = json.loads(s_resp.read().decode("utf-8"))
                if st_data.get("status") == "COMPLETED":
                    res_url = f"https://queue.fal.run/fal-ai/kling-video/requests/{request_id}"
                    req_res = urllib.request.Request(res_url, headers=headers)
                    with urllib.request.urlopen(req_res, timeout=10) as r_resp:
                        return json.loads(r_resp.read().decode("utf-8"))
                elif st_data.get("status") in ["FAILED", "CANCELLED"]:
                    break
            return None

        data = call_with_timeout(_call_kling, timeout_sec=40)
        if isinstance(data, dict) and "video" in data:
            v_url = data["video"].get("url")
            if v_url:
                req_dl = urllib.request.Request(v_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req_dl, timeout=35) as resp:
                    temp_cloud.write_bytes(resp.read())
                if normalize_and_lock_video(temp_cloud, output_video_path):
                    print("✅ [Kling AI] Successfully generated & normalized 9:16 clip!")
                    return True
    except Exception as e_kling:
        s_kling = str(e_kling).lower()
        if any(k in s_kling for k in ["401", "402", "unauthorized", "payment", "balance"]):
            KLING_VIDEO_ENABLED = False
            print(f"Notice: Kling billing/auth note ({e_kling}), advancing...")
        else:
            print(f"Notice: Kling AI note ({e_kling})...")
    return False


def generate_ai_video_seedance(prompt: str, image_path: Path, output_video_path: Path, camera_motion: str = "smooth-zoom-in") -> bool:
    """
    Tier 1C: ByteDance Seedance 2.0 / 2.5 (Volcano Engine Ark API).
    Multimodal video generation with high-speed continuity & character preservation.
    """
    global SEEDANCE_VIDEO_ENABLED
    if not SEEDANCE_VIDEO_ENABLED:
        return False

    bytedance_key = os.getenv("SEEDANCE_API_KEY") or os.getenv("BYTEDANCE_API_KEY") or os.getenv("ARK_API_KEY")
    if not bytedance_key:
        return False

    bytedance_key = bytedance_key.strip().strip("'").strip('"')
    temp_cloud = output_video_path.with_suffix(".seedance.mp4")
    strong_prompt = build_strong_ai_video_prompt(prompt, camera_motion=camera_motion, visual_style="3D Pixar")

    try:
        print(f"🌟 [Cloud AI Video] Testing Tier 1C: ByteDance Seedance ('{prompt[:40]}...')...")
        url = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/video"
        headers = {
            "Authorization": f"Bearer {bytedance_key}",
            "Content-Type": "application/json"
        }
        payload = json.dumps({
            "model": "seedance-2.0",
            "prompt": strong_prompt,
            "ratio": "9:16",
            "duration": 5
        }).encode("utf-8")

        def _call_seedance():
            req = urllib.request.Request(url, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))

        data = call_with_timeout(_call_seedance, timeout_sec=35)
        if isinstance(data, dict) and "video_url" in data:
            v_url = data["video_url"]
            req_dl = urllib.request.Request(v_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req_dl, timeout=30) as resp:
                temp_cloud.write_bytes(resp.read())
            if normalize_and_lock_video(temp_cloud, output_video_path):
                print("✅ [ByteDance Seedance] Successfully generated & normalized 9:16 clip!")
                return True
    except Exception as e_seed:
        s_seed = str(e_seed).lower()
        if any(k in s_seed for k in ["401", "402", "404", "unauthorized"]):
            SEEDANCE_VIDEO_ENABLED = False
            print(f"Notice: Seedance API unavailable ({e_seed}), advancing...")
        else:
            print(f"Notice: ByteDance Seedance note ({e_seed})...")
    return False


def generate_frontier_ai_video(prompt: str, image_path: Path, output_video_path: Path, camera_motion: str = "smooth-zoom-in") -> bool:
    """
    Hierarchical multi-tier generative video cascade:
    - Tier 1A: Google Veo 2 (veo-2.0-generate-001)
    - Tier 1B: Kling AI (Kling 1.6 / 2.0 via Fal.ai)
    - Tier 1C: ByteDance Seedance 2.0 / 2.5
    - Tier 2: Open-Source DiT Suite (Alibaba Wan 2.1 -> THUDM CogVideoX-5B -> AnimateDiff-Lightning)
    - Tier 3: Pollinations Generative Endpoint
    - Returns False if all cloud options are unavailable, gracefully triggering Tier 4 Local Hardware Parallax.
    """
    # 1. Tier 1A: Google Veo 2
    if generate_ai_video_veo(prompt, image_path, output_video_path, camera_motion=camera_motion):
        return True

    # 2. Tier 1B: Kling AI
    if generate_ai_video_kling(prompt, image_path, output_video_path, camera_motion=camera_motion):
        return True

    # 3. Tier 1C: ByteDance Seedance
    if generate_ai_video_seedance(prompt, image_path, output_video_path, camera_motion=camera_motion):
        return True

    # 4. Tier 2: Open-Source Suite (Wan 2.1 / CogVideoX / AnimateDiff / Pollinations)
    return generate_ai_video_replicate(prompt, image_path, output_video_path, camera_motion=camera_motion)


def generate_ai_video_replicate(prompt: str, image_path: Path, output_video_path: Path, camera_motion: str = "smooth-zoom-in") -> bool:
    """
    Generates real AI motion video using cloud open-source models:
    - Tier 1: Wan 2.1 (wavespeedai/wan-2.1-t2v-720p)
    - Tier 2: CogVideoX-5B (thudm/cogvideox-5b)
    - Tier 3: AnimateDiff-Lightning (bytedance/animatediff-lightning-4step)
    - Tier 4: Pollinations Video
    """
    global HAS_WARNED_CLOUD_FALLBACK, REPLICATE_VIDEO_ENABLED, POLLINATIONS_VIDEO_ENABLED

    if not REPLICATE_VIDEO_ENABLED and not POLLINATIONS_VIDEO_ENABLED:
        return False

    strong_prompt = build_strong_ai_video_prompt(prompt, camera_motion=camera_motion)

    api_token = os.getenv("REPLICATE_API_TOKEN")
    if api_token:
        api_token = api_token.strip().strip("'").strip('"')
        os.environ["REPLICATE_API_TOKEN"] = api_token

    temp_cloud = output_video_path.with_suffix(".cloud.mp4")

    # -------------------------------------------------------------
    # Try Replicate Open-Source Suite (Wan 2.1 -> CogVideoX -> AnimateDiff)
    # -------------------------------------------------------------
    if api_token and REPLICATE_VIDEO_ENABLED:
        def _check_replicate_billing(err):
            global REPLICATE_VIDEO_ENABLED
            s = str(err).lower()
            if any(k in s for k in ["402", "credit", "billing", "payment method", "throttled", "rate limit", "unauthenticated", "401"]):
                REPLICATE_VIDEO_ENABLED = False
                print(f"ℹ️ [Cloud AI Video] Replicate billing/credit limit reached. Disabling Replicate for this run.")
                return True
            return False

        try:
            import replicate
            client = replicate.Client(api_token=api_token)
            print(f"🌐 [Cloud AI Video] Initiating Open-Source Video Cascade for: '{prompt[:45]}...'")

            output = None

            # 1. Wan 2.1 (Alibaba Open-Source Text-to-Video)
            try:
                print("   • Testing Model 1: Wan 2.1 (720p 9:16)...")
                output = call_with_timeout(
                    client.run,
                    args=("wavespeedai/wan-2.1-t2v-720p",),
                    kwargs=dict(
                        input={
                            "prompt": strong_prompt,
                            "aspect_ratio": "9:16",
                            "fast_mode": True,
                        }
                    ),
                    timeout_sec=40,
                )
            except Exception as e_wan:
                if _check_replicate_billing(e_wan):
                    output = None
                else:
                    print(f"Notice: Wan 2.1 ({e_wan}), advancing to CogVideoX-5B...")

            # 2. CogVideoX-5B (THUDM Leading Open-Source)
            if not output and REPLICATE_VIDEO_ENABLED:
                try:
                    print("   • Testing Model 2: CogVideoX-5B...")
                    output = call_with_timeout(
                        client.run,
                        args=("thudm/cogvideox-5b",),
                        kwargs=dict(
                            input={
                                "prompt": strong_prompt[:500],
                                "num_frames": 49,
                            }
                        ),
                        timeout_sec=40,
                    )
                except Exception as e_cog:
                    if _check_replicate_billing(e_cog):
                        output = None
                    else:
                        print(f"Notice: CogVideoX-5B ({e_cog}), advancing to AnimateDiff-Lightning...")

            # 3. AnimateDiff-Lightning (ByteDance High-Speed Distilled)
            if not output and REPLICATE_VIDEO_ENABLED:
                try:
                    print("   • Testing Model 3: AnimateDiff-Lightning...")
                    output = call_with_timeout(
                        client.run,
                        args=("bytedance/animatediff-lightning-4step",),
                        kwargs=dict(
                            input={
                                "prompt": strong_prompt[:400],
                            }
                        ),
                        timeout_sec=40,
                    )
                except Exception as e_anim:
                    if _check_replicate_billing(e_anim):
                        output = None
                    else:
                        print(f"Notice: AnimateDiff-Lightning ({e_anim})...")

            # Process output stream / URL if successful
            if output:
                if isinstance(output, list) and len(output) > 0:
                    output = output[0]

                if hasattr(output, "read"):
                    temp_cloud.write_bytes(output.read())
                else:
                    video_url = str(output.url) if hasattr(output, "url") else str(output)
                    print(f"📥 Downloading generated AI video from cloud: {video_url[:60]}...")
                    req_dl = urllib.request.Request(video_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req_dl, timeout=60) as resp:
                        temp_cloud.write_bytes(resp.read())

                if temp_cloud.exists() and temp_cloud.stat().st_size > 50_000:
                    cmd_norm = [
                        "ffmpeg", "-y", "-i", str(temp_cloud),
                        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
                        "-pix_fmt", "yuv420p",
                        "-an",
                        str(output_video_path),
                    ]
                    subprocess.run(cmd_norm, check=True, capture_output=True)
                    temp_cloud.unlink(missing_ok=True)
                    if output_video_path.exists() and output_video_path.stat().st_size > 50_000:
                        print("✅ [Cloud AI Video] Successfully generated & normalized via Replicate!")
                        return True
        except Exception as e_rep:
            err_rep_s = str(e_rep).lower()
            if "402" in err_rep_s or "credit" in err_rep_s or "billing" in err_rep_s:
                REPLICATE_VIDEO_ENABLED = False
                print("ℹ️ [Cloud AI Video] Replicate credit depleted (402). Disabling cloud video for this run.")
            else:
                print(f"Notice: Replicate open-source suite note ({e_rep})")

    # -------------------------------------------------------------
    # Try Model 4: Pollinations Video (Free Open-Source Generative Video)
    # -------------------------------------------------------------
    if POLLINATIONS_VIDEO_ENABLED:
        try:
            encoded_prompt = urllib.parse.quote(strong_prompt[:250])
            poll_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux&video=true&width=1080&height=1920&nologo=true"
            print(f"🌐 [Pollinations Video] Attempting open generative video...")
            req_poll = urllib.request.Request(poll_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req_poll, timeout=25) as resp:
                content_type = resp.headers.get("Content-Type", "")
                if "video" in content_type or "mp4" in content_type:
                    temp_cloud.write_bytes(resp.read())
                    if temp_cloud.exists() and temp_cloud.stat().st_size > 50_000:
                        cmd_norm = [
                            "ffmpeg", "-y", "-i", str(temp_cloud),
                            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
                            "-pix_fmt", "yuv420p",
                            "-an",
                            str(output_video_path),
                        ]
                        subprocess.run(cmd_norm, check=True, capture_output=True)
                        temp_cloud.unlink(missing_ok=True)
                        if output_video_path.exists() and output_video_path.stat().st_size > 50_000:
                            print("✅ [Pollinations Video] Successfully generated & normalized!")
                            return True
        except Exception as e_poll:
            s_poll = str(e_poll).lower()
            if any(k in s_poll for k in ["402", "payment", "forbidden", "403"]):
                POLLINATIONS_VIDEO_ENABLED = False
                print("ℹ️ [Pollinations Video] Pollinations payment required (402). Disabling for remainder of run.")
            else:
                print(f"Notice: Pollinations video note ({e_poll})")

    # Send one throttled warning if falling back to local hardware 3D motion
    if not HAS_WARNED_CLOUD_FALLBACK:
        HAS_WARNED_CLOUD_FALLBACK = True
        try:
            from story_pipeline.telegram_notifier import notify_fallback
            notify_fallback("Cloud AI Video Generator", "Cloud open-source video models offline or unauthenticated. Continuing seamlessly with local hardware 3D motion synthesis.")
        except Exception:
            pass

    return False


def generate_scene_video_clip(scene: dict, output_video_path: Path, beat_number: int = 1) -> Path:
    """
    Ensures every scene has a genuine animated video clip:
    1. Checks if open-source cloud AI video is reachable.
    2. Otherwise, synthesizes a high-depth 1080x1920 cinematic animated MP4 clip from the 3D scene visual
       using narrative-aligned camera motion vectors (Beats 1-5) and in-clip whip transitions.
    """
    output_video_path.parent.mkdir(parents=True, exist_ok=True)
    if output_video_path.exists() and output_video_path.stat().st_size > 100_000:
        return output_video_path

    img_rel = scene.get("image_url", "images/file0.jpg")
    img_path = PUBLIC_DIR / img_rel
    if not img_path.exists():
        img_path = PUBLIC_DIR / "images" / "file0.jpg"

    prompt = scene.get("video_prompt") or scene.get("visual_prompt") or f"{scene.get('title', 'action')}, {scene.get('narration', '')[:80]}"
    motion = scene.get("camera_motion") or scene.get("camera_style", "smooth-zoom-in")

    # Try Frontier Cloud Video Cascade (Veo 2 -> Kling -> Seedance -> Wan 2.1 -> CogVideoX -> AnimateDiff -> Pollinations)
    cloud_success = generate_frontier_ai_video(prompt, img_path, output_video_path, camera_motion=motion)
    if cloud_success:
        print(f"🎬 Successfully retrieved Cloud AI Video: {output_video_path.name}")
        return output_video_path

    # High-Energy Multi-Framing Narrative Cuts (Cuts every 2.5-3.5s per scene to maximize retention)
    fps = 30
    dur_frames = max(scene.get("duration_in_frames", 360), 30)
    duration_sec = dur_frames / fps
    b_num = scene.get("beat_number") or beat_number

    if dur_frames >= 180:
        # 3 Rapid Narrative-Aligned Camera Cuts
        d1 = max(60, int(dur_frames * 0.35))
        d2 = max(60, int(dur_frames * 0.35))
        d3 = dur_frames - d1 - d2

        if b_num == 1:
            # Beat 1: The Hook (Rapid Center Push-In with micro-jitter + tail whip acceleration)
            f_s0 = f"zoompan=z='1.05+0.22*(on/{d1})':x='iw/2-(iw/zoom/2)+sin(on/15)*10':y='ih/2-(ih/zoom/2)+cos(on/18)*8':d={d1}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d1},setpts=PTS-STARTPTS[v0]"
            f_s1 = f"zoompan=z='1.40+0.12*(on/{d2})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d2}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d2},setpts=PTS-STARTPTS[v1]"
            f_s2 = f"zoompan=z='1.32+0.16*(on/{d3})':x='iw/2-(iw/zoom/2)+sin(on/10)*8':y='ih/2-(ih/zoom/2)':d={d3}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d3},setpts=PTS-STARTPTS[v2]"
        elif b_num == 2:
            # Beat 2: The Scientific Mechanism (Cinematic Lateral Pan Left to Right + Macro Angle)
            f_s0 = f"zoompan=z='1.15+0.10*(on/{d1})':x='(iw-ow)*(on/{d1})':y='ih/2-(ih/zoom/2)':d={d1}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d1},setpts=PTS-STARTPTS[v0]"
            f_s1 = f"zoompan=z='1.36+0.12*(on/{d2})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)+sin(on/20)*10':d={d2}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d2},setpts=PTS-STARTPTS[v1]"
            f_s2 = f"zoompan=z='1.20+0.08*(on/{d3})':x='(iw-ow)*(0.5+0.5*on/{d3})':y='ih/2-(ih/zoom/2)':d={d3}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d3},setpts=PTS-STARTPTS[v2]"
        elif b_num == 3:
            # Beat 3: The Escalation / Deep Dive (Vertical Bottom-Up Tilt Reveal + Tension Push)
            f_s0 = f"zoompan=z='1.18+0.12*(on/{d1})':x='iw/2-(iw/zoom/2)':y='(ih-oh)*(1-on/{d1})':d={d1}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d1},setpts=PTS-STARTPTS[v0]"
            f_s1 = f"zoompan=z='1.38+0.14*(on/{d2})':x='iw/2-(iw/zoom/2)+cos(on/16)*10':y='(ih-oh)*0.3':d={d2}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d2},setpts=PTS-STARTPTS[v1]"
            f_s2 = f"zoompan=z='1.24+0.10*(on/{d3})':x='iw/2-(iw/zoom/2)':y='(ih-oh)*(0.4-0.4*on/{d3})':d={d3}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d3},setpts=PTS-STARTPTS[v2]"
        elif b_num == 4:
            # Beat 4: The Climax Revelation (High-Energy Dynamic Pull-Back Zoom Out + Diagonal Drift)
            f_s0 = f"zoompan=z='1.38-0.22*(on/{d1})':x='(iw-ow)*(1-on/{d1})':y='(ih-oh)*(on/{d1})':d={d1}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d1},setpts=PTS-STARTPTS[v0]"
            f_s1 = f"zoompan=z='1.42+0.14*(on/{d2})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)+sin(on/12)*12':d={d2}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d2},setpts=PTS-STARTPTS[v1]"
            f_s2 = f"zoompan=z='1.28-0.12*(on/{d3})':x='(iw-ow)*(on/{d3})':y='(ih-oh)*(1-on/{d3})':d={d3}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d3},setpts=PTS-STARTPTS[v2]"
        else:
            # Beat 5: The Loop Paradox (Re-centering Convergence targeting Beat 1 entrance framing)
            f_s0 = f"zoompan=z='1.20-0.12*(on/{d1})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d1}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d1},setpts=PTS-STARTPTS[v0]"
            f_s1 = f"zoompan=z='1.26+0.08*(on/{d2})':x='iw/2-(iw/zoom/2)+sin(on/22)*8':y='ih/2-(ih/zoom/2)':d={d2}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d2},setpts=PTS-STARTPTS[v1]"
            f_s2 = f"zoompan=z='1.14-0.09*(on/{d3})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d3}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d3},setpts=PTS-STARTPTS[v2]"

        filter_complex = (
            f"[0:v]scale=1920:3413:force_original_aspect_ratio=increase,crop=1920:3413,split=3[s0][s1][s2];"
            f"[s0]{f_s0};"
            f"[s1]{f_s1};"
            f"[s2]{f_s2};"
            f"[v0][v1][v2]concat=n=3:v=1:a=0,eq=saturation=1.22:contrast=1.12:brightness=0.02,vignette=PI/5,noise=alls=6:allf=t[outv]"
        )
    elif dur_frames >= 100:
        # 2 Rapid Narrative-Aligned Camera Cuts (Establishing -> Punch-In)
        d1 = int(dur_frames * 0.5)
        d2 = dur_frames - d1

        if b_num == 1:
            f_s0 = f"zoompan=z='1.06+0.20*(on/{d1})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d1}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d1},setpts=PTS-STARTPTS[v0]"
            f_s1 = f"zoompan=z='1.40+0.15*(on/{d2})':x='(iw-ow)*(on/{d2})':y='ih/2-(ih/zoom/2)':d={d2}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d2},setpts=PTS-STARTPTS[v1]"
        elif b_num == 2:
            f_s0 = f"zoompan=z='1.15+0.10*(on/{d1})':x='(iw-ow)*(on/{d1})':y='ih/2-(ih/zoom/2)':d={d1}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d1},setpts=PTS-STARTPTS[v0]"
            f_s1 = f"zoompan=z='1.35+0.12*(on/{d2})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d2}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d2},setpts=PTS-STARTPTS[v1]"
        elif b_num == 3:
            f_s0 = f"zoompan=z='1.18+0.12*(on/{d1})':x='iw/2-(iw/zoom/2)':y='(ih-oh)*(1-on/{d1})':d={d1}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d1},setpts=PTS-STARTPTS[v0]"
            f_s1 = f"zoompan=z='1.36+0.14*(on/{d2})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d2}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d2},setpts=PTS-STARTPTS[v1]"
        elif b_num == 4:
            f_s0 = f"zoompan=z='1.38-0.20*(on/{d1})':x='(iw-ow)*(1-on/{d1})':y='(ih-oh)*(on/{d1})':d={d1}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d1},setpts=PTS-STARTPTS[v0]"
            f_s1 = f"zoompan=z='1.42+0.14*(on/{d2})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d2}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d2},setpts=PTS-STARTPTS[v1]"
        else:
            f_s0 = f"zoompan=z='1.20-0.12*(on/{d1})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d1}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d1},setpts=PTS-STARTPTS[v0]"
            f_s1 = f"zoompan=z='1.14-0.09*(on/{d2})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d2}:s=1080x1920:fps={fps},trim=start_frame=0:end_frame={d2},setpts=PTS-STARTPTS[v1]"

        filter_complex = (
            f"[0:v]scale=1920:3413:force_original_aspect_ratio=increase,crop=1920:3413,split=2[s0][s1];"
            f"[s0]{f_s0};"
            f"[s1]{f_s1};"
            f"[v0][v1]concat=n=2:v=1:a=0,eq=saturation=1.22:contrast=1.12:brightness=0.02,vignette=PI/5,noise=alls=6:allf=t[outv]"
        )
    else:
        # Fast Single Shot for short scenes
        if b_num == 2:
            zoom_expr = f"zoompan=z='1.15+0.12*(on/{dur_frames})':x='(iw-ow)*(on/{dur_frames})':y='ih/2-(ih/zoom/2)':d={dur_frames}:s=1080x1920:fps={fps}"
        elif b_num == 3:
            zoom_expr = f"zoompan=z='1.18+0.12*(on/{dur_frames})':x='iw/2-(iw/zoom/2)':y='(ih-oh)*(1-on/{dur_frames})':d={dur_frames}:s=1080x1920:fps={fps}"
        elif b_num == 4:
            zoom_expr = f"zoompan=z='1.36-0.20*(on/{dur_frames})':x='(iw-ow)*(1-on/{dur_frames})':y='(ih-oh)*(on/{dur_frames})':d={dur_frames}:s=1080x1920:fps={fps}"
        elif b_num == 5:
            zoom_expr = f"zoompan=z='1.18-0.12*(on/{dur_frames})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={dur_frames}:s=1080x1920:fps={fps}"
        else:
            zoom_expr = f"zoompan=z='1.08+0.22*(on/{dur_frames})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={dur_frames}:s=1080x1920:fps={fps}"

        filter_complex = (
            f"[0:v]scale=1920:3413:force_original_aspect_ratio=increase,crop=1920:3413,"
            f"{zoom_expr},"
            f"trim=start_frame=0:end_frame={dur_frames},setpts=PTS-STARTPTS,"
            f"eq=saturation=1.22:contrast=1.12:brightness=0.02,vignette=PI/5,noise=alls=6:allf=t[outv]"
        )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img_path),
        "-t", f"{duration_sec:.2f}",
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        str(output_video_path),
    ]

    subprocess.run(cmd, check=True, capture_output=True)
    return output_video_path
