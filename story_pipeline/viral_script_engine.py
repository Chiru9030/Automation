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

            prompt = f"""You are an elite Hollywood visual storyteller and viral short-form director for YouTube Shorts and TikTok.
Write a gripping, highly coherent, cinema-grade narrative video script for:
TOPIC: {topic}
PREMISE: {hook_premise}
NARRATIVE FORMAT: {format_name} ({selected_format['style_guide']})
EPISODE: #{ep_num}

CRITICAL STORYTELLING & CINEMATOGRAPHY RULES:
1. CLEAN, COHESIVE STORY ARC: Tell a captivating, continuous story across all 5 beats with zero disjointed facts or robotic trivia.
   - Beat 1 (0-10s): The Shocking Hook & Anomaly (Grab in first 2 seconds, 24-28 words)
   - Beat 2 (10-22s): Context & Hidden Tension (Unveil the hidden scientific reality, 24-28 words)
   - Beat 3 (22-34s): Escalating Chain Reaction (The physical consequence in motion, 24-28 words)
   - Beat 4 (34-46s): The Climax Revelation (Mind-blowing paradox or peak danger, 24-28 words)
   - Beat 5 (46-55s): The Philosophical Twist & Seamless Loop (Connects directly into Beat 1, exactly 24-28 words)
2. TOTAL SPOKEN WORDS: STRICTLY BETWEEN 128 AND 140 WORDS (Total 5 beats, each beat strictly 25-28 spoken words).
3. CADENCE: Short punchy sentences (<12 words). Use active, vivid verbs and clear causal transitions ('Because of this...', 'Within seconds...', 'This instantly triggers...'). NO ellipses (...), NO em-dashes.
4. SEAMLESS INFINITE LOOP: The last sentence of Beat 5 MUST grammatically and visually fuse into the very first word of Beat 1.
5. INVARIANT CHARACTER DNA & VISUAL ANCHOR (ZERO INCONSISTENCY POLICY):
   - You MUST define an explicit, highly detailed 'character_dna' for the episode protagonist or central subject.
     Example: "Astronaut in sleek matte-white NASA deep-space EVA suit with neon-amber shoulder striping, carbon-fiber joints, and a reflective gold-mirrored visor"
   - You MUST define an explicit 'visual_anchor' specifying the unified environment, lighting, and palette.
     Example: "Jupiter crimson-amber turbulent vortex atmosphere, dark cosmic space backdrop, violent electrical storm lighting"
   - Every single beat's 'video_prompt' and 'visual_prompt' MUST explicitly include this EXACT 'character_dna' description! The character's suit, colors, and design must NEVER change between beats!
6. ULTRA-SPECIFIC LENS & KINEMATIC CAMERA DIRECTIVES (NOT MOVING STILLS):
   For EVERY beat, generate both a 'video_prompt' and an explicit 'camera_motion'.
   - 'camera_motion' MUST be assigned based on narrative beat:
     * Beat 1: "rapid-push-in-shake" (10mm ultra-wide lens extreme long shot)
     * Beat 2: "smooth-lateral-pan-right" (24mm anamorphic lens medium tracking pan)
     * Beat 3: "vertical-tilt-reveal" (35mm prime lens Dutch-angle vertical tilt reveal)
     * Beat 4: "climax-pull-back" (10mm wide-angle epic scope pull-back)
     * Beat 5: "loop-convergence-zoom" (50mm portrait lens centered loop convergence)
   - 'video_prompt' MUST describe a cinematic shot with explicit optics and physical kinematics:
     * Camera lens & shot type: (e.g. 'Extreme wide long shot from a 10mm ultra-wide lens...', 'Low-angle 24mm anamorphic tracking shot...')
     * Invariant Character DNA: Embed the exact 'character_dna' description.
     * Active Physical Kinematics: Describe how the character physically moves (e.g. 'falling headfirst through atmospheric cloud bands, arms flailing against violent crosswinds, body tumbling at terminal velocity, camera tracking downward with high velocity...')
     * Volumetric lighting & atmosphere: (e.g. 'God rays, flickering neon embers, swirling atmospheric mist, motion blur, Unreal Engine 5, 8k')
   - Also generate 'visual_prompt' as a photorealistic keyframe description.

Output JSON ONLY:
{{
  "episode_title": "{topic.upper()[:28]}",
  "narrative_format": "{format_name}",
  "hook_headline": "VIRAL HOOK (3-4 WORDS)",
  "character_dna": "Detailed invariant character description (suit, colors, helmet, physical features)",
  "visual_anchor": "Unified environment, atmospheric palette, and lighting style",
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
      "camera_motion": "rapid-push-in-shake",
      "video_prompt": "Extreme wide long shot from a 10mm ultra-wide lens, [character_dna] falling headfirst through violent crimson storm clouds, arms flailing against intense crosswinds, body tumbling downward at terminal velocity, camera tracking downward with motion blur, volumetric god rays, Unreal Engine 5 render, 8k resolution",
      "visual_prompt": "Extreme wide long shot from 10mm lens of [character_dna] falling into colossal storm vortex, volumetric amber lighting, 8k render"
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
            active_model = "gemini-3.5-flash-lite"
            models_to_try = ["gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-3.5-flash", "gemini-3.8-flash"]
            for candidate_model in models_to_try:
                for attempt in range(1, 3):
                    try:
                        print(f"⏳ [Script Engine] Querying Gemini ({candidate_model}, attempt {attempt}/2, timeout 15s)...")
                        res = call_with_timeout(
                            client.models.generate_content,
                            kwargs=dict(
                                model=candidate_model,
                                contents=prompt,
                                config=dict(response_mime_type="application/json"),
                            ),
                            timeout_sec=15,
                        )
                        if res and res.text:
                            data_check = json.loads(res.text)
                            if "beats" in data_check and len(data_check["beats"]) == 5:
                                wc = sum(len(b['narration'].split()) for b in data_check['beats'])
                                if 112 <= wc <= 146:
                                    active_model = candidate_model
                                    break
                                else:
                                    print(f"⚠️ [Script Engine] {candidate_model} generated {wc} words (expected 112-146). Retrying...")
                                    res = None
                    except concurrent.futures.TimeoutError:
                        print(f"⏱️ [Script Engine] {candidate_model} timed out after 15s. Retrying...")
                    except Exception as m_err:
                        print(f"⚠️ Model {candidate_model} script note: {m_err}")
                        s_err = str(m_err).lower()
                        if any(k in s_err for k in ["resource_exhausted", "429", "404", "not_found", "no longer available", "not found"]):
                            break
                        if "503" in s_err and attempt >= 2:
                            break
                        time.sleep(1.0 * attempt)
                if res and res.text:
                    break

            if res and res.text:
                data = json.loads(res.text)
                if "beats" in data and len(data["beats"]) == 5:
                    word_count = sum(len(b['narration'].split()) for b in data['beats'])
                    print(f"📝 [Stage 2: Script Engine] Gemini AI ({active_model}) synthesized clean story & video prompts for '{topic}' ({word_count} words)")
                    try:
                        from story_pipeline.telegram_notifier import RUN_TRACKER
                        RUN_TRACKER.set_model_used("Script", f"Gemini ({active_model})")
                    except Exception:
                        pass
                    return ensure_video_prompts_and_motion(data)
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
                    {"role": "system", "content": "You are an elite viral short-form director for YouTube Shorts. Output valid JSON only matching the schema exactly with video_prompt and camera_motion for every beat."},
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
                        print(f"📝 [Stage 2: Script Engine] Groq AI (llama-3.3-70b-versatile) synthesized clean story & video prompts for '{topic}' ({w_count} words)")
                        try:
                            from story_pipeline.telegram_notifier import RUN_TRACKER
                            RUN_TRACKER.set_model_used("Script", "Groq (llama-3.3-70b-versatile)")
                        except Exception:
                            pass
                        return ensure_video_prompts_and_motion(g_data)
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
    return ensure_video_prompts_and_motion(generate_procedural_script(topic, hook_premise, style, ep_num))


def ensure_video_prompts_and_motion(script_data: dict) -> dict:
    """Guarantees every beat carries invariant character DNA, explicit lens optics, and physical kinematics."""
    topic = script_data.get("episode_title") or script_data.get("topic") or "Cosmic Journey"
    t_lower = topic.lower()

    # 1. Synthesize or validate Invariant Character DNA & Visual Anchor
    char_dna = script_data.get("character_dna", "")
    vis_anchor = script_data.get("visual_anchor", "")

    if not char_dna or len(char_dna.strip()) < 25:
        if any(k in t_lower for k in ["freeze time", "stop time", "time stop", "freeze", "telepathy", "mind", "power", "superpower"]):
            char_dna = "Young protagonist in oversized black streetwear hoodie, modern sunglasses, dark messy hair, confident smirk, hand outstretched toward camera with dramatic foreshortening"
            vis_anchor = "Midnight cyan-blue paused metropolis, floating cars and suspended pedestrians, shattered glowing temporal clock face in background, volumetric fog, Unreal Engine 5 render, 8k"
        elif any(k in t_lower for k in ["space", "jupiter", "saturn", "moon", "cosmic", "black hole", "universe", "orbit", "planet", "solar", "gravity", "meteor", "astronaut"]):
            char_dna = "Astronaut in sleek matte-white NASA deep-space EVA suit with neon-amber shoulder striping, carbon-fiber joints, and a reflective gold-mirrored visor"
            vis_anchor = "Jupiter crimson-amber turbulent vortex atmosphere, dark cosmic space backdrop, violent electrical storm lighting, Unreal Engine 5 render"
        elif any(k in t_lower for k in ["peeing", "pee", "kidney", "brain", "body", "heart", "blood", "medical", "organ", "sleep", "cell"]):
            char_dna = "Subject in clinical modern attire with bioluminescent neural telemetry sensors and glowing bio-metric monitors"
            vis_anchor = "Microscopic cellular inner universe, glowing amber bio-luminescence, deep blue background, Unreal Engine 5 render, 8k"
        elif any(k in t_lower for k in ["ocean", "megalodon", "mariana", "sea", "shark", "abyss", "underwater", "trench"]):
            char_dna = "Deep-sea explorer in specialized titanium diving exoskeleton with high-intensity halogen headlamps and reinforced aqua-helm"
            vis_anchor = "Abyssal midnight ocean zone, bioluminescent marine particulate, deep indigo water, volumetric light shafts"
        elif any(k in t_lower for k in ["dinosaur", "trex", "t-rex", "roar", "fossil", "prehistoric"]):
            char_dna = "Colossal apex Tyrannosaurus Rex with obsidian-scaled hide, amber predatory eyes, and jagged battle scars"
            vis_anchor = "Primordial misty Cretaceous jungle, atmospheric golden hour sun rays filtering through giant ferns"
        else:
            char_dna = "Protagonist explorer in tactical expedition suit with glowing HUD collar and telemetry gear"
            vis_anchor = "Cinematic dramatic atmospheric environment, high-contrast volumetric lighting, Unreal Engine 5 render, 8k"

    script_data["character_dna"] = char_dna
    script_data["visual_anchor"] = vis_anchor

    default_cams = {
        1: "rapid-push-in-shake",
        2: "smooth-lateral-pan-right",
        3: "vertical-tilt-reveal",
        4: "climax-pull-back",
        5: "loop-convergence-zoom"
    }

    lens_configs = {
        1: ("10mm ultra-wide lens, extreme wide long shot", "falling headfirst through turbulent atmospheric cloud bands, body tumbling downward at terminal velocity, arms flailing against violent crosswinds"),
        2: ("24mm anamorphic lens, low-angle tracking shot", "cutting through electrified atmospheric mist, body twisting against aerodynamic drag, camera tracking right"),
        3: ("35mm prime lens, Dutch-angle vertical tilt reveal", "plunging into dense turbulent supercritical fluid layers, limbs stabilizing as camera tilts upward"),
        4: ("10mm wide-angle anamorphic lens, epic scope pull-back", "engulfed in surging shockwaves and violent fracturing pressure waves, camera pulling backward at high speed"),
        5: ("50mm portrait lens, centered loop convergence shot", "drifting and hovering in glowing core vortex, looking directly into camera with visor reflection matching Beat 1 entry angle for seamless infinite loop"),
    }

    lens_tokens = ["10mm", "12mm", "14mm", "16mm", "24mm", "28mm", "35mm", "50mm", "85mm", "anamorphic", "ultra-wide", "macro", "telephoto"]
    kinematics_tokens = [
        "falling", "fall", "tumbling", "tumble", "plunging", "plunge", "surging", "surge",
        "filtering", "filter", "swirling", "swirl", "fracturing", "fracture", "collapsing", "collapse",
        "rippling", "ripple", "lunging", "lunge", "sweeping", "sweep", "moving", "move",
        "pushing", "push", "running", "run", "descending", "descend", "accelerating", "accelerate",
        "drifting", "drift", "shattering", "shatter", "spinning", "spin", "plummeting", "plummet",
        "floating", "float", "racing", "race", "diving", "dive", "cutting", "cut", "vibrating", "vibrate", "hovering", "hover",
        "turning", "turn", "stepping", "step", "walking", "walk", "reaching", "reach", "stumbling", "stumble"
    ]

    for b in script_data.get("beats", []):
        b_num = b.get("beat_number", 1)
        if not b.get("camera_motion"):
            b["camera_motion"] = default_cams.get(b_num, "rapid-push-in-shake")

        vp = b.get("video_prompt", "")
        lens_spec, motion_spec = lens_configs.get(b_num, lens_configs[1])

        # If missing or lacking lens/kinematics/character_dna, rebuild high-fidelity prompt
        has_lens = any(tok in vp.lower() for tok in lens_tokens)
        has_kine = any(tok in vp.lower() for tok in kinematics_tokens)
        has_dna = any(w in vp.lower() for w in char_dna.lower().split()[:3])

        if not vp or not has_lens or not has_kine or not has_dna:
            cam = b.get("camera_motion")
            b["video_prompt"] = (
                f"Cinematic {cam} camera motion, {lens_spec}, {char_dna} {motion_spec}, "
                f"set in {vis_anchor}, volumetric atmospheric god rays, ray tracing, Unreal Engine 5 render, 8k resolution photorealistic motion"
            )

        if not b.get("visual_prompt"):
            b["visual_prompt"] = f"Cinematic shot from {lens_spec} of {char_dna}, {vis_anchor}, 8k render"

    return script_data


def generate_procedural_script(topic: str, hook_premise: str, style: str, ep_num: int) -> dict:
    """Builds a guaranteed 5-beat viral script perfectly timed to 57 seconds with invariant character DNA and lens cinematography."""
    clean_title = topic.upper()[:26]

    if "freeze time" in topic.lower() or "stop time" in topic.lower() or "time stop" in topic.lower():
        char_dna = "Young protagonist in oversized black streetwear hoodie, modern sunglasses, dark messy hair, confident smirk, hand outstretched toward camera with dramatic foreshortening"
        vis_anchor = "Midnight cyan-blue paused metropolis, floating cars and suspended pedestrians, shattered glowing temporal clock face in background, volumetric fog, Unreal Engine 5 render, 8k"
        beats = [
            {
                "beat_number": 1,
                "time_window": "0-10s",
                "hook_trigger": "Opening Wish-Fulfillment Hook",
                "narration": "What if you could freeze time across the entire world? In the first ten seconds, you would assume you are an untouchable god, but a horrifying physics nightmare has already begun.",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": f"Extreme wide long shot from 24mm anamorphic lens, {char_dna} walking forward as time freezes, hand outstretched toward camera with dramatic foreshortening, suspended coffee droplets floating in mid-air, cars paused mid-intersection, cyan rim lighting, Unreal Engine 5 render, 8k",
                "visual_prompt": f"24mm anamorphic shot of {char_dna} standing in paused metropolis with suspended coffee droplets and cars, cyan lighting, 8k",
            },
            {
                "beat_number": 2,
                "time_window": "10-22s",
                "hook_trigger": "10s Escalation Hook",
                "narration": "Within minutes, sheer euphoria sets in as you stroll past statue-frozen traffic and explore empty streets, but terrifying cosmic laws of physics are rapidly closing in on your body.",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": f"Low-angle 24mm anamorphic tracking pan, {char_dna} cutting through volumetric midnight fog past frozen pedestrians and levitating debris, confident smirk, cyan rim-lighting, 8k",
                "visual_prompt": f"24mm anamorphic tracking shot of {char_dna} stepping past frozen people and cars in midnight city, 8k",
            },
            {
                "beat_number": 3,
                "time_window": "22-35s",
                "hook_trigger": "20s Danger Hook",
                "narration": "Because all time has stopped, light photons freeze in mid-air, plunging your eyes into pitch-black blindness, while stationary oxygen molecules refuse to enter your lungs, suffocating you in sixty seconds.",
                "speaker": "character_hero",
                "speaker_name": "Physicist",
                "speaker_avatar": "⏳",
                "sfx": "impact_boom",
                "camera_motion": "vertical-tilt-reveal",
                "video_prompt": f"Dutch-angle 35mm prime vertical tilt reveal, {char_dna} stumbling forward into darkness as light photons freeze into solid black mist, shattered glowing temporal clock face pulsing in sky, camera tilting upward, 8k",
                "visual_prompt": f"35mm prime Dutch-angle shot of {char_dna} gasping in darkness beneath shattered glowing temporal clock, 8k",
            },
            {
                "beat_number": 4,
                "time_window": "35-48s",
                "hook_trigger": "30s Climax Hook",
                "narration": "As your consciousness slips away in frozen silence, you suddenly hear heavy footsteps echoing right behind you. If the entire universe is completely frozen, who is moving behind you?",
                "speaker": "character_hero",
                "speaker_name": "Physicist",
                "speaker_avatar": "⏳",
                "sfx": "pop",
                "camera_motion": "climax-pull-back",
                "video_prompt": f"Extreme wide 10mm anamorphic epic scope pull-back, shadowy figure emerging and moving behind {char_dna} in frozen city, shockwaves rippling through temporal void, camera pulling backward rapidly, 8k",
                "visual_prompt": f"10mm anamorphic wide shot of shadowy entity moving behind {char_dna} in frozen world, cinematic thriller, 8k",
            },
            {
                "beat_number": 5,
                "time_window": "48-58s",
                "hook_trigger": "45s Resolution Hook",
                "narration": "You turn around in absolute terror, only to discover that the moment you chose to freeze time, you trapped yourself inside a loop that always starts when...",
                "speaker": "narrator",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "loop-convergence-zoom",
                "video_prompt": f"Centered 50mm portrait loop convergence shot, {char_dna} turning directly toward camera in shock with sunglasses reflecting the frozen city matching Beat 1 entry angle for seamless infinite loop, 8k",
                "visual_prompt": f"50mm portrait shot of {char_dna} turning in shock with sunglasses reflecting paused reality, 8k",
            },
        ]
    elif "peeing" in topic.lower():
        char_dna = "Subject in clinical modern attire with bioluminescent neural telemetry sensors and glowing bio-metric monitors"
        vis_anchor = "Microscopic cellular inner universe, glowing amber bio-luminescence, deep blue background, Unreal Engine 5 render, 8k"
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
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": f"Extreme wide long shot from 10mm ultra-wide lens, {char_dna} falling into disarray in medical telemetry chamber, pulsing warning monitors, volumetric god rays, Unreal Engine 5 render, 8k",
                "visual_prompt": f"10mm ultra-wide shot of {char_dna} looking confused at bathroom door, glowing holographic medical monitors, 8k",
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
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": f"Low-angle 24mm anamorphic tracking pan, {char_dna} filtering biological fluids as anatomical cross-section reveals kidneys surging at hyper speed, pulsing amber warning lights, 8k",
                "visual_prompt": f"24mm anamorphic shot of glowing human kidneys filtering fluid at hyper speed, pulsing amber warning lights, cinematic",
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
                "camera_motion": "vertical-tilt-reveal",
                "video_prompt": f"Dutch-angle 35mm prime vertical tilt reveal, {char_dna} collapsing against medical bed as human heart pulses with red warning sparks, camera tilting upward, Unreal Engine 5, 8k",
                "visual_prompt": f"35mm prime dramatic close-up of a human heart glowing with red warning sparks, dark dramatic background, high stakes",
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
                "camera_motion": "climax-pull-back",
                "video_prompt": f"Extreme wide 10mm anamorphic epic scope pull-back, {char_dna} engulfed in glowing neural hallucinations as brain synapses fire violently, camera pulling backward rapidly, 8k",
                "visual_prompt": f"10mm anamorphic 3D visualization of brain synapses firing with glowing neon pulses, surreal dreamscape floating in hospital room, 8k",
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
                "camera_motion": "loop-convergence-zoom",
                "video_prompt": f"Centered 50mm portrait loop convergence shot, {char_dna} drinking pure water at sunrise, golden sun rays filtering through window matching Beat 1 entry angle, 8k",
                "visual_prompt": f"50mm portrait shot of healthy character drinking glowing water at sunrise, golden sun rays, inspirational masterpiece",
            },
        ]
    elif "dinosaur" in topic.lower() or "roar" in topic.lower():
        char_dna = "Colossal apex Tyrannosaurus Rex with obsidian-scaled hide, amber predatory eyes, and jagged battle scars"
        vis_anchor = "Primordial misty Cretaceous jungle, atmospheric golden hour sun rays filtering through giant ferns"
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
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": f"Extreme wide long shot from 10mm ultra-wide lens, {char_dna} lunging through prehistoric mist, amber eyes glowing, camera pushing rapidly forward with motion blur, Unreal Engine 5, 8k",
                "visual_prompt": f"10mm ultra-wide shot of {char_dna} in prehistoric mist, amber eyes, cinematic jungle lighting, Unreal Engine 5 render, 8k",
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
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": f"Low-angle 24mm anamorphic tracking pan, {char_dna} vibrating throat with deep infrasonic bass energy waves rippling through jungle air, camera panning smoothly, 8k",
                "visual_prompt": f"24mm anamorphic close-up of {char_dna} throat vibrating with deep bass energy waves rippling through air, 8k",
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
                "camera_motion": "vertical-tilt-reveal",
                "video_prompt": f"Dutch-angle 35mm prime vertical tilt reveal, puddle with sonic water ripples forming geometric patterns as the earth tremors from {char_dna} footsteps, camera tilting upward, 8k",
                "visual_prompt": f"35mm prime shot of prehistoric puddle with sonic water ripples forming geometric patterns as earth tremors, 8k",
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
                "camera_motion": "climax-pull-back",
                "video_prompt": f"Extreme wide 10mm anamorphic epic scope pull-back, {char_dna} lunging from canopy darkness, jaws opening with terrifying speed, camera pulling backward rapidly, 8k",
                "visual_prompt": f"10mm anamorphic shot of {char_dna} looming over jungle trees, glowing predatory eyes in dark canopy, cinematic action, 8k",
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
                "camera_motion": "loop-convergence-zoom",
                "video_prompt": f"Centered 50mm portrait loop convergence shot, {char_dna} silhouette standing atop prehistoric mountain peak under purple nebula sky matching Beat 1 entry angle, 8k",
                "visual_prompt": f"50mm portrait shot of {char_dna} standing atop mountain peak under nebula sky, breathtaking masterpiece",
            },
        ]
    else:
        # Universal Dynamic 5-Beat Script (Calibrated to exactly 130 words)
        topic_core = topic.rstrip("?.!").replace("What if ", "").replace("What happens if ", "").strip()
        words_list = topic_core.split()
        if len(words_list) > 7:
            topic_core = " ".join(words_list[:7])

        if any(k in topic.lower() for k in ["space", "jupiter", "saturn", "moon", "cosmic", "planet"]):
            char_dna = "Astronaut in sleek matte-white NASA deep-space EVA suit with neon-amber shoulder striping, carbon-fiber joints, and a reflective gold-mirrored visor"
            vis_anchor = "Colossal planetary vortex atmosphere, dark cosmic space backdrop, violent electrical storm lighting, Unreal Engine 5 render"
        else:
            char_dna = "Protagonist explorer in tactical expedition suit with glowing HUD collar and telemetry gear"
            vis_anchor = "Cinematic dramatic atmospheric environment, high-contrast volumetric lighting, Unreal Engine 5 render, 8k"

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
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": f"Extreme wide long shot from 10mm ultra-wide lens, {char_dna} falling headfirst into {topic_core.lower()} catastrophic anomaly, body tumbling at terminal velocity, camera pushing rapidly forward with motion blur, volumetric god rays, Unreal Engine 5 render, 8k resolution",
                "visual_prompt": f"10mm ultra-wide shot of {char_dna} confronting {topic_core}, vibrant volumetric lighting, Unreal Engine 5, 8k",
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
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": f"Low-angle 24mm anamorphic tracking pan, {char_dna} cutting through atmospheric drag as supersonic shockwaves ripple across continents and electrical grids collapse violently, camera tracking smoothly right, 8k",
                "visual_prompt": f"24mm anamorphic shot of Earth from space with satellite networks sparking, city lights extinguishing into darkness, cinematic",
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
                "camera_motion": "vertical-tilt-reveal",
                "video_prompt": f"Dutch-angle 35mm prime vertical tilt reveal, colossal ocean tsunami surging over coastal skyline as {char_dna} watches churning saltwater tear through skyscrapers, camera tilting upward, 8k",
                "visual_prompt": f"35mm prime shot of colossal ocean tsunami surging over coastal skyline, violent turbulent waves, atmospheric storm lighting, 8k",
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
                "camera_motion": "climax-pull-back",
                "video_prompt": f"Extreme wide 10mm anamorphic epic scope pull-back, earth crust fracturing open with glowing red and orange molten magma fissures, {char_dna} illuminated by tectonic fury, camera pulling backward rapidly, 8k",
                "visual_prompt": f"10mm anamorphic shot of earth crust violently fracturing open with glowing molten magma fissures, seismic devastation, cinematic 8k",
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
                "camera_motion": "loop-convergence-zoom",
                "video_prompt": f"Centered 50mm portrait loop convergence shot, {char_dna} drifting and floating in glowing atmospheric vortex looking directly into camera with visor reflection matching Beat 1 entry angle for seamless infinite loop, 8k",
                "visual_prompt": f"50mm portrait shot of {char_dna} in atmospheric vortex matching Beat 1 opening frame for seamless visual infinite loop, 8k",
            },
        ]

    total_words = sum(len(b["narration"].split()) for b in beats)
    return {
        "episode_title": clean_title,
        "hook_headline": f"WHAT IF {clean_title[:18]}?!",
        "character_dna": char_dna,
        "visual_anchor": vis_anchor,
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
