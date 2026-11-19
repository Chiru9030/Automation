"""
Autonomous Dynamic Topic & Viral Narrative Generator.
Generates infinite, self-sustaining story concepts on demand across viral storytelling genres:
- Animal Legends & Wildlife Sagas (Pixar style)
- Ancient Mysteries & Mythological Lore
- Deep Space & Cosmic Anomalies
- Extreme Survival Thrillers
Zero manual book uploads required. Runs perpetually in the cloud or locally.
"""

import json
import os
import random
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = BASE_DIR / "story_pipeline" / "story_history.json"

# Procedural High-Retention Universe of Story Concepts
PROCEDURAL_STORIES = [
    {
        "title": "Koda the Lone White Wolf",
        "genre": "Wildlife Adventure / Emotional",
        "hook_headline": "THE LONE WOLF'S SACRIFICE",
        "scenes": [
            {
                "scene_number": 1,
                "title": "THE SNOWSTORM",
                "narration": "In the frozen peaks of the Yukon, a pure white wolf pup was abandoned to the merciless winter blizzard.",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_style": "smooth-zoom-in",
                "image_prompt": "3D Pixar animation, pure white wolf pup shivering in a majestic snowy mountain blizzard, glowing amber eyes, volumetric snowflakes, Disney cinematic style, 8k",
            },
            {
                "scene_number": 2,
                "title": "THE SHADOW HUNTER",
                "narration": "Weak and freezing, he heard footsteps in the deep snow. A massive grizzly bear loomed out of the swirling frost.",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_style": "pan-right",
                "image_prompt": "3D Pixar animation, massive shadowy grizzly bear emerging from a snowy forest blizzard, dramatic low-angle perspective, cinematic lighting, 8k",
            },
            {
                "scene_number": 3,
                "title": "THE DESPERATE STAND",
                "narration": "With nowhere to run, the tiny pup bared his fangs and let out a fierce, desperate howl: I will never surrender!",
                "speaker": "character_hero",
                "speaker_name": "Koda",
                "speaker_avatar": "🐺",
                "sfx": "impact_boom",
                "camera_style": "dramatic-pulse",
                "image_prompt": "3D Pixar animation, fierce little white wolf pup howling with immense courage on a snowy cliff, dramatic sunset lighting, high detail fur, Disney masterpiece",
            },
            {
                "scene_number": 4,
                "title": "THE ALPHA'S ARRIVAL",
                "narration": "Suddenly, a thunderous roar answered his call! The legendary silver alpha pack burst through the pines, surrounding the cub in protection.",
                "speaker": "character_guide",
                "speaker_name": "Alpha Wolf",
                "speaker_avatar": "👑",
                "sfx": "pop",
                "camera_style": "warm-dolly",
                "image_prompt": "3D Pixar animation, magnificent silver alpha wolf standing protectively over the white pup, warm golden sunset lighting, heroic composition",
            },
            {
                "scene_number": 5,
                "title": "THE NEW ALPHA",
                "narration": "That night, Koda found his true family. Real strength isn't the size of your fangs—it's the fire in your heart. Follow for Episode Two!",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_style": "sunset-drift",
                "image_prompt": "3D Pixar animation, white wolf pup and alpha wolf standing on a glowing mountain peak beneath the starry Aurora Borealis, magical Disney cinematic style",
            },
        ],
    },
    {
        "title": "The Deep Sea Abyssal Creature",
        "genre": "Ocean Mystery / Thriller",
        "hook_headline": "WHAT LURKS IN THE TRENCH?",
        "scenes": [
            {
                "scene_number": 1,
                "title": "THE MARIANA TRENCH",
                "narration": "Seven miles beneath the ocean surface, where no sunlight has ever reached, deep-sea research submarine Proteus spotted something impossible.",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_style": "smooth-zoom-in",
                "image_prompt": "3D Pixar animation, glowing yellow research submarine descending into the pitch-black Mariana Trench, headlights cutting through dark blue water, floating bioluminescent jellyfish",
            },
            {
                "scene_number": 2,
                "title": "THE BIOLUMINESCENT GLOW",
                "narration": "A rhythm of pulsing blue lights began flashing across the underwater canyon walls. It was communicating in pulses.",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_style": "pan-right",
                "image_prompt": "3D Pixar animation, ancient underwater cavern glowing with neon cyan bioluminescent patterns, mysterious coral reefs, cinematic lighting",
            },
            {
                "scene_number": 3,
                "title": "THE LEVIATHAN AWAKENS",
                "narration": "Warning sirens blared! A gargantuan eye opened in the sea floor. The entire trench wall was alive, and it was watching them.",
                "speaker": "character_hero",
                "speaker_name": "Diver Leo",
                "speaker_avatar": "🌊",
                "sfx": "impact_boom",
                "camera_style": "dramatic-pulse",
                "image_prompt": "3D Pixar animation, colossal mythical sea dragon eye opening in deep ocean abyss, glowing amber iris, majestic scale, cinematic suspense",
            },
            {
                "scene_number": 4,
                "title": "THE GENTLE TITAN",
                "narration": "Instead of crushing the submarine, the ancient guardian gently nudged the vessel toward safety, shielding it from a volcanic rupture.",
                "speaker": "character_guide",
                "speaker_name": "Captain Ray",
                "speaker_avatar": "⚓",
                "sfx": "pop",
                "camera_style": "warm-dolly",
                "image_prompt": "3D Pixar animation, friendly ancient sea leviathan guiding a tiny yellow submarine through underwater currents, warm bioluminescent glow, breathtaking spectacle",
            },
            {
                "scene_number": 5,
                "title": "THE FORGOTTEN GUARDIAN",
                "narration": "Some wonders are meant to remain untouched. We are never truly alone on this planet. Drop a follow right now for Episode Two!",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_style": "sunset-drift",
                "image_prompt": "3D Pixar animation, submarine ascending toward ocean surface sunrise, silhouette of the giant sea guardian in the depths below, Disney masterpiece",
            },
        ],
    },
    {
        "title": "Apollo the Golden Hawk",
        "genre": "Airborne Adventure / Epic",
        "hook_headline": "RULER OF THE SKIES",
        "scenes": [
            {
                "scene_number": 1,
                "title": "THE CANYON NEST",
                "narration": "High atop the red cliffs of the Grand Canyon, young golden hawk Apollo spread his wings for his very first flight.",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_style": "smooth-zoom-in",
                "image_prompt": "3D Pixar animation, majestic young golden hawk perched on a red canyon ledge, golden feathers glowing in sunlight, vast canyon landscape below, Disney style",
            },
            {
                "scene_number": 2,
                "title": "THE RAGING THERMALS",
                "narration": "A sudden desert gale violently ripped him from the cliffside, spiraling him into a dark canyon storm.",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_style": "pan-right",
                "image_prompt": "3D Pixar animation, young hawk diving through swirling desert windstorm clouds, dramatic sunset colors, intense action perspective, 8k",
            },
            {
                "scene_number": 3,
                "title": "THE NARROW ESCAPE",
                "narration": "Rocks plummeted around him! With inches to spare before the jagged canyon floor, he locked his wings and caught the updraft!",
                "speaker": "character_hero",
                "speaker_name": "Apollo",
                "speaker_avatar": "🦅",
                "sfx": "impact_boom",
                "camera_style": "dramatic-pulse",
                "image_prompt": "3D Pixar animation, hawk skimming inches above red canyon river rapids, wings angled sharply, motion blur on water splashes, cinematic lighting",
            },
            {
                "scene_number": 4,
                "title": "THE MOTHER'S FLIGHT",
                "narration": "Screeching through the storm, his mother dove beside him, teaching him the ancient dance of the winds.",
                "speaker": "character_guide",
                "speaker_name": "Sky Queen",
                "speaker_avatar": "👑",
                "sfx": "pop",
                "camera_style": "warm-dolly",
                "image_prompt": "3D Pixar animation, two golden hawks soaring side by side through breaking golden clouds, rays of sunlight piercing storm, emotional triumph",
            },
            {
                "scene_number": 5,
                "title": "KING OF THE WIND",
                "narration": "You cannot discover new horizons until you find the courage to lose sight of the ground. Hit follow for the next wild adventure!",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_style": "sunset-drift",
                "image_prompt": "3D Pixar animation, golden hawk soaring high into a dramatic purple and orange sunset sky, mountain peaks in distance, Disney masterpiece",
            },
        ],
    },
    {
        "title": "The Cyber Samurai of Neo-Kyoto",
        "genre": "Sci-Fi / Action Mystery",
        "hook_headline": "THE LAST BLADE OF NEO-KYOTO",
        "scenes": [
            {
                "scene_number": 1,
                "title": "RAIN OVER NEO-KYOTO",
                "narration": "In the neon-drenched alleys of Neo-Kyoto, year 2089, one robotic ronin still honored the ancient warrior code.",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_style": "smooth-zoom-in",
                "image_prompt": "3D Pixar animation, futuristic cyber samurai standing on a neon rooftop in the rain, glowing katana on back, holographic neon signs of Neo-Kyoto, cinematic cyberpunk",
            },
            {
                "scene_number": 2,
                "title": "THE STOLEN POWER CORE",
                "narration": "When a corrupt megacorporation drained the district's energy grid, plunging orphan wards into darkness, Jin unholstered his plasma blade.",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_style": "pan-right",
                "image_prompt": "3D Pixar animation, cyber samurai dashing across futuristic neon bridges, glowing cyan plasma blade, rainy reflections, dynamic action pose",
            },
            {
                "scene_number": 3,
                "title": "THE ENFORCER SHOWDOWN",
                "narration": "A squad of heavy war mechs cornered him. Jin took a low stance and whispered: Honor never rusts.",
                "speaker": "character_hero",
                "speaker_name": "Ronin Jin",
                "speaker_avatar": "⚔️",
                "sfx": "impact_boom",
                "camera_style": "dramatic-pulse",
                "image_prompt": "3D Pixar animation, cyber samurai parrying glowing laser blasts from towering mechanical enforcers, sparks flying, high tension action",
            },
            {
                "scene_number": 4,
                "title": "THE RESTORED LIGHT",
                "narration": "With a single fluid slice, he disabled the main reactor siphon, flooding the entire city with brilliant golden power.",
                "speaker": "character_guide",
                "speaker_name": "Master Chen",
                "speaker_avatar": "🏮",
                "sfx": "pop",
                "camera_style": "warm-dolly",
                "image_prompt": "3D Pixar animation, futuristic city lighting up with warm golden lanterns and glowing neon towers, children cheering, cyber samurai sheathing blade",
            },
            {
                "scene_number": 5,
                "title": "THE SHADOW GUARDIAN",
                "narration": "True power isn't in control—it's in protection. Follow right now for Episode Two of the Cyber Samurai!",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_style": "sunset-drift",
                "image_prompt": "3D Pixar animation, cyber samurai looking over glowing neon skyline as morning sun rises over futuristic Mount Fuji, cinematic Disney style",
            },
        ],
    },
]


def load_topic_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"processed_chapters": [], "episode_count": 0, "generated_topics": []}


def save_topic_history(history: dict):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def generate_gemini_dynamic_story(topic_index: int) -> dict:
    """Attempts to generate a fresh dynamic story using Gemini AI."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        prompt = f"""You are a master viral storyteller for YouTube Shorts and TikTok.
Create an epic 60-second animated story script for Episode #{topic_index + 1}.
Theme: An emotional animal hero or mythical legend (Pixar 3D style).
Return ONLY a valid JSON object matching this schema:
{{
  "title": "Story Title",
  "genre": "Genre Name",
  "hook_headline": "VIRAL HOOK IN 4 WORDS",
  "scenes": [
    {{
      "scene_number": 1,
      "title": "BEAT TITLE",
      "narration": "Verbatim spoken words (20-25 words)",
      "speaker": "narrator",
      "speaker_name": "Narrator",
      "speaker_avatar": "🎙️",
      "sfx": "whoosh",
      "camera_style": "smooth-zoom-in",
      "image_prompt": "3D Pixar animation prompt..."
    }},
    ... (exactly 5 scenes covering Hook, Journey, Crisis, Rescue, Cliffhanger)
  ]
}}"""
        resp = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=dict(response_mime_type="application/json")
        )
        data = json.loads(resp.text)
        if "scenes" in data and len(data["scenes"]) == 5:
            print(f"✨ [Gemini AI] Dynamically invented fresh viral story: '{data['title']}'")
            return data
    except Exception as e:
        print(f"Notice: Gemini dynamic generation fallback ({e})")

    return None


def get_next_dynamic_story() -> dict:
    """
    Returns the next dynamic story without any manual file uploads:
    1. Tries Gemini AI for an infinite, novel concept.
    2. Cycles seamlessly through the procedural viral story universe.
    """
    history = load_topic_history()
    ep_count = history.get("episode_count", 0) + 1
    used_topics = history.get("generated_topics", [])

    # 1. Try Gemini AI dynamic creation
    dynamic_story = generate_gemini_dynamic_story(ep_count)
    if not dynamic_story:
        # 2. Procedural story selection
        idx = (ep_count - 1) % len(PROCEDURAL_STORIES)
        dynamic_story = PROCEDURAL_STORIES[idx].copy()

    dynamic_story["episode"] = ep_count
    dynamic_story["chapter"] = f"Episode {ep_count}: {dynamic_story['title']}"

    # Generate image paths for each scene
    for s in dynamic_story["scenes"]:
        s_num = s["scene_number"]
        s["image_url"] = f"images/ep_{ep_count}_scene_{s_num}.jpg"

    return dynamic_story
