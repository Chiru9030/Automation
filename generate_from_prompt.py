"""
Prompt-to-Video Generator with Automatic Background Music.
Reads 'prompt.txt', synthesizes genre-matched background music,
updates the Remotion composition data, and renders the final MP4.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from audio_generator import generate_music_for_genre

BASE_DIR = Path(__file__).resolve().parent
PROMPT_FILE = BASE_DIR / "prompt.txt"
VIDEO_APP_DIR = BASE_DIR / "video-app"
PUBLIC_AUDIO_DIR = VIDEO_APP_DIR / "public" / "audio"
DATA_JSON_PATH = VIDEO_APP_DIR / "src" / "videoData.json"
OUTPUT_DIR = VIDEO_APP_DIR / "out"


def parse_prompt_file(prompt_path: Path) -> dict:
    """Parses prompt.txt using Gemini if API key is available, or fallback regex parser."""
    text = prompt_path.read_text(encoding="utf-8")

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            print(" Using Gemini AI to structure video from prompt.txt...")
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            prompt_instruction = f"""
            You are an expert viral video producer for YouTube Shorts and Instagram Reels.
            Convert the following user prompt into a strictly structured JSON for a 15-second vertical video (3 facts).

            USER PROMPT:
            {text}

            Respond with JSON ONLY in this exact format:
            {{
              "genre": "Short genre name (e.g. Sci-Fi, Mystery, Action)",
              "category": "ALL CAPS CATEGORY TAG (e.g. DEEP SPACE MYSTERIES)",
              "title": "Main Title (supports newline)",
              "subtitle": "Short hook text (e.g. WAIT UNTIL #3... 🤯)",
              "hookEmoji": "relevant single emoji",
              "facts": [
                {{
                  "number": 1,
                  "badge": "Short badge title",
                  "headline": "Punchy 1-sentence statement",
                  "subtext": "Explanation or mindblowing detail",
                  "highlightWord": "Word from headline to highlight in yellow",
                  "emoji": "emoji"
                }},
                {{
                  "number": 2,
                  "badge": "Short badge title",
                  "headline": "Punchy 1-sentence statement",
                  "subtext": "Explanation or mindblowing detail",
                  "highlightWord": "Word from headline to highlight in yellow",
                  "emoji": "emoji"
                }},
                {{
                  "number": 3,
                  "badge": "Short badge title",
                  "headline": "Punchy 1-sentence statement",
                  "subtext": "Explanation or mindblowing detail",
                  "highlightWord": "Word from headline to highlight in yellow",
                  "emoji": "emoji"
                }}
              ],
              "outroTitle": "FOLLOW FOR MORE",
              "outroSubtitle": "Which fact shocked you most? 👇",
              "outroEmoji": "🚀",
              "audioFile": "audio/background.wav"
            }}
            """
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_instruction,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            data = json.loads(response.text)
            return data
        except Exception as e:
            print(f"Notice: Gemini parsing skipped ({e}), falling back to offline parser.")

    # Offline regex parser
    print(" Using offline prompt parser...")
    genre_match = re.search(r"Genre:\s*(.*)", text, re.IGNORECASE)
    topic_match = re.search(r"Topic:\s*(.*)", text, re.IGNORECASE)

    genre = genre_match.group(1).strip() if genre_match else "Sci-Fi / Space"
    topic = topic_match.group(1).strip() if topic_match else "3 Mind-Blowing Facts"

    # Default structured payload
    data = {
        "genre": genre,
        "category": topic.upper()[:28],
        "title": topic.replace("About ", "About\n"),
        "subtitle": "WAIT UNTIL #3... 🤯",
        "hookEmoji": "🪐" if "space" in genre.lower() else "⚡",
        "facts": [
            {
                "number": 1,
                "badge": "Fact #1",
                "headline": "A day on Venus is longer than its whole year!",
                "subtext": "Venus rotates so slowly that it takes 243 Earth days to spin once, but only 225 Earth days to orbit the Sun.",
                "highlightWord": "longer",
                "emoji": "🔥",
            },
            {
                "number": 2,
                "badge": "Fact #2",
                "headline": "There is a giant reservoir of water floating in space!",
                "subtext": "Hovering around a distant quasar, this cloud holds 140 TRILLION times more water than all Earth's oceans combined.",
                "highlightWord": "140 TRILLION",
                "emoji": "🌊",
            },
            {
                "number": 3,
                "badge": "Fact #3",
                "headline": "One teaspoon of a neutron star weighs 6 billion tons!",
                "subtext": "They are so dense and spin up to 700 times per second — a single grain would crush through Earth's crust.",
                "highlightWord": "6 billion tons",
                "emoji": "⚡",
            },
        ],
        "outroTitle": "FOLLOW FOR MORE",
        "outroSubtitle": "Which fact shocked you most? 👇",
        "outroEmoji": "🚀",
        "audioFile": "audio/background.wav",
    }
    return data


def run_pipeline():
    print("=======================================================")
    print(" 🚀 Autonomous Prompt-to-Video Engine (with BG Music) ")
    print("=======================================================")

    if not PROMPT_FILE.exists():
        print(f"Error: {PROMPT_FILE} not found!")
        sys.exit(1)

    # 1. Parse prompt
    print(f"Reading prompt from: {PROMPT_FILE}")
    video_data = parse_prompt_file(PROMPT_FILE)
    genre = video_data.get("genre", "Sci-Fi")
    print(f"Detected Genre: '{genre}' | Topic: '{video_data.get('category', '')}'")

    # 2. Generate matching background music
    bg_music_path = PUBLIC_AUDIO_DIR / "background.wav"
    print(f"\n Synthesizing background music for genre '{genre}'...")
    generate_music_for_genre(genre, bg_music_path)

    # 3. Save dynamic video data
    video_data["audioFile"] = "audio/background.wav"
    with open(DATA_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(video_data, f, indent=2)
    print(f" Updated composition data in: {DATA_JSON_PATH}")

    # 4. Render Remotion video
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_mp4 = OUTPUT_DIR / "space_facts.mp4"
    print(f"\n Rendering 15-second vertical video with background music to: {out_mp4}...")

    cmd = [
        "npx",
        "remotion",
        "render",
        "src/index.ts",
        "SpaceFacts",
        str(out_mp4),
    ]

    result = subprocess.run(cmd, cwd=str(VIDEO_APP_DIR))
    if result.returncode == 0:
        print("\n VIDEO GENERATION COMPLETE!")
        print(f" Output Video File: {out_mp4}")
    else:
        print(f"\n Video rendering failed with exit code: {result.returncode}")


if __name__ == "__main__":
    run_pipeline()

