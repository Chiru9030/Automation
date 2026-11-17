import React, { useMemo } from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { ProgressBar } from './components/ProgressBar';
import storyDataRaw from './storyData.json';

// --- Smooth Ambient Cinematic Sparkles (Zero Lag, Pre-calculated) ---
const CinematicMotes: React.FC = () => {
  const frame = useCurrentFrame();

  const motes = useMemo(() => {
    return Array.from({ length: 24 }).map((_, i) => ({
      seedX: i * 19.3,
      baseX: (i * 33) % 100,
      baseY: (i * 41) % 100,
      size: 4 + (i % 3) * 2.5,
      opacity: 0.35 + (i % 3) * 0.2,
      color: i % 2 === 0 ? '#FFE600' : '#FFFFFF',
    }));
  }, []);

  return (
    <AbsoluteFill style={{ overflow: 'hidden', pointerEvents: 'none' }}>
      {motes.map((m, i) => {
        const offsetX = Math.sin(frame * 0.04 + m.seedX) * 20;
        const offsetY = ((m.baseY - frame * 0.3) % 100) + 100;
        const currentY = offsetY % 100;
        const pulse = 0.7 + 0.3 * Math.sin((frame + i * 10) * 0.1);

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${(m.baseX + offsetX * 0.1) % 100}%`,
              top: `${currentY}%`,
              width: m.size,
              height: m.size,
              borderRadius: '50%',
              backgroundColor: m.color,
              boxShadow: `0 0 ${m.size * 2}px ${m.color}`,
              opacity: m.opacity * pulse,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

export interface ChunkWord {
  word: string;
  start_frame: number;
  end_frame: number;
}

export interface SubtitleChunk {
  chunk_id: number;
  text: string;
  start_frame: number;
  end_frame: number;
  words: ChunkWord[];
}

export interface SceneItem {
  scene_number: number;
  title: string;
  narration: string;
  image_url?: string;
  audio_url?: string;
  duration_in_frames?: number;
  camera_style?: string;
  speaker?: string;
  speaker_name?: string;
  speaker_avatar?: string;
  sfx?: string;
  subtitle_chunks?: SubtitleChunk[];
}

export interface StoryPayload {
  title: string;
  chapter: string;
  episode: number;
  genre: string;
  hook_headline: string;
  scenes: SceneItem[];
}

const storyData = storyDataRaw as unknown as StoryPayload;

interface StorySceneProps {
  scene: SceneItem;
  durationInFrames: number;
}

const StoryScene: React.FC<StorySceneProps> = ({ scene, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 1. Butter-Smooth 2.5D Living Camera Engine (Zero Jitter, Zero Black Flicker)
  const style = scene.camera_style || 'smooth-zoom-in';

  let scale = 1.1;
  let panX = 0;
  let panY = 0;
  let rotX = 0;
  let rotY = 0;
  let rotZ = 0;

  const progress = frame / durationInFrames;

  if (style === 'pan-right') {
    scale = interpolate(frame, [0, durationInFrames], [1.10, 1.20]);
    panX = interpolate(frame, [0, durationInFrames], [-35, 35]);
    rotY = interpolate(frame, [0, durationInFrames], [-4, 4]);
    rotX = Math.cos(progress * Math.PI) * -1.5;
  } else if (style === 'dramatic-pulse') {
    // Climax tension: dramatic push with subtle heartbeat pulse
    const heartbeat = Math.sin(frame * 0.16) * 3;
    scale = interpolate(frame, [0, durationInFrames], [1.04, 1.25]) + (heartbeat * 0.005);
    panY = heartbeat * 0.5;
    rotX = interpolate(frame, [0, 20, durationInFrames], [-4, 0, 3]);
  } else if (style === 'warm-dolly') {
    // Gentle floating dolly
    scale = interpolate(frame, [0, durationInFrames], [1.18, 1.08]);
    panX = interpolate(frame, [0, durationInFrames], [20, -20]);
    rotY = interpolate(frame, [0, durationInFrames], [3, -3]);
  } else if (style === 'sunset-drift') {
    // Slow cinematic crane upward
    scale = interpolate(frame, [0, durationInFrames], [1.08, 1.22]);
    panY = interpolate(frame, [0, durationInFrames], [25, -25]);
    rotX = interpolate(frame, [0, durationInFrames], [2, -3]);
  } else {
    // smooth-zoom-in (Hook entrance)
    scale = interpolate(frame, [0, durationInFrames], [1.05, 1.24]);
    rotY = Math.sin(progress * Math.PI) * 3.5;
    rotX = Math.cos(progress * Math.PI) * -2;
  }

  // Organic harmonic float
  const organicFloat = Math.sin(frame * 0.06) * 1.5;

  // Seamless entrance spring (no opacity dip to black!)
  const entranceScale = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 100, mass: 0.6 },
  });

  const hasImage = Boolean(scene.image_url);
  const chunks = scene.subtitle_chunks || [];

  // Active Submagic 2-3 word chunk
  const activeChunk = chunks.find(
    (c) => frame >= c.start_frame && frame <= c.end_frame
  ) || (chunks.length > 0 && frame > chunks[chunks.length - 1].end_frame ? chunks[chunks.length - 1] : chunks[0]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#030206',
        overflow: 'hidden',
        perspective: 1200,
      }}
    >
      {/* SFX Foley Audio Trigger */}
      {scene.sfx && (
        <Audio
          src={staticFile(`sfx/${scene.sfx}.wav`)}
          volume={scene.sfx === 'impact_boom' ? 0.70 : 0.35}
        />
      )}

      {/* Voiceover for this scene */}
      {scene.audio_url && (
        <Audio
          src={staticFile(scene.audio_url)}
          volume={1.0}
        />
      )}

      {/* LAYER 1: Deep Atmospheric Ambient Backdrop */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(ellipse at 50% 40%, rgba(45, 18, 90, 0.95) 0%, #030208 100%)',
        }}
      />
      {hasImage && (
        <div
          style={{
            position: 'absolute',
            inset: -40,
            backgroundImage: `url(${staticFile(scene.image_url!)})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            opacity: 0.25,
            filter: 'saturate(1.3) brightness(0.4)',
            transform: `scale(${1.15 + (scale - 1.0) * 0.3}) translate3d(${panX * 0.15}px, ${panY * 0.15}px, 0)`,
          }}
        />
      )}

      {/* LAYER 2: Floating Golden Particle Sparkles */}
      <CinematicMotes />

      {/* LAYER 3: 2.5D Living Hero Artwork (Smooth Parallax, 3D Tilt & Lens Flare Glint) */}
      <div
        style={{
          position: 'absolute',
          top: 155,
          left: 0,
          right: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          transformStyle: 'preserve-3d',
        }}
      >
        {hasImage && (
          <div
            style={{
              width: 980,
              height: 980,
              borderRadius: 44,
              overflow: 'hidden',
              position: 'relative',
              boxShadow: `${-panX * 0.5}px 30px 90px rgba(0, 0, 0, 0.95), 0 0 50px rgba(255, 230, 0, 0.3), 0 0 0 4px rgba(255, 230, 0, 0.5)`,
              transform: `scale(${entranceScale * scale}) translate3d(${panX}px, ${panY + organicFloat}px, 0) rotateX(${rotX}deg) rotateY(${rotY}deg) rotateZ(${rotZ}deg)`,
              backgroundColor: '#0d0d15',
              transformStyle: 'preserve-3d',
            }}
          >
            {/* Main Illustration */}
            <Img
              src={staticFile(scene.image_url!)}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
            />

            {/* Anamorphic Lens Flare Light Sweep Glint */}
            <div
              style={{
                position: 'absolute',
                inset: -60,
                pointerEvents: 'none',
                background:
                  'linear-gradient(115deg, transparent 25%, rgba(255,255,255,0.0) 40%, rgba(255,255,255,0.40) 50%, rgba(255,255,255,0.0) 60%, transparent 75%)',
                transform: `translateX(${interpolate(frame, [0, durationInFrames], [-120, 140], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })}%)`,
                mixBlendMode: 'overlay',
              }}
            />
          </div>
        )}

        {/* Dynamic Character Action Badge */}
        <div
          style={{
            marginTop: 26,
            padding: '10px 32px',
            borderRadius: 30,
            background: 'rgba(5, 5, 15, 0.88)',
            border: '2px solid #FFE600',
            backdropFilter: 'blur(14px)',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            boxShadow: '0 8px 30px rgba(0,0,0,0.8), 0 0 22px rgba(255,230,0,0.35)',
          }}
        >
          <span style={{ fontSize: 28 }}>{scene.speaker_avatar || '🦁'}</span>
          <span
            style={{
              fontFamily: "'Impact', 'Arial Black', sans-serif",
              fontSize: 22,
              letterSpacing: 2,
              color: '#FFFFFF',
              textTransform: 'uppercase',
            }}
          >
            {scene.speaker_name ? `${scene.speaker_name.toUpperCase()} • ` : ''}
          </span>
          <span
            style={{
              fontFamily: "'Impact', 'Arial Black', sans-serif",
              fontSize: 22,
              letterSpacing: 2,
              color: '#FFE600',
              textTransform: 'uppercase',
            }}
          >
            {scene.title}
          </span>
        </div>
      </div>

      {/* LAYER 4: VIRAL SUBMAGIC / OPUS 2-3 WORD ACTIVE KARAOKE CAPTIONS */}
      <div
        style={{
          position: 'absolute',
          bottom: 165,
          left: 40,
          right: 40,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: 140,
        }}
      >
        {activeChunk && (
          <div
            style={{
              background: 'rgba(0, 0, 0, 0.90)',
              backdropFilter: 'blur(16px)',
              padding: '20px 42px',
              borderRadius: 32,
              border: '3px solid rgba(255, 230, 0, 0.90)',
              boxShadow:
                '0 20px 60px rgba(0, 0, 0, 0.95), 0 0 50px rgba(255, 230, 0, 0.45), inset 0 0 20px rgba(255, 230, 0, 0.15)',
              textAlign: 'center',
              display: 'flex',
              flexWrap: 'wrap',
              justifyContent: 'center',
              alignItems: 'center',
              gap: 14,
            }}
          >
            {activeChunk.words.map((item, wIdx) => {
              const isSpoken = frame >= item.start_frame && frame <= item.end_frame;
              const isPast = frame > item.end_frame;

              return (
                <span
                  key={wIdx}
                  style={{
                    fontFamily: "'Impact', 'Arial Black', -apple-system, sans-serif",
                    fontSize: 54,
                    fontWeight: 900,
                    lineHeight: 1.15,
                    letterSpacing: 2.0,
                    textTransform: 'uppercase',
                    WebkitTextStroke: '2.5px #000',
                    display: 'inline-block',
                    padding: isSpoken ? '4px 16px' : '4px 8px',
                    borderRadius: 14,
                    backgroundColor: isSpoken ? 'rgba(255, 230, 0, 0.28)' : 'transparent',
                    border: isSpoken ? '2px solid #FFE600' : '2px solid transparent',
                    color: isSpoken ? '#FFE600' : isPast ? '#FFFFFF' : 'rgba(255, 255, 255, 0.65)',
                    transform: isSpoken ? 'scale(1.18)' : 'scale(1.0)',
                    transition: 'transform 0.06s ease-out, color 0.06s ease-out',
                    textShadow: isSpoken
                      ? '0 0 40px rgba(255, 230, 0, 1.0), 0 4px 0 #000'
                      : '0 4px 0 #000, 0 8px 20px rgba(0,0,0,0.8)',
                  }}
                >
                  {item.word}
                </span>
              );
            })}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

export const StoryVideo: React.FC = () => {
  const scenes = storyData.scenes || [];

  let runningFrame = 0;
  const sceneTimeline = scenes.map((scene) => {
    const startFrame = runningFrame;
    const duration = scene.duration_in_frames || 360;
    runningFrame += duration;
    return {
      scene,
      startFrame,
      duration,
    };
  });

  return (
    <AbsoluteFill style={{ backgroundColor: '#020208', color: '#fff' }}>
      {/* Background Music: Ducked down to 15% during voiceover */}
      <Audio
        src={staticFile('audio/story_bg.wav')}
        volume={(f) =>
          interpolate(f, [0, 30, 1740, 1800], [0, 0.15, 0.15, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          })
        }
      />

      {/* Top Header: Book Title & Episode Pill */}
      <div
        style={{
          position: 'absolute',
          top: 55,
          left: 0,
          right: 0,
          zIndex: 20,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <div
          style={{
            background: 'rgba(5, 5, 15, 0.88)',
            backdropFilter: 'blur(16px)',
            padding: '12px 36px',
            borderRadius: 35,
            border: '2px solid rgba(255, 230, 0, 0.7)',
            display: 'flex',
            alignItems: 'center',
            gap: 14,
            boxShadow: '0 8px 30px rgba(0,0,0,0.8), 0 0 25px rgba(255,230,0,0.3)',
          }}
        >
          <span
            style={{
              fontFamily: "'Impact', 'Arial Black', sans-serif",
              fontSize: 24,
              letterSpacing: 2.5,
              color: '#FFE600',
              textTransform: 'uppercase',
            }}
          >
            🦁 {storyData.title || 'STORY TIME'}
          </span>
          <span style={{ color: 'rgba(255, 230, 0, 0.4)' }}>•</span>
          <span
            style={{
              fontFamily: "'Impact', 'Arial Black', sans-serif",
              fontSize: 20,
              fontWeight: 700,
              color: '#FFFFFF',
              letterSpacing: 1.5,
            }}
          >
            EPISODE #{storyData.episode || 1}
          </span>
        </div>
      </div>

      {/* 5 Seamless Audio-Synchronized Cinematic Beats (No black dips, full immersion) */}
      {sceneTimeline.map(({ scene, startFrame, duration }) => (
        <Sequence
          key={scene.scene_number}
          from={startFrame}
          durationInFrames={duration}
        >
          <StoryScene scene={scene} durationInFrames={duration} />
        </Sequence>
      ))}

      {/* 60-Second Bottom Neon Progress Bar */}
      <ProgressBar />
    </AbsoluteFill>
  );
};
