import React from 'react';
import {
  AbsoluteFill,
  Audio,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { Starfield } from './components/Starfield';
import { ProgressBar } from './components/ProgressBar';
import { FactCard } from './components/FactCard';
import videoDataRaw from './videoData.json';

interface FactItem {
  number: number;
  badge: string;
  headline: string;
  subtext: string;
  highlightWord: string;
  emoji: string;
}

interface VideoPayload {
  genre?: string;
  category?: string;
  title?: string;
  subtitle?: string;
  hookEmoji?: string;
  outroTitle?: string;
  outroSubtitle?: string;
  outroEmoji?: string;
  audioFile?: string;
  facts: FactItem[];
}

const videoData = videoDataRaw as unknown as VideoPayload;

export const SpaceFacts: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Intro animation
  const introScale = spring({
    frame,
    fps,
    config: { damping: 10, stiffness: 90 },
  });

  return (
    <AbsoluteFill style={{ backgroundColor: '#02040a', color: '#fff' }}>
      {/* Background Music Layer */}
      <Audio
        src={staticFile(videoData.audioFile || 'audio/background.wav')}
        volume={(f) =>
          interpolate(f, [0, 15, 420, 450], [0, 0.75, 0.75, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          })
        }
      />

      {/* Background Starfield */}
      <Starfield />

      {/* Top Banner Header */}
      <div
        style={{
          position: 'absolute',
          top: 80,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: 12,
        }}
      >
        <span
          style={{
            fontFamily: 'system-ui, -apple-system, sans-serif',
            fontSize: 24,
            fontWeight: 900,
            letterSpacing: 4,
            color: 'rgba(255, 255, 255, 0.6)',
            textTransform: 'uppercase',
          }}
        >
          ✦ {videoData.category || 'FEATURED SPOTLIGHT'} ✦
        </span>
      </div>

      {/* SCENE 0: Hook / Intro (0 - 60 frames = 2 seconds) */}
      <Sequence from={0} durationInFrames={60}>
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            transform: `scale(${introScale})`,
            textAlign: 'center',
            padding: '0 50px',
          }}
        >
          <div style={{ fontSize: 90, marginBottom: 20 }}>{videoData.hookEmoji || '✨'}</div>
          <h1
            style={{
              fontFamily: 'system-ui, -apple-system, sans-serif',
              fontSize: 78,
              fontWeight: 900,
              lineHeight: 1.15,
              background: 'linear-gradient(135deg, #FFF 30%, #00F0FF 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              marginBottom: 20,
              whiteSpace: 'pre-line',
            }}
          >
            {videoData.title}
          </h1>
          <p
            style={{
              fontFamily: 'system-ui, -apple-system, sans-serif',
              fontSize: 32,
              fontWeight: 600,
              color: '#FF007A',
              letterSpacing: 2,
            }}
          >
            {videoData.subtitle}
          </p>
        </div>
      </Sequence>

      {/* SCENES 1..3: Facts dynamically loaded from videoData.json */}
      {videoData.facts.map((fact: FactItem, index: number) => {
        // Frame ranges: 60-180 (Fact 1), 180-300 (Fact 2), 300-410 (Fact 3)
        const startFrames = [60, 180, 300];
        const durations = [120, 120, 110];
        const start = startFrames[index] ?? 60 + index * 120;
        const duration = durations[index] ?? 110;

        return (
          <Sequence key={fact.number || index} from={start} durationInFrames={duration}>
            <FactCard
              factNumber={fact.number || index + 1}
              badge={fact.badge}
              headline={fact.headline}
              subtext={fact.subtext}
              highlightWord={fact.highlightWord}
              emoji={fact.emoji}
            />
          </Sequence>
        );
      })}

      {/* SCENE 4: Outro (410 - 450 frames) */}
      <Sequence from={410} durationInFrames={40}>
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            textAlign: 'center',
            padding: '0 50px',
          }}
        >
          <div style={{ fontSize: 90, marginBottom: 20 }}>{videoData.outroEmoji || '🚀'}</div>
          <h2
            style={{
              fontFamily: 'system-ui, -apple-system, sans-serif',
              fontSize: 68,
              fontWeight: 900,
              color: '#FFFFFF',
              marginBottom: 16,
            }}
          >
            {videoData.outroTitle}
          </h2>
          <p
            style={{
              fontFamily: 'system-ui, -apple-system, sans-serif',
              fontSize: 36,
              fontWeight: 700,
              color: '#00F0FF',
            }}
          >
            {videoData.outroSubtitle}
          </p>
        </div>
      </Sequence>

      {/* Persistent Bottom Progress Bar */}
      <ProgressBar />
    </AbsoluteFill>
  );
};
