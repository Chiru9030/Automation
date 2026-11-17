import React from 'react';
import { useCurrentFrame, useVideoConfig } from 'remotion';

export const ProgressBar: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const progress = Math.min((frame / durationInFrames) * 100, 100);

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 70,
        left: '10%',
        width: '80%',
        height: 10,
        backgroundColor: 'rgba(255, 255, 255, 0.15)',
        borderRadius: 5,
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          width: `${progress}%`,
          height: '100%',
          background: 'linear-gradient(90deg, #00F0FF, #7000FF, #FF007A)',
          borderRadius: 5,
          boxShadow: '0 0 12px rgba(0, 240, 255, 0.8)',
        }}
      />
    </div>
  );
};

