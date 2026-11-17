# Autonomous Story-to-Shorts Video Pipeline 📖🚀

An automated, non-blocking AI video production pipeline powered by **Google Antigravity SDK**, **Remotion**, **edge-tts**, **YouTube Data API**, and **Instagram Reels**.

Every 8 hours, it ingests the next chapter of an uploaded storybook, synthesizes voice narration + background music, renders a 60-second vertical video (1080x1920), and publishes it to social media.

---

## Supported Ebook Formats

Drop any of the following file types into [`books/`](file:///Users/chiranjeevi/PROJECTS/remotion-video-pipeline/books/):
- **`.epub`** (Standard EPUB ebooks with chapter detection)
- **`.pdf`** (Digital storybooks & novels)
- **`.txt`** (Raw story text)
- **`.md`** (Markdown chapters)

---

## System Architecture

```
remotion-video-pipeline/
├── books/                                  # Drop .epub, .pdf, .txt storybooks here
├── story_pipeline/
│   ├── story_extractor.py                  # EPUB/PDF/TXT chapter slicer & Gemini script adapter
│   ├── voice_generator.py                  # edge-tts cinematic narration generator
│   └── story_history.json                  # Episode & chapter progression tracker
├── video-app/                              # Remotion project
│   ├── src/StoryVideo.tsx                  # 60s vertical video (Ken Burns zoom + kinetic subtitles)
│   ├── src/Root.tsx                        # Composition registry (1800 frames @ 30fps)
│   └── public/audio/                       # Dual-track audio (voiceover.mp3 + ducked bg_music.wav)
├── audio_generator.py                      # Genre-adaptive cinematic soundtrack synthesizer
├── story_runner.py                         # Single-run execution with breakout & circuit breaker
├── continuous_scheduler.py                 # 8-hour autonomous daemon
└── Dockerfile                              # Headless Cloud Run / AWS Fargate container
```

---

## Robust Loop & Crash Protection (Circuit Breakers)

1. **Subprocess Timeout (6 Minutes)**:
   Remotion rendering has a strict 360-second timeout. If Chromium hangs or stalls, it is force-terminated.
2. **Retry with Automatic Breakout**:
   Retries up to 2 times. If both fail, it breaks out cleanly to avoid infinite loops and logs the error.
3. **Daemon Cooldown**:
   If 3 consecutive cycles fail, the continuous scheduler enters a 10-minute cooldown before safely resetting.

---

## Quickstart

### 1. Ingest a Story
Place any `.epub`, `.pdf`, or `.txt` file into the `books/` folder.

### 2. Test a Single Video Cycle
```bash
python3 story_runner.py
```
*(Extracts the next chapter, synthesizes voiceover and background music, and exports `video-app/out/story_episode_X.mp4`).*

### 3. Start the 8-Hour Continuous Daemon
```bash
python3 continuous_scheduler.py
```
Runs continuously in the background, advancing chapter-by-chapter every 8 hours!
