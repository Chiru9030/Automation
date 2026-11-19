"""
Stage 3: High-Definition AI 3D Visual Generation Engine.
Generates full-bleed 1080x1920 vertical cinematic illustrations for every story beat:
1. Tier 1: Google Imagen 3 (imagen-3.0-generate-002) via GEMINI_API_KEY
2. Tier 2: Hugging Face FLUX.1-schnell Space (via authenticated client with HF_TOKEN)
3. Tier 3: Pollinations AI Clean Free Engine (with resilient retry and streaming)

Zero Procedural Lines Policy:
Every asset must be an authentic, photorealistic or 3D AI generation.
If all models fail, execution is halted by the Zero-Upload Safety Guard.
"""

import json
import math
import os
import random
import time
import urllib.parse
import urllib.request
import concurrent.futures
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageFilter

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_IMAGES_DIR = BASE_DIR / "video-app" / "public" / "images"

GOOGLE_IMAGEN_ACTIVE = True
HF_ZEROGPU_ACTIVE = True
POLLINATIONS_IMAGE_ACTIVE = True


def call_with_timeout(func, args=(), kwargs=None, timeout_sec=30):
    """Executes a function inside a worker thread with a strict maximum timeout."""
    if kwargs is None:
        kwargs = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        return future.result(timeout=timeout_sec)


def enrich_prompt(base_prompt: str) -> str:
    """Enriches image prompt with cinema-grade 3D Pixar / Unreal Engine 5 lighting tokens."""
    cinematic_modifiers = (
        "3D Pixar animated film style, Disney character design, Unreal Engine 5 render, "
        "8k resolution, volumetric dramatic lighting, subsurface scattering, "
        "ray tracing reflections, shallow depth of field, masterpiece"
    )
    return f"{base_prompt}, {cinematic_modifiers}"


def standardize_to_1080x1920(im: Image.Image) -> Image.Image:
    """Standardizes any source image to exact 1080x1920 vertical 9:16 using high-quality Lanczos resampling."""
    w, h = im.size
    target_w, target_h = 1080, 1920
    scale = max(target_w / w, target_h / h)
    new_w, new_h = int(round(w * scale)), int(round(h * scale))
    im_scaled = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    im_cropped = im_scaled.crop((left, top, left + target_w, top + target_h))
    return im_cropped


def generate_imagen3_google(prompt: str, output_path: Path, seed: int = 42) -> bool:
    """Tier 1: Generates cinema-grade 1080x1920 visuals using Google Imagen 3."""
    global GOOGLE_IMAGEN_ACTIVE
    if not GOOGLE_IMAGEN_ACTIVE:
        return False

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False
    api_key = api_key.strip().strip("'").strip('"')

    try:
        from google import genai

        print(f"[IMAGE-ENGINE] [TIER-1: Google Imagen 3] Generating: '{prompt[:48]}...'")
        client = genai.Client(api_key=api_key)

        def _call_imagen():
            return client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=prompt[:450],
                config=dict(
                    number_of_images=1,
                    aspect_ratio="9:16",
                    output_mime_type="image/jpeg",
                    person_generation="ALLOW_ADULT",
                ),
            )

        res = call_with_timeout(_call_imagen, timeout_sec=25)
        if res and res.generated_images:
            img_bytes = res.generated_images[0].image.image_bytes
            temp_raw = output_path.with_suffix(".tmp.jpg")
            temp_raw.write_bytes(img_bytes)
            with Image.open(temp_raw) as im:
                im_std = standardize_to_1080x1920(im.convert("RGB"))
                im_std.save(output_path, "JPEG", quality=95)
            temp_raw.unlink(missing_ok=True)
            if output_path.exists() and output_path.stat().st_size > 25_000:
                print(f"[IMAGE-ENGINE] [TIER-1] Google Imagen 3 rendered {output_path.name} successfully!")
                try:
                    from story_pipeline.telegram_notifier import RUN_TRACKER
                    RUN_TRACKER.set_model_used("Visuals", "Google Imagen 3 (imagen-3.0-generate-002)")
                except Exception:
                    pass
                return True
    except Exception as e:
        err_s = str(e).lower()
        if any(k in err_s for k in ["404", "not_found", "quota", "resource_exhausted", "permission"]):
            print(f"[IMAGE-ENGINE] [TIER-1 Notice] Imagen 3 unavailable on current tier ({str(e)[:90]}). Falling back...")
            GOOGLE_IMAGEN_ACTIVE = False
        else:
            print(f"[IMAGE-ENGINE] [TIER-1 Notice] Imagen 3 note ({str(e)[:90]})")
        try:
            from story_pipeline.telegram_notifier import RUN_TRACKER
            RUN_TRACKER.record_model_failure("Google Imagen 3", f"{str(e)[:60]}")
        except Exception:
            pass
    return False


def generate_flux_hf_space(prompt: str, output_path: Path, seed: int = 42) -> bool:
    """Tier 2: Generates photorealistic 3D visuals using Hugging Face FLUX.1-schnell Space."""
    global HF_ZEROGPU_ACTIVE
    if not HF_ZEROGPU_ACTIVE:
        return False

    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        return False
    hf_token = hf_token.strip().strip("'").strip('"')

    try:
        from gradio_client import Client

        print(f"[IMAGE-ENGINE] [TIER-2: FLUX.1-schnell] Dispatching prompt: '{prompt[:48]}...'")
        client = Client("black-forest-labs/FLUX.1-schnell", token=hf_token)

        def _predict():
            return client.predict(
                prompt=prompt[:350],
                seed=seed,
                randomize_seed=True,
                width=768,
                height=1360,
                num_inference_steps=4,
                api_name="/infer",
            )

        result_tuple = call_with_timeout(_predict, timeout_sec=25)
        result = result_tuple[0] if isinstance(result_tuple, tuple) else result_tuple

        res_path = None
        if isinstance(result, dict) and "path" in result:
            res_path = Path(result["path"])
        elif isinstance(result, str):
            res_path = Path(result)

        if res_path and res_path.exists():
            with Image.open(res_path) as im:
                im_std = standardize_to_1080x1920(im.convert("RGB"))
                im_std.save(output_path, "JPEG", quality=95)
            if output_path.exists() and output_path.stat().st_size > 25_000:
                try:
                    from story_pipeline.telegram_notifier import RUN_TRACKER
                    RUN_TRACKER.set_model_used("Visuals", "HF FLUX.1-schnell")
                except Exception:
                    pass
                return True
    except Exception as e:
        err_s = str(e).lower()
        if "zerogpu" in err_s or "quota" in err_s or "limit" in err_s:
            HF_ZEROGPU_ACTIVE = False
            print(f"[IMAGE-ENGINE] [TIER-2 Notice] ZeroGPU quota exceeded. Disabling for remainder of run.")
            try:
                from story_pipeline.telegram_notifier import RUN_TRACKER
                RUN_TRACKER.record_model_failure("HF FLUX.1-schnell", "ZeroGPU queue limit / timeout")
            except Exception:
                pass
        else:
            print(f"[IMAGE-ENGINE] [TIER-2 Notice] FLUX.1-schnell note ({str(e)[:100]})")
            try:
                from story_pipeline.telegram_notifier import RUN_TRACKER
                RUN_TRACKER.record_model_failure("HF FLUX.1-schnell", f"Inference note ({str(e)[:60]})")
            except Exception:
                pass
    return False


def generate_pollinations_clean(prompt: str, output_path: Path, seed: int = 42) -> bool:
    """Tier 3: Generates AI visuals using clean Pollinations streaming endpoint."""
    global POLLINATIONS_IMAGE_ACTIVE
    if not POLLINATIONS_IMAGE_ACTIVE:
        return False

    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    try:
        clean_p = urllib.parse.quote(prompt[:280])
        url = f"https://image.pollinations.ai/prompt/{clean_p}?nologo=true&seed={seed}"
        print(f"[IMAGE-ENGINE] [TIER-3: Pollinations] Fetching: '{prompt[:48]}...'")

        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = resp.read()
            if len(data) > 15_000:
                temp_raw = output_path.with_suffix(".tmp.jpg")
                temp_raw.write_bytes(data)
                with Image.open(temp_raw) as im:
                    im_std = standardize_to_1080x1920(im.convert("RGB"))
                    im_std = im_std.filter(ImageFilter.UnsharpMask(radius=2, percent=160, threshold=3))
                    im_std.save(output_path, "JPEG", quality=95)
                temp_raw.unlink(missing_ok=True)
                if output_path.exists() and output_path.stat().st_size > 25_000:
                    try:
                        from story_pipeline.telegram_notifier import RUN_TRACKER
                        RUN_TRACKER.set_model_used("Visuals", "Pollinations AI Engine")
                    except Exception:
                        pass
                    return True
    except Exception as e:
        s_err = str(e).lower()
        if any(k in s_err for k in ["402", "payment", "403", "forbidden"]):
            POLLINATIONS_IMAGE_ACTIVE = False
            print(f"[IMAGE-ENGINE] [TIER-3 Notice] Pollinations returned 402/403. Disabling for remainder of run.")
            try:
                from story_pipeline.telegram_notifier import RUN_TRACKER
                RUN_TRACKER.record_model_failure("Pollinations AI", "HTTP 402/403 Payment Required")
            except Exception:
                pass
        else:
            print(f"[IMAGE-ENGINE] [TIER-3 Notice] Pollinations note ({str(e)[:100]})")
            try:
                from story_pipeline.telegram_notifier import RUN_TRACKER
                RUN_TRACKER.record_model_failure("Pollinations AI", f"Network error ({str(e)[:60]})")
            except Exception:
                pass
    return False


def generate_hd_image(prompt: str, output_path: Path, seed: int = 1, beat_num: int = 1) -> Path:
    """Generates an authentic 9:16 vertical 1080x1920 visual with strict multi-tier AI model failover."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    enriched = enrich_prompt(prompt)

    # 1. Tier 1: Google Imagen 3 (imagen-3.0-generate-002)
    if generate_imagen3_google(enriched, output_path, seed=seed):
        return output_path

    # 2. Tier 2: Hugging Face FLUX.1-schnell Space
    if generate_flux_hf_space(enriched, output_path, seed=seed):
        return output_path

    # 3. Tier 3: Pollinations Clean Free Engine
    if generate_pollinations_clean(enriched, output_path, seed=seed):
        return output_path

    # Hard Failure: Zero-upload safety guard strictly prohibits fake or missing images!
    raise RuntimeError(
        f"All AI image generation models failed for Beat #{beat_num} ('{prompt[:50]}...'). "
        f"Zero-upload safety guard strictly rejects crude drawings or missing images."
    )


def generate_all_beat_images(beats: list[dict], episode_num: int) -> list[dict]:
    """Generates enhanced visuals for all beats with active quality auditing and retry loops."""
    from story_pipeline.strict_pipeline_auditor import (
        audit_single_visual_asset,
        QualityAuditError,
    )
    from story_pipeline.telegram_notifier import notify_audit_rejection

    PUBLIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    spacing = 3

    for idx, beat in enumerate(beats):
        b_num = beat["beat_number"]
        out_file = PUBLIC_IMAGES_DIR / f"ep_{episode_num}_beat_{b_num}.jpg"
        prompt = beat.get("visual_prompt") or f"{beat.get('title', 'Action')}, {beat.get('narration', '')}"
        seed = int(episode_num * 100 + b_num * 17)

        # Active quality audit loop (up to 3 attempts with dynamic prompt enhancement)
        beat_certified = False
        beat_title = beat.get("title", f"Beat #{b_num}")
        for attempt in range(1, 4):
            try:
                generate_hd_image(prompt, out_file, seed=seed + attempt * 31, beat_num=b_num)
                metrics = audit_single_visual_asset(out_file, prompt=prompt, beat_title=beat_title)

                print(
                    f"[AUDITOR] [GATE-2] Beat #{b_num} Image Certified: {out_file.name} "
                    f"(Content: PASS, Quality: {metrics['quality']}, Clarity: {metrics['clarity']}, Relation: PASS)"
                )
                beat_certified = True
                break
            except QualityAuditError as q_err:
                print(f"[AUDITOR] [GATE-2 Rejection] Beat #{b_num} attempt {attempt}/3 rejected: {q_err}")
                notify_audit_rejection(
                    gate_name="Gate 2: Visual Assets",
                    item_name=out_file.name,
                    reason=str(q_err),
                    attempt=attempt,
                    max_attempts=3,
                    action="Regenerating with enhanced subject-specific visual tokens...",
                )
                out_file.unlink(missing_ok=True)
                prompt += ", dramatic cinematic focus, 3D Pixar character action, highly detailed subject, volumetric lighting"
            except Exception as gen_err:
                print(f"⚠️ [Image Engine Error] Beat #{b_num} generation attempt {attempt}/3 error: {gen_err}")
                if attempt == 3:
                    raise

        if not beat_certified:
            raise QualityAuditError(
                f"Visual Asset Hard Block: Beat #{b_num} failed all AI generation attempts and strict auditor inspection. "
                f"Publication halted by Zero-Upload Safety Guard."
            )

        beat["image_url"] = f"images/{out_file.name}"

        if idx < len(beats) - 1:
            time.sleep(spacing)

    return beats
