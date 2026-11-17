import React, { useMemo } from 'react';
import { AbsoluteFill, random, useCurrentFrame } from 'remotion';

export const Starfield: React.FC = () => {
  const frame = useCurrentFrame();

  const stars = useMemo(() => {
    return Array.from({ length: 90 }).map((_, i) => ({
      x: random(`star-x-${i}`) * 100,
      y: random(`star-y-${i}`) * 100,
      size: 1 + random(`star-size-${i}`) * 3.5,
      speed: 0.15 + random(`star-speed-${i}`) * 0.4,
      twinkleOffset: random(`star-twinkle-${i}`) * 10,
    }));
  }, []);

  return (
    <AbsoluteFill
      style={{
        background: 'radial-gradient(ellipse at center, #0d1326 0%, #030611 100%)',
        overflow: 'hidden',
      }}
    >
      {stars.map((star, i) => {
        const currentY = (star.y + frame * star.speed) % 100;
        const opacity = 0.35 + 0.65 * Math.sin((frame + star.twinkleOffset) / 8);

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${star.x}%`,
              top: `${currentY}%`,
              width: star.size,
              height: star.size,
              borderRadius: '50%',
              backgroundColor: '#ffffff',
              boxShadow: `0 0 ${star.size * 2}px rgba(255, 255, 255, 0.8)`,
              opacity,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

