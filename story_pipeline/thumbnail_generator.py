"""
High-CTR Automatic A/B/C Thumbnail Generator Suite (Item 18).
Generates 3 distinct viral thumbnail variants optimized for YouTube's native 'Test & Compare' split tests:
- Variant A (Mystery & Revelation): Climax frame, neon cyan border, bold question hook
- Variant B (High-Tension Callout): Opening frame, neon yellow border, shocking badge
- Variant C (Cinematic Focus): Climax revelation frame, cinematic vignette, bold center copy
"""

import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).resolve().parent.parent
VIDEO_APP_DIR = BASE_DIR / "video-app"
OUTPUT_DIR = VIDEO_APP_DIR / "out"


def get_category_emoji(category: str) -> str:
    c = category.lower()
    if any(k in c for k in ["sea", "ocean", "trench", "abyss", "submarine"]):
        return "🌊"
    if any(k in c for k in ["space", "cosmic", "saturn", "moon", "planet"]):
        return "🪐"
    if any(k in c for k in ["dinosaur", "monster", "prehistoric"]):
        return "🦖"
    if any(k in c for k in ["body", "brain", "medical", "immune"]):
        return "🧠"
    return "⚡"


def extract_video_still(video_path: Path, timestamp_sec: float, output_path: Path) -> bool:
    """Extracts a sharp frame at a specific timestamp via FFmpeg."""
    if not video_path or not video_path.exists():
        return False
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{timestamp_sec:.2f}",
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "2",
        str(output_path),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path.exists() and output_path.stat().st_size > 10_000
    except Exception:
        return False


def get_impact_font(size: int):
    """Loads Impact font with safe fallbacks across OS environments."""
    for path in [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/Library/Fonts/Impact.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def generate_high_ctr_thumbnail(
    episode_num: int, headline: str, video_path: Path = None, category: str = "Science"
) -> Path:
    """Generates the primary production thumbnail (Variant A)."""
    suite = generate_abc_thumbnail_suite(episode_num, headline, category, video_path)
    return suite["variant_a"]


def generate_abc_thumbnail_suite(
    episode_num: int, headline: str, category: str = "Science", video_path: Path = None
) -> dict:
    """Generates 3 distinct high-CTR thumbnail variants for A/B/C testing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    emoji = get_category_emoji(category)

    clean_headline = headline.strip().rstrip("?!.").upper()
    if len(clean_headline) > 28:
        clean_headline = clean_headline[:25] + "..."

    font_large = get_impact_font(58)
    font_badge = get_impact_font(44)

    results = {}

    # -------------------------------------------------------------
    # VARIANT A: Mystery & Urgency Hook (Extract at 24s)
    # -------------------------------------------------------------
    still_a = OUTPUT_DIR / f"raw_still_a_{episode_num}.jpg"
    extract_video_still(video_path, 24.0, still_a)
    img_a = Image.open(still_a).convert("RGBA") if still_a.exists() else Image.new("RGBA", (1080, 1920), (15, 10, 30))

    overlay_a = Image.new("RGBA", img_a.size, (0, 0, 0, 0))
    draw_a = ImageDraw.Draw(overlay_a)
    w, h = img_a.size

    # Neon Yellow Outer Border
    draw_a.rectangle([12, 12, w - 12, h - 12], outline=(255, 230, 0, 245), width=18)

    # Top Viral Hook Pill
    pill_w = 880
    pill_h = 135
    draw_a.rounded_rectangle(
        [(w - pill_w) // 2, 120, (w + pill_w) // 2, 120 + pill_h],
        radius=35,
        fill=(0, 0, 0, 230),
        outline=(255, 230, 0, 255),
        width=6,
    )
    draw_a.text((w // 2, 120 + pill_h // 2), f"{emoji} {clean_headline}", fill=(255, 230, 0, 255), font=font_large, anchor="mm")

    # Bottom Callout Badge
    badge_w = 900
    badge_h = 150
    draw_a.rounded_rectangle(
        [(w - badge_w) // 2, h - 330, (w + badge_w) // 2, h - 180],
        radius=40,
        fill=(235, 30, 60, 245),
        outline=(255, 255, 255, 255),
        width=8,
    )
    draw_a.text((w // 2, h - 255), f"EPISODE #{episode_num} • WATCH NOW! 🔥", fill=(255, 255, 255, 255), font=font_badge, anchor="mm")

    path_a = OUTPUT_DIR / f"thumbnail_episode_{episode_num}.jpg"
    Image.alpha_composite(img_a, overlay_a).convert("RGB").save(path_a, "JPEG", quality=95)
    still_a.unlink(missing_ok=True)
    results["variant_a"] = path_a

    # -------------------------------------------------------------
    # VARIANT B: Shock & Curiosity Hook (Extract at 6s)
    # -------------------------------------------------------------
    still_b = OUTPUT_DIR / f"raw_still_b_{episode_num}.jpg"
    extract_video_still(video_path, 6.0, still_b)
    img_b = Image.open(still_b).convert("RGBA") if still_b.exists() else Image.new("RGBA", (1080, 1920), (20, 15, 35))

    overlay_b = Image.new("RGBA", img_b.size, (0, 0, 0, 0))
    draw_b = ImageDraw.Draw(overlay_b)

    # Neon Cyan Outer Border
    draw_b.rectangle([12, 12, w - 12, h - 12], outline=(0, 230, 255, 245), width=18)

    # Top Shock Pill
    draw_b.rounded_rectangle(
        [(w - pill_w) // 2, 120, (w + pill_w) // 2, 120 + pill_h],
        radius=35,
        fill=(0, 0, 0, 235),
        outline=(0, 230, 255, 255),
        width=6,
    )
    draw_b.text((w // 2, 120 + pill_h // 2), f"⚠️ WHAT THEY HIDDEN!", fill=(0, 230, 255, 255), font=font_large, anchor="mm")

    # Bottom Yellow CTA
    draw_b.rounded_rectangle(
        [(w - badge_w) // 2, h - 330, (w + badge_w) // 2, h - 180],
        radius=40,
        fill=(255, 220, 0, 245),
        outline=(0, 0, 0, 255),
        width=8,
    )
    draw_b.text((w // 2, h - 255), f"DON'T LOOK AWAY ⚡", fill=(0, 0, 0, 255), font=font_badge, anchor="mm")

    path_b = OUTPUT_DIR / f"thumbnail_episode_{episode_num}_B.jpg"
    Image.alpha_composite(img_b, overlay_b).convert("RGB").save(path_b, "JPEG", quality=95)
    still_b.unlink(missing_ok=True)
    results["variant_b"] = path_b

    # -------------------------------------------------------------
    # VARIANT C: Deep-Vignette Dramatic Statement (Extract at 40s)
    # -------------------------------------------------------------
    still_c = OUTPUT_DIR / f"raw_still_c_{episode_num}.jpg"
    extract_video_still(video_path, 40.0, still_c)
    img_c = Image.open(still_c).convert("RGBA") if still_c.exists() else Image.new("RGBA", (1080, 1920), (10, 10, 25))

    overlay_c = Image.new("RGBA", img_c.size, (0, 0, 0, 0))
    draw_c = ImageDraw.Draw(overlay_c)

    # Heavy dark vignette band in middle
    mid_y = h // 2
    draw_c.rectangle([0, mid_y - 180, w, mid_y + 180], fill=(0, 0, 0, 210))
    draw_c.text((w // 2, mid_y - 40), f"{emoji} {clean_headline}", fill=(255, 230, 0, 255), font=font_large, anchor="mm")
    draw_c.text((w // 2, mid_y + 50), "THE SCIENTIFIC TRUTH", fill=(255, 255, 255, 240), font=font_badge, anchor="mm")

    path_c = OUTPUT_DIR / f"thumbnail_episode_{episode_num}_C.jpg"
    Image.alpha_composite(img_c, overlay_c).convert("RGB").save(path_c, "JPEG", quality=95)
    still_c.unlink(missing_ok=True)
    results["variant_c"] = path_c

    print(f"🌟 High-CTR A/B/C Thumbnail Suite generated: {path_a.name}, {path_b.name}, {path_c.name}")
    return results
