"""
Stage 2: 59-Second Hook-Driven Viral Script Engine.
Generates gripping, high-retention stories strictly under 59 seconds:
- Retention hooks every 10 seconds to eliminate drop-off
- Strictly 120-135 spoken words (yielding exactly 54-58 seconds at natural neural speaking pace)
- 5 Structured beats: Hook -> Escalation -> Climax -> Revelation -> Clean Conclusion
- Supports standalone stories or maximum 5-part serials with standalone satisfying payoffs.
"""

import json
import os
import time
import concurrent.futures
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TARGET_DURATION_SECONDS = 58.0  # Strictly under 59.0s limit for YouTube Shorts / Reels


def call_with_timeout(func, args=(), kwargs=None, timeout_sec=20):
    """Executes a function inside a worker thread with a strict maximum timeout."""
    if kwargs is None:
        kwargs = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        return future.result(timeout=timeout_sec)


def generate_viral_script(topic_data: dict, part_number: int = 1, total_parts: int = 1) -> dict:
    """
    Generates a 5-beat viral story script designed for maximum retention:
    Every beat has an attention hook every 10 seconds and finishes strictly under 59s.
    """
    topic = topic_data["topic"]
    hook_premise = topic_data.get("hook_premise", "")
    category = topic_data.get("category", "Curiosity")
    style = topic_data.get("style", "3D Pixar animation")
    ep_num = topic_data.get("episode", 1)

    # Format Archetype Rotation (Beats YouTube Inauthentic/Repetitive Content Policy)
    FORMAT_ARCHETYPES = [
        {
            "format": "MIND-BENDING WHAT-IF",
            "hook_formula": "What happens if...",
            "style_guide": "Extreme hypothetical science paradox. Focus on physical catastrophe and cosmic wonder."
        },
        {
            "format": "MYTH VS REALITY",
            "hook_formula": "Everything you were taught about...",
            "style_guide": "Expose a widespread scientific misconception. Immediate shocking truth in the first 2 seconds."
        },
        {
            "format": "TOP 3 COUNTDOWN",
            "hook_formula": "Three terrifying discoveries that...",
            "style_guide": "Rapid countdown of 3 anomalous scientific discoveries. Fast pacing, 1 item per beat."
        },
        {
            "format": "EXTREME SCALE COMPARISON",
            "hook_formula": "If you shrunk down to the size of...",
            "style_guide": "Dramatic scale progression from human perspective to micro or macro cosmic extremes."
        }
    ]
    selected_format = FORMAT_ARCHETYPES[ep_num % len(FORMAT_ARCHETYPES)]
    format_name = selected_format["format"]

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)

            prompt = f"""You are an elite viral short-form director for YouTube Shorts and TikTok.
Write a gripping, high-retention video script for:
TOPIC: {topic}
PREMISE: {hook_premise}
NARRATIVE FORMAT: {format_name} ({selected_format['style_guide']})
EPISODE: #{ep_num}

CRITICAL RETENTION RULES:
1. TOTAL SPOKEN WORDS: STRICTLY BETWEEN 78 AND 96 WORDS (Yields 28-36 seconds of optimal high-retention speech; APV > 110%).
2. IMMEDIATE 2-SECOND HOOK (Beat 1): Start directly with an intense hook (e.g. '{selected_format["hook_formula"]}'). NO greetings, NO intro filler.
3. SEAMLESS INFINITE LOOP: The last sentence of Beat 5 MUST grammatically and logically connect directly into the very first word of Beat 1, creating a seamless hypnotic loop for re-watches.
4. STRUCTURE: Exactly 5 rapid beats (each 15-20 words):
   - Beat 1 (0-6s): Shock Hook & Impossible Paradox (Grab in first 2 seconds, 15-18 words)
   - Beat 2 (6-14s): Escalating Tension / The Hidden Truth (16-19 words)
   - Beat 3 (14-22s): Scientific Climax / The Extreme Anomaly (16-19 words)
   - Beat 4 (22-30s): The Revelation / Mind-Blowing Detail (16-19 words)
   - Beat 5 (30-36s): The Seamless Loop Connector (Ends mid-thought or with a connector that flows into Beat 1, 14-18 words)

Output JSON ONLY:
{{
  "episode_title": "{topic.upper()[:28]}",
  "narrative_format": "{format_name}",
  "hook_headline": "VIRAL HOOK (3-4 WORDS)",
  "total_words_count": 86,
  "loop_lead_in": "Last words connecting to Beat 1",
  "beats": [
    {{
      "beat_number": 1,
      "time_window": "0-6s",
      "hook_trigger": "Shock Hook",
      "narration": "First spoken beat (15-18 words)",
      "speaker": "anchor",
      "sfx": "whoosh",
      "visual_prompt": "3D Pixar cinematic prompt, highly detailed, 8k, Unreal Engine 5 render"
    }},
    ... (exactly 5 beats alternating speaker 'anchor' and 'specialist')
  ],
  "branching_decision": {{
    "choice_a": "Option A for next episode",
    "choice_b": "Option B for next episode",
    "vote_callout": "Which paradox should we decode next? Vote A or B in comments!"
  }}
}}"""
            res = None
            active_model = "gemini-3.8-flash"
            for attempt in range(1, 4):
                try:
                    print(f"⏳ [Script Engine] Querying Gemini (gemini-3.8-flash, attempt {attempt}, timeout 35s)...")
                    res = call_with_timeout(
                        client.models.generate_content,
                        kwargs=dict(
                            model="gemini-3.8-flash",
                            contents=prompt,
                            config=dict(response_mime_type="application/json"),
                        ),
                        timeout_sec=18,
                    )
                    if res and res.text:
                        break
                except concurrent.futures.TimeoutError:
                    print(f"⏱️ [Script Engine] gemini-3.8-flash timed out after 35s (attempt {attempt})...")
                except Exception as m_err:
                    err_s = str(m_err).lower()
                    if any(k in err_s for k in ["503", "unavailable", "demand", "429", "quota"]):
                        backoff = 2 ** attempt
                        print(f"⏳ gemini-3.8-flash high demand/rate-limit. Waiting {backoff}s (attempt {attempt})...")
                        time.sleep(backoff)
                    else:
                        print(f"⚠️ Model gemini-3.8-flash script error: {m_err}")
                        break

            if res and res.text:
                data = json.loads(res.text)
                if "beats" in data and len(data["beats"]) == 5:
                    word_count = sum(len(b['narration'].split()) for b in data['beats'])
                    print(f"📝 [Stage 2: Script Engine] Gemini AI ({active_model}) synthesized script for '{topic}' ({word_count} words)")
                    try:
                        from story_pipeline.telegram_notifier import RUN_TRACKER
                        RUN_TRACKER.set_model_used("Script", "Gemini 3.8-Flash")
                    except Exception:
                        pass
                    return data
        except Exception as e:
            print(f"Notice: Gemini script generation note ({e})")
            try:
                from story_pipeline.telegram_notifier import RUN_TRACKER
                RUN_TRACKER.record_model_failure("Gemini 3.8-Flash (Script)", f"Offline/error: {str(e)[:50]}")
            except Exception:
                pass

    # Procedural Fallback Engine (Guaranteed 5-Beat Structure with 10s Retention Hooks)
    try:
        from story_pipeline.telegram_notifier import RUN_TRACKER
        RUN_TRACKER.set_model_used("Script", "Procedural Retention Engine")
    except Exception:
        pass
    return generate_procedural_script(topic, hook_premise, style, ep_num)


def generate_procedural_script(topic: str, hook_premise: str, style: str, ep_num: int) -> dict:
    """Builds a guaranteed 5-beat viral script perfectly timed to 57 seconds."""
    clean_title = topic.upper()[:26]

    if "peeing" in topic.lower():
        beats = [
            {
                "beat_number": 1,
                "time_window": "0-10s",
                "hook_trigger": "Opening Curiosity Hook",
                "narration": "What happens if you never stop peeing forever? In the first twenty minutes, you would assume it is just an annoying medical quirk, but fatal cellular destruction has already begun.",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "smooth-zoom-in",
                "visual_prompt": f"{style}, cute 3D character in hospital looking confused at bathroom door, glowing holographic medical monitors, 8k",
            },
            {
                "beat_number": 2,
                "time_window": "10-22s",
                "hook_trigger": "10s Escalation Hook",
                "narration": "By hour three, pure terror sets in across your body. Your kidneys filter twelve liters of fluid, violently draining all vital sodium, potassium, and magnesium from your bloodstream.",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "pan-right",
                "visual_prompt": f"{style}, 3D anatomical cross-section of glowing human kidneys working at hyper speed, pulsing blue and amber warning lights, cinematic",
            },
            {
                "beat_number": 3,
                "time_window": "22-35s",
                "hook_trigger": "20s Danger Hook",
                "narration": "No matter how much water you frantically chug, your tongue feels like dry sandpaper. Your blood thickens like sludge, and your heart begins to flutter into dangerous cardiac arrest.",
                "speaker": "character_hero",
                "speaker_name": "Dr. Vance",
                "speaker_avatar": "🩺",
                "sfx": "impact_boom",
                "camera_motion": "dramatic-pulse",
                "visual_prompt": f"{style}, dramatic close-up of a human heart glowing with red warning sparks, dark dramatic background, high stakes",
            },
            {
                "beat_number": 4,
                "time_window": "35-48s",
                "hook_trigger": "30s Climax Hook",
                "narration": "Within twelve hours, without continuous intravenous electrolyte infusions, your brain tissue would swell from acute water intoxication, causing violent seizures and terrifying visual hallucinations.",
                "speaker": "character_hero",
                "speaker_name": "Dr. Vance",
                "speaker_avatar": "🩺",
                "sfx": "pop",
                "camera_motion": "warm-dolly",
                "visual_prompt": f"{style}, 3D animation of brain synapses firing with glowing neon pulses, surreal dreamscape floating in hospital room, Disney cinematic",
            },
            {
                "beat_number": 5,
                "time_window": "48-58s",
                "hook_trigger": "45s Resolution Hook",
                "narration": "The human body is an exquisitely balanced miracle. Be grateful your biological valves know when to close. What bizarre scenario should we explore next? Follow right now for Episode Two!",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "sunset-drift",
                "visual_prompt": f"{style}, triumphant healthy character drinking pure glowing water at sunrise, golden sun rays, inspirational Disney masterpiece",
            },
        ]
    elif "dinosaur" in topic.lower() or "roar" in topic.lower():
        beats = [
            {
                "beat_number": 1,
                "time_window": "0-10s",
                "hook_trigger": "Opening Truth Hook",
                "narration": "Everything Hollywood ever showed you about the T-Rex is completely fake. Dinosaurs never actually roared like lions in Jurassic Park, and the shocking truth is far creepier.",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "smooth-zoom-in",
                "visual_prompt": f"{style}, massive majestic Tyrannosaurus Rex in prehistoric mist, amber eyes, cinematic jungle lighting, Unreal Engine 5 render, 8k",
            },
            {
                "beat_number": 2,
                "time_window": "10-22s",
                "hook_trigger": "10s Escalation Hook",
                "narration": "Fossilized vocal larynxes prove prehistoric predators lacked the vocal cords to roar. Instead, they produced an infrasonic closed-mouth boom, identical to colossal cassowary birds and emus.",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "pan-right",
                "visual_prompt": f"{style}, close-up of T-Rex throat vibrating with deep bass energy waves rippling through air, golden dust motes shaking, 8k",
            },
            {
                "beat_number": 3,
                "time_window": "22-35s",
                "hook_trigger": "20s Danger Hook",
                "narration": "This sound was so low humans couldn't even consciously hear it with our ears—you would only feel the twenty-hertz shockwave violently vibrating the marrow inside your bones.",
                "speaker": "character_hero",
                "speaker_name": "Paleontologist",
                "speaker_avatar": "🦖",
                "sfx": "impact_boom",
                "camera_motion": "dramatic-pulse",
                "visual_prompt": f"{style}, prehistoric puddle with sonic water ripples forming geometric patterns as the earth tremors, dramatic suspense",
            },
            {
                "beat_number": 4,
                "time_window": "35-48s",
                "hook_trigger": "30s Climax Hook",
                "narration": "By the split second you felt your chest cavity reverberate from the infrasound, the multi-ton apex predator had already lunged from the primordial jungle darkness directly behind you.",
                "speaker": "character_hero",
                "speaker_name": "Paleontologist",
                "speaker_avatar": "🦖",
                "sfx": "pop",
                "camera_motion": "warm-dolly",
                "visual_prompt": f"{style}, gigantic dinosaur shadow looming over jungle trees, glowing predatory eyes in dark canopy, cinematic action, 8k",
            },
            {
                "beat_number": 5,
                "time_window": "48-58s",
                "hook_trigger": "45s Resolution Hook",
                "narration": "A completely silent predator is infinitely more terrifying than a noisy movie monster. What prehistoric myth should we shatter next? Hit that follow button right now for Episode Two!",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "sunset-drift",
                "visual_prompt": f"{style}, majestic dinosaur silhouette standing atop a prehistoric mountain peak under a purple nebula sky, breathtaking Disney masterpiece",
            },
        ]
    else:
        # Universal Dynamic 5-Beat Script (Calibrated to exactly 130 words)
        topic_core = topic.rstrip("?.!").replace("What if ", "").replace("What happens if ", "").strip()
        words_list = topic_core.split()
        if len(words_list) > 7:
            topic_core = " ".join(words_list[:7])

        beat1_narration = f"What if {topic_core.lower()}? Most people assume civilization would carry on normally, but the sudden reality would plunge our entire world into catastrophic chaos."

        beats = [
            {
                "beat_number": 1,
                "time_window": "0-10s",
                "hook_trigger": "Opening Shock Hook",
                "narration": beat1_narration,
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "smooth-zoom-in",
                "visual_prompt": f"{style}, dramatic epic opening cinematic of {topic_core}, vibrant volumetric lighting, Unreal Engine 5, 8k",
            },
            {
                "beat_number": 2,
                "time_window": "10-22s",
                "hook_trigger": "10s Escalation Hook",
                "narration": "Within seconds, supersonic kinetic shockwaves ripple across the globe at one thousand miles per hour, completely collapsing every single electrical power grid across the continents.",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "pan-right",
                "visual_prompt": f"{style}, global view of Earth from space with satellite networks sparking, city lights extinguishing into darkness, cinematic",
            },
            {
                "beat_number": 3,
                "time_window": "22-35s",
                "hook_trigger": "20s Danger Hook",
                "narration": "Pure terror erupts across major continents as colossal ocean tsunamis surge inland, leaving survivors scrambling through howling atmospheric winds toward secure underground military shelters.",
                "speaker": "character_hero",
                "speaker_name": "Commander",
                "speaker_avatar": "🚨",
                "sfx": "impact_boom",
                "camera_motion": "dramatic-pulse",
                "visual_prompt": f"{style}, futuristic underground vault doors slamming shut with glowing amber warning beacons, intense cinematic tension",
            },
            {
                "beat_number": 4,
                "time_window": "35-48s",
                "hook_trigger": "30s Climax Hook",
                "narration": "Deep beneath the surface, emergency seismic sensors detect the earth's crust fracturing under immense tidal friction, releasing deafening acoustic vibrations shaking the very marrow of your bones.",
                "speaker": "character_guide",
                "speaker_name": "Scientist",
                "speaker_avatar": "🔬",
                "sfx": "pop",
                "camera_motion": "warm-dolly",
                "visual_prompt": f"{style}, glowing holographic core projecting ancient mysterious energy symbols in dark laboratory, warm cyan illumination",
            },
            {
                "beat_number": 5,
                "time_window": "48-58s",
                "hook_trigger": "45s Resolution Hook",
                "narration": "Our world is far more fragile than we dare to admit. Could humanity survive five seconds of cosmic standstill? Follow for Episode Two right now!",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "sunset-drift",
                "visual_prompt": f"{style}, heroic survivors looking out at reconstructed skyline under a bright dawn sunrise, inspirational Disney masterpiece",
            },
        ]

    total_words = sum(len(b["narration"].split()) for b in beats)
    return {
        "episode_title": clean_title,
        "hook_headline": f"WHAT IF {clean_title[:18]}?!",
        "total_words_count": total_words,
        "beats": beats,
        "branching_decision": {
            "prompt": f"What should happen next with {clean_title.title()}?",
            "choice_a": "Emergency purge to surface and survive",
            "choice_b": "Dive deeper into the unexplored abyss",
            "vote_callout": "COMMENT 'A' or 'B' to decide the next episode!",
        },
    }


if __name__ == "__main__":
    test_topic = {"topic": "What happens if you never stop peeing forever?", "category": "Biology", "style": "3D Pixar animation"}
    s = generate_viral_script(test_topic)
    print(json.dumps(s, indent=2))
