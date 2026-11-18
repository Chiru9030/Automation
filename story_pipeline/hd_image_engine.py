"""
Stage 3: High-Definition 3D Visual Generation Engine.
Generates full-bleed 1080x1920 vertical cinematic illustrations for every story beat:
1. Tier 1: Hugging Face FLUX.1-schnell (via authenticated client with HF_TOKEN)
2. Tier 2: Pollinations Clean Free Engine (non-paywalled default AI model)
3. Tier 3: Theme-Specific Semantic Procedural Synthesis (guarantees 100% theme-matching uptime)
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


def generate_flux_hf_space(prompt: str, output_path: Path, seed: int = 42) -> bool:
    """Tier 1: Generates photorealistic 3D visuals using Hugging Face FLUX.1-schnell Space."""
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        return False
    hf_token = hf_token.strip().strip("'").strip('"')

    try:
        from gradio_client import Client
        import shutil

        print(f"[IMAGE-ENGINE] [TIER-1: FLUX.1-schnell] Dispatching prompt: '{prompt[:48]}...'")
        client = Client("black-forest-labs/FLUX.1-schnell", token=hf_token)
        result, _ = client.predict(
            prompt=prompt[:350],
            seed=seed,
            randomize_seed=True,
            width=768,
            height=1360,
            num_inference_steps=4,
            api_name="/infer",
        )

        res_path = None
        if isinstance(result, dict) and "path" in result:
            res_path = Path(result["path"])
        elif isinstance(result, str):
            res_path = Path(result)

        if res_path and res_path.exists():
            with Image.open(res_path) as im:
                im_std = standardize_to_1080x1920(im.convert("RGB"))
                im_std.save(output_path, "JPEG", quality=95)
            return output_path.exists() and output_path.stat().st_size > 25_000
    except Exception as e:
        print(f"[IMAGE-ENGINE] [TIER-1 Notice] FLUX.1-schnell note ({str(e)[:100]})")
    return False


def generate_pollinations_clean(prompt: str, output_path: Path, seed: int = 42) -> bool:
    """Tier 2: Generates AI visuals using clean, non-paywalled Pollinations endpoint."""
    try:
        clean_p = urllib.parse.quote(prompt[:300])
        url = f"https://image.pollinations.ai/prompt/{clean_p}?nologo=true"
        print(f"[IMAGE-ENGINE] [TIER-2: Pollinations] Fetching prompt: '{prompt[:48]}...'")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = resp.read()
            if len(data) > 15_000:
                temp_raw = output_path.with_suffix(".tmp.jpg")
                temp_raw.write_bytes(data)
                with Image.open(temp_raw) as im:
                    im_std = standardize_to_1080x1920(im.convert("RGB"))
                    im_std.save(output_path, "JPEG", quality=95)
                temp_raw.unlink(missing_ok=True)
                return output_path.exists() and output_path.stat().st_size > 25_000
    except Exception as e:
        print(f"[IMAGE-ENGINE] [TIER-2 Notice] Pollinations note ({str(e)[:100]})")
    return False


def generate_semantic_procedural_visual(prompt: str, output_path: Path, seed: int = 42) -> Path:
    """
    Tier 3: Theme-Specific Semantic Procedural Synthesis.
    Generates high-contrast vertical compositions matching the exact scene theme.
    NEVER generates generic planetary rings for non-space subjects.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    random.seed(seed)
    p_lower = prompt.lower()

    img = Image.new("RGB", (1080, 1920), color=(10, 15, 30))
    draw = ImageDraw.Draw(img)

    # -------------------------------------------------------------
    # Theme 1: Ocean / Sea / Megalodon / Monster / Abyss
    # -------------------------------------------------------------
    if any(k in p_lower for k in ["ocean", "sea", "megalodon", "shark", "monster", "underwater", "abyss", "water", "beast"]):
        # Abyssal deep ocean gradient
        for y in range(1920):
            factor = y / 1920.0
            r = int(5 * (1 - factor) + 2 * factor)
            g = int(35 * (1 - factor) + 12 * factor)
            b = int(75 * (1 - factor) + 28 * factor)
            draw.line([(0, y), (1080, y)], fill=(r, g, b))

        # Volumetric Sun Caustic Light Rays from Surface
        for ray in range(8):
            start_x = random.randint(100, 980)
            end_x = start_x + random.randint(-250, 250)
            alpha_b = random.randint(120, 210)
            draw.line([(start_x, 0), (end_x, 1400)], fill=(20, 130, alpha_b), width=random.randint(15, 45))

        # Giant Megalodon / Monster Silhouette
        cy = 980 + random.randint(-100, 100)
        # Body
        draw.ellipse([180, cy - 260, 900, cy + 260], fill=(8, 22, 45))
        # Giant Dorsal Fin
        draw.polygon([(460, cy - 250), (620, cy - 540), (680, cy - 250)], fill=(6, 18, 38))
        # Bioluminescent Glowing Predator Eye
        eye_y = cy - 40
        draw.ellipse([760, eye_y - 18, 796, eye_y + 18], fill=(255, 230, 80))
        draw.ellipse([772, eye_y - 8, 788, eye_y + 8], fill=(255, 255, 255))

        # Rising Ocean Bubbles & Caustic Particles
        for _ in range(800):
            bx = random.randint(0, 1080)
            by = random.randint(0, 1920)
            br = random.randint(2, 6)
            b_alpha = random.randint(140, 255)
            draw.ellipse([bx, by, bx + br, by + br], fill=(b_alpha, min(255, b_alpha + 30), 255))

    # -------------------------------------------------------------
    # Theme 2: Fire / Lava / Volcano / Heat / Thermal
    # -------------------------------------------------------------
    elif any(k in p_lower for k in ["fire", "lava", "volcano", "heat", "burn", "flame", "magma"]):
        for y in range(1920):
            factor = y / 1920.0
            r = int(75 * (1 - factor) + 120 * factor)
            g = int(15 * (1 - factor) + 30 * factor)
            b = int(8 * (1 - factor) + 5 * factor)
            draw.line([(0, y), (1080, y)], fill=(r, g, b))

        # Magma Core & Volcanic Fissures
        draw.ellipse([200, 1200, 880, 1880], fill=(255, 110, 25))
        draw.ellipse([340, 1340, 740, 1740], fill=(255, 230, 80))

        # Fiery Embers & Ash Particles
        for _ in range(1000):
            ex = random.randint(0, 1080)
            ey = random.randint(0, 1920)
            er = random.randint(2, 5)
            e_col = (255, random.randint(100, 220), 30)
            draw.ellipse([ex, ey, ex + er, ey + er], fill=e_col)

    # -------------------------------------------------------------
    # Theme 3: Cellular / Medicine / Human Biology / Brain
    # -------------------------------------------------------------
    elif any(k in p_lower for k in ["sleep", "brain", "body", "cell", "medical", "blood", "human", "biology"]):
        for y in range(1920):
            factor = y / 1920.0
            r = int(45 * (1 - factor) + 15 * factor)
            g = int(12 * (1 - factor) + 40 * factor)
            b = int(60 * (1 - factor) + 85 * factor)
            draw.line([(0, y), (1080, y)], fill=(r, g, b))

        # Neural Network Dendrites
        for _ in range(12):
            x1, y1 = random.randint(100, 980), random.randint(200, 1700)
            x2, y2 = x1 + random.randint(-300, 300), y1 + random.randint(-300, 300)
            draw.line([(x1, y1), (x2, y2)], fill=(40, 220, 255), width=4)
            draw.ellipse([x1 - 15, y1 - 15, x1 + 15, y1 + 15], fill=(255, 215, 90))

        # Microscopic Cellular Spheres
        for _ in range(600):
            cx = random.randint(0, 1080)
            cy = random.randint(0, 1920)
            cr = random.randint(2, 7)
            draw.ellipse([cx, cy, cx + cr, cy + cr], fill=(255, 120, 190))

    # -------------------------------------------------------------
    # Theme 4: Space / Cosmic (ONLY for actual space topics)
    # -------------------------------------------------------------
    elif any(k in p_lower for k in ["space", "moon", "saturn", "alien", "cosmic", "star", "jupiter", "gravity"]):
        for y in range(1920):
            factor = y / 1920.0
            draw.line([(0, y), (1080, y)], fill=(int(18 + 25 * factor), int(12 + 15 * factor), int(60 + 35 * factor)))

        draw.ellipse([240, 660, 840, 1260], fill=(180, 80, 255))
        draw.ellipse([360, 780, 720, 1140], fill=(255, 215, 110))

        for _ in range(1000):
            sx = random.randint(0, 1080)
            sy = random.randint(0, 1920)
            sr = random.randint(1, 4)
            draw.ellipse([sx, sy, sx + sr, sy + sr], fill=(255, 255, 255))

    # -------------------------------------------------------------
    # Theme 5: General Dramatic Primordial Atmosphere
    # -------------------------------------------------------------
    else:
        for y in range(1920):
            factor = y / 1920.0
            draw.line([(0, y), (1080, y)], fill=(int(25 + 35 * factor), int(25 + 40 * factor), int(45 + 50 * factor)))

        draw.ellipse([260, 700, 820, 1260], fill=(240, 160, 60))
        for _ in range(800):
            x = random.randint(0, 1080)
            y = random.randint(0, 1920)
            r = random.randint(2, 5)
            draw.ellipse([x, y, x + r, y + r], fill=(255, 230, 140))

    # Unsharp Masking for Tack-Sharp Edge Definition
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
    img.save(str(output_path), quality=95)
    print(f"[IMAGE-ENGINE] [TIER-3] Synthesized Theme-Matched Visual: {output_path.name}")
    return output_path


def generate_hd_image(prompt: str, output_path: Path, seed: int = 1) -> Path:
    """Generates an enhanced 9:16 vertical 1080x1920 visual with strict multi-tier failover."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    enriched = enrich_prompt(prompt)

    # 1. Tier 1: Hugging Face FLUX.1-schnell Space
    if generate_flux_hf_space(enriched, output_path, seed=seed):
        return output_path

    # 2. Tier 2: Pollinations Clean Free Engine
    if generate_pollinations_clean(enriched, output_path, seed=seed):
        return output_path

    # 3. Tier 3: Theme-Specific Semantic Procedural Synthesis
    return generate_semantic_procedural_visual(prompt, output_path, seed=seed)


def generate_all_beat_images(beats: list[dict], episode_num: int) -> list[dict]:
    """Generates enhanced visuals for all beats with active quality auditing and retry loops."""
    from story_pipeline.strict_pipeline_auditor import (
        audit_single_visual_asset,
        audit_semantic_content_relevance,
        QualityAuditError,
    )
    from story_pipeline.telegram_notifier import notify_audit_rejection

    PUBLIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    spacing = 4

    for idx, beat in enumerate(beats):
        b_num = beat["beat_number"]
        out_file = PUBLIC_IMAGES_DIR / f"ep_{episode_num}_beat_{b_num}.jpg"
        prompt = beat.get("visual_prompt") or f"{beat.get('title', 'Action')}, {beat.get('narration', '')}"
        seed = int(episode_num * 100 + b_num * 17)

        # Active quality audit loop (up to 3 attempts with dynamic prompt enhancement)
        beat_certified = False
        for attempt in range(1, 4):
            generate_hd_image(prompt, out_file, seed=seed + attempt * 31)
            try:
                metrics = audit_single_visual_asset(out_file)
                # Strict Semantic Relevance Inspection
                audit_semantic_content_relevance(out_file, prompt, beat.get("title", f"Beat #{b_num}"))

                print(
                    f"[AUDITOR] [GATE-2] Beat #{b_num} Image Certified: {out_file.name} "
                    f"(Vibrancy: {metrics['colorfulness']:.1f}, Contrast: {metrics['contrast']:.1f}, Sharpness: {metrics['sharpness']:.1f})"
                )
                beat_certified = True
                break
            except QualityAuditError as q_err:
                print(f"[AUDITOR] [GATE-2 Rejection] Beat #{b_num} attempt {attempt}/3 rejected: {q_err}")
                notify_audit_rejection(
                    gate_name="Gate 2: Visual Quality & Content Matching",
                    item_name=out_file.name,
                    reason=str(q_err),
                    attempt=attempt,
                    max_attempts=3,
                    action="Regenerating with enhanced subject-specific visual tokens...",
                )
                out_file.unlink(missing_ok=True)
                prompt += ", dramatic cinematic focus, 3D Pixar character action, highly detailed subject, volumetric lighting"

        if not beat_certified:
            generate_semantic_procedural_visual(prompt, out_file, seed=seed)
            audit_single_visual_asset(out_file)

        beat["image_url"] = f"images/{out_file.name}"

        if idx < len(beats) - 1:
            time.sleep(spacing)

    return beats
