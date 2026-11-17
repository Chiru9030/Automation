"""
AI Illustration Generator for Text-Only Storybooks.
When a storybook has no embedded illustrations, this module generates
high-resolution 1024x1024 3D Pixar / Storybook style artwork for every scene.
"""

import os
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_IMAGES_DIR = BASE_DIR / "video-app" / "public" / "images"


def generate_scene_image(prompt: str, output_path: Path, style: str = "3D Pixar animated film style") -> Path:
    """Generates a high-quality illustration using free Pollinations AI or Gemini Imagen."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Check if Gemini Imagen API is available
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            result = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=f"{prompt}, {style}, vibrant colors, high detail, masterpiece, 8k",
                config=dict(number_of_images=1, aspect_ratio="1:1"),
            )
            for generated_image in result.generated_images:
                output_path.write_bytes(generated_image.image.image_bytes)
                print(f"🎨 Generated Imagen illustration: {output_path.name}")
                return output_path
        except Exception as e:
            print(f"Notice: Imagen generation fallback ({e})")

    # 2. Universal Free High-Res Generator (Pollinations Flux)
    try:
        clean_prompt = f"{prompt}, {style}, cute, expressive, vibrant lighting, highly detailed storybook"
        encoded = urllib.parse.quote(clean_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&nologo=true&seed=42"

        req = urllib.request.Request(url, headers={"User-Agent": "StoryVideoPipeline/2.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            if len(data) > 5000:
                output_path.write_bytes(data)
                print(f"🎨 Generated AI story illustration: {output_path.name}")
                return output_path
    except Exception as e:
        print(f"Notice: Remote image generator exception: {e}")

    return output_path
