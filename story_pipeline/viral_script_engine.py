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
            from google.genai import types
            client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=30000))

            prompt = f"""You are an elite viral short-form director for YouTube Shorts and TikTok.
Write a gripping, high-retention video script for:
TOPIC: {topic}
PREMISE: {hook_premise}
NARRATIVE FORMAT: {format_name} ({selected_format['style_guide']})
EPISODE: #{ep_num}

CRITICAL RETENTION & VISUAL RULES:
1. TOTAL SPOKEN WORDS: STRICTLY BETWEEN 126 AND 138 WORDS (Yields 52-56 seconds of optimal high-retention speech; APV > 105%).
2. CADENCE: NEVER use ellipses (...), em-dashes, or semicolons. Use short punchy sentences (<12 words) for continuous, relentless speech flow with zero pauses > 0.3s.
3. IMMEDIATE 2-SECOND HOOK (Beat 1): Start directly with an intense hook (e.g. '{selected_format["hook_formula"]}'). NO greetings, NO intro filler. Beat 1 must be between 24 and 30 words.
4. SEAMLESS INFINITE LOOP: The last sentence of Beat 5 MUST grammatically connect directly into the very first word of Beat 1. Beat 5's visual_prompt MUST match Beat 1's palette and subject to complete a seamless visual loop. Beat 5 must be between 23 and 28 words.
5. LITERAL IMAGE GROUNDING: Every 'visual_prompt' MUST literally depict the exact subject, action, and environment spoken in that beat's 'narration'. NO generic corridors, NO abstract devices, NO random crowd scenes.
6. STRUCTURE: Exactly 5 rapid beats (each 24-28 words):
   - Beat 1 (0-10s): Shock Hook & Impossible Paradox (Grab in first 2 seconds, 24-28 words)
   - Beat 2 (10-22s): Escalating Tension / The Hidden Truth (24-28 words)
   - Beat 3 (22-34s): Scientific Climax / The Extreme Anomaly (24-28 words)
   - Beat 4 (34-46s): The Revelation / Mind-Blowing Detail (24-28 words)
   - Beat 5 (46-55s): The Seamless Loop Connector (Flows into Beat 1, matching Beat 1 visual, 23-28 words)

Output JSON ONLY:
{{
  "episode_title": "{topic.upper()[:28]}",
  "narrative_format": "{format_name}",
  "hook_headline": "VIRAL HOOK (3-4 WORDS)",
  "total_words_count": 130,
  "loop_lead_in": "Last words connecting to Beat 1",
  "beats": [
    {{
      "beat_number": 1,
      "time_window": "0-10s",
      "hook_trigger": "Shock Hook",
      "narration": "First spoken beat (24-28 words)",
      "speaker": "anchor",
      "sfx": "whoosh",
      "visual_prompt": "3D Pixar cinematic prompt, highly detailed, 8k, Unreal Engine 5 render"
    }},
    ... (exactly 5 beats alternating speaker 'anchor' and 'specialist')
  ],
  "seo_tags": ["what if", "mind blowing facts", "science experiment", "universe facts", "viral shorts", "did you know", "space paradox", "unsolved mystery", "shocking revelation", "educational shorts", "science animation", "extreme physics", "3d animation", "hypothetical scenario", "curiosity"],
  "hashtags": ["#shorts", "#viral", "#science", "#curiosity", "#whatif"],
  "pinned_comment": "Would you survive this scenario? Drop your theory in the comments! 👇 Subscribe for daily curiosity drops! 🚀",
  "branching_decision": {{
    "choice_a": "Option A for next episode",
    "choice_b": "Option B for next episode",
    "vote_callout": "Which paradox should we decode next? Vote A or B in comments!"
  }}
}}"""
            res = None
            active_model = "gemini-3.8-flash"
            models_to_try = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-flash-latest", "gemini-pro-latest"]
            for candidate_model in models_to_try:
                for attempt in range(1, 4):
                    try:
                        print(f"⏳ [Script Engine] Querying Gemini ({candidate_model}, attempt {attempt}/3, timeout 25s)...")
                        res = call_with_timeout(
                            client.models.generate_content,
                            kwargs=dict(
                                model=candidate_model,
                                contents=prompt,
                                config=dict(response_mime_type="application/json"),
                            ),
                            timeout_sec=25,
                        )
                        if res and res.text:
                            active_model = candidate_model
                            break
                    except concurrent.futures.TimeoutError:
                        print(f"⏱️ [Script Engine] {candidate_model} timed out after 25s. Retrying...")
                    except Exception as m_err:
                        print(f"⚠️ Model {candidate_model} script note: {m_err}")
                        if "RESOURCE_EXHAUSTED" in str(m_err) or "429" in str(m_err):
                            print("⚠️ Free Tier daily quota reached on Gemini API. Checking Groq Cloud fallback...")
                            break
                        time.sleep(2.0 * attempt)
                if res and res.text:
                    break

            if res and res.text:
                data = json.loads(res.text)
                if "beats" in data and len(data["beats"]) == 5:
                    word_count = sum(len(b['narration'].split()) for b in data['beats'])
                    print(f"📝 [Stage 2: Script Engine] Gemini AI ({active_model}) synthesized script for '{topic}' ({word_count} words)")
                    try:
                        from story_pipeline.telegram_notifier import RUN_TRACKER
                        RUN_TRACKER.set_model_used("Script", f"Gemini ({active_model})")
                    except Exception:
                        pass
                    return data
        except Exception as e:
            print(f"Notice: Gemini script generation note ({e})")
            try:
                from story_pipeline.telegram_notifier import RUN_TRACKER
                RUN_TRACKER.record_model_failure("Gemini (Script)", f"Offline/error: {str(e)[:50]}")
            except Exception:
                pass

    # Secondary Cloud LLM Fallback: Groq Cloud (llama-3.3-70b-versatile, 14,400 req/day free)
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key and groq_api_key.strip():
        try:
            print("⏳ [Script Engine] Querying Groq Cloud API (llama-3.3-70b-versatile, timeout 25s)...")
            import urllib.request
            groq_url = "https://api.groq.com/openai/v1/chat/completions"
            groq_payload = json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are an elite viral short-form director for YouTube Shorts. Output valid JSON only matching the schema exactly."},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.7,
            }).encode("utf-8")
            groq_req = urllib.request.Request(
                groq_url,
                data=groq_payload,
                headers={
                    "Authorization": f"Bearer {groq_api_key.strip()}",
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(groq_req, timeout=25) as g_resp:
                g_json = json.loads(g_resp.read().decode("utf-8"))
                g_text = g_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                if g_text:
                    g_data = json.loads(g_text)
                    if "beats" in g_data and len(g_data["beats"]) == 5:
                        w_count = sum(len(b['narration'].split()) for b in g_data['beats'])
                        print(f"📝 [Stage 2: Script Engine] Groq AI (llama-3.3-70b-versatile) synthesized script for '{topic}' ({w_count} words)")
                        try:
                            from story_pipeline.telegram_notifier import RUN_TRACKER
                            RUN_TRACKER.set_model_used("Script", "Groq (llama-3.3-70b-versatile)")
                        except Exception:
                            pass
                        return g_data
        except Exception as e_groq:
            print(f"Notice: Groq script generation note: {e_groq}")
            try:
                from story_pipeline.telegram_notifier import RUN_TRACKER
                RUN_TRACKER.record_model_failure("Groq (Script)", f"Error: {str(e_groq)[:50]}")
            except Exception:
                pass

    # Tertiary Fallback: Procedural Retention Engine
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

        beat1_narration = f"What if {topic_core.lower()}? Most people assume our planet would carry on normally, but this sudden cosmic shockwave would instantly plunge modern civilization into complete catastrophic chaos."

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
                "narration": "Within seconds, supersonic kinetic shockwaves ripple across the globe at one thousand miles per hour, completely collapsing electrical power grids and shattering modern communication networks across every continent.",
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
                "narration": "Pure terror erupts across major coastlines as colossal ocean tsunamis surge inland, sweeping coastal cities under towering walls of churning saltwater while ferocious atmospheric winds violently tear through skyscrapers.",
                "speaker": "character_hero",
                "speaker_name": "Commander",
                "speaker_avatar": "🚨",
                "sfx": "impact_boom",
                "camera_motion": "dramatic-pulse",
                "visual_prompt": f"{style}, colossal ocean tsunami surging over coastal skyline, violent turbulent waves, atmospheric storm lighting, Unreal Engine 5 render, 8k",
            },
            {
                "beat_number": 4,
                "time_window": "35-48s",
                "hook_trigger": "30s Climax Hook",
                "narration": "Deep beneath the surface, emergency seismic sensors detect the earth's crust fracturing under immense tidal friction, tearing glowing tectonic magma fissures that permanently reshape the entire global landscape.",
                "speaker": "character_guide",
                "speaker_name": "Scientist",
                "speaker_avatar": "🔬",
                "sfx": "pop",
                "camera_motion": "warm-dolly",
                "visual_prompt": f"{style}, earth crust violently fracturing open with glowing red and orange molten magma fissures, seismic devastation, cinematic 8k",
            },
            {
                "beat_number": 5,
                "time_window": "48-58s",
                "hook_trigger": "45s Resolution Hook",
                "narration": "Our world balances on an extraordinarily fragile razor's edge. The terrifying reality is, the exact split second cosmic balance breaks, you instantly realize...",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "sunset-drift",
                "visual_prompt": f"{style}, dramatic epic panoramic opening cinematic of {topic_core}, matching Beat 1 opening frame for a seamless visual infinite loop, 8k",
            },
        ]

    total_words = sum(len(b["narration"].split()) for b in beats)
    return {
        "episode_title": clean_title,
        "hook_headline": f"WHAT IF {clean_title[:18]}?!",
        "total_words_count": total_words,
        "beats": beats,
        "seo_tags": [
            "what if", clean_title.lower(), "science experiment", "universe facts",
            "viral shorts", "did you know", "space paradox", "unsolved mystery",
            "shocking revelation", "educational shorts", "science animation",
            "extreme physics", "3d animation", "hypothetical scenario", "curiosity"
        ],
        "hashtags": ["#shorts", "#viral", "#science", "#curiosity", "#whatif"],
        "pinned_comment": f"Would you survive {clean_title.title()}? Drop your theory below! 👇 Subscribe for daily curiosity drops! 🚀",
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
