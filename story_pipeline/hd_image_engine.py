"""
Stage 3: High-Definition 3D Pixar & CGI Image Generator.
Generates vertical 1080x1920 illustrations for every story beat:
1. Gemini Imagen 3 with rate-limit backoff and retries.
2. Universal free fallback generator (Pollinations).
3. Procedural Cinematic 3D Engine (Pillow) guarantees 100% asset uptime even during network blocks.
"""

import json
import math
import os
import random
import time
import urllib.parse
import urllib.request
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFilter

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_IMAGES_DIR = BASE_DIR / "video-app" / "public" / "images"


def enrich_prompt(base_prompt: str) -> str:
    """Enriches image prompt with cinema-grade 3D Pixar / Unreal Engine 5 lighting tokens."""
    cinematic_modifiers = (
        "3D Pixar animated film style, Disney character design, Unreal Engine 5 render, "
        "8k resolution, volumetric golden hour lighting, subsurface scattering on skin and fur, "
        "ray tracing reflections, shallow depth of field, masterpiece"
    )
    return f"{base_prompt}, {cinematic_modifiers}"


def generate_procedural_3d_visual(prompt: str, output_path: Path, seed: int = 42) -> Path:
    """Procedurally synthesizes a high-contrast, vibrant 1080x1920 vertical cinematic 3D visual."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    random.seed(seed)

    # Vibrant, saturated color palettes (never dark or black)
    p_lower = prompt.lower()
    if any(k in p_lower for k in ["space", "moon", "saturn", "alien", "cosmic", "star", "jupiter"]):
        bg_top = (18, 14, 65)
        bg_bottom = (45, 15, 80)
        glow_col = (160, 80, 255)
        core_col = (255, 200, 90)
        ring_col = (100, 210, 255)
    elif any(k in p_lower for k in ["sea", "ocean", "jellyfish", "water", "abyss"]):
        bg_top = (10, 35, 75)
        bg_bottom = (5, 65, 95)
        glow_col = (40, 210, 240)
        core_col = (140, 255, 210)
        ring_col = (80, 180, 255)
    elif any(k in p_lower for k in ["fire", "lava", "volcano", "heat"]):
        bg_top = (65, 12, 10)
        bg_bottom = (95, 25, 15)
        glow_col = (255, 90, 40)
        core_col = (255, 225, 80)
        ring_col = (255, 160, 40)
    else:
        bg_top = (35, 15, 60)
        bg_bottom = (60, 25, 90)
        glow_col = (210, 90, 240)
        core_col = (255, 215, 110)
        ring_col = (130, 220, 255)

    img = Image.new("RGB", (1080, 1920), color=bg_top)
    draw = ImageDraw.Draw(img)

    # Vertical gradient background
    for y in range(1920):
        factor = y / 1920.0
        r = int(bg_top[0] * (1 - factor) + bg_bottom[0] * factor)
        g = int(bg_top[1] * (1 - factor) + bg_bottom[1] * factor)
        b = int(bg_top[2] * (1 - factor) + bg_bottom[2] * factor)
        draw.line([(0, y), (1080, y)], fill=(r, g, b))

    # Volumetric Radiant Celestial Sphere (Center)
    center_y = int(960 + random.randint(-120, 120))
    for r in range(600, 0, -6):
        factor = 1.0 - (r / 600.0)
        cr = int(glow_col[0] * factor + core_col[0] * (factor**1.8))
        cg = int(glow_col[1] * factor + core_col[1] * (factor**1.8))
        cb = int(glow_col[2] * factor + core_col[2] * (factor**1.8))
        draw.ellipse([540 - r, center_y - r, 540 + r, center_y + r], fill=(min(255, cr), min(255, cg), min(255, cb)))

    # Brilliant 3D Planetary Ring System
    for rw in range(-25, 26, 2):
        draw.ellipse([540 - 750, center_y - 140 + rw, 540 + 750, center_y + 140 + rw], outline=ring_col, width=2)

    # Vibrant Foreground Particle Field
    for _ in range(400):
        sx = random.randint(0, 1080)
        sy = random.randint(0, 1920)
        sr = random.randint(2, 6)
        alpha = random.randint(180, 255)
        p_col = (alpha, min(255, alpha + 20), min(255, int(alpha * 0.9)))
        draw.ellipse([sx, sy, sx + sr, sy + sr], fill=p_col)

    # Soft cinematic diffusion blur
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
    img.save(str(output_path), quality=95)
    print(f"🎨 [Stage 3: Image Engine] Synthesized Vibrant 3D Visual: {output_path.name}")
    return output_path


def generate_hd_image(prompt: str, output_path: Path, seed: int = 1) -> Path:
    """Generates an enhanced 9:16 vertical 1080x1920 visual with multi-tier failover."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and output_path.stat().st_size > 20_000:
        return output_path

    enriched = enrich_prompt(prompt)

    # 1. Primary: Gemini Imagen 3 (Developer API mode & Enterprise support)
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        api_key = api_key.strip().strip("'").strip('"')
        for attempt in range(1, 3):
            try:
                import base64
                # Google AI Studio Developer REST API (works with all standard AI Studio keys)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
                req_data = json.dumps({
                    "instances": [{"prompt": enriched}],
                    "parameters": {"sampleCount": 1, "aspectRatio": "9:16"}
                }).encode("utf-8")
                req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    preds = resp_json.get("predictions", [])
                    if preds and "bytesBase64Encoded" in preds[0]:
                        img_bytes = base64.b64decode(preds[0]["bytesBase64Encoded"])
                        output_path.write_bytes(img_bytes)
                        print(f"🎨 [Stage 3: Image Engine] Generated Imagen 3 Visual: {output_path.name}")
                        return output_path

                # Fallback to SDK method
                from google import genai
                client = genai.Client(api_key=api_key)
                result = client.models.generate_images(
                    model="imagen-3.0-generate-002",
                    prompt=enriched,
                    config=dict(number_of_images=1, aspect_ratio="9:16"),
                )
                for gen_img in result.generated_images:
                    output_path.write_bytes(gen_img.image.image_bytes)
                    print(f"🎨 [Stage 3: Image Engine] Generated Imagen 3 Visual: {output_path.name}")
                    return output_path
            except Exception as e_genai:
                err_str = str(e_genai).lower()
                print(f"⚠️ Gemini Imagen Attempt #{attempt} note: {e_genai}")
                if "resource_exhausted" in err_str or "429" in err_str or "quota" in err_str:
                    wait_time = 20 * attempt
                    print(f"⏳ Rate limit pause. Waiting {wait_time}s for Google quota reset...")
                    time.sleep(wait_time)
                else:
                    break

    # 2. Secondary: Fal.ai Flux Schnell (Ultra-Fast 4-Step 3D Imagery)
    fal_key = os.getenv("FAL_KEY")
    if fal_key:
        fal_key = fal_key.strip().strip("'").strip('"')
        try:
            fal_url = "https://fal.run/fal-ai/flux/schnell"
            fal_payload = json.dumps({
                "prompt": enriched[:400],
                "image_size": "portrait_16_9",
                "num_inference_steps": 4,
                "seed": seed,
            }).encode("utf-8")
            fal_req = urllib.request.Request(
                fal_url,
                data=fal_payload,
                headers={"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
            )
            with urllib.request.urlopen(fal_req, timeout=25) as f_resp:
                f_json = json.loads(f_resp.read().decode("utf-8"))
                images = f_json.get("images", [])
                if images and "url" in images[0]:
                    dl_req = urllib.request.Request(images[0]["url"], headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(dl_req, timeout=20) as dl_resp:
                        data = dl_resp.read()
                        if len(data) > 20_000:
                            output_path.write_bytes(data)
                            print(f"🎨 [Stage 3: Image Engine] Generated Fal.ai Flux Visual: {output_path.name}")
                            return output_path
        except Exception as e_fal:
            print(f"Notice: Fal.ai note ({e_fal})")

    # 3. Tertiary: Hugging Face Serverless Inference (FLUX.1-schnell, 100% Free)
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        hf_token = hf_token.strip().strip("'").strip('"')
        try:
            hf_url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
            hf_payload = json.dumps({"inputs": enriched[:400]}).encode("utf-8")
            hf_req = urllib.request.Request(
                hf_url,
                data=hf_payload,
                headers={"Authorization": f"Bearer {hf_token}", "Content-Type": "application/json"}
            )
            with urllib.request.urlopen(hf_req, timeout=30) as hf_resp:
                data = hf_resp.read()
                if len(data) > 20_000:
                    output_path.write_bytes(data)
                    print(f"🎨 [Stage 3: Image Engine] Generated Hugging Face FLUX Visual: {output_path.name}")
                    return output_path
        except Exception as e_hf:
            print(f"Notice: Hugging Face inference note ({e_hf})")

    # 4. Quaternary: Replicate Flux/SDXL (if configured)
    rep_token = os.getenv("REPLICATE_API_TOKEN")
    if rep_token:
        rep_token = rep_token.strip().strip("'").strip('"')
        os.environ["REPLICATE_API_TOKEN"] = rep_token
        try:
            import replicate
            client = replicate.Client(api_token=rep_token)
            out = client.run(
                "black-forest-labs/flux-schnell",
                input={"prompt": enriched[:400], "aspect_ratio": "9:16"},
            )
            if out and len(out) > 0:
                img_url = str(out[0])
                req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = resp.read()
                    if len(data) > 20_000:
                        output_path.write_bytes(data)
                        print(f"🎨 [Stage 3: Image Engine] Generated Replicate Flux Visual: {output_path.name}")
                        return output_path
        except Exception as e_rep:
            print(f"⚠️ Replicate image note: {e_rep}")

    # 3. Universal Free AI Tier (Pollinations Flux & Flux-Realism)
    for model_name in ["flux", "flux-realism"]:
        for attempt in range(1, 3):
            try:
                clean_prompt = urllib.parse.quote(enriched[:320])
                url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=768&height=1344&nologo=true&seed={seed}&model={model_name}"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                with urllib.request.urlopen(req, timeout=35) as response:
                    data = response.read()
                    if len(data) > 15_000:
                        output_path.write_bytes(data)
                        print(f"🎨 [Stage 3: Image Engine] Generated 3D Pixar Visual ({model_name}): {output_path.name}")
                        return output_path
            except Exception as e_poll:
                print(f"⚠️ Pollinations {model_name} note (attempt {attempt}): {e_poll}")
                time.sleep(2)

    # 4. Guaranteed Procedural Fallback (Never leaves missing files on disk)
    return generate_procedural_3d_visual(prompt, output_path, seed=seed)


def generate_all_beat_images(beats: list[dict], episode_num: int) -> list[dict]:
    """Generates enhanced visuals for all beats in the script with spacing."""
    PUBLIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    spacing = 10 if has_gemini else 4

    for idx, beat in enumerate(beats):
        b_num = beat["beat_number"]
        out_file = PUBLIC_IMAGES_DIR / f"ep_{episode_num}_beat_{b_num}.jpg"
        prompt = beat.get("visual_prompt") or f"{beat['title']}, {beat['narration']}"

        # Generate with distinct seed per beat
        seed = int(episode_num * 100 + b_num * 17)
        generate_hd_image(prompt, out_file, seed=seed)
        beat["image_url"] = f"images/{out_file.name}"

        # Spacing to prevent API burst throttling
        if idx < len(beats) - 1:
            time.sleep(spacing)

    return beats
