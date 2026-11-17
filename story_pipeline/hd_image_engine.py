"""
Stage 3: High-Definition 3D Pixar & CGI Image Generator.
Generates vertical 1080x1920 illustrations for every story beat:
1. Gemini Imagen 3 with rate-limit backoff and retries.
2. Universal free fallback generator (Pollinations).
3. Procedural Cinematic 3D Engine (Pillow) guarantees 100% asset uptime even during network blocks.
"""

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
    """Procedurally synthesizes a 1080x1920 vertical cinematic 3D visual."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    random.seed(seed)

    # Determine color theme from prompt
    p_lower = prompt.lower()
    if any(k in p_lower for k in ["space", "moon", "saturn", "alien", "cosmic", "star"]):
        bg_col = (8, 6, 22)
        glow_col = (130, 70, 240)
        core_col = (255, 180, 80)
    elif any(k in p_lower for k in ["sea", "ocean", "jellyfish", "water", "abyss"]):
        bg_col = (4, 18, 32)
        glow_col = (30, 180, 220)
        core_col = (120, 255, 200)
    elif any(k in p_lower for k in ["fire", "lava", "volcano", "heat"]):
        bg_col = (25, 6, 4)
        glow_col = (230, 80, 30)
        core_col = (255, 210, 60)
    else:
        bg_col = (14, 12, 28)
        glow_col = (180, 90, 210)
        core_col = (240, 200, 100)

    img = Image.new("RGB", (1080, 1920), color=bg_col)
    draw = ImageDraw.Draw(img)

    # Multi-layered 3D spherical glow & volumetric horizon
    center_y = int(960 + random.randint(-150, 150))
    for r in range(750, 0, -8):
        factor = 1.0 - (r / 750.0)
        cr = int(glow_col[0] * factor + core_col[0] * (factor**2) * 0.4)
        cg = int(glow_col[1] * factor + core_col[1] * (factor**2) * 0.4)
        cb = int(glow_col[2] * factor + core_col[2] * (factor**2) * 0.4)
        draw.ellipse([540 - r, center_y - r, 540 + r, center_y + r], fill=(min(255, cr), min(255, cg), min(255, cb)))

    # Atmospheric particles / starfield
    for _ in range(350):
        sx = random.randint(0, 1080)
        sy = random.randint(0, 1920)
        sr = random.randint(1, 4)
        alpha = random.randint(140, 255)
        draw.ellipse([sx, sy, sx + sr, sy + sr], fill=(alpha, alpha, alpha))

    # Soft cinematic diffusion blur
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    img.save(str(output_path), quality=95)
    print(f"🎨 [Stage 3: Image Engine] Synthesized 3D Procedural Visual: {output_path.name}")
    return output_path


def generate_hd_image(prompt: str, output_path: Path, seed: int = 1) -> Path:
    """Generates an enhanced 9:16 vertical 1080x1920 visual with multi-tier failover."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and output_path.stat().st_size > 20_000:
        return output_path

    enriched = enrich_prompt(prompt)

    # 1. Primary: Gemini Imagen 3 (with retry & quota reset backoff)
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        for attempt in range(1, 4):
            try:
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
                    print(f"⏳ Rate limit pause ({err_str[:60]}). Waiting {wait_time}s for Google quota reset...")
                    time.sleep(wait_time)
                else:
                    break

    # 2. Secondary: Replicate Flux/SDXL (if configured)
    rep_token = os.getenv("REPLICATE_API_TOKEN")
    if rep_token:
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

    # 3. Universal Free AI Tier (Pollinations Flux & Turbo)
    for model_name in ["flux", "turbo"]:
        try:
            clean_prompt = urllib.parse.quote(enriched[:320])
            url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=768&height=1344&nologo=true&seed={seed}&model={model_name}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=18) as response:
                data = response.read()
                if len(data) > 15_000:
                    output_path.write_bytes(data)
                    print(f"🎨 [Stage 3: Image Engine] Generated 3D Pixar Visual ({model_name}): {output_path.name}")
                    return output_path
        except Exception:
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
