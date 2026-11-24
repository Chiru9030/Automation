"""
Stage 2: Rapid-Cut Viral Script Engine (The 2-Second Visual Rule).
Generates high-retention, dynamic scripts matching the pace of top viral reels (e.g. @agovindmenon):
- 12 to 16 rapid visual cuts (scenes) lasting 1.8 to 2.4 seconds each.
- Total spoken words: 95 to 135 words (yielding exactly 30 to 42 seconds of total video).
- Persistent 'top_hook_banner' context headline anchored at the top throughout the entire video.
- Two-speaker alternating dialogue / banter or rapid-fire narrative shifts.
- Distinct 3D Pixar / cinema-grade visual prompt for EVERY single cut.
- Sound effects (whoosh, pop, impact_boom) synchronized to every 2-second visual cut.
"""

import json
import os
import time
import concurrent.futures
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TARGET_DURATION_SECONDS = 36.0  # High-retention sweet spot for YouTube Shorts & Instagram Reels


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
    Generates a rapid-cut (12 to 16 scenes) viral script designed for modern high-retention reels.
    Every scene changes visual and dialogue every 1.8 - 2.4 seconds with a persistent top hook banner.
    """
    topic = topic_data["topic"]
    hook_premise = topic_data.get("hook_premise", "")
    category = topic_data.get("category", "Curiosity")
    style = topic_data.get("style", "3D Pixar animation")
    ep_num = topic_data.get("episode", 1)
    banner = topic_data.get("top_hook_banner") or topic[:55]

    t_lower = topic.lower()
    # High-Priority Precision Archetypes for Viral Instagram Recreations (@riddlelantern & @gutter.gyan)
    if any(k in t_lower for k in ["nakli", "note", "golu", "samosa", "riddle", "paheli", "jungle", "lion", "sher", "don"]):
        print(f"🎬 [Script Engine] Prioritizing Curated 2D Vector Cartoon Archetype for '{topic}'...")
        proc_script = generate_procedural_script(topic, hook_premise, style, ep_num, banner=banner)
        if topic_data.get("riddle_options") and not proc_script.get("riddle_options"):
            proc_script["riddle_options"] = topic_data.get("riddle_options")
        return ensure_video_prompts_and_motion(proc_script)

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=30000))

            prompt = f"""You are an elite short-form video director for Instagram Reels, YouTube Shorts, and TikTok.
Write a fast-paced, high-retention video script with RAPID VISUAL CUTS (Every 2 seconds cuts to a new image, like viral Instagram skits & breakdowns).

TOPIC: {topic}
PREMISE: {hook_premise}
TOP HOOK BANNER: {banner}
CATEGORY: {category}
VISUAL ART STYLE: {style}
EPISODE: #{ep_num}

CRITICAL PACING & VISUAL RULES (THE 2-SECOND RULE):
1. RAPID SCENE CUTS:
   - You MUST generate between 12 and 16 discrete scenes (cuts).
   - Each scene MUST contain strictly 6 to 11 spoken words (spoken in 1.8 to 2.4 seconds).
   - TOTAL SPOKEN WORDS across all scenes: STRICTLY BETWEEN 95 AND 135 WORDS (Total video duration 30-42 seconds).
   - NEVER generate only 5 long beats. Every 2 seconds MUST have a new cut!
2. PERSISTENT TOP HOOK BANNER:
   - Provide "top_hook_banner": "{banner}" (bold, catchy headline, under 55 characters).
3. TWO-SPEAKER DIALOGUE / BANTER:
   - Alternate the "speaker" between "speaker_1" (Creator / Protagonist / Host) and "speaker_2" (Brand / Anomaly / Character / Specialist) for dynamic comedic or dramatic back-and-forth.
4. INVARIANT CHARACTER DNA & VISUAL ANCHOR:
   - Define "character_dna": explicit visual appearance of the central protagonist.
   - Define "visual_anchor": lighting, palette, and environment.
5. DISTINCT PROMPTS FOR EVERY SINGLE SCENE (A NEW IMAGE EVERY 2 SECONDS):
   - For EVERY scene, write a distinct 'video_prompt' and 'visual_prompt'.
   - Describe close-up facial reactions, absurd objects, contrasting viewpoints, and dynamic body movement.
   - Include camera lens tokens: 10mm ultra-wide, 24mm tracking pan, 35mm portrait, 50mm close-up, anamorphic.
   - Include active motion verbs: falling, tumbling, gesturing, holding, pointing, reacting, lunging, drifting.
   - Assign camera_motion: "rapid-push-in-shake", "smooth-lateral-pan-right", "vertical-tilt-reveal", "climax-pull-back", "loop-convergence-zoom".
   - Assign sfx: "whoosh", "pop", "impact_boom", or "whip_pan".

Output JSON ONLY:
{{
  "episode_title": "{topic.upper()[:28]}",
  "top_hook_banner": "{banner}",
  "hook_headline": "VIRAL HOOK (3-4 WORDS)",
  "character_dna": "Detailed invariant protagonist description",
  "visual_anchor": "Unified environment and lighting palette",
  "total_words_count": 115,
  "loop_lead_in": "Last sentence connecting into Scene 1",
  "scenes": [
    {{
      "scene_number": 1,
      "beat_number": 1,
      "time_window": "0-2s",
      "hook_trigger": "Opening Hook",
      "narration": "First punchy line grabbing curiosity (7-10 words)",
      "speaker": "speaker_1",
      "speaker_name": "Host",
      "speaker_avatar": "🎙️",
      "sfx": "pop",
      "camera_motion": "rapid-push-in-shake",
      "video_prompt": "Close-up 24mm anamorphic shot, [character_dna] reacting with wide eyes in shock, looking down at smartphone, 3D Pixar character design, cinematic rim lighting, 8k render",
      "visual_prompt": "24mm anamorphic close up shot of [character_dna] looking shocked at smartphone, 3D Pixar, 8k"
    }},
    ... (12 to 16 scenes total, each strictly 6-11 words)
  ],
  "seo_tags": ["viral", "reels", "shorts", "comedy", "whatif", "relatable", "funny", "animation", "trending"],
  "hashtags": ["#shorts", "#viral", "#reels", "#relatable", "#trending"],
  "pinned_comment": "Drop your thoughts below! 👇 Subscribe for daily viral drops! 🚀"
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
                            if 10 <= len(scenes_check) <= 18:
                                wc = sum(len(s.get('narration', '').split()) for s in scenes_check)
                                if 80 <= wc <= 145:
                                    active_model = candidate_model
                                    break
                                else:
                                    print(f"⚠️ [Script Engine] {candidate_model} generated {wc} words (expected 80-145). Retrying...")
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
                if 10 <= len(scenes) <= 18:
                    data["scenes"] = scenes
                    data["beats"] = scenes
                    if not data.get("top_hook_banner"):
                        data["top_hook_banner"] = banner
                    word_count = sum(len(s.get('narration', '').split()) for s in scenes)
                    print(f"📝 [Stage 2: Script Engine] Gemini AI ({active_model}) synthesized {len(scenes)} rapid-cut scenes for '{topic}' ({word_count} words)")
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
                    {"role": "system", "content": "You are an elite viral short-form director. Output JSON with 12-16 rapid visual scenes, top_hook_banner, video_prompt, and camera_motion for every scene."},
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
                    if 10 <= len(scenes) <= 18:
                        g_data["scenes"] = scenes
                        g_data["beats"] = scenes
                        if not g_data.get("top_hook_banner"):
                            g_data["top_hook_banner"] = banner
                        w_count = sum(len(s.get('narration', '').split()) for s in scenes)
                        print(f"📝 [Stage 2: Script Engine] Groq AI synthesized {len(scenes)} rapid-cut scenes for '{topic}' ({w_count} words)")
                        try:
                            from story_pipeline.telegram_notifier import RUN_TRACKER
                            RUN_TRACKER.set_model_used("Script", "Groq (llama-3.3-70b-versatile)")
                        except Exception:
                            pass
                        return ensure_video_prompts_and_motion(g_data)
        except Exception as e_groq:
            print(f"Notice: Groq script generation note: {e_groq}")

    # Tertiary Fallback: High-Quality Procedural Rapid-Cut Script
    try:
        from story_pipeline.telegram_notifier import RUN_TRACKER
        RUN_TRACKER.set_model_used("Script", "Procedural Rapid-Cut Engine")
    except Exception:
        pass
    return ensure_video_prompts_and_motion(generate_procedural_script(topic, hook_premise, style, ep_num, banner=banner))


def ensure_video_prompts_and_motion(script_data: dict) -> dict:
    """Guarantees every scene carries invariant character DNA, explicit lens optics, and physical kinematics."""
    topic = script_data.get("episode_title") or script_data.get("topic") or "Viral Reel"
    t_lower = topic.lower()

    is_2d = any(k in t_lower or k in str(script_data.get("style", "")).lower() or k in str(script_data.get("category", "")).lower() for k in ["2d", "cartoon", "vector", "paheli", "riddle", "fable", "storybook", "chibi", "comic", "nakli", "note", "golu", "samosa", "lion", "jungle", "sher"])

    char_dna = script_data.get("character_dna", "")
    vis_anchor = script_data.get("visual_anchor", "")

    if not char_dna or len(char_dna.strip()) < 20:
        if is_2d:
            if any(k in t_lower for k in ["lion", "jungle", "sher", "don"]):
                char_dna = "Cute unimpressed 2D cartoon lion king wearing a golden crown sitting on an ornate wooden throne, thick clean black outlines, storybook aesthetic, vibrant flat colors, deadpan comic gaze"
                vis_anchor = "Lush vibrant 2D cartoon jungle foliage with sunburst background rays and floating green leaves, children's storybook flat vector illustration, 9:16 vertical"
            else:
                char_dna = "Chibi 2D cartoon Indian street vendor with white chef cap, colorful apron, expressive cartoon mustache and comical sweat drops"
                vis_anchor = "Vibrant Indian street food stall GOLU SAMOSA CORNER, sizzling golden samosas in glass display, thick clean black outlines, storybook flat 2D vector illustration, 9:16 vertical"
        elif any(k in t_lower for k in ["brand", "comment", "reels", "friend", "instagram", "phone", "social media", "skit", "comedy"]):
            char_dna = "Expressive young man in casual streetwear with colorful stylish jacket and modern haircut, comedic animated expressions"
            vis_anchor = "Vibrant modern studio apartment with warm neon LED ambient lighting, glowing smartphone screen reflections, 3D Pixar film render, 8k"
        elif any(k in t_lower for k in ["space", "jupiter", "saturn", "moon", "cosmic", "black hole", "astronaut"]):
            char_dna = "Astronaut in sleek matte-white NASA deep-space EVA suit with neon-amber shoulder striping and a reflective gold-mirrored visor"
            vis_anchor = "Jupiter colossal crimson vortex atmosphere, violent electrical storm lighting, Unreal Engine 5 render, 8k"
        elif any(k in t_lower for k in ["brain", "sleep", "dream", "overthink", "bed"]):
            char_dna = "Relatable young protagonist in comfortable pajamas looking comical and exhausted, wide expressive eyes"
            vis_anchor = "Cozy nighttime bedroom illuminated by cool blue moonlight and glowing alarm clock digits, 3D Pixar comedy aesthetic"
        else:
            char_dna = "Curious charismatic protagonist with vibrant styling and highly expressive features"
            vis_anchor = "Cinematic dramatic atmospheric environment, high-contrast volumetric lighting, Unreal Engine 5 render, 8k"

    script_data["character_dna"] = char_dna
    script_data["visual_anchor"] = vis_anchor

    scenes = script_data.get("scenes") or script_data.get("beats", [])
    script_data["scenes"] = scenes
    script_data["beats"] = scenes

    if not script_data.get("top_hook_banner"):
        script_data["top_hook_banner"] = topic[:55]

    cam_cycle = [
        "rapid-push-in-shake",
        "smooth-lateral-pan-right",
        "vertical-tilt-reveal",
        "climax-pull-back",
        "loop-convergence-zoom",
        "pan-right",
        "dramatic-pulse",
        "warm-dolly",
    ]

    lens_cycle = [
        "10mm ultra-wide lens, dynamic push-in shot",
        "24mm anamorphic lens, low-angle tracking shot",
        "35mm prime lens, expressive reaction portrait",
        "50mm cinema lens, medium conversational framing",
        "85mm portrait lens, tight macro reaction close-up",
    ]

    kinematics_cycle = [
        "reacting with wide eyes and pointing at screen",
        "gesturing in humorous disbelief as hands fly into frame",
        "turning quickly toward camera with comedic shock",
        "holding up prop with triumphant hilarious grin",
        "stumbling backward in comical bewilderment",
        "leaning into camera with exaggerated conspiratorial whisper",
        "shaking head with hands on cheeks in absolute disbelief",
    ]

    lens_tokens = ["10mm", "12mm", "14mm", "16mm", "24mm", "28mm", "35mm", "50mm", "85mm", "anamorphic", "ultra-wide", "macro", "telephoto"]
    kinematics_tokens = [
        "falling", "fall", "tumbling", "tumble", "plunging", "plunge", "surging", "surge",
        "reacting", "react", "gesturing", "gesture", "holding", "hold", "pointing", "point",
        "turning", "turn", "shaking", "shake", "stumbling", "stumble", "leaning", "lean",
        "lunging", "lunge", "moving", "move", "running", "run", "drifting", "drift", "spinning", "spin",
        "looking", "look", "stepping", "step", "walking", "walk", "reaching", "reach"
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

        if is_2d:
            sc["style"] = "Flat 2D vector cartoon, thick clean black outlines, storybook aesthetic, zero photorealism, zero 3D"
            if vp and ("2d" in vp.lower() or "cartoon" in vp.lower() or "vector" in vp.lower()):
                # Preserve existing high-quality 2D prompt while guaranteeing lens and kinematics for auditor
                if not has_lens:
                    vp = f"{lens_spec}, {vp}"
                if not has_kine:
                    vp = f"{vp}, {motion_spec}"
                sc["video_prompt"] = vp
            else:
                cam = sc.get("camera_motion")
                sc["video_prompt"] = (
                    f"Flat 2D vector cartoon, {lens_spec}, cute chibi {char_dna} {motion_spec}, "
                    f"set in {vis_anchor}, thick clean black outlines, storybook aesthetic, "
                    f"vibrant flat colors, clean flat cell shading, zero 3D, zero photorealism, 9:16 vertical"
                )
            if not sc.get("visual_prompt"):
                sc["visual_prompt"] = f"Flat 2D vector cartoon illustration of {char_dna}, {motion_spec}, {vis_anchor}, 9:16"
        else:
            if not vp or not has_lens or not has_kine or not has_dna:
                cam = sc.get("camera_motion")
                sc["video_prompt"] = (
                    f"Cinematic {cam} camera motion, {lens_spec}, {char_dna} {motion_spec}, "
                    f"set in {vis_anchor}, volumetric atmospheric god rays, ray tracing, 3D Pixar render, 8k resolution"
                )
            if not sc.get("visual_prompt"):
                sc["visual_prompt"] = f"{lens_spec} of {char_dna}, {motion_spec}, {vis_anchor}, 8k render"

        if not sc.get("sfx"):
            sc["sfx"] = "pop" if sc_num % 2 == 1 else "whoosh"

    return script_data


def generate_procedural_script(topic: str, hook_premise: str, style: str, ep_num: int, banner: str = "") -> dict:
    """Builds a guaranteed 14 to 15 scene rapid-cut viral script matching the @agovindmenon pacing (32-38s)."""
    clean_title = topic.upper()[:28]
    t_lower = topic.lower()

    if not banner:
        banner = topic[:55]

    riddle_options = None

    # Archetype 0: Indian Paheli / Counterfeit Note Math Riddle Skit (@riddlelantern format)
    if any(k in t_lower for k in ["nakli", "note", "golu", "samosa", "riddle", "paheli", "paheliyan", "puzzle", "loss", "nuksaan"]):
        char_dna = "Chibi 2D cartoon Indian street vendor with white chef cap, colorful apron, expressive cartoon mustache and comical sweat drops"
        vis_anchor = "Vibrant Indian street food stall GOLU SAMOSA CORNER, sizzling golden samosas in glass display, thick clean black outlines, storybook flat 2D vector illustration, 9:16 vertical"
        banner = "GOLU SAMOSA CORNER: KUL NUKSAAN KITNA HUA?"
        riddle_options = ["₹200", "₹500", "₹800", "₹1000"]

        scenes = [
            {
                "scene_number": 1,
                "narration": "Ek nakli note ne Golu ke papa ka poora din bigaad diya!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "impact_boom",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": "Flat 2D vector cartoon, cute chibi Indian samosa shopkeeper holding a 500 rupee note marked NAKLI with shocked face and sweat drops, Golu Samosa Corner signboard, thick black outlines, storybook aesthetic, vibrant saturated colors, 9:16 vertical",
                "visual_prompt": "Flat 2D vector cartoon of cute Indian shopkeeper shocked holding fake 500 note, thick outlines, 9:16",
            },
            {
                "scene_number": 2,
                "narration": "Subah-subah pehla customer aaya aur bola, do sau rupaye ke garam samose do!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": "Flat 2D vector cartoon, hungry customer in bright green kurta pointing at sizzling golden triangular samosas inside display counter, cute shopkeeper smiling, clean flat art, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon customer ordering samosas at street food counter, vibrant colors, 9:16",
            },
            {
                "scene_number": 3,
                "narration": "Customer ne paanch sau ka note thama diya, par dukan mein chutta nahi tha!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "pop",
                "camera_motion": "dramatic-pulse",
                "video_prompt": "Flat 2D vector cartoon, customer hand extending a crisp 500 rupee banknote across counter, shopkeeper opening wooden cash drawer showing zero change, comical panic expression, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon hand giving 500 note to shopkeeper with empty drawer, 9:16",
            },
            {
                "scene_number": 4,
                "narration": "Papa bagal wale kirana chacha ke paas gaye aur paanch sau ka chutta karwake laaye!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": "Flat 2D vector cartoon, shopkeeper hurrying to neighboring grocery shop counter where an elderly Indian uncle with glasses happily exchanges 500 note for hundred rupee bills, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon shopkeeper exchanging 500 note with neighbor uncle, 9:16",
            },
            {
                "scene_number": 5,
                "narration": "Customer ko do sau ke samose aur teen sau rupaye cash wapas de diya!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "pop",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": "Flat 2D vector cartoon, shopkeeper handing customer a steaming brown paper bag of samosas and three crisp 100 rupee notes, customer smiling cheekily, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon shopkeeper handing samosa bag and 300 cash to customer, 9:16",
            },
            {
                "scene_number": 6,
                "narration": "Customer muskurate hue garam samose leke market mein gayab ho gaya!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "climax-pull-back",
                "video_prompt": "Flat 2D vector cartoon, customer walking away briskly into sunny vibrant Indian street market with steam wafting from bag, shopkeeper waving peacefully, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon customer walking away fast into market alley with samosas, 9:16",
            },
            {
                "scene_number": 7,
                "narration": "Do ghante baad, bagal wale chacha gusse mein laal-peele daudte hue aaye!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "impact_boom",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": "Flat 2D vector cartoon, angry neighboring uncle with red face storming into Golu Samosa stall, steam venting from ears in anime style, pointing angrily, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon angry neighbor uncle marching with furious expression, 9:16",
            },
            {
                "scene_number": 8,
                "narration": "Chacha chillaye: arey bhai, yeh paanch sau ka note toh bilkul nakli nikla!",
                "speaker": "speaker_2",
                "speaker_name": "Chacha",
                "speaker_avatar": "👴",
                "sfx": "pop",
                "camera_motion": "dramatic-pulse",
                "video_prompt": "Flat 2D vector cartoon, extreme close-up of 500 banknote with giant red diagonal stamp reading NAKLI, uncle holding it with furious glare, thick outlines, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon close-up of fake 500 rupee note stamped NAKLI, 9:16",
            },
            {
                "scene_number": 9,
                "narration": "Mera paanch sau rupaye asli cash abhi ke abhi wapas karo!",
                "speaker": "speaker_2",
                "speaker_name": "Chacha",
                "speaker_avatar": "👴",
                "sfx": "whoosh",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": "Flat 2D vector cartoon, angry uncle thrusting open palm forward demanding his money back at the samosa counter, shopkeeper sweating in terror, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon uncle demanding real cash with outstretched hand, 9:16",
            },
            {
                "scene_number": 10,
                "narration": "Golu ke papa ko majboori mein apni jeb se paanch sau asli rupaye dene pade!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": "Flat 2D vector cartoon, devastated shopkeeper reluctantly pulling 500 real cash from personal wallet and handing to uncle, comic waterfall tears streaming, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon sad shopkeeper handing 500 real cash to uncle, 9:16",
            },
            {
                "scene_number": 11,
                "narration": "Ab dukan band karke Golu ke papa sar pakad kar sochte reh gaye!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "dramatic-pulse",
                "camera_motion": "dramatic-pulse",
                "video_prompt": "Flat 2D vector cartoon, shopkeeper sitting on wooden stool holding head with both hands, three giant question marks orbiting his head, empty samosa trays, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon shopkeeper sitting on stool clutching head in deep thought, 9:16",
            },
            {
                "scene_number": 12,
                "narration": "Samose bhi gaye, cash bhi gaya, poora din barbaad ho gaya!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "climax-pull-back",
                "video_prompt": "Flat 2D vector cartoon, shopkeeper looking at a calculator with smoke puffing out, floating math equations and torn fake note on floor, dramatic storybook lighting, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon shopkeeper looking at calculator with funny smoke puffs, 9:16",
            },
            {
                "scene_number": 13,
                "narration": "Toh aakhir Golu ke papa ka kul nuksaan kitna hua?",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "impact_boom",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": "Flat 2D vector cartoon, giant glowing golden question mark above Golu Samosa Corner, shopkeeper pointing forward at the viewer with suspenseful expression, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon shopkeeper pointing at viewer under giant glowing question mark, 9:16",
            },
            {
                "scene_number": 14,
                "narration": "Option A do sau, B paanch sau, C aath sau, ya D hazaar rupaye? Comment your answer!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "loop-convergence-zoom",
                "camera_motion": "loop-convergence-zoom",
                "video_prompt": "Flat 2D vector cartoon, vibrant multiple choice quiz card hovering in center displaying options A 200, B 500, C 800, D 1000, shopkeeper waiting eagerly for comments, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon multiple choice options board A 200 B 500 C 800 D 1000, 9:16",
            },
        ]

    # Archetype 0B: Jungle Ka Asli Don (Lion King on Golden Throne Fable Comedy - @gutter.gyan format)
    elif any(k in t_lower for k in ["jungle", "lion", "sher", "don", "king", "fable"]):
        char_dna = "Cute unimpressed 2D cartoon lion king wearing a golden crown sitting on an ornate wooden throne, thick clean black outlines, storybook aesthetic, vibrant flat colors, deadpan comic gaze"
        vis_anchor = "Lush vibrant 2D cartoon jungle foliage with sunburst background rays and floating green leaves, children's storybook flat vector illustration, 9:16 vertical"
        banner = "JUNGLE KA ASLI DON: WHO RULES THE WILD?"
        riddle_options = ["Sher 🦁", "Haathi 🐘", "Bhalu 🐻", "Bandar 🐒"]

        scenes = [
            {
                "scene_number": 1,
                "narration": "Kya jungle ka asli don sher hi hai? Dekho!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "impact_boom",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": "Flat 2D vector cartoon, cute unimpressed cartoon lion king wearing a golden crown sitting on an ornate throne in lush jungle, 10mm ultra-wide lens, dynamic push-in shot, animals arguing in background, thick clean black outlines, storybook aesthetic, vibrant flat colors, 9:16 vertical",
                "visual_prompt": "Flat 2D vector cartoon, cute lion king with crown on throne looking unimpressed, jungle foliage, thick black outlines, 9:16",
            },
            {
                "scene_number": 2,
                "narration": "Sher apne takht par baitha bore ho raha tha.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": "Flat 2D vector cartoon, deadpan cartoon lion king resting chin on paw looking sideways with bored half-open eyes, 24mm tracking pan, golden crown tilted, sunburst background rays, thick black outlines, storybook aesthetic, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon lion king resting chin on paw bored on throne, 9:16",
            },
            {
                "scene_number": 3,
                "narration": "Bhalu bola: 'Mera panja sabse zyada bhaari hai!'",
                "speaker": "speaker_2",
                "speaker_name": "Bhalu",
                "speaker_avatar": "🐻",
                "sfx": "pop",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": "Flat 2D vector cartoon, giant comical cartoon brown bear slamming massive furry paw on a jungle rock with aggressive roar, 35mm prime lens, dust flying, thick black outlines, vibrant colors, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon brown bear slamming heavy paw on rock roaring, 9:16",
            },
            {
                "scene_number": 4,
                "narration": "Bandar chilla: 'Main sabse tez aur chatur hoon!'",
                "speaker": "speaker_2",
                "speaker_name": "Bandar",
                "speaker_avatar": "🐒",
                "sfx": "pop",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": "Flat 2D vector cartoon, cheeky cartoon monkey hanging upside down by tail from jungle vine waving a banana and mocking, 24mm low-angle shot, thick clean outlines, vibrant saturated colors, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon monkey hanging by tail mocking with banana, 9:16",
            },
            {
                "scene_number": 5,
                "narration": "Haathi ne soond utha kar zor se dahaad di!",
                "speaker": "speaker_2",
                "speaker_name": "Haathi",
                "speaker_avatar": "🐘",
                "sfx": "impact_boom",
                "camera_motion": "vertical-tilt-reveal",
                "video_prompt": "Flat 2D vector cartoon, colossal cute cartoon elephant raising long trunk high trumpeting loudly, 10mm ultra-wide low angle shot, ground trembling shockwaves, thick black outlines, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon elephant trumpeting with raised trunk, 9:16",
            },
            {
                "scene_number": 6,
                "narration": "Lomdi muskuraayi: 'Asli dimaag toh sirf mere paas hai!'",
                "speaker": "speaker_2",
                "speaker_name": "Lomdi",
                "speaker_avatar": "🦊",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": "Flat 2D vector cartoon, sly cartoon orange fox tapping forehead with paw and winking with cunning smile, 35mm prime reaction shot, thick clean black outlines, storybook aesthetic, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon sly fox tapping forehead winking, 9:16",
            },
            {
                "scene_number": 7,
                "narration": "Sher ne aadhi aankh kholi aur sabko ghoora.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "dramatic-pulse",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": "Flat 2D vector cartoon, intense extreme close up 50mm cinema lens of cartoon lion king golden eyes narrowing into piercing royal gaze, golden crown glinting, thick black outlines, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon close up of lion king golden eyes staring sharply, 9:16",
            },
            {
                "scene_number": 8,
                "narration": "Ek pal mein poora jungle bilkul shaant ho gaya!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "climax-pull-back",
                "video_prompt": "Flat 2D vector cartoon, bear, elephant, monkey and fox all freezing in terror with comical sweat drops and wide eyes, 24mm wide angle shot, thick clean outlines, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon animals frozen in silence with sweat drops, 9:16",
            },
            {
                "scene_number": 9,
                "narration": "Sher bola: 'Dahaadna toh kamzoron ka kaam hai!'",
                "speaker": "speaker_1",
                "speaker_name": "Sher Raja",
                "speaker_avatar": "🦁",
                "sfx": "pop",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": "Flat 2D vector cartoon, lion king on golden throne calmly waving one front paw dismissively with royal smirk, 35mm medium shot, floating leaves, thick black outlines, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon lion king waving paw dismissively on throne, 9:16",
            },
            {
                "scene_number": 10,
                "narration": "Asli raja wahi jiske aage sab chup ho jaayein!",
                "speaker": "speaker_1",
                "speaker_name": "Sher Raja",
                "speaker_avatar": "🦁",
                "sfx": "impact_boom",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": "Flat 2D vector cartoon, majestic cartoon lion king standing tall on throne rock with flowing golden mane, 10mm ultra-wide hero angle, sunburst rays radiating behind him, thick black outlines, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon majestic lion king standing tall with sunburst rays, 9:16",
            },
            {
                "scene_number": 11,
                "narration": "Sabhi janwar chupchap sar jhuka kar piche hat gaye.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": "Flat 2D vector cartoon, sheepish bear, elephant and monkey bowing heads and tiptoeing backward into bushes, 24mm tracking pan, thick clean black outlines, storybook aesthetic, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon animals bowing heads and backing into bushes, 9:16",
            },
            {
                "scene_number": 12,
                "narration": "Sachi taakat shor mein nahi, khamoshi mein hoti hai.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "dramatic-pulse",
                "camera_motion": "climax-pull-back",
                "video_prompt": "Flat 2D vector cartoon, lion king relaxing back into throne cushion with satisfied peaceful grin and folded paws, golden crown glowing, 35mm prime shot, thick outlines, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon lion king relaxing peacefully on throne, 9:16",
            },
            {
                "scene_number": 13,
                "narration": "Toh batao, jungle ka asli don kaun hai?",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "impact_boom",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": "Flat 2D vector cartoon, lion king leaning forward pointing majestic royal paw directly at viewer under glowing jungle title banner, 10mm ultra-wide shot, thick clean black outlines, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon lion pointing paw at camera under jungle banner, 9:16",
            },
            {
                "scene_number": 14,
                "narration": "A Sher, B Haathi, C Bhalu, ya D Bandar? Comment now!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "loop-convergence-zoom",
                "camera_motion": "loop-convergence-zoom",
                "video_prompt": "Flat 2D vector cartoon, vibrant multiple choice quiz card hovering in center displaying options A Sher, B Haathi, C Bhalu, D Bandar, lion king smiling knowingly on throne, 9:16 vertical",
                "visual_prompt": "Flat 2D cartoon multiple choice options board A Sher B Haathi C Bhalu D Bandar, 9:16",
            },
        ]

    # Archetype A: Brands Commenting Under Reels / Viral Skit
    elif any(k in t_lower for k in ["brand", "comment", "reels", "friend", "instagram"]):
        char_dna = "Young comedic creator in stylish orange and blue streetwear jacket with expressive eyes and modern haircut"
        vis_anchor = "Vibrant colorful modern apartment with glowing neon ambient lighting and floating social media icons, 3D Pixar comedy animation, 8k"
        banner = "Brands commenting under reels like they're our friends"

        scenes = [
            {
                "scene_number": 1,
                "narration": "Why do brands comment under reels like we grew up together?",
                "speaker": "speaker_1",
                "speaker_name": "Creator",
                "speaker_avatar": "🙋‍♂️",
                "sfx": "pop",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": f"Close-up 24mm anamorphic shot, {char_dna} looking down at glowing smartphone in disbelief, eyebrows raised, 3D Pixar character design, warm cinematic rim lighting, 8k",
                "visual_prompt": f"24mm anamorphic close-up of {char_dna} reacting to smartphone screen in disbelief, 3D Pixar, 8k",
            },
            {
                "scene_number": 2,
                "narration": "I post about a bad day, and Zepto comments:",
                "speaker": "speaker_1",
                "speaker_name": "Creator",
                "speaker_avatar": "🙋‍♂️",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": f"Medium 35mm prime shot, {char_dna} holding phone toward viewer, pointing at incoming comment notification bubble, modern apartment backdrop, 8k",
                "visual_prompt": f"35mm prime shot of {char_dna} pointing at glowing comment notification bubble, 3D Pixar, 8k",
            },
            {
                "scene_number": 3,
                "narration": "Order a fresh brinjal king, cures heartbreak in ten minutes!",
                "speaker": "speaker_2",
                "speaker_name": "Delivery App",
                "speaker_avatar": "🍆",
                "sfx": "pop",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": f"Playful 50mm portrait shot of cute anthropomorphic neon-green delivery bag mascot holding up a giant glossy purple cartoon brinjal, smiling cheekily, 3D Pixar character design, bright volumetric lighting",
                "visual_prompt": f"50mm portrait of cute green delivery mascot holding shiny cartoon eggplant, 3D Pixar, 8k",
            },
            {
                "scene_number": 4,
                "narration": "A brinjal?! How does an eggplant fix my emotional trauma?!",
                "speaker": "speaker_1",
                "speaker_name": "Creator",
                "speaker_avatar": "🙋‍♂️",
                "sfx": "whip_pan",
                "camera_motion": "dramatic-pulse",
                "video_prompt": f"Close-up 24mm wide angle lens, {char_dna} clutching head in hilarious confusion holding a cartoon eggplant with comic disbelief, 3D Pixar animation, high contrast lighting",
                "visual_prompt": f"24mm wide shot of {char_dna} staring in hilarious confusion at purple brinjal, 3D Pixar, 8k",
            },
            {
                "scene_number": 5,
                "narration": "Then an ergonomic chair company slides into the replies:",
                "speaker": "speaker_1",
                "speaker_name": "Creator",
                "speaker_avatar": "🙋‍♂️",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": f"Medium 35mm tracking shot, {char_dna} gesturing toward a second glowing social comment bubble popping above desk, colorful rim lighting, 8k",
                "visual_prompt": f"35mm tracking shot of {char_dna} gesturing at comment bubble, 3D Pixar, 8k",
            },
            {
                "scene_number": 6,
                "narration": "Sitting with lumbar support heals the soul! Code CHAIR20 for discount!",
                "speaker": "speaker_2",
                "speaker_name": "Chair Co",
                "speaker_avatar": "🪑",
                "sfx": "pop",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": f"Humorous 50mm shot of a sleek executive leather office chair with cartoon eyes and smiling mouth holding a glowing discount coupon voucher, 3D Pixar style, raytraced reflections",
                "visual_prompt": f"50mm shot of living cartoon executive office chair holding glowing discount voucher, 3D Pixar, 8k",
            },
            {
                "scene_number": 7,
                "narration": "Are you selling furniture or running a therapy clinic?!",
                "speaker": "speaker_1",
                "speaker_name": "Creator",
                "speaker_avatar": "🙋‍♂️",
                "sfx": "whoosh",
                "camera_motion": "dramatic-pulse",
                "video_prompt": f"Expressive 35mm portrait lens, {char_dna} sitting on office chair throwing hands up in comedic exasperation, 3D Pixar film render, vibrant colors",
                "visual_prompt": f"35mm portrait of {char_dna} throwing hands up in comedic exasperation, 3D Pixar, 8k",
            },
            {
                "scene_number": 8,
                "narration": "Next, an underwear brand comments:",
                "speaker": "speaker_1",
                "speaker_name": "Creator",
                "speaker_avatar": "🙋‍♂️",
                "sfx": "pop",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": f"Medium 24mm tracking pan, {char_dna} turning toward screen with facepalm expression as another comment floats down, 3D Pixar animation",
                "visual_prompt": f"24mm shot of {char_dna} doing facepalm reaction, 3D Pixar, 8k",
            },
            {
                "scene_number": 9,
                "narration": "Stay supported through tough times king, check our seamless trunks!",
                "speaker": "speaker_2",
                "speaker_name": "Boxer Brand",
                "speaker_avatar": "👑",
                "sfx": "pop",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": f"Heroic 50mm shot of a muscular cartoon mannequin wearing colorful patterned boxer trunks and a tiny golden crown, proud heroic posture, 3D Pixar character render, spotlight glow",
                "visual_prompt": f"50mm heroic shot of cartoon mannequin in boxer trunks with tiny crown, 3D Pixar, 8k",
            },
            {
                "scene_number": 10,
                "narration": "Bro, nobody needs emotional support underwear at two in the morning!",
                "speaker": "speaker_1",
                "speaker_name": "Creator",
                "speaker_avatar": "🙋‍♂️",
                "sfx": "whoosh",
                "camera_motion": "vertical-tilt-reveal",
                "video_prompt": f"Wide 10mm Dutch-angle shot, {char_dna} lunging forward toward camera pointing finger in comical shock, dramatic perspective foreshortening, 3D Pixar",
                "visual_prompt": f"10mm wide angle shot of {char_dna} pointing finger in comical shock, 3D Pixar, 8k",
            },
            {
                "scene_number": 11,
                "narration": "Then a random dosa restaurant chimes in:",
                "speaker": "speaker_1",
                "speaker_name": "Creator",
                "speaker_avatar": "🙋‍♂️",
                "sfx": "pop",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": f"Medium 35mm prime shot, {char_dna} holding phone sideways with wide grin of absolute comedic surrender, colorful apartment background, 8k",
                "visual_prompt": f"35mm shot of {char_dna} holding phone sideways with wide comedic grin, 3D Pixar, 8k",
            },
            {
                "scene_number": 12,
                "narration": "Ghee roast doesn't judge. Ghee roast truly understands.",
                "speaker": "speaker_2",
                "speaker_name": "Dosa Shop",
                "speaker_avatar": "🥞",
                "sfx": "pop",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": f"Delicious 50mm macro shot of a giant golden crispy rolled masala dosa wearing cool black sunglasses resting on banana leaf plate like an ancient wise master, steam swirling, 3D Pixar food character",
                "visual_prompt": f"50mm macro shot of giant golden crispy dosa wearing sunglasses on banana leaf plate, 3D Pixar, 8k",
            },
            {
                "scene_number": 13,
                "narration": "Why is South Indian food giving me philosophical enlightenment?!",
                "speaker": "speaker_1",
                "speaker_name": "Creator",
                "speaker_avatar": "🙋‍♂️",
                "sfx": "whoosh",
                "camera_motion": "dramatic-pulse",
                "video_prompt": f"Close-up 35mm lens, {char_dna} wiping tears of laughter from cheek while holding hands in prayer toward ceiling, warm glowing illumination, 3D Pixar",
                "visual_prompt": f"35mm close-up of {char_dna} wiping tears of laughter in comedic prayer, 3D Pixar, 8k",
            },
            {
                "scene_number": 14,
                "narration": "Please stop trying to be my family and just deliver my food!",
                "speaker": "speaker_1",
                "speaker_name": "Creator",
                "speaker_avatar": "🙋‍♂️",
                "sfx": "whoosh",
                "camera_motion": "climax-pull-back",
                "video_prompt": f"Epic wide 10mm lens pull-back, {char_dna} surrounded by swirling floating brand logos, cartoon eggplants, chairs, and delivery bags cheering him up in a lively fiesta, 3D Pixar render, 8k",
                "visual_prompt": f"10mm wide pull back of {char_dna} surrounded by cheerful cartoon brand characters, 3D Pixar party, 8k",
            },
            {
                "scene_number": 15,
                "narration": "I am deleting this app, right after I check who commented first because...",
                "speaker": "speaker_1",
                "speaker_name": "Creator",
                "speaker_avatar": "🙋‍♂️",
                "sfx": "impact_boom",
                "camera_motion": "loop-convergence-zoom",
                "video_prompt": f"Centered 50mm portrait loop convergence shot, {char_dna} staring directly into camera lens with wide eyes, finger hovering over delete button matching Scene 1 entry angle for seamless infinite loop, 8k",
                "visual_prompt": f"50mm portrait shot of {char_dna} hovering finger over phone screen for seamless infinite loop, 3D Pixar, 8k",
            },
        ]

    # Archetype B: Space / Jupiter Fall Extreme
    elif any(k in t_lower for k in ["jupiter", "space", "astronaut", "fall"]):
        char_dna = "Astronaut in sleek matte-white NASA deep-space EVA suit with neon-amber shoulder striping and a reflective gold-mirrored visor"
        vis_anchor = "Jupiter colossal crimson-amber turbulent vortex atmosphere, violent electrical storm lighting, Unreal Engine 5 render, 8k"
        banner = "What happens if an astronaut falls into Jupiter?"

        scenes = [
            {
                "scene_number": 1,
                "narration": "What if an astronaut accidentally fell into Jupiter?",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "impact_boom",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": f"Extreme wide long shot from 10mm ultra-wide lens, {char_dna} falling headfirst from space into colossal swirling crimson Jupiter vortex, body tumbling, motion blur, 8k",
                "visual_prompt": f"10mm shot of {char_dna} falling toward giant Jupiter atmosphere from space, 8k",
            },
            {
                "scene_number": 2,
                "narration": "At first, you hit the outer cloud tops at one hundred thousand miles an hour.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": f"Low-angle 24mm anamorphic tracking pan, {char_dna} plunging through white ammonia cloud bands, atmospheric heat friction glowing orange around suit, 8k",
                "visual_prompt": f"24mm tracking pan of {char_dna} cutting through white ammonia cloud bands, 8k",
            },
            {
                "scene_number": 3,
                "narration": "Telemetry warns: entry velocity is ten times faster than any bullet on Earth!",
                "speaker": "speaker_2",
                "speaker_name": "Ship AI",
                "speaker_avatar": "🤖",
                "sfx": "pop",
                "camera_motion": "dramatic-pulse",
                "video_prompt": f"Close-up 50mm portrait lens, holographic HUD reflections dancing across gold visor of {char_dna}, displaying screaming red descent velocity telemetry, 8k",
                "visual_prompt": f"50mm close-up of {char_dna} gold visor reflecting glowing red descent numbers, 8k",
            },
            {
                "scene_number": 4,
                "narration": "Within minutes, sunlight completely vanishes into total abyssal darkness.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "vertical-tilt-reveal",
                "video_prompt": f"Dutch-angle 35mm prime vertical tilt reveal, {char_dna} tumbling down into dense murky brown and amber cloud abyss as sunlight fades to black, 8k",
                "visual_prompt": f"35mm Dutch-angle shot of {char_dna} falling into dark murky cloud abyss, 8k",
            },
            {
                "scene_number": 5,
                "narration": "Then, colossal lightning bolts thirty times more powerful than Earth strike!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "impact_boom",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": f"Action 24mm wide angle lens, colossal multi-mile electric purple lightning forks illuminating {char_dna} tumbling against dark turbulent storm clouds, 8k",
                "visual_prompt": f"24mm wide shot of giant purple lightning striking near falling {char_dna}, 8k",
            },
            {
                "scene_number": 6,
                "narration": "External hull pressure reaches one thousand atmospheres. Suit integrity is failing!",
                "speaker": "speaker_2",
                "speaker_name": "Ship AI",
                "speaker_avatar": "🤖",
                "sfx": "pop",
                "camera_motion": "dramatic-pulse",
                "video_prompt": f"Tight 50mm lens shot of titanium gauntlet and shoulder joints of {char_dna} groaning under massive atmospheric pressure, carbon fiber flexing, 8k",
                "visual_prompt": f"50mm shot of spacesuit joint flexing under extreme atmospheric pressure, 8k",
            },
            {
                "scene_number": 7,
                "narration": "Fifty miles deeper, the sky begins raining solid diamond hail.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": f"Macro 35mm prime lens, glittering crystalline diamond hail stones pelting past helmet of {char_dna}, bouncing off visor with bright reflections, 8k",
                "visual_prompt": f"35mm shot of sparkling diamond hail ricocheting off astronaut visor in Jupiter storm, 8k",
            },
            {
                "scene_number": 8,
                "narration": "Superheated methane storms crush carbon soot into pure sparkling diamonds!",
                "speaker": "speaker_2",
                "speaker_name": "Scientist",
                "speaker_avatar": "🔬",
                "sfx": "pop",
                "camera_motion": "pan-right",
                "video_prompt": f"Low-angle 24mm anamorphic lens, swirling vortex of glowing diamonds raining down like a crystalline blizzard around {char_dna}, amber lighting, 8k",
                "visual_prompt": f"24mm shot of glowing diamond blizzard swirling around {char_dna}, 8k",
            },
            {
                "scene_number": 9,
                "narration": "You fall through this diamond blizzard for five hours without landing.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "warm-dolly",
                "video_prompt": f"Cinematic 50mm dolly shot, {char_dna} drifting endlessly downward through deep crimson supercritical gas mist, serene yet terrifying scale, 8k",
                "visual_prompt": f"50mm dolly shot of {char_dna} floating through crimson planetary mist, 8k",
            },
            {
                "scene_number": 10,
                "narration": "Because Jupiter has zero solid surface to ever stand on!",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "impact_boom",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": f"Extreme wide 10mm lens, boundless planetary depth extending infinite miles below {char_dna}, gas gradually condensing into liquid ocean without boundary, 8k",
                "visual_prompt": f"10mm wide shot showing endless bottomless planetary interior beneath {char_dna}, 8k",
            },
            {
                "scene_number": 11,
                "narration": "Eventually, the atmosphere turns as dense as soup, stopping your fall.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": f"Medium 35mm tracking pan, {char_dna} hovering and bobbing in dense supercritical fluid gas ocean, limbs floating weightlessly in glowing liquid mist, 8k",
                "visual_prompt": f"35mm shot of {char_dna} suspended in dense glowing supercritical fluid ocean, 8k",
            },
            {
                "scene_number": 12,
                "narration": "Beneath you lies a colossal ocean of liquid metallic hydrogen.",
                "speaker": "speaker_2",
                "speaker_name": "Scientist",
                "speaker_avatar": "🔬",
                "sfx": "pop",
                "camera_motion": "vertical-tilt-reveal",
                "video_prompt": f"Dutch-angle 35mm vertical tilt reveal, shining reflective silver waves of liquid metallic hydrogen churning below, reflecting giant lightning arches, 8k",
                "visual_prompt": f"35mm shot of metallic liquid silver ocean waves surging on Jupiter, 8k",
            },
            {
                "scene_number": 13,
                "narration": "Temperatures here surpass twenty thousand degrees, hotter than the Sun's surface!",
                "speaker": "speaker_2",
                "speaker_name": "Scientist",
                "speaker_avatar": "🔬",
                "sfx": "impact_boom",
                "camera_motion": "dramatic-pulse",
                "video_prompt": f"Dramatic 24mm wide angle shot, thermal heat haze rippling as golden molten radiation envelopes the silhouette of {char_dna}, incandescent glow, 8k",
                "visual_prompt": f"24mm shot of thermal golden radiation wave surging toward astronaut silhouette, 8k",
            },
            {
                "scene_number": 14,
                "narration": "Any human vessel dissolves into pure atomic particles in seconds.",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "climax-pull-back",
                "video_prompt": f"Epic wide 10mm anamorphic pull-back, microscopic glowing particles scattering into Jupiter's magnetic core dynamo, colossal cosmic scale, 8k",
                "visual_prompt": f"10mm wide pull back of golden particles scattering in planetary magnetic core, 8k",
            },
            {
                "scene_number": 15,
                "narration": "You are now forever a part of the king of planets. But what if...",
                "speaker": "speaker_1",
                "speaker_name": "Narrator",
                "speaker_avatar": "🎙️",
                "sfx": "impact_boom",
                "camera_motion": "loop-convergence-zoom",
                "video_prompt": f"Centered 50mm portrait loop convergence shot, {char_dna} floating in glowing core vortex looking directly into camera with visor reflection matching Scene 1 entry angle for seamless infinite loop, 8k",
                "visual_prompt": f"50mm portrait shot of astronaut visor reflecting storm vortex for seamless infinite loop, 8k",
            },
        ]

    # Archetype C: Universal Dynamic 14-Scene Rapid-Cut Script
    else:
        topic_core = topic.rstrip("?.!").replace("What if ", "").replace("What happens if ", "").strip()
        char_dna = "Expressive protagonist explorer in modern dynamic attire with vibrant styling and reactive features"
        vis_anchor = "Cinematic dramatic atmospheric environment, high-contrast volumetric lighting, 3D Pixar render, 8k"

        scenes = [
            {
                "scene_number": 1,
                "narration": f"What if {topic_core.lower()} right now?",
                "speaker": "speaker_1",
                "speaker_name": "Host",
                "speaker_avatar": "🎙️",
                "sfx": "impact_boom",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": f"Close-up 24mm anamorphic shot, {char_dna} reacting with shock looking directly at camera, wide eyes, 3D Pixar style, cinematic rim lighting, 8k",
                "visual_prompt": f"24mm close-up of {char_dna} looking shocked into camera, 3D Pixar, 8k",
            },
            {
                "scene_number": 2,
                "narration": "Most people assume life would just carry on normally.",
                "speaker": "speaker_1",
                "speaker_name": "Host",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": f"Medium 35mm tracking shot, {char_dna} walking past bustling city sidewalk where people glance at phones unaware, vibrant lighting, 8k",
                "visual_prompt": f"35mm tracking shot of {char_dna} on city street, 3D Pixar, 8k",
            },
            {
                "scene_number": 3,
                "narration": "But in the first five seconds, catastrophic physics ignite!",
                "speaker": "speaker_2",
                "speaker_name": "Specialist",
                "speaker_avatar": "🚨",
                "sfx": "pop",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": f"Dynamic 24mm wide angle shot, ground shaking violently as atmospheric air pressure warps with visible shockwaves, 3D Pixar animation, 8k",
                "visual_prompt": f"24mm shot of ground shaking and air pressure warping, 3D Pixar, 8k",
            },
            {
                "scene_number": 4,
                "narration": "Kinetic shockwaves tear across every major continent instantly.",
                "speaker": "speaker_1",
                "speaker_name": "Host",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "vertical-tilt-reveal",
                "video_prompt": f"Dutch-angle 35mm vertical tilt reveal, city skyline wobbling as supersonic wind waves shatter glass windows, camera tilting upward, 8k",
                "visual_prompt": f"35mm Dutch-angle shot of skyscraper glass reflecting supersonic shockwaves, 8k",
            },
            {
                "scene_number": 5,
                "narration": "Global electrical power grids collapse into total darkness.",
                "speaker": "speaker_1",
                "speaker_name": "Host",
                "speaker_avatar": "🎙️",
                "sfx": "pop",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": f"Wide 24mm shot, metropolitan city lights blinking out in rapid succession leaving dark silhouette skyline under stars, 3D Pixar, 8k",
                "visual_prompt": f"24mm wide shot of city lights extinguishing into darkness, 8k",
            },
            {
                "scene_number": 6,
                "narration": "Satellites orbiting space lose synchronization and spiral downward.",
                "speaker": "speaker_2",
                "speaker_name": "Specialist",
                "speaker_avatar": "🛰️",
                "sfx": "whoosh",
                "camera_motion": "climax-pull-back",
                "video_prompt": f"Extreme wide 10mm space shot, glowing orbital satellites tumbling out of alignment with sparkling debris trails above Earth curve, 8k",
                "visual_prompt": f"10mm space shot of satellites tumbling above Earth, 8k",
            },
            {
                "scene_number": 7,
                "narration": "Oceans violently slosh inland in towering saltwater walls.",
                "speaker": "speaker_1",
                "speaker_name": "Host",
                "speaker_avatar": "🎙️",
                "sfx": "impact_boom",
                "camera_motion": "rapid-push-in-shake",
                "video_prompt": f"Colossal 24mm wide angle shot, massive ocean wave surging over coastal highway, water churning with foam and power, 3D Pixar disaster, 8k",
                "visual_prompt": f"24mm wide shot of massive ocean surge over coastal highway, 8k",
            },
            {
                "scene_number": 8,
                "narration": "Emergency alarms blare across every smartphone and radio.",
                "speaker": "speaker_2",
                "speaker_name": "Specialist",
                "speaker_avatar": "🚨",
                "sfx": "pop",
                "camera_motion": "dramatic-pulse",
                "video_prompt": f"Close-up 50mm portrait shot, {char_dna} staring at flashing red emergency screen on smartphone, vivid red alarm lighting, 8k",
                "visual_prompt": f"50mm close up of {char_dna} illuminated by red flashing phone alarm, 8k",
            },
            {
                "scene_number": 9,
                "narration": "Atmospheric pressure shifts trigger deafening sonic thunderclaps.",
                "speaker": "speaker_1",
                "speaker_name": "Host",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "smooth-lateral-pan-right",
                "video_prompt": f"Medium 35mm tracking shot, clouds rolling rapidly into geometric storm vortex, lightning pulsing through purple sky, 3D Pixar, 8k",
                "visual_prompt": f"35mm shot of swirling geometric storm vortex in sky, 8k",
            },
            {
                "scene_number": 10,
                "narration": "Animals sense the disturbance and flee in mass panic.",
                "speaker": "speaker_1",
                "speaker_name": "Host",
                "speaker_avatar": "🎙️",
                "sfx": "pop",
                "camera_motion": "pan-right",
                "video_prompt": f"Dynamic 24mm tracking pan, flock of birds and city wildlife taking off together in synchronized flight against sunset sky, 8k",
                "visual_prompt": f"24mm tracking shot of wildlife taking flight in synchronized flock, 8k",
            },
            {
                "scene_number": 11,
                "narration": "Deep beneath us, the Earth's tectonic plates grind furiously.",
                "speaker": "speaker_2",
                "speaker_name": "Specialist",
                "speaker_avatar": "🌋",
                "sfx": "impact_boom",
                "camera_motion": "vertical-tilt-reveal",
                "video_prompt": f"Dutch-angle 35mm vertical tilt reveal, deep ground fissure opening with glowing orange magma glow beneath pavement, camera tilting upward, 8k",
                "visual_prompt": f"35mm shot of glowing magma fissure opening in street, 8k",
            },
            {
                "scene_number": 12,
                "narration": "Within thirty minutes, the entire landscape is completely transformed.",
                "speaker": "speaker_1",
                "speaker_name": "Host",
                "speaker_avatar": "🎙️",
                "sfx": "whoosh",
                "camera_motion": "warm-dolly",
                "video_prompt": f"Cinematic 50mm dolly shot, {char_dna} standing atop hill overlooking transformed surreal landscape with glowing horizon, 8k",
                "visual_prompt": f"50mm dolly shot of {char_dna} looking out over transformed surreal landscape, 8k",
            },
            {
                "scene_number": 13,
                "narration": "Our daily routine hangs on an unimaginably delicate balance.",
                "speaker": "speaker_1",
                "speaker_name": "Host",
                "speaker_avatar": "🎙️",
                "sfx": "pop",
                "camera_motion": "dramatic-pulse",
                "video_prompt": f"Close-up 35mm portrait shot, {char_dna} turning toward camera with expressive reflective eyes, warm golden rim lighting, 3D Pixar, 8k",
                "visual_prompt": f"35mm portrait of {char_dna} looking reflective toward camera, 8k",
            },
            {
                "scene_number": 14,
                "narration": "Would you survive this scenario? Tell us below, because...",
                "speaker": "speaker_1",
                "speaker_name": "Host",
                "speaker_avatar": "🎙️",
                "sfx": "impact_boom",
                "camera_motion": "loop-convergence-zoom",
                "video_prompt": f"Centered 50mm portrait loop convergence shot, {char_dna} looking directly into lens with intense curiosity matching Scene 1 entry angle for seamless infinite loop, 8k",
                "visual_prompt": f"50mm portrait of {char_dna} looking directly into camera for infinite loop, 8k",
            },
        ]

    total_words = sum(len(sc["narration"].split()) for sc in scenes)
    return {
        "episode_title": clean_title,
        "top_hook_banner": banner,
        "hook_headline": f"WHAT HAPPENS NEXT?!",
        "character_dna": char_dna,
        "visual_anchor": vis_anchor,
        "riddle_options": riddle_options,
        "total_words_count": total_words,
        "scenes": scenes,
        "beats": scenes,
        "seo_tags": [
            clean_title.lower(), "viral shorts", "reels", "what if", "mind blowing",
            "funny animation", "3d pixar", "trending", "comedy skit", "relatable"
        ],
        "hashtags": ["#shorts", "#viral", "#reels", "#relatable", "#trending"],
        "pinned_comment": f"Would you survive {clean_title.title()}? Drop your comment below! 👇 Subscribe for daily viral drops! 🚀",
        "branching_decision": {
            "choice_a": "Option A for next episode",
            "choice_b": "Option B for next episode",
            "vote_callout": "Vote A or B in comments!"
        }
    }


if __name__ == "__main__":
    t_test = {
        "topic": "Brands commenting under reels like they’re our friends",
        "category": "Viral Skit / Relatable Comedy",
        "style": "3D Pixar animation comedy"
    }
    script = generate_viral_script(t_test)
    print(f"Generated {len(script['scenes'])} scenes ({script['total_words_count']} words)")
    print(json.dumps(script, indent=2))
