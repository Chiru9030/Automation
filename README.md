# Autonomous Story-to-Shorts Video Pipeline (v1.0.0 Production Release) 🎬🚀

An autonomous, production-grade AI short-form video generation pipeline powered by **Google Gemini 2.5/3.8 Flash**, **Hugging Face FLUX.1-schnell**, **Edge-TTS**, **FFmpeg Hardware Acceleration**, and the **YouTube Data API v3**.

Runs automatically on a **5-hour scheduled cloud cron** (or 1-click cloud / local trigger), synthesizing gripping narrative scripts, cinema-grade 3D visuals, multi-plane continuous camera motion, multi-track audio with transition SFX at every cut, and frame-accurate kinetic subtitles.

---

## 🛡️ Production Quality Standard (5 Auditor Gates)

Every episode must pass all 5 multi-pillar quality gates before publishing. If any metric falls below the production threshold, the **Zero-Upload Safety Guard** immediately halts publication, alerts your mobile phone via Telegram, and retries generation:

1. **Gate 1: Story Script & Hook Inspector**
   - Beat 1 strictly requires a psychological curiosity hook trigger (*"What happens if...", "Imagine if...", "Did you know..."*).
   - Word count strictly bounded to 105–138 words (locking duration to 52s–58.5s).
   - Pacing verified with escalation markers and a satisfying narrative conclusion.

2. **Gate 2: 4-Pillar Visual Quality Auditor (Content, Quality, Relation, Clarity)**
   - **Content**: Non-blank, non-corrupt, structural information check (grayscale stddev $\ge 5.0$, $6.0 \le \text{mean\_lum} \le 252.0$).
   - **Quality**: Strict 9:16 vertical resolution (1080x1920), clean 3-channel RGB decode.
   - **Relation**: Thematic narrative alignment (marine scenes require underwater blue/cyan tones; fire scenes require magma red/orange) and distinct beat-to-beat visual progression (Hamming distance $\ge 6$).
   - **Clarity**: Sharp edge definition and focus ($\ge 8.0$) to prevent blurry or smudged renders without penalizing artistic low-saturation palettes.

3. **Gate 3: Neural Audio & Dynamic Range Auditor**
   - Duration strictly verified between 50.0s and 58.5s (< 59.0s limit for YouTube Shorts).
   - Neural word timestamp verification (monotonic with positive durations).

4. **Gate 4: Kinetic Typography & Safe Lower-Third Subtitles**
   - MarginV bounded between 180 and 260 to keep captions clear of YouTube Shorts UI buttons and header bars.
   - At least 25 discrete word-highlight events per episode.

5. **Gate 5: Pre-Flight Final Video Certification & Motion Differential**
   - 5-point visual frame sampling (10%, 30%, 50%, 70%, 90% duration).
   - FFmpeg `volumedetect` rejects silent or flatline audio tracks ($< -45\text{ dB}$).
   - **Motion Differential**: Verifies continuous camera motion across frames to reject frozen videos.
   - 0% blank screens, 0% frozen frames.

---

## 🧠 System Architecture (v1.0.0)

```
remotion-video-pipeline/
├── story_pipeline/
│   ├── viral_topic_engine.py         # Stage 1: Curiosity hook & topic generator
│   ├── viral_script_engine.py        # Stage 2: 5-beat retention scriptwriter
│   ├── hd_image_engine.py            # Stage 3: FLUX.1-schnell / Pollinations / Semantic visuals
│   ├── neural_audio_engine.py        # Stage 4 & 5: Edge-TTS neural speech & exact word boundaries
│   ├── kinetic_subtitle_engine.py    # Stage 6: ASS discrete word highlighting (Submagic style)
│   ├── sfx_generator.py              # Foley audio synthesizer (impact booms, whooshes)
│   ├── fast_video_engine.py          # Stage 7: Native hardware-accelerated video synthesis
│   ├── strict_pipeline_auditor.py    # Multi-pillar 5-gate quality auditor
│   ├── telegram_notifier.py          # Mobile dispatch (status reports, previews, error alerts)
│   └── story_history.json            # Perpetual topic and episode history tracker
├── video-app/                        # Remotion composition framework
│   └── public/                       # Audio, visual, and SFX asset store
├── story_runner.py                   # Master v1.0.0 pipeline runner with Zero-Upload Guard
└── .github/workflows/
    └── story_pipeline.yml            # 5-hour automated GitHub Actions workflow
```

---

## 🚀 Running Pipeline v1.0.0

### Run Locally in Sample Mode (Bypasses Social Upload)
```bash
python3 story_runner.py --sample
```

### Run with a Custom Topic
```bash
python3 story_runner.py --topic "The deepest creature discovered in the Mariana Trench"
```

### Run Production Cloud Pipeline
The GitHub Actions workflow runs autonomously every 5 hours:
```bash
gh workflow run "5-Hour Autonomous Story Video Pipeline" --ref main
```
