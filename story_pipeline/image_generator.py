"""
AI Illustration Generator for Dynamic Storytelling.
Generates high-resolution 3D Pixar / cinematic vertical artwork for every scene
using the 100% free public AI engine or Gemini Imagen.
"""

import os
import urllib.parse
import urllib.request
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_IMAGES_DIR = BASE_DIR / "video-app" / "public" / "images"


def generate_scene_image(prompt: str, output_path: Path, style: str = "3D Pixar animated film style") -> Path:
    """Generates a high-quality vertical 3D Pixar illustration."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Check if Gemini Imagen API is available
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            result = client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=f"{prompt}, {style}, vibrant colors, highly detailed fur, masterpiece, 8k",
                config=dict(number_of_images=1, aspect_ratio="9:16"),
            )
            for generated_image in result.generated_images:
                output_path.write_bytes(generated_image.image.image_bytes)
                print(f"🎨 Generated Imagen illustration: {output_path.name}")
                return output_path
        except Exception as e:
            pass

    # 2. Universal Free High-Res Generator (Pollinations Default Free Tier)
    try:
        clean_prompt = f"{prompt}, {style}, cute, expressive character, vibrant cinematic lighting, highly detailed storybook, 8k"
        encoded = urllib.parse.quote(clean_prompt)
        # Using default tier (100% free, zero 402 errors)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1344&nologo=true&seed={int(time.time()) % 10000}"

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            if len(data) > 5000:
                output_path.write_bytes(data)
                print(f"🎨 Generated 3D Pixar visual: {output_path.name}")
                return output_path
    except Exception as e:
        print(f"Notice: Image generator note: {e}")

    # Fallback to copy an existing illustration if network blocks
    fallback_img = PUBLIC_IMAGES_DIR / "file0.jpg"
    if fallback_img.exists() and not output_path.exists():
        output_path.write_bytes(fallback_img.read_bytes())

    return output_path
