"""
Stage 1: Viral Topic & Shocking Curiosity Hook Generator.
Generates unique, high-retention viral concepts:
- "What happens if..." bizarre human & cosmic scenarios
- Mind-bending science & nature paradoxes
- Shocking historical & prehistoric discoveries
Ensures 100% uniqueness by tracking history and avoiding duplicates.
"""

import json
import os
import random
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = BASE_DIR / "story_pipeline" / "story_history.json"

# Extensive Curated Pool of High-CTR "What If" & Shocking Curiosity Topics
VIRAL_TOPIC_POOL = [
    {
        "topic": "What happens if you never stop peeing forever?",
        "hook_premise": "If your body started peeing continuously without stopping, you would lose 1 liter of vital electrolytes every 40 minutes.",
        "category": "Human Biology Extreme",
        "style": "3D Pixar medical animation",
    },
    {
        "topic": "What if aliens land on Earth tomorrow?",
        "hook_premise": "If an alien armada entered Earth's atmosphere tomorrow, governments wouldn't call the military first—they would immediately shut down the global internet.",
        "category": "Sci-Fi / Global Event",
        "style": "Cinematic sci-fi Unreal Engine 5",
    },
    {
        "topic": "Dinosaurs never actually roared like in Jurassic Park",
        "hook_premise": "Everything movies taught you about the T-Rex is wrong. Dinosaurs couldn't roar—they produced deep, vibrating sub-bass purrs that liquefied prey from inside.",
        "category": "Mind-Blowing Prehistoric Facts",
        "style": "3D photorealistic cinematic prehistoric",
    },
    {
        "topic": "What happens if Earth stops spinning for just 5 seconds?",
        "hook_premise": "If the Earth halted its rotation for just five seconds, everything not bolted to bedrock would instantly fly eastward at 1,000 miles per hour.",
        "category": "Cosmic Catastrophe",
        "style": "Cinematic 3D disaster simulation",
    },
    {
        "topic": "What happens if you fall into an abandoned gold mine?",
        "hook_premise": "Deep inside forgotten 1800s gold mines lies a silent, invisible killer that can suffocate you in less than 3 breaths before you even smell it.",
        "category": "Survival Thriller",
        "style": "Cinematic 3D underground suspense",
    },
    {
        "topic": "What if the Moon was replaced by Saturn?",
        "hook_premise": "If Saturn took the Moon's orbit tonight, the sky would be filled with colossal golden rings—before catastrophic tidal forces ripped Earth's crust in half.",
        "category": "Space / Cosmic Paradox",
        "style": "3D Pixar cosmic spectacle",
    },
    {
        "topic": "What happens if you drink boiling lava?",
        "hook_premise": "If you somehow swallowed a single spoonful of boiling molten lava, your mouth wouldn't just burn—the water in your organs would instantly detonate into steam.",
        "category": "Science Extreme",
        "style": "3D Pixar thermal physics simulation",
    },
    {
        "topic": "The immortal jellyfish that can live forever",
        "hook_premise": "There is a creature swimming in our oceans right now that has figured out how to cheat death by hitting a biological rewind button whenever it gets old.",
        "category": "Wild Nature Secrets",
        "style": "Bioluminescent 3D Pixar ocean",
    },
]


def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            if "used_topics" not in data and "generated_topics" in data:
                data["used_topics"] = list(data["generated_topics"])
            return data
        except Exception:
            pass
    return {"episode_count": 0, "used_topics": []}


def save_history(history: dict):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def generate_unique_viral_topic() -> dict:
    """
    Generates a unique, high-CTR viral topic:
    1. Attempts dynamic generation via Gemini AI if available.
    2. Falls back to the curated pool, guaranteeing zero repeats.
    """
    history = load_history()
    used_topics = set(history.get("used_topics", []))
    ep_count = history.get("episode_count", 0) + 1

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)

            prompt = f"""Generate ONE unique, viral, mind-blowing YouTube Shorts topic.
Examples: 'What happens if you never stop peeing forever?', 'What if aliens land tomorrow?', 'T-Rex actually purred like birds'.
Must be high-curiosity, shocking, and impossible to scroll past.
Already used topics: {list(used_topics)[-20:]}
Return JSON format ONLY:
{{
  "topic": "Shocking title as a question or paradox",
  "hook_premise": "The shocking premise in 1 sentence",
  "category": "Category name",
  "style": "Visual style description (e.g. 3D Pixar animation / Unreal Engine 5)"
}}"""
            res = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=dict(response_mime_type="application/json")
            )
            data = json.loads(res.text)
            if data.get("topic") and data["topic"] not in used_topics:
                data["episode"] = ep_count
                used_topics.add(data["topic"])
                history["used_topics"] = list(used_topics)
                history["episode_count"] = ep_count
                save_history(history)
                print(f"💡 [Stage 1: Topic Engine] Generated AI Topic #{ep_count}: '{data['topic']}'")
                return data
        except Exception as e:
            print(f"Notice: Gemini topic generation note: {e}")

    # Fallback to curated pool
    available = [t for t in VIRAL_TOPIC_POOL if t["topic"] not in used_topics]
    if not available:
        # Reset if exhausted
        available = VIRAL_TOPIC_POOL
        used_topics.clear()

    chosen = random.choice(available).copy()
    chosen["episode"] = ep_count
    used_topics.add(chosen["topic"])
    history["used_topics"] = list(used_topics)
    history["episode_count"] = ep_count
    save_history(history)

    print(f"💡 [Stage 1: Topic Engine] Selected Unique Topic #{ep_count}: '{chosen['topic']}'")
    return chosen


if __name__ == "__main__":
    t = generate_unique_viral_topic()
    print(json.dumps(t, indent=2))
