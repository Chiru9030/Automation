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
    """Loads Anton or Impact font with safe fallbacks across OS environments."""
    anton_bundled = BASE_DIR / "video-app" / "public" / "fonts" / "Anton.ttf"
    candidates = [
        str(anton_bundled),
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/Library/Fonts/Impact.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def wrap_text_into_lines(text: str, max_words_per_line: int = 3, max_chars_per_line: int = 16) -> list[str]:
    """Wraps headline text into 2-3 punchy viral lines for 1080x1920 mobile screens."""
    words = text.split()
    if not words:
        return [text]
    lines = []
    current_line = []
    for w in words:
        test_line = " ".join(current_line + [w])
        if len(current_line) < max_words_per_line and len(test_line) <= max_chars_per_line:
            current_line.append(w)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [w]
    if current_line:
        lines.append(" ".join(current_line))
    return lines[:3]  # Maximum 3 lines for high CTR legibility


def get_sticker_badge(category: str, episode_num: int) -> str:
    c = category.lower()
    if "biology" in c or "human" in c:
        return f"🚨 MEDICAL ANOMALY #{episode_num}"
    if "space" in c or "cosmic" in c:
        return f"🪐 COSMIC PARADOX #{episode_num}"
    if "ocean" in c or "trench" in c:
        return f"🌊 DEEP SEA SECRETS #{episode_num}"
    if "prehistoric" in c or "dinosaur" in c:
        return f"🦖 PREHISTORIC TRUTH #{episode_num}"
    return f"⚡ VIRAL PARADOX #{episode_num}"


def draw_backed_text_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font: ImageFont.ImageFont,
    start_y: int,
    canvas_w: int,
    text_color=(255, 230, 0, 255),
    box_color=(0, 0, 0, 240),
    box_outline=(255, 230, 0, 255),
    outline_width=4,
    pad_x=32,
    pad_y=16,
    line_spacing=20,
) -> int:
    """Draws multiple lines of 110px+ text with high-contrast individual backing pill boxes."""
    curr_y = start_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        box_w = tw + pad_x * 2
        box_h = th + pad_y * 2
        box_left = (canvas_w - box_w) // 2
        box_top = curr_y
        box_right = box_left + box_w
        box_bottom = box_top + box_h

        draw.rounded_rectangle(
            [box_left, box_top, box_right, box_bottom],
            radius=24,
            fill=box_color,
            outline=box_outline,
            width=outline_width,
        )
        draw.text(
            (canvas_w // 2, box_top + box_h // 2),
            line,
            fill=text_color,
            font=font,
            anchor="mm",
        )
        curr_y += box_h + line_spacing
    return curr_y


def generate_high_ctr_thumbnail(
    episode_num: int, headline: str, video_path: Path = None, category: str = "Science"
) -> Path:
    """Generates the primary production thumbnail (Variant A)."""
    suite = generate_abc_thumbnail_suite(episode_num, headline, category, video_path)
    return suite["variant_a"]


def generate_abc_thumbnail_suite(
    episode_num: int, headline: str, category: str = "Science", video_path: Path = None
) -> dict:
    """Generates 3 distinct high-CTR thumbnail variants for A/B/C testing with 110-120px Anton typography."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    emoji = get_category_emoji(category)
    sticker = get_sticker_badge(category, episode_num)

    clean_headline = headline.strip().rstrip("?!.").upper()
    for prefix in ["WHAT IF WHAT HAPPENS IF ", "WHAT HAPPENS IF WHAT IF ", "WHAT HAPPENS IF ", "WHAT IF "]:
        if clean_headline.startswith(prefix):
            clean_headline = clean_headline[len(prefix):].strip()
            clean_headline = f"WHAT IF {clean_headline}"
            break
    lines = wrap_text_into_lines(clean_headline, max_words_per_line=3, max_chars_per_line=16)

    font_large = get_impact_font(110)
    font_badge = get_impact_font(50)
    font_sticker = get_impact_font(38)

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
    draw_a.rectangle([12, 12, w - 12, h - 12], outline=(255, 230, 0, 245), width=20)

    # Top Category Sticker Badge
    badge_w = 580
    badge_h = 75
    draw_a.rounded_rectangle(
        [(w - badge_w) // 2, 80, (w + badge_w) // 2, 80 + badge_h],
        radius=20,
        fill=(255, 230, 0, 255),
        outline=(0, 0, 0, 255),
        width=4,
    )
    draw_a.text((w // 2, 80 + badge_h // 2), sticker, fill=(0, 0, 0, 255), font=font_sticker, anchor="mm")

    # High-CTR 110px Backed Text Lines (Center Upper Third)
    draw_backed_text_lines(
        draw_a,
        lines,
        font_large,
        start_y=210,
        canvas_w=w,
        text_color=(255, 230, 0, 255),
        box_color=(0, 0, 0, 240),
        box_outline=(255, 230, 0, 255),
        outline_width=6,
    )

    # Bottom Callout Badge
    callout_w = 920
    callout_h = 140
    draw_a.rounded_rectangle(
        [(w - callout_w) // 2, h - 300, (w + callout_w) // 2, h - 160],
        radius=35,
        fill=(235, 30, 60, 245),
        outline=(255, 255, 255, 255),
        width=8,
    )
    draw_a.text((w // 2, h - 230), f"EPISODE #{episode_num} • WATCH NOW! 🔥", fill=(255, 255, 255, 255), font=font_badge, anchor="mm")

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
    draw_b.rectangle([12, 12, w - 12, h - 12], outline=(0, 230, 255, 245), width=20)

    # Top Shock Sticker
    draw_b.rounded_rectangle(
        [(w - badge_w) // 2, 80, (w + badge_w) // 2, 80 + badge_h],
        radius=20,
        fill=(0, 230, 255, 255),
        outline=(0, 0, 0, 255),
        width=4,
    )
    draw_b.text((w // 2, 80 + badge_h // 2), "⚠️ CLASSIFIED FACT", fill=(0, 0, 0, 255), font=font_sticker, anchor="mm")

    # High-CTR Cyan/White Text Lines
    draw_backed_text_lines(
        draw_b,
        lines,
        font_large,
        start_y=210,
        canvas_w=w,
        text_color=(0, 240, 255, 255),
        box_color=(0, 0, 0, 240),
        box_outline=(0, 230, 255, 255),
        outline_width=6,
    )

    # Bottom Yellow CTA
    draw_b.rounded_rectangle(
        [(w - callout_w) // 2, h - 300, (w + callout_w) // 2, h - 160],
        radius=35,
        fill=(255, 220, 0, 245),
        outline=(0, 0, 0, 255),
        width=8,
    )
    draw_b.text((w // 2, h - 230), f"DON'T LOOK AWAY ⚡", fill=(0, 0, 0, 255), font=font_badge, anchor="mm")

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

    # Heavy dark cinematic vignette band across center
    mid_y = h // 2
    draw_c.rectangle([0, mid_y - 320, w, mid_y + 320], fill=(0, 0, 0, 220))

    # Center Backed Text
    draw_backed_text_lines(
        draw_c,
        lines,
        font_large,
        start_y=mid_y - 200,
        canvas_w=w,
        text_color=(255, 230, 0, 255),
        box_color=(20, 20, 20, 240),
        box_outline=(255, 255, 255, 200),
        outline_width=4,
    )
    draw_c.text((w // 2, mid_y + 240), "THE SCIENTIFIC TRUTH", fill=(255, 255, 255, 240), font=font_badge, anchor="mm")

    path_c = OUTPUT_DIR / f"thumbnail_episode_{episode_num}_C.jpg"
    Image.alpha_composite(img_c, overlay_c).convert("RGB").save(path_c, "JPEG", quality=95)
    still_c.unlink(missing_ok=True)
    results["variant_c"] = path_c

    print(f"🌟 High-CTR A/B/C Anton 110px Thumbnail Suite generated: {path_a.name}, {path_b.name}, {path_c.name}")
    return results
