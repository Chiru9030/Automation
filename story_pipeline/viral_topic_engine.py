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
import time
import concurrent.futures
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = BASE_DIR / "story_pipeline" / "story_history.json"


def call_with_timeout(func, args=(), kwargs=None, timeout_sec=15):
    """Executes a function inside a worker thread with a strict maximum timeout."""
    if kwargs is None:
        kwargs = {}
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    try:
        future = executor.submit(func, *args, **kwargs)
        return future.result(timeout=timeout_sec)
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

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
    {
        "topic": "What if you fell into Jupiter's atmosphere?",
        "hook_premise": "If you jumped into Jupiter's storm clouds, you would fall for thousands of miles through crushing diamond hail before liquid metallic hydrogen dissolved you.",
        "category": "Space Extreme",
        "style": "3D Pixar cosmic storm simulation",
    },
    {
        "topic": "What happens if a nuclear submarine sinks to Mariana Trench?",
        "hook_premise": "At 36,000 feet beneath the waves, the water pressure is so intense that a titanium submarine hull would crumple inward in less than two milliseconds.",
        "category": "Deep Sea Thriller",
        "style": "Cinematic 3D deep sea pressure simulation",
    },
    {
        "topic": "The sound of the Sun would be deafening if sound traveled in space",
        "hook_premise": "If space had an atmosphere, the nuclear fusion roaring on the Sun's surface would reach Earth at 130 decibels—the deafening roar of a jet engine right next to your ear.",
        "category": "Cosmic Paradox",
        "style": "3D Pixar solar flare animation",
    },
    {
        "topic": "What if oxygen disappeared from Earth for 5 seconds?",
        "hook_premise": "If oxygen vanished for five seconds, the sky would turn pitch black, every concrete building would crumble to dust, and the daytime sun would burn your skin instantly.",
        "category": "Catastrophe Simulation",
        "style": "Cinematic 3D disaster animation",
    },
    {
        "topic": "The terrifying secret behind sleep paralysis demons",
        "hook_premise": "When your brain wakes up before your motor cortex, your amygdala floods your vision with terrifying shadow figures that feel 100% physically present in your room.",
        "category": "Neuroscience Thriller",
        "style": "3D Pixar neuroscience shadow simulation",
    },
    {
        "topic": "What happens if you never sleep for 11 straight days?",
        "hook_premise": "After 72 hours without sleep, your brain cells begin literally consuming their own synapses in a desperate bid to clear toxic waste proteins.",
        "category": "Human Biology Extreme",
        "style": "3D Pixar medical cellular animation",
    },
    {
        "topic": "What if gravity suddenly doubled across the entire world?",
        "hook_premise": "If Earth's gravity doubled this second, you would instantly collapse under your own weight, bridges would snap, and birds would plummet out of the sky.",
        "category": "Physics Paradox",
        "style": "Cinematic 3D gravity physics simulation",
    },
    {
        "topic": "The secret Soviet borehole that dug 40,000 feet into Earth",
        "hook_premise": "Deep beneath Russia lies a 9-inch metal cap covering the deepest hole humans ever dug, where temperatures reached 356 degrees and the rock flowed like plastic.",
        "category": "Historical Mystery",
        "style": "Cinematic 3D underground borehole render",
    },
    {
        "topic": "What happens if an asteroid the size of a coin hit Earth at lightspeed?",
        "hook_premise": "A single copper penny traveling at 99.99% the speed of light carries enough kinetic energy to vaporize an entire metropolis in a blinding nuclear fireball.",
        "category": "Astrophysics Extreme",
        "style": "Cinematic 3D particle impact simulation",
    },
    {
        "topic": "What lies beneath Antarctica's 2-mile thick ice sheet?",
        "hook_premise": "Trapped beneath two miles of Antarctic ice are prehistoric subterranean lakes that have been completely sealed from Earth's atmosphere for 15 million years.",
        "category": "Earth Mysteries",
        "style": "3D Pixar glacial cavern render",
    },
    {
        "topic": "The ancient monster that hunted Megalodons for breakfast",
        "hook_premise": "Livyatan Melvillei was a prehistoric sperm whale with 14-inch teeth that actively wrestled and hunted giant Megalodon sharks in primordial oceans.",
        "category": "Prehistoric Beasts",
        "style": "Cinematic 3D ocean monster battle",
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
        api_key = api_key.strip().strip("'").strip('"')
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=12000))

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
            res = None
            active_model = "gemini-3.8-flash"
            models_to_try = ["gemini-3.8-flash"]
            for candidate_model in models_to_try:
                try:
                    print(f"⏳ [Topic Engine] Querying Gemini ({candidate_model}, timeout 12s)...")
                    res = call_with_timeout(
                        client.models.generate_content,
                        kwargs=dict(
                            model=candidate_model,
                            contents=prompt,
                            config=dict(response_mime_type="application/json"),
                        ),
                        timeout_sec=12,
                    )
                    if res and res.text:
                        active_model = candidate_model
                        break
                except concurrent.futures.TimeoutError:
                    print(f"⏱️ [Topic Engine] {candidate_model} timed out after 12s. Trying next candidate...")
                except Exception as m_err:
                    print(f"⚠️ Model {candidate_model} note: {m_err}")

            if res and res.text:
                data = json.loads(res.text)
                if data.get("topic") and data["topic"] not in used_topics:
                    data["episode"] = ep_count
                    used_topics.add(data["topic"])
                    history["used_topics"] = list(used_topics)
                    history["episode_count"] = ep_count
                    save_history(history)
                    print(f"💡 [Stage 1: Topic Engine] Gemini AI ({active_model}) generated Topic #{ep_count}: '{data['topic']}'")
                    try:
                        from story_pipeline.telegram_notifier import RUN_TRACKER
                        RUN_TRACKER.set_model_used("Topic", f"Gemini ({active_model})")
                    except Exception:
                        pass
                    return data
        except Exception as e:
            print(f"Notice: Gemini topic generation note: {e}")
            try:
                from story_pipeline.telegram_notifier import RUN_TRACKER
                RUN_TRACKER.record_model_failure("Gemini (Topic)", f"Offline/timeout: {str(e)[:50]}")
            except Exception:
                pass

    # Fallback to curated pool
    try:
        from story_pipeline.telegram_notifier import RUN_TRACKER
        RUN_TRACKER.set_model_used("Topic", "Curated Viral Pool")
    except Exception:
        pass
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
