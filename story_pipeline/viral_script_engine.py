"""
Stage 2: Cinematic Storytelling Script Engine.
Generates atmospheric, high-retention cinematic narratives matching top viral reels (e.g. @soch.bhosdike):
- 5 to 6 deliberate, immersive scenes lasting 6 to 9 seconds each (total duration ~38-48 seconds).
- Total spoken words: 90 to 125 words (natural documentary gravitas, ~2.2 words/second).
- Persistent 'top_hook_banner' context headline anchored at top throughout the video.
- Deep, suspenseful English narration (no hurried pacing or fragmented cuts).
- Distinct Unreal Engine 5 / 3D cinema-grade visual prompts with explicit optics & physical kinematics.
- Sound effects (impact_boom, whoosh, dramatic-pulse, riser) synchronized to scene transitions.
"""

import json
import os
import time
import concurrent.futures
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TARGET_DURATION_SECONDS = 42.0


def call_with_timeout(func, args=(), kwargs=None, timeout_sec=20):
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
    Generates an immersive cinematic storytelling script (5 to 6 scenes, 38-48s).
    Paced for deep, engaging narrative retention, cinematic optics, and Unreal Engine 5 visual majesty.
    """
    topic = topic_data["topic"]
    hook_premise = topic_data.get("hook_premise", "")
    category = topic_data.get("category", "Curiosity")
    style = topic_data.get("style", "Hyper-realistic CGI dark sci-fi Unreal Engine 5 render, 8k")
    ep_num = topic_data.get("episode", 1)
    banner = topic_data.get("top_hook_banner") or topic[:55]

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=30000))

            prompt = f"""You are an elite cinematic short-form video director for Instagram Reels, YouTube Shorts, and TikTok.
Write a powerful, atmospheric, high-retention cinematic storytelling script in pure English.

TOPIC: {topic}
PREMISE: {hook_premise}
TOP HOOK BANNER: {banner}
CATEGORY: {category}
VISUAL ART STYLE: {style}
EPISODE: #{ep_num}

CRITICAL CINEMATIC PACING & NARRATIVE RULES:
1. DELIBERATE CINEMATIC SCENE PACING:
   - Generate STRICTLY 5 to 6 immersive scenes (DO NOT generate 10+ rapid cuts!).
   - Each scene lasts 6 to 9 seconds, giving time for the viewer to absorb the cinematography, optics, and sound design.
   - TOTAL SPOKEN WORDS across all scenes: STRICTLY BETWEEN 90 AND 125 WORDS (Total video duration ~38-48 seconds).
   - Language: Pure, fluent, natural English with documentary gravitas.
2. NARRATIVE ARC:
   - Scene 1: The Hook - Shocking premise question grabbing immediate curiosity (14-20 words).
   - Scene 2: The Eerie Wonder - The surreal initial experience or illusion of control (16-22 words).
   - Scene 3: The Physics Breakdown - The terrifying scientific consequence setting in (16-22 words).
   - Scene 4: The Escalating Stakes - Physical survival failure and atmospheric collapse (16-22 words).
   - Scene 5 (or 6): The Climax & Paradox - The mind-bending conclusion connecting to a loop (18-24 words).
3. PERSISTENT TOP HOOK BANNER:
   - Provide "top_hook_banner": "{banner}" (bold, catchy headline, under 55 characters).
4. INVARIANT CHARACTER DNA & VISUAL ANCHOR:
   - Define "character_dna": explicit visual appearance of the central protagonist (e.g. young man in dark charcoal hoodie, sleek sunglasses, determined).
   - Define "visual_anchor": unified environment and lighting (e.g. frozen city under deep midnight blue, cyan volumetric rim lighting, levitating droplets).
5. CINEMA-GRADE PROMPTS FOR EVERY SCENE:
   - For EVERY scene, write a distinct 'video_prompt' and 'visual_prompt'.
   - Include camera lens tokens: 10mm ultra-wide, 24mm anamorphic, 35mm portrait macro, 50mm cinema lens.
   - Include active physical kinematics: stepping, floating, walking, reaching, clutching, collapsing, plummeting, fracturing, sweeping, vibrating.
   - Assign camera_motion: "smooth-zoom-in", "smooth-lateral-pan-right", "vertical-tilt-reveal", "dramatic-pulse", "climax-pull-back".
   - Assign sfx: "impact_boom", "whoosh", "pop", "riser".

Output JSON ONLY:
{{
  "episode_title": "{topic.upper()[:28]}",
  "top_hook_banner": "{banner}",
  "hook_headline": "VIRAL HOOK (3-4 WORDS)",
  "character_dna": "Detailed invariant protagonist description",
  "visual_anchor": "Unified environment and lighting palette",
  "total_words_count": 105,
  "loop_lead_in": "Last sentence connecting into Scene 1",
  "scenes": [
    {{
      "scene_number": 1,
      "beat_number": 1,
      "hook_trigger": "Opening Hook",
      "narration": "First punchy line grabbing curiosity (15-20 words)",
      "speaker": "speaker_1",
      "speaker_name": "Narrator",
      "sfx": "impact_boom",
      "camera_motion": "smooth-zoom-in",
      "video_prompt": "24mm anamorphic wide angle shot, low-angle perspective, young man in dark charcoal hoodie stepping forward through a frozen city avenue, hand outstretched in extreme foreshortening, suspended raindrops floating in mid-air, levitating yellow cabs, shattered glowing cyan clock in sky, Unreal Engine 5 render, ray-traced volumetric lighting, 8k vertical 9:16",
      "visual_prompt": "24mm anamorphic wide angle shot of young man in dark hoodie stepping through frozen city with floating raindrops and glowing clock, 8k"
    }}
  ],
  "seo_tags": ["viral", "reels", "shorts", "whatif", "scifi", "paradox", "cinematic", "trending"],
  "hashtags": ["#shorts", "#viral", "#reels", "#whatif", "#scifi", "#trending"],
  "pinned_comment": "Would you freeze time if you had the chance? Comment below! 👇 Subscribe for daily mysteries! 🚀"
}}"""

            res = None
            active_model = "gemini-3.5-flash-lite"
            models_to_try = ["gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-3.5-flash", "gemini-3.8-flash"]
            for candidate_model in models_to_try:
                for attempt in range(1, 3):
                    try:
                        print(f"⏳ [Script Engine] Querying Gemini ({candidate_model}, attempt {attempt}/2, timeout 20s)...")
                        res = call_with_timeout(
                            client.models.generate_content,
                            kwargs=dict(
                                model=candidate_model,
                                contents=prompt,
                                config=dict(response_mime_type="application/json"),
                            ),
                            timeout_sec=20,
                        )
                        if res and res.text:
                            data_check = json.loads(res.text)
                            scenes_check = data_check.get("scenes") or data_check.get("beats", [])
                            if 5 <= len(scenes_check) <= 8:
                                wc = sum(len(s.get('narration', '').split()) for s in scenes_check)
                                if 80 <= wc <= 145:
                                    active_model = candidate_model
                                    break
                                else:
                                    print(f"⚠️ [Script Engine] {candidate_model} generated {wc} words (expected 80-145). Retrying...")
                                    res = None
                            else:
                                print(f"⚠️ [Script Engine] {candidate_model} generated {len(scenes_check)} scenes (expected 5-8). Retrying...")
                                res = None
                    except concurrent.futures.TimeoutError:
                        print(f"⏱️ [Script Engine] {candidate_model} timed out. Retrying...")
                    except Exception as m_err:
                        print(f"⚠️ Model {candidate_model} script note: {m_err}")
                        s_err = str(m_err).lower()
                        if any(k in s_err for k in ["resource_exhausted", "429", "404", "not_found"]):
                            break
                        time.sleep(1.0 * attempt)
                if res and res.text:
                    break

            if res and res.text:
                data = json.loads(res.text)
                scenes = data.get("scenes") or data.get("beats", [])
                if 5 <= len(scenes) <= 8:
                    data["scenes"] = scenes
                    data["beats"] = scenes
                    if not data.get("top_hook_banner"):
                        data["top_hook_banner"] = banner
                    word_count = sum(len(s.get('narration', '').split()) for s in scenes)
                    print(f"📝 [Stage 2: Script Engine] Gemini AI ({active_model}) synthesized {len(scenes)} cinematic scenes for '{topic}' ({word_count} words)")
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

    # Secondary Fallback: Groq Cloud
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key and groq_api_key.strip():
        try:
            print("⏳ [Script Engine] Querying Groq Cloud API (llama-3.3-70b-versatile, timeout 25s)...")
            import urllib.request
            groq_url = "https://api.groq.com/openai/v1/chat/completions"
            groq_payload = json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are an elite viral short-form director. Output JSON with strictly 5-6 cinematic scenes, top_hook_banner, video_prompt with lens and kinematics, and 90-125 words total in pure English."},
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
                    scenes = g_data.get("scenes") or g_data.get("beats", [])
                    if 5 <= len(scenes) <= 8:
                        g_data["scenes"] = scenes
                        g_data["beats"] = scenes
                        if not g_data.get("top_hook_banner"):
                            g_data["top_hook_banner"] = banner
                        w_count = sum(len(s.get('narration', '').split()) for s in scenes)
                        print(f"📝 [Stage 2: Script Engine] Groq AI synthesized {len(scenes)} cinematic scenes for '{topic}' ({w_count} words)")
                        try:
                            from story_pipeline.telegram_notifier import RUN_TRACKER
                            RUN_TRACKER.set_model_used("Script", "Groq (llama-3.3-70b-versatile)")
                        except Exception:
                            pass
                        return ensure_video_prompts_and_motion(g_data)
        except Exception as e_groq:
            print(f"Notice: Groq script generation note: {e_groq}")

    # Tertiary Fallback: High-Quality Procedural Cinematic Script
    try:
        from story_pipeline.telegram_notifier import RUN_TRACKER
        RUN_TRACKER.set_model_used("Script", "Procedural Cinematic Engine")
    except Exception:
        pass
    return ensure_video_prompts_and_motion(generate_procedural_script(topic, hook_premise, style, ep_num, banner=banner))


def ensure_video_prompts_and_motion(script_data: dict) -> dict:
    """Guarantees every scene carries invariant character DNA, explicit lens optics, and physical kinematics."""
    topic = script_data.get("episode_title") or script_data.get("topic") or "Cinematic Short"
    t_lower = topic.lower()

    char_dna = script_data.get("character_dna", "")
    vis_anchor = script_data.get("visual_anchor", "")

    if not char_dna or len(char_dna.strip()) < 20:
        if any(k in t_lower for k in ["freeze", "time", "pause", "clock", "temporal"]):
            char_dna = "A young man in a dark charcoal streetwear hoodie with modern sleek black sunglasses and wavy dark hair"
            vis_anchor = "Frozen modern metropolis under deep midnight navy and glowing cyan volumetric rim lighting, suspended raindrops and shattered giant Roman-numeral clock in the sky"
        elif any(k in t_lower for k in ["space", "jupiter", "saturn", "moon", "cosmic", "black hole", "astronaut"]):
            char_dna = "Astronaut in sleek matte-white NASA deep-space EVA suit with neon-amber shoulder striping and a reflective gold-mirrored visor"
            vis_anchor = "Jupiter colossal crimson vortex atmosphere, violent electrical storm lighting, Unreal Engine 5 render, 8k"
        elif any(k in t_lower for k in ["gravity", "fall", "float", "orbit", "earth"]):
            char_dna = "Young athletic protagonist in casual black streetwear jacket struggling against anti-gravity forces"
            vis_anchor = "Urban cityscape where cars, water, and debris are suspended and drifting into the sky, volumetric lighting, Unreal Engine 5 render, 8k"
        else:
            char_dna = "Charismatic determined protagonist in modern streetwear with expressive features and sharp styling"
            vis_anchor = "Atmospheric high-contrast cinematic environment with volumetric lighting and deep color grading, Unreal Engine 5 render, 8k"

    script_data["character_dna"] = char_dna
    script_data["visual_anchor"] = vis_anchor

    scenes = script_data.get("scenes") or script_data.get("beats", [])
    script_data["scenes"] = scenes
    script_data["beats"] = scenes

    if not script_data.get("top_hook_banner"):
        script_data["top_hook_banner"] = topic[:55]

    cam_cycle = [
        "smooth-zoom-in",
        "smooth-lateral-pan-right",
        "vertical-tilt-reveal",
        "dramatic-pulse",
        "climax-pull-back",
    ]

    lens_cycle = [
        "24mm anamorphic wide angle lens, low-angle perspective",
        "10mm ultra-wide lens, dynamic expansive perspective",
        "35mm prime macro lens, intense close-up reaction",
        "50mm cinema lens, dramatic medium shot",
        "10mm wide-angle epic scope pull-back lens",
    ]

    kinematics_cycle = [
        "stepping forward through frozen traffic with hand outstretched in extreme foreshortening, floating raindrops",
        "walking calmly past frozen pedestrians stuck mid-stride as suspended liquid droplets drift in mid-air",
        "reaching upward with trembling hands as darkness creeps across face, light beams freezing like solid luminescent rods",
        "clutching throat gasping for breath as frozen oxygen crystals resist inhalation, collapsing to one knee",
        "plummeting backward as giant temporal clock vibrates violently, fracturing into blinding cyan sparks",
    ]

    lens_tokens = ["10mm", "12mm", "14mm", "16mm", "24mm", "28mm", "35mm", "50mm", "85mm", "anamorphic", "ultra-wide", "macro", "telephoto"]
    kinematics_tokens = [
        "falling", "fall", "tumbling", "tumble", "plunging", "plunge", "surging", "surge",
        "reacting", "react", "gesturing", "gesture", "holding", "hold", "pointing", "point",
        "turning", "turn", "shaking", "shake", "stumbling", "stumble", "leaning", "lean",
        "lunging", "lunge", "moving", "move", "running", "run", "drifting", "drift", "spinning", "spin",
        "looking", "look", "stepping", "step", "walking", "walk", "reaching", "reach",
        "clutching", "clutch", "collapsing", "collapse", "plummeting", "plummet", "fracturing", "fracture",
        "floating", "float", "vibrating", "vibrate", "sweeping", "sweep"
    ]

    for idx, sc in enumerate(scenes):
        sc_num = idx + 1
        sc["scene_number"] = sc_num
        sc["beat_number"] = sc_num

        if not sc.get("camera_motion"):
            sc["camera_motion"] = cam_cycle[idx % len(cam_cycle)]

        vp = sc.get("video_prompt", "")
        lens_spec = lens_cycle[idx % len(lens_cycle)]
        motion_spec = kinematics_cycle[idx % len(kinematics_cycle)]

        has_lens = any(tok in vp.lower() for tok in lens_tokens)
        has_kine = any(tok in vp.lower() for tok in kinematics_tokens)
        has_dna = any(w in vp.lower() for w in char_dna.lower().split()[:3])

        if not vp or not has_lens or not has_kine or not has_dna:
            cam = sc.get("camera_motion")
            sc["video_prompt"] = (
                f"Cinematic {lens_spec}, {char_dna} {motion_spec}, "
                f"set in {vis_anchor}, volumetric atmospheric god rays, ray tracing, Unreal Engine 5 render, 8k vertical 9:16"
            )
        if not sc.get("visual_prompt"):
            sc["visual_prompt"] = f"{lens_spec} of {char_dna}, {motion_spec}, {vis_anchor}, 8k render"

        if not sc.get("sfx"):
            sfx_cycle = ["impact_boom", "whoosh", "pop", "dramatic-pulse", "riser"]
            sc["sfx"] = sfx_cycle[idx % len(sfx_cycle)]

    return script_data


def generate_procedural_script(topic: str, hook_premise: str, style: str, ep_num: int, banner: str = "") -> dict:
    """Builds a guaranteed 5-scene cinematic storytelling script (38-48s) with English narrative, optics & kinematics."""
    clean_title = topic.upper()[:28]
    t_lower = topic.lower()

    if not banner:
        banner = topic[:55]

    # Archetype 1: Freezing Time for 24 Hours (@soch.bhosdike format)
    if any(k in t_lower for k in ["freeze", "time", "pause", "temporal", "clock", "24 hours"]):
        banner = "WHAT IF YOU COULD FREEZE TIME FOR 24 HOURS?"
        char_dna = "A young man in a dark charcoal streetwear hoodie with modern sleek black sunglasses and wavy dark hair"
        vis_anchor = "Frozen modern metropolis under deep midnight navy and glowing cyan volumetric rim lighting, suspended raindrops and shattered giant Roman-numeral clock in the sky"

        scenes = [
            {
                "scene_number": 1,
                "narration": "What if you woke up tomorrow with the power to freeze time for 24 hours?",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "impact_boom",
                "camera_motion": "smooth-zoom-in",
                "video_prompt": "24mm anamorphic wide angle shot, low-angle perspective, young man in dark charcoal hoodie stepping forward through a frozen city avenue, hand outstretched in extreme foreshortening, suspended raindrops floating in mid-air, levitating yellow cabs, shattered glowing cyan clock in sky, Unreal Engine 5 render, ray-traced volumetric lighting, 8k vertical 9:16",
                "visual_prompt": "24mm anamorphic wide angle shot of young man in dark hoodie stepping through frozen city with floating raindrops and glowing clock, 8k",
            },
            {
                "scene_number": 2,
                "narration": "At first, it feels like the ultimate playground: floating raindrops, frozen traffic, and complete silence in the city.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": "10mm ultra-wide lens tracking pan, young man walking calmly past frozen pedestrians stuck mid-stride on urban sidewalk, a cup of coffee suspended mid-spill with floating liquid droplets, dramatic depth, Unreal Engine 5 cinematic render, glowing blue rim light, 8k vertical 9:16",
                "visual_prompt": "10mm ultra-wide lens tracking pan of young man walking past frozen pedestrians with floating coffee droplets, 8k",
            },
            {
                "scene_number": 3,
                "narration": "Within ten seconds, sheer terror sets in. Light photons stop moving, instantly plunging your vision into pitch-black darkness.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "pop",
                "camera_motion": "vertical-tilt-reveal",
                "video_prompt": "35mm prime lens macro close-up, young man reacting with wide eyes in shock, reaching upward with trembling hands as pitch darkness creeps across his face, light beams freezing like solid luminescent glass rods, volumetric cyan lighting, ray tracing, 8k vertical 9:16",
                "visual_prompt": "35mm prime lens close up of young man reacting in shock reaching upward as darkness creeps across face, 8k",
            },
            {
                "scene_number": 4,
                "narration": "Oxygen molecules freeze in place like solid glass, meaning your lungs cannot pull a single breath of air.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "dramatic-pulse",
                "camera_motion": "dramatic-pulse",
                "video_prompt": "50mm cinema lens medium shot, young man clutching throat gasping for breath, glowing blue frost crystals forming around mouth as frozen air resists inhalation, collapsing to one knee on frozen asphalt street, shattered temporal clock above, Unreal Engine 5 render, 8k vertical 9:16",
                "visual_prompt": "50mm cinema lens medium shot of young man clutching throat collapsing to one knee on frozen street, 8k",
            },
            {
                "scene_number": 5,
                "narration": "The colossal temporal clock in the sky shatters violently, proving that freezing time won't make you a god—it will erase you.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "climax-pull-back",
                "camera_motion": "climax-pull-back",
                "video_prompt": "10mm wide-angle epic scope pull-back shot, giant shattered Roman-numeral clock in the sky vibrating violently, clock hands fracturing into blinding cyan sparks, temporal shockwaves sweeping across the frozen city, cinematic masterpiece, Unreal Engine 5 render, 8k vertical 9:16",
                "visual_prompt": "10mm wide-angle pull-back shot of giant shattered clock in sky vibrating and fracturing into sparks over frozen city, 8k",
            },
        ]

    # Archetype 2: Gravity Vanished for 60 Seconds
    elif any(k in t_lower for k in ["gravity", "vanished", "60 seconds", "weightless"]):
        banner = "IF GRAVITY TURNED OFF FOR 60 SECONDS..."
        char_dna = "Young athletic man in a black streetwear flight jacket and dark cargo pants with wide terrified eyes"
        vis_anchor = "A colossal metropolis violently ascending into outer space, skyscrapers ripping from bedrock, blue volumetric atmospheric lighting, 8k"

        scenes = [
            {
                "scene_number": 1,
                "narration": "What if Earth's gravity suddenly switched off for exactly sixty seconds?",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "impact_boom",
                "camera_motion": "smooth-zoom-in",
                "video_prompt": "24mm anamorphic wide angle shot, low-angle perspective, young man in flight jacket floating helplessly upward as asphalt street cracks, yellow taxis and pedestrians tumbling into the sky, volumetric rim lighting, Unreal Engine 5 render, 8k vertical 9:16",
                "visual_prompt": "24mm anamorphic shot of young man floating upward as cars and city street lift into sky, 8k",
            },
            {
                "scene_number": 2,
                "narration": "Because Earth spins at one thousand miles an hour, everything not bolted down instantly catapults eastward into the stratosphere.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": "10mm ultra-wide tracking pan shot, entire ocean bays and skyscrapers tearing from bedrock, swirling violently through the troposphere, catastrophic cosmic scale, Unreal Engine 5 render, 8k vertical 9:16",
                "visual_prompt": "10mm ultra-wide shot of ocean waves and skyscrapers tearing upward into clouds, 8k",
            },
            {
                "scene_number": 3,
                "narration": "Atmospheric air pressure violently decompresses, causing everyone's eardrums to pop as oxygen rushes toward outer space.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "pop",
                "camera_motion": "vertical-tilt-reveal",
                "video_prompt": "35mm prime macro shot, young man gasping in terror, hands reaching to cover ears as vapor clouds swirl around his face, drifting helplessly past cloud formations, 8k vertical 9:16",
                "visual_prompt": "35mm prime shot of young man reaching to cover ears as clouds swirl past in upper atmosphere, 8k",
            },
            {
                "scene_number": 4,
                "narration": "Then, at second sixty, gravity violently slams back on. Everything drops forty miles straight down at supersonic speeds.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "dramatic-pulse",
                "camera_motion": "dramatic-pulse",
                "video_prompt": "50mm cinema lens medium shot, young man plummeting downward at supersonic speed, shockwave condensation cone forming around body, city horizon rushing upward, Unreal Engine 5 render, 8k vertical 9:16",
                "visual_prompt": "50mm cinema shot of person plummeting downward toward Earth at terminal velocity, 8k",
            },
            {
                "scene_number": 5,
                "narration": "The impact shockwave shatters continents, proving that even sixty seconds without gravity is an absolute global extinction.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "climax-pull-back",
                "camera_motion": "climax-pull-back",
                "video_prompt": "10mm wide-angle epic scope pull-back shot, colossal continent-wide impact shockwave radiating across Earth from orbit, blinding glowing debris sweeping across the globe, Unreal Engine 5 cinematic render, 8k vertical 9:16",
                "visual_prompt": "10mm wide-angle orbital view of continent-wide shockwave sweeping across Earth, 8k",
            },
        ]

    # Archetype 3: Falling into Jupiter's Atmosphere
    elif any(k in t_lower for k in ["jupiter", "fall", "astronaut", "giant planet"]):
        banner = "WHAT IF AN ASTRONAUT FELL INTO JUPITER?"
        char_dna = "Astronaut in sleek matte-white NASA deep-space EVA suit with neon-amber shoulder striping and a reflective gold-mirrored visor"
        vis_anchor = "Jupiter colossal crimson vortex atmosphere, violent electrical storm lighting, Unreal Engine 5 render, 8k"

        scenes = [
            {
                "scene_number": 1,
                "narration": "What if you jumped out of a spacecraft directly into Jupiter's storm clouds?",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "impact_boom",
                "camera_motion": "smooth-zoom-in",
                "video_prompt": "10mm ultra-wide lens long shot, astronaut in white EVA suit falling headfirst into colossal swirling crimson Jupiter clouds, violent lightning storms sweeping across the vortex, Unreal Engine 5 render, 8k vertical 9:16",
                "visual_prompt": "10mm long shot of astronaut falling headfirst into Jupiter colossal storm clouds, 8k",
            },
            {
                "scene_number": 2,
                "narration": "You accelerate past one hundred thousand miles an hour, plunging through ammonia ice clouds into pitch-black hurricane winds.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": "24mm anamorphic lens tracking pan, astronaut plunging through towering white ammonia clouds, friction sparks flying off titanium suit, dramatic atmospheric depth, Unreal Engine 5 render, 8k vertical 9:16",
                "visual_prompt": "24mm tracking pan of astronaut plunging through thick ammonia cloud wall, 8k",
            },
            {
                "scene_number": 3,
                "narration": "Seven hundred miles deep, atmospheric pressure sky-rockets until trillions of tons of diamond hail start pelting your suit.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "pop",
                "camera_motion": "vertical-tilt-reveal",
                "video_prompt": "35mm prime macro shot, shimmering jagged diamond hail crystals striking the reflective gold helmet visor, astronaut reaching out gloved hand in awe, electrical storm glow, 8k vertical 9:16",
                "visual_prompt": "35mm macro shot of sparkling diamond hail bouncing off astronaut gold helmet visor, 8k",
            },
            {
                "scene_number": 4,
                "narration": "The air becomes so dense that you stop falling, floating suspended inside an endless ocean of boiling liquid metallic hydrogen.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "dramatic-pulse",
                "camera_motion": "dramatic-pulse",
                "video_prompt": "50mm cinema lens medium shot, astronaut floating suspended inside a shimmering metallic liquid ocean, suit thrusters flickering, crushing depth shadows, Unreal Engine 5 render, 8k vertical 9:16",
                "visual_prompt": "50mm cinema shot of astronaut floating in glowing metallic liquid hydrogen sea, 8k",
            },
            {
                "scene_number": 5,
                "narration": "Millions of atmospheres of pressure finally dissolve your titanium armor, permanently integrating your atoms into Jupiter's molten core.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "climax-pull-back",
                "camera_motion": "climax-pull-back",
                "video_prompt": "10mm wide-angle epic scope pull-back shot, astronaut silhouette dissolving into blinding golden thermal core of Jupiter, colossal plasma energy vortex sweeping inward, Unreal Engine 5 render, 8k vertical 9:16",
                "visual_prompt": "10mm wide-angle pull-back of astronaut silhouette dissolving in Jupiter molten glowing core, 8k",
            },
        ]

    # Archetype 4: Universal High-Concept English Mystery
    else:
        banner = topic[:55].upper()
        char_dna = "Curious determined young protagonist in modern dark streetwear jacket with expressive eyes and sharp modern styling"
        vis_anchor = "Dramatic cinematic environment with high-contrast volumetric rim lighting and atmospheric depth, Unreal Engine 5 render, 8k"

        scenes = [
            {
                "scene_number": 1,
                "narration": f"Did you know that {topic.lower()} holds a secret that scientists could not explain for decades?",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "impact_boom",
                "camera_motion": "smooth-zoom-in",
                "video_prompt": f"24mm anamorphic wide angle shot, low-angle perspective, {char_dna} stepping forward into dramatic mysterious environment, hand outstretched in extreme foreshortening, volumetric god rays, Unreal Engine 5 render, 8k vertical 9:16",
                "visual_prompt": f"24mm anamorphic shot of {char_dna} stepping forward into mysterious dramatic environment, 8k",
            },
            {
                "scene_number": 2,
                "narration": f"At first glance, {hook_premise[:60] if hook_premise else 'the phenomenon seemed completely impossible according to classical physics'}.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": f"10mm ultra-wide tracking pan shot, {char_dna} walking calmly past swirling glowing energy fields, dramatic depth, Unreal Engine 5 cinematic render, 8k vertical 9:16",
                "visual_prompt": f"10mm tracking pan of {char_dna} walking past glowing atmospheric phenomenon, 8k",
            },
            {
                "scene_number": 3,
                "narration": "When researchers inspected the molecular structure, the fundamental laws of nature completely broke down.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "pop",
                "camera_motion": "vertical-tilt-reveal",
                "video_prompt": f"35mm prime macro shot, {char_dna} reacting with wide eyes in shock, reaching upward as glowing quantum particles shatter into luminescent sparks, 8k vertical 9:16",
                "visual_prompt": f"35mm macro shot of {char_dna} reaching toward glowing shattering particles in shock, 8k",
            },
            {
                "scene_number": 4,
                "narration": "The energetic reaction accelerated exponentially, threatening to trigger an irreversible cascade across the entire containment field.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "dramatic-pulse",
                "camera_motion": "dramatic-pulse",
                "video_prompt": f"50mm cinema lens medium shot, {char_dna} clutching control console as violent energy shockwaves sweep the laboratory chamber, Unreal Engine 5 render, 8k vertical 9:16",
                "visual_prompt": f"50mm cinema shot of {char_dna} clutching console in glowing energy storm, 8k",
            },
            {
                "scene_number": 5,
                "narration": "This mind-bending discovery proved that reality itself is far more terrifying than anyone ever dared to imagine.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "sfx": "climax-pull-back",
                "camera_motion": "climax-pull-back",
                "video_prompt": f"10mm wide-angle epic scope pull-back shot, colossal glowing portal fracturing into brilliant blinding sparks, {char_dna} silhouetted against the cosmic light, Unreal Engine 5 render, 8k vertical 9:16",
                "visual_prompt": f"10mm wide-angle pull-back of glowing cosmic portal fracturing into sparks, 8k",
            },
        ]

    total_words = sum(len(sc["narration"].split()) for sc in scenes)
    loop_lead = scenes[-1]["narration"][:45]

    return {
        "episode_title": clean_title,
        "top_hook_banner": banner,
        "hook_headline": clean_title[:20],
        "character_dna": char_dna,
        "visual_anchor": vis_anchor,
        "total_words_count": total_words,
        "loop_lead_in": loop_lead,
        "scenes": scenes,
        "beats": scenes,
        "seo_tags": ["viral", "reels", "shorts", "whatif", "scifi", "paradox", "cinematic", "trending"],
        "hashtags": ["#shorts", "#viral", "#reels", "#whatif", "#scifi", "#trending"],
        "pinned_comment": "What would you do in this situation? Comment below! 👇 Subscribe for daily mysteries! 🚀"
    }
