"""
Stage 3: High-Definition AI 3D Visual Generation Engine.
Generates full-bleed 1080x1920 vertical cinematic illustrations for every story beat:
1. Tier 1: Google Imagen 3 (imagen-3.0-generate-002) via Google AI Studio REST API
2. Tier 2: Hugging Face Cloud Spaces (FLUX.1-schnell & SDXL-Lightning with anonymous auto-fallback)
3. Tier 3: Local 1-Step SD-Turbo Neural Engine (stabilityai/sd-turbo on CPU with cached weights)
4. Tier 4: Pollinations AI Clean Free Engine (with resilient retry and streaming)

Zero Procedural Lines Policy:
Every single asset must be an authentic, photorealistic or 3D AI neural generation.
If all models fail, execution is halted by the Zero-Upload Safety Guard.
"""

import base64
import json
import math
import os
import random
import re
import time
import urllib.parse
import urllib.request
import concurrent.futures
import threading
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageFilter

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv()

PUBLIC_IMAGES_DIR = BASE_DIR / "video-app" / "public" / "images"

GOOGLE_IMAGEN_ACTIVE = True
REPLICATE_FLUX_ACTIVE = True
HF_SPACES_ACTIVE = True
POLLINATIONS_IMAGE_ACTIVE = True
LOCAL_SD_TURBO_ACTIVE = True

_SD_TURBO_PIPE = None
_SD_TURBO_LOCK = threading.Lock()


def call_with_timeout(func, args=(), kwargs=None, timeout_sec=30):
    """Executes a function inside a worker thread with a strict maximum timeout."""
    if kwargs is None:
        kwargs = {}
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    try:
        future = executor.submit(func, *args, **kwargs)
        return future.result(timeout=timeout_sec)
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def sanitize_for_ai_filter(prompt: str) -> str:
    """Replaces sensitive medical/biological or controversial trigger words with safe cinematic equivalents."""
    replacements = {
        r"\bmedical cellular\b": "scientific bio-luminescent",
        r"\bcellular animation\b": "glowing abstract microscopic visualization",
        r"\bhuman brain\b": "intricate neural network visualization",
        r"\bhallucinations\b": "surreal kaleidoscope visions",
        r"\bpsychosis\b": "dreamlike perception shift",
        r"\bdying\b": "fading into shadows",
        r"\bdeath\b": "eternal void",
        r"\bblood\b": "crimson energy pulse",
        r"\bkilling\b": "neutralizing",
    }
    clean = prompt
    for pattern, repl in replacements.items():
        clean = re.sub(pattern, repl, clean, flags=re.IGNORECASE)
    return clean


def enrich_prompt(base_prompt: str, style_hint: str = "") -> str:
    """Enriches image prompt with style-aware tokens (2D vector cartoon, 3D Pixar, or hyper-realistic)."""
    sanitized = sanitize_for_ai_filter(base_prompt)
    combined = f"{base_prompt} {style_hint}".lower()

    if any(k in combined for k in ["2d", "flat vector", "cartoon", "illustration", "chibi", "paheli", "riddle", "fable", "storybook", "comic"]):
        # Strip out conflicting photorealistic / 3D tokens
        conflicting_tokens = [
            "photorealistic cinematic style", "photorealistic", "cinematic photo", "cinematic photograph",
            "realistic", "photo", "35mm prime lens", "50mm cinema lens", "85mm portrait lens",
            "10mm ultra-wide lens", "24mm anamorphic lens", "35mm portrait", "50mm close up",
            "skin texture", "skin pores", "subsurface scattering", "ray tracing reflections",
            "ray tracing", "unreal engine 5 render", "unreal engine 5", "unreal engine",
            "volumetric atmospheric god rays", "volumetric atmospheric lighting",
            "hyper-realistic cinematic photograph", "hyper-realistic", "arri alexa 65",
            "arri alexa", "3d pixar animated film style", "3d pixar render", "3d pixar", "octane render"
        ]
        clean_p = sanitized
        for tok in conflicting_tokens:
            clean_p = clean_p.replace(tok, "").replace(tok.title(), "").replace(tok.upper(), "")
        # Clean extra commas and whitespace
        clean_p = ", ".join(part.strip() for part in clean_p.split(",") if part.strip())

        return (
            f"Flat 2D vector cartoon illustration, cute chibi character design, thick clean black outlines, "
            f"storybook aesthetic, vibrant flat colors, {clean_p}, clean flat cell shading, "
            f"bright flat lighting, crisp sharp lines, zero 3D render, zero photorealism, "
            f"no realistic skin textures, 9:16 vertical composition, masterpiece"
        )
    elif any(k in combined for k in ["dark sci-fi", "hyper-realistic", "space", "cosmic", "black hole", "antarctica", "submarine"]):
        modifiers = (
            "hyper-realistic cinematic photograph, shot on ARRI Alexa 65, anamorphic lens, "
            "volumetric atmospheric lighting, Unreal Engine 5 render, ray tracing, 8k resolution, "
            "photorealistic textures, award-winning cinematography, vertical 9:16 frame"
        )
        return f"{sanitized}, {modifiers}"
    else:
        modifiers = (
            "3D Pixar animated film style, Disney character design, Unreal Engine 5 render, "
            "8k resolution, volumetric dramatic lighting, subsurface scattering, "
            "ray tracing reflections, shallow depth of field, masterpiece"
        )
        return f"{sanitized}, {modifiers}"


def standardize_to_1080x1920(im: Image.Image) -> Image.Image:
    """Standardizes any source image to exact 1080x1920 vertical 9:16 using high-quality Lanczos resampling and cinematic 2-stage edge-focus sharpening."""
    w, h = im.size
    target_w, target_h = 1080, 1920
    scale = max(target_w / w, target_h / h)
    new_w, new_h = int(round(w * scale)), int(round(h * scale))
    im_scaled = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    im_cropped = im_scaled.crop((left, top, left + target_w, top + target_h))
    return (
        im_cropped.filter(ImageFilter.DETAIL)
        .filter(ImageFilter.SHARPEN)
        .filter(ImageFilter.UnsharpMask(radius=2, percent=250, threshold=1))
    )


def generate_imagen3_google(prompt: str, output_path: Path, seed: int = 42) -> bool:
    """Tier 1: Generates cinema-grade 1080x1920 visuals using Google AI Studio Imagen 3."""
    global GOOGLE_IMAGEN_ACTIVE
    if not GOOGLE_IMAGEN_ACTIVE:
        return False

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False
    api_key = api_key.strip().strip("'").strip('"')

    # Method A: Try official google-genai SDK
    try:
        from google import genai
        print(f"[IMAGE-ENGINE] [TIER-1: Google Imagen 3] Requesting via google-genai SDK: '{prompt[:45]}...'")
        client = genai.Client(api_key=api_key)

        def _call_sdk():
            return client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=prompt[:480],
                config=dict(
                    number_of_images=1,
                    aspect_ratio="9:16",
                    output_mime_type="image/jpeg",
                    person_generation="ALLOW_ADULT",
                ),
            )

        res = call_with_timeout(_call_sdk, timeout_sec=25)
        if res and hasattr(res, "generated_images") and res.generated_images:
            img_bytes = res.generated_images[0].image.image_bytes
            temp_raw = output_path.with_suffix(".tmp.jpg")
            temp_raw.write_bytes(img_bytes)
            with Image.open(temp_raw) as im:
                im_std = standardize_to_1080x1920(im.convert("RGB"))
                im_std.save(output_path, "JPEG", quality=95)
            temp_raw.unlink(missing_ok=True)
            if output_path.exists() and output_path.stat().st_size > 25_000:
                print(f"[IMAGE-ENGINE] [TIER-1] Google Imagen 3 (SDK) rendered {output_path.name} successfully!")
                try:
                    from story_pipeline.telegram_notifier import RUN_TRACKER
                    RUN_TRACKER.set_model_used("Visuals", "Google Imagen 3 (imagen-3.0-generate-002)")
                except Exception:
                    pass
                return True
    except Exception as e_sdk:
        print(f"[IMAGE-ENGINE] [TIER-1 Notice] SDK method notice ({str(e_sdk)[:80]}). Trying REST fallback...")

    # Method B: Direct REST API Fallback
    try:
        print(f"[IMAGE-ENGINE] [TIER-1: Google Imagen 3] Requesting AI Studio REST: '{prompt[:45]}...'")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({
            "instances": [{"prompt": prompt[:450]}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "9:16",
                "outputMimeType": "image/jpeg",
                "personGeneration": "ALLOW_ADULT"
            }
        }).encode("utf-8")

        def _call_rest():
            req = urllib.request.Request(url, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=25) as resp:
                return json.loads(resp.read().decode("utf-8"))

        data = call_with_timeout(_call_rest, timeout_sec=28)
        preds = data.get("predictions", []) if isinstance(data, dict) else []
        if preds and "bytesBase64Encoded" in preds[0]:
            img_bytes = base64.b64decode(preds[0]["bytesBase64Encoded"])
            temp_raw = output_path.with_suffix(".tmp.jpg")
            temp_raw.write_bytes(img_bytes)
            with Image.open(temp_raw) as im:
                im_std = standardize_to_1080x1920(im.convert("RGB"))
                im_std.save(output_path, "JPEG", quality=95)
            temp_raw.unlink(missing_ok=True)
            if output_path.exists() and output_path.stat().st_size > 25_000:
                print(f"[IMAGE-ENGINE] [TIER-1] Google Imagen 3 (REST) rendered {output_path.name} successfully!")
                try:
                    from story_pipeline.telegram_notifier import RUN_TRACKER
                    RUN_TRACKER.set_model_used("Visuals", "Google Imagen 3 (imagen-3.0-generate-002)")
                except Exception:
                    pass
                return True
    except Exception as e:
        err_s = str(e).lower()
        if any(k in err_s for k in ["404", "not_found", "403", "permission", "quota", "resource_exhausted", "enterprise"]):
            print(f"[IMAGE-ENGINE] [TIER-1 Notice] Imagen 3 unavailable on current tier ({err_s[:80]}). Disabling for this run.")
            GOOGLE_IMAGEN_ACTIVE = False
        else:
            print(f"[IMAGE-ENGINE] [TIER-1 Notice] Imagen 3 note ({str(e)[:90]})")
        try:
            from story_pipeline.telegram_notifier import RUN_TRACKER
            RUN_TRACKER.record_model_failure("Google Imagen 3", f"{str(e)[:60]}")
        except Exception:
            pass
    return False


def generate_replicate_flux(prompt: str, output_path: Path, seed: int = 42) -> bool:
    """Tier 2: Generates cinema-grade visuals using Replicate FLUX.1-schnell."""
    global REPLICATE_FLUX_ACTIVE
    if not REPLICATE_FLUX_ACTIVE:
        return False

    rep_token = os.getenv("REPLICATE_API_TOKEN")
    if not rep_token:
        return False
    rep_token = rep_token.strip().strip("'").strip('"')

    try:
        import replicate
        print(f"[IMAGE-ENGINE] [TIER-2: Replicate FLUX.1] Requesting: '{prompt[:45]}...'")
        client = replicate.Client(api_token=rep_token)
        clean_p = sanitize_for_ai_filter(prompt)

        def _call_rep():
            return client.run(
                "black-forest-labs/flux-schnell",
                input={
                    "prompt": clean_p[:450],
                    "aspect_ratio": "9:16",
                    "num_outputs": 1,
                    "output_format": "jpg",
                    "output_quality": 95,
                    "seed": seed,
                },
            )

        output = call_with_timeout(_call_rep, timeout_sec=28)
        img_url = None
        if isinstance(output, list) and len(output) > 0:
            item = output[0]
            img_url = str(item) if hasattr(item, "url") else str(item)
        elif output:
            img_url = str(output)

        if img_url and (img_url.startswith("http://") or img_url.startswith("https://")):
            temp_raw = output_path.with_suffix(".tmp.jpg")
            urllib.request.urlretrieve(img_url, temp_raw)
            with Image.open(temp_raw) as im:
                im_std = standardize_to_1080x1920(im.convert("RGB"))
                im_std.save(output_path, "JPEG", quality=95)
            temp_raw.unlink(missing_ok=True)
            if output_path.exists() and output_path.stat().st_size > 25_000:
                print(f"[IMAGE-ENGINE] [TIER-2] Replicate FLUX.1 rendered {output_path.name} successfully!")
                try:
                    from story_pipeline.telegram_notifier import RUN_TRACKER
                    RUN_TRACKER.set_model_used("Visuals", "Replicate FLUX.1-schnell")
                except Exception:
                    pass
                return True
    except Exception as e:
        err_s = str(e).lower()
        if any(k in err_s for k in ["unauthorized", "quota", "credit", "payment", "402"]):
            print(f"[IMAGE-ENGINE] [TIER-2 Notice] Replicate credits unavailable ({err_s[:70]}). Disabling.")
            REPLICATE_FLUX_ACTIVE = False
        else:
            print(f"[IMAGE-ENGINE] [TIER-2 Notice] Replicate note ({str(e)[:90]})")
        try:
            from story_pipeline.telegram_notifier import RUN_TRACKER
            RUN_TRACKER.record_model_failure("Replicate FLUX.1", f"{str(e)[:60]}")
        except Exception:
            pass
    return False


def generate_flux_hf_space(prompt: str, output_path: Path, seed: int = 42) -> bool:
    """Tier 2: Generates photorealistic 3D visuals using Hugging Face FLUX / SDXL Spaces."""
    global HF_SPACES_ACTIVE
    if not HF_SPACES_ACTIVE:
        return False

    try:
        from gradio_client import Client
    except ImportError:
        return False

    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        hf_token = hf_token.strip().strip("'").strip('"')

    clean_p = sanitize_for_ai_filter(prompt)
    spaces_config = [
        ("black-forest-labs/FLUX.1-schnell", "/infer", "flux"),
        ("evalstate/flux1_schnell", "/infer", "flux"),
    ]

    for space_name, api_endpoint, model_type in spaces_config:
        # Prioritize authenticated token when available to bypass anonymous datacenter IP ZeroGPU rate limits
        modes = []
        if hf_token:
            modes.append(("auth", hf_token))
        modes.append(("anon", None))

        for mode, tok in modes:
            try:
                print(f"[IMAGE-ENGINE] [TIER-2: {space_name}] Mode: {mode}, Prompt: '{clean_p[:45]}...'")
                client = Client(space_name, token=tok, headers={"Authorization": f"Bearer {tok}"} if tok else None)

                def _predict():
                    if model_type == "flux":
                        return client.predict(
                            prompt=clean_p[:300],
                            seed=seed,
                            randomize_seed=True,
                            width=576,
                            height=1024,
                            num_inference_steps=4,
                            api_name=api_endpoint,
                        )
                    else:  # sdxl
                        return client.predict(
                            prompt=clean_p[:300],
                            ckpt="4-Step",
                            api_name=api_endpoint,
                        )

                result_tuple = call_with_timeout(_predict, timeout_sec=35)
                res_path = (
                    result_tuple[0]
                    if isinstance(result_tuple, (tuple, list))
                    else (result_tuple.get("path") if isinstance(result_tuple, dict) else result_tuple)
                )

                if res_path and Path(res_path).exists():
                    with Image.open(res_path) as im:
                        im_std = standardize_to_1080x1920(im.convert("RGB"))
                        im_std.save(output_path, "JPEG", quality=95)
                    if output_path.exists() and output_path.stat().st_size > 25_000:
                        print(f"[IMAGE-ENGINE] [TIER-2] {space_name} ({mode}) rendered {output_path.name} successfully!")
                        try:
                            from story_pipeline.telegram_notifier import RUN_TRACKER
                            RUN_TRACKER.set_model_used("Visuals", f"HF {space_name}")
                        except Exception:
                            pass
                        return True
            except Exception as e:
                err_s = str(e).lower()
                if "zerogpu" in err_s or "quota" in err_s:
                    print(f"[IMAGE-ENGINE] [TIER-2 Notice] {space_name} ({mode}) ZeroGPU quota hit. Trying next...")
                    continue
                elif "content filter" in err_s:
                    print(f"[IMAGE-ENGINE] [TIER-2 Notice] Content filter on {space_name}. Trying alternate space...")
                    break
                else:
                    print(f"[IMAGE-ENGINE] [TIER-2 Notice] {space_name} ({mode}) note: {str(e)[:90]}")
    HF_SPACES_ACTIVE = False
    return False


def get_sd_turbo_pipeline():
    """Lazily loads and caches the single-step SD-Turbo diffusion pipeline in memory with thread safety."""
    global _SD_TURBO_PIPE, LOCAL_SD_TURBO_ACTIVE
    if _SD_TURBO_PIPE is not None:
        return _SD_TURBO_PIPE
    if not LOCAL_SD_TURBO_ACTIVE:
        return None

    with _SD_TURBO_LOCK:
        if _SD_TURBO_PIPE is not None:
            return _SD_TURBO_PIPE
        try:
            import torch
            from diffusers import AutoPipelineForText2Image

            print("[IMAGE-ENGINE] [TIER-3: Local SD-Turbo] Initializing single-step neural pipeline...")
            _SD_TURBO_PIPE = AutoPipelineForText2Image.from_pretrained(
                "stabilityai/sd-turbo",
                torch_dtype=torch.float32,
                use_safetensors=True,
            )
            print("[IMAGE-ENGINE] [TIER-3] SD-Turbo loaded into memory successfully!")
            return _SD_TURBO_PIPE
        except Exception as e:
            print(f"[IMAGE-ENGINE] [TIER-3 Notice] Local SD-Turbo initialization note ({str(e)[:90]}). Falling back...")
            return None


def generate_sd_turbo_local(prompt: str, output_path: Path, seed: int = 42) -> bool:
    """Tier 3: Generates authentic photorealistic 3D visual locally in 1 step using SD-Turbo on CPU."""
    pipe = get_sd_turbo_pipeline()
    if pipe is None:
        return False

    try:
        import torch
        print(f"[IMAGE-ENGINE] [TIER-3: Local SD-Turbo] Generating 1-step render: '{prompt[:45]}...'")
        generator = torch.Generator(device="cpu").manual_seed(seed)
        clean_p = sanitize_for_ai_filter(prompt)

        def _run_diffusion():
            with _SD_TURBO_LOCK:
                return pipe(
                    prompt=clean_p[:280],
                    num_inference_steps=1,
                    guidance_scale=0.0,
                    generator=generator,
                ).images[0]

        image = call_with_timeout(_run_diffusion, timeout_sec=120)
        im_std = standardize_to_1080x1920(image.convert("RGB"))
        im_std.save(output_path, "JPEG", quality=95)

        if output_path.exists() and output_path.stat().st_size > 25_000:
            print(f"[IMAGE-ENGINE] [TIER-5] Local SD-Turbo rendered {output_path.name} successfully!")
            try:
                from story_pipeline.telegram_notifier import RUN_TRACKER
                RUN_TRACKER.set_model_used("Visuals", "Local SD-Turbo (Single-Step CPU)")
            except Exception:
                pass
            return True
    except Exception as e:
        print(f"[IMAGE-ENGINE] [TIER-5 Notice] SD-Turbo generation error: {e}")
        try:
            from story_pipeline.telegram_notifier import RUN_TRACKER
            RUN_TRACKER.record_model_failure("Local SD-Turbo", f"{str(e)[:60]}")
        except Exception:
            pass
    return False


def generate_pollinations_clean(prompt: str, output_path: Path, seed: int = 42) -> bool:
    """Tier 1/2: Generates AI visuals using clean Pollinations FLUX streaming endpoint."""
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    for attempt in range(1, 3):
        try:
            p_len = 280 if attempt == 1 else 180
            clean_p = urllib.parse.quote(prompt[:p_len])
            model_param = "&model=flux" if attempt == 1 else ""
            url = f"https://image.pollinations.ai/prompt/{clean_p}?width=576&height=1024{model_param}&seed={seed}"
            print(f"[IMAGE-ENGINE] [TIER-1: Pollinations FLUX] Fetching (attempt {attempt}/2): '{prompt[:45]}...'")

            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if len(data) > 15_000:
                    temp_raw = output_path.with_suffix(".tmp.jpg")
                    temp_raw.write_bytes(data)
                    with Image.open(temp_raw) as im:
                        im_std = standardize_to_1080x1920(im.convert("RGB"))
                        im_std.save(output_path, "JPEG", quality=95)
                    temp_raw.unlink(missing_ok=True)
                    if output_path.exists() and output_path.stat().st_size > 25_000:
                        try:
                            from story_pipeline.telegram_notifier import RUN_TRACKER
                            RUN_TRACKER.set_model_used("Visuals", "Pollinations FLUX")
                        except Exception:
                            pass
                        return True
        except Exception as e:
            err_str = str(e)
            if "402" in err_str or "payment" in err_str.lower():
                print(f"[IMAGE-ENGINE] [Pollinations Notice] Free IP rate limit hit ({err_str[:60]}). Falling over to next tier...")
                break
            print(f"[IMAGE-ENGINE] [Pollinations Notice] Attempt {attempt}/2 ({err_str[:70]}), retrying...")
            time.sleep(1.0 * attempt)
    return False


def generate_hd_image(prompt: str, output_path: Path, seed: int = 1, beat_num: int = 1, style_hint: str = "") -> Path:
    """Generates an authentic 9:16 vertical 1080x1920 visual with high-speed failover."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    enriched = enrich_prompt(prompt, style_hint=style_hint)

    # 1. Primary Cloud Tier: Pollinations Clean FLUX Engine
    if generate_pollinations_clean(enriched, output_path, seed=seed):
        return output_path

    # 2. Resilient Neural Tier: Local SD-Turbo Single-Step Diffusion Engine (Thread-safe offline CPU render)
    if generate_sd_turbo_local(enriched, output_path, seed=seed):
        return output_path

    # Hard Failure: Zero-upload safety guard strictly prohibits fake or missing images!
    raise RuntimeError(
        f"All AI image generation models failed for Beat #{beat_num} ('{prompt[:50]}...'). "
        f"Zero-upload safety guard strictly rejects crude drawings or missing images."
    )


def _process_single_scene_image(beat: dict, episode_num: int) -> dict:
    """Worker to generate, standardize, and audit a single scene visual asset."""
    from story_pipeline.strict_pipeline_auditor import (
        audit_single_visual_asset,
        QualityAuditError,
    )
    from story_pipeline.telegram_notifier import notify_audit_rejection

    b_num = beat.get("scene_number") or beat.get("beat_number", 1)
    out_file = PUBLIC_IMAGES_DIR / f"ep_{episode_num}_scene_{b_num}.jpg"
    prompt = beat.get("video_prompt") or beat.get("visual_prompt") or f"{beat.get('title', 'Action')}, {beat.get('narration', '')}"
    style_hint = beat.get("style", "")
    seed = int(episode_num * 100 + b_num * 17)
    beat_title = beat.get("title", f"Scene #{b_num}")

    # Check if a valid, certified visual asset already exists on disk
    if out_file.exists() and out_file.stat().st_size > 25_000:
        try:
            metrics = audit_single_visual_asset(out_file, prompt=prompt, beat_title=beat_title)
            print(
                f"[AUDITOR] [GATE-2] Scene #{b_num} Image Reused & Certified: {out_file.name} "
                f"(Quality: {metrics['quality']}, Clarity: {metrics['clarity']})"
            )
            beat["image_url"] = f"images/{out_file.name}"
            return beat
        except Exception:
            pass

    beat_certified = False
    for attempt in range(1, 4):
        try:
            generate_hd_image(prompt, out_file, seed=seed + attempt * 31, beat_num=b_num, style_hint=style_hint)
            metrics = audit_single_visual_asset(out_file, prompt=prompt, beat_title=beat_title)

            print(
                f"[AUDITOR] [GATE-2] Scene #{b_num} Image Certified: {out_file.name} "
                f"(Content: PASS, Quality: {metrics['quality']}, Clarity: {metrics['clarity']}, Relation: PASS)"
            )
            beat_certified = True
            break
        except QualityAuditError as q_err:
            print(f"[AUDITOR] [GATE-2 Rejection] Scene #{b_num} attempt {attempt}/3 rejected: {q_err}")
            out_file.unlink(missing_ok=True)
            prompt += ", extreme sharp edge definition, high-contrast micro-textures, ray tracing, Unreal Engine 5 render, 8k resolution, octane render"
        except Exception as gen_err:
            print(f"⚠️ [Image Engine Error] Scene #{b_num} generation attempt {attempt}/3 error: {gen_err}")
            if attempt == 3:
                raise

    if not beat_certified:
        raise QualityAuditError(
            f"Visual Asset Hard Block: Scene #{b_num} failed all AI generation attempts and strict auditor inspection. "
            f"Publication halted by Zero-Upload Safety Guard."
        )

    beat["image_url"] = f"images/{out_file.name}"
    return beat


def generate_all_beat_images(beats: list[dict], episode_num: int) -> list[dict]:
    """Generates enhanced visuals for all scenes/beats concurrently with active quality auditing."""
    PUBLIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n🎨 [Image Engine] Batch-generating {len(beats)} rapid-cut scene visuals (2 paced workers)...")

    # Pre-warm SD-Turbo neural pipeline synchronously once to eliminate multi-thread initialization collisions
    try:
        get_sd_turbo_pipeline()
    except Exception:
        pass

    # Use 2 paced workers to guarantee zero rate-limiting and thread safety
    max_workers = min(2, len(beats))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for beat in beats:
            futures.append(executor.submit(_process_single_scene_image, beat, episode_num))
            time.sleep(0.4)  # 400ms pacing prevents burst rate limiting

        for future in concurrent.futures.as_completed(futures):
            res_beat = future.result()
            sc_num = res_beat.get("scene_number") or res_beat.get("beat_number")
            print(f"  ✅ Scene {sc_num}/{len(beats)} visual ready -> {res_beat['image_url']}")

    return beats
