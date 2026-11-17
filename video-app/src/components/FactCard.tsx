import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface FactCardProps {
  factNumber: number;
  badge: string;
  headline: string;
  subtext: string;
  highlightWord: string;
  emoji: string;
}

export const FactCard: React.FC<FactCardProps> = ({
  factNumber,
  badge,
  headline,
  subtext,
  highlightWord,
  emoji,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const scale = spring({
    frame,
    fps,
    config: { damping: 11, stiffness: 100, mass: 0.6 },
  });

  const opacity = interpolate(frame, [0, 10], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Highlight word pulse
  const pulse = 1 + 0.05 * Math.sin(frame / 4);

  // Render text with highlight
  const parts = headline.split(highlightWord);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        padding: '0 60px',
        opacity,
        transform: `scale(${scale})`,
        textAlign: 'center',
      }}
    >
      {/* Category / Number Tag */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '10px 28px',
          borderRadius: 30,
          background: 'rgba(255, 255, 255, 0.08)',
          border: '1px solid rgba(0, 240, 255, 0.4)',
          marginBottom: 35,
          boxShadow: '0 0 20px rgba(0, 240, 255, 0.25)',
        }}
      >
        <span style={{ fontSize: 32 }}>{emoji}</span>
        <span
          style={{
            fontFamily: 'system-ui, -apple-system, sans-serif',
            fontSize: 26,
            fontWeight: 800,
            letterSpacing: 2,
            color: '#00F0FF',
            textTransform: 'uppercase',
          }}
        >
          FACT #{factNumber}: {badge}
        </span>
      </div>

      {/* Main Kinetic Headline */}
      <h1
        style={{
          fontFamily: 'system-ui, -apple-system, sans-serif',
          fontSize: 62,
          fontWeight: 900,
          lineHeight: 1.25,
          color: '#FFFFFF',
          marginBottom: 30,
          textShadow: '0 4px 20px rgba(0, 0, 0, 0.8)',
        }}
      >
        {parts[0]}
        <span
          style={{
            color: '#FFD700',
            textShadow: '0 0 25px rgba(255, 215, 0, 0.7)',
            display: 'inline-block',
            transform: `scale(${pulse})`,
          }}
        >
          {highlightWord}
        </span>
        {parts[1] || ''}
      </h1>

      {/* Explanatory Subtext */}
      <p
        style={{
          fontFamily: 'system-ui, -apple-system, sans-serif',
          fontSize: 34,
          fontWeight: 500,
          lineHeight: 1.45,
          color: 'rgba(255, 255, 255, 0.85)',
          maxWidth: 900,
          background: 'rgba(0, 0, 0, 0.4)',
          padding: '24px 36px',
          borderRadius: 20,
          border: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        {subtext}
      </p>
    </div>
  );
};

