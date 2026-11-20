"""
Autonomous TikTok & Instagram Swipeable Image Carousel Generator (Item 19).
Transforms the 5 high-definition 1080x1920 3D scene renders into swipeable carousel cards
with viral typography, slide count pills (e.g., '1/5', '2/5'), and engagement callouts.
Produces 5 individual slides ready for Instagram Carousel & TikTok Photo Mode.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
VIDEO_APP_DIR = BASE_DIR / "video-app"
PUBLIC_DIR = VIDEO_APP_DIR / "public"
OUTPUT_DIR = VIDEO_APP_DIR / "out"


def get_carousel_font(size: int):
    """Safe font loader across macOS and Linux runners."""
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


def generate_swipeable_carousel(script_data: dict, episode_num: int) -> list[Path]:
    """
    Renders 5 swipeable 1080x1920 carousel cards with bold typographic overlays:
    Slide 1: Viral Hook & Opening Paradox (with 'Swipe 👉' indicator)
    Slide 2: Escalating Pressure / Danger
    Slide 3: The Catastrophic Climax
    Slide 4: The Scientific Secret
    Slide 5: The Closing Paradox & Comment Engagement Prompt
    """
    beats = script_data.get("beats", [])
    if not beats:
        return []

    topic = script_data.get("topic") or script_data.get("title", "Curiosity Paradox")
    category = script_data.get("category", "Science")

    carousel_out_dir = OUTPUT_DIR / f"carousel_ep_{episode_num}"
    carousel_out_dir.mkdir(parents=True, exist_ok=True)

    font_title = get_carousel_font(56)
    font_body = get_carousel_font(42)
    font_pill = get_carousel_font(34)

    generated_slides = []

    for idx, beat in enumerate(beats):
        slide_num = idx + 1
        img_rel = beat.get("image_url", "")
        img_path = PUBLIC_DIR / img_rel
        if not img_path.exists():
            img_path = PUBLIC_DIR / "images" / f"ep_{episode_num}_beat_{slide_num}.jpg"

        if img_path.exists():
            base_img = Image.open(img_path).convert("RGBA")
        else:
            base_img = Image.new("RGBA", (1080, 1920), (12, 10, 24))

        overlay = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        w, h = base_img.size

        # 1. Slide Counter Pill in Top-Right Corner (e.g. '1/5')
        pill_text = f"{slide_num}/5"
        draw.rounded_rectangle([w - 170, 70, w - 50, 130], radius=25, fill=(0, 0, 0, 210), outline=(255, 230, 0, 255), width=4)
        draw.text((w - 110, 100), pill_text, fill=(255, 230, 0, 255), font=font_pill, anchor="mm")

        # 2. Top Channel Watermark
        draw.text((60, 100), "CURIOSITY UNIVERSE ⚡", fill=(255, 255, 255, 220), font=font_pill, anchor="lm")

        # 3. Lower-Third Dark Glass Card for Narrative Text
        card_h = 440
        card_y0 = h - card_h - 100
        draw.rounded_rectangle([50, card_y0, w - 50, card_y0 + card_h], radius=35, fill=(0, 0, 0, 220), outline=(255, 255, 255, 120), width=4)

        # 4. Slide Content Formatting
        narration = beat.get("narration", "")
        # Wrap text to 34 chars per line
        words = narration.split()
        lines = []
        cur_line = []
        cur_len = 0
        for wd in words:
            if cur_len + len(wd) + 1 > 32:
                lines.append(" ".join(cur_line))
                cur_line = [wd]
                cur_len = len(wd)
            else:
                cur_line.append(wd)
                cur_len += len(wd) + 1
        if cur_line:
            lines.append(" ".join(cur_line))

        text_block = "\n".join(lines[:4])  # Max 4 punchy lines
        draw.text((w // 2, card_y0 + 130), text_block, fill=(255, 255, 255, 255), font=font_body, anchor="mm", align="center", spacing=12)

        # 5. Slide Footer Action
        if slide_num == 1:
            draw.text((w // 2, card_y0 + card_h - 55), "SWIPE FOR THE TRUTH 👉", fill=(255, 230, 0, 255), font=font_pill, anchor="mm")
        elif slide_num == len(beats):
            draw.text((w // 2, card_y0 + card_h - 55), "💬 WHAT WOULD YOU DO? COMMENT BELOW!", fill=(0, 230, 255, 255), font=font_pill, anchor="mm")
        else:
            draw.text((w // 2, card_y0 + card_h - 55), f"BEAT #{slide_num} • SWIPE NEXT 👉", fill=(200, 200, 200, 240), font=font_pill, anchor="mm")

        slide_path = carousel_out_dir / f"slide_{slide_num}.jpg"
        flat_slide_path = OUTPUT_DIR / f"carousel_ep_{episode_num}_slide_{slide_num}.jpg"
        img_final = Image.alpha_composite(base_img, overlay).convert("RGB")
        img_final.save(slide_path, "JPEG", quality=95)
        img_final.save(flat_slide_path, "JPEG", quality=95)
        generated_slides.append(slide_path)

    print(f"📸 [Carousel Generator] Rendered {len(generated_slides)} swipeable slides in {carousel_out_dir.name}/")
    return generated_slides
