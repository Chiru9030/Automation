# Remotion Studio-Grade Video Production & VFX Best Practices

This skill provides production standards for creating viral, broadcast-quality vertical videos using Remotion, WebGL, SVG, and modern motion graphics.

---

## 1. Visual Hierarchy (Graphics-First)

1. **The Hero Subject**:
   - The central illustration or graphic must take up the upper/middle 65% of the frame.
   - Use high-contrast rounded framing (`border-radius: 32px-40px`), triple-layered drop shadows, and subtle gold/ambient edge glows.
2. **Atmosphere & Depth (Parallax Layering)**:
   - **Background Layer**: Re-use the scene image with `filter: blur(35px) brightness(0.35)` and continuous subtle scale (1.25x -> 1.35x).
   - **Midground Layer**: The framed hero illustration with Ken Burns Pan & Zoom (`scale: 1.0 -> 1.15`, `translateY: 0 -> -20px`).
   - **Particle / VFX Layer**: Procedural floating embers, golden stardust motes, or Simplex noise shimmer (`@remotion/noise`).
   - **Foreground Layer**: Kinetic lower-third subtitle badge with spring physics (`@remotion/motion-blur`).

---

## 2. Motion Design & Transitions

1. **Ken Burns Motion**:
   - Never show a static image. Always apply non-linear interpolation across the scene duration:
     ```tsx
     const zoom = interpolate(frame, [0, durationInFrames], [1.0, 1.15], {
       extrapolateLeft: 'clamp',
       extrapolateRight: 'clamp',
     });
     ```
2. **Spring Physics**:
   - Use `spring()` for element entrances (damping: 12-14, stiffness: 80-100, mass: 0.5-0.7).
   - Chain entrance springs so the badge pops in at frame 0, the illustration at frame 4, and subtitles at frame 8.

---

## 3. Kinetic Subtitle Design (Reels / Shorts)

1. **Safe Area**:
   - Place captions in the bottom 25% safe zone (`bottom: 160px - 200px`), avoiding platform navigation UI.
2. **Badge Styling**:
   - Use frosted-glass backdrops (`background: rgba(5, 5, 12, 0.82)`, `backdrop-filter: blur(16px)`).
   - Highlight key emotional words in glowing yellow (`#FFD700`) or cyan (`#00F0FF`).

---

## 4. Audio Mastering & Dynamic Ducking

1. **Narration Priority**:
   - Voiceover narration must always be centered at 100% volume (`volume: 1.0`).
2. **Automatic Audio Ducking**:
   - Background music must be ducked to 15-20% (`volume: 0.18`) during speech.
   - Fade in background music smoothly over the first 30 frames and fade out smoothly over the final 60 frames.
