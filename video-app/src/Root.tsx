import React from 'react';
import { Composition } from 'remotion';
import { SpaceFacts } from './SpaceFacts';
import { StoryVideo } from './StoryVideo';

export const Root: React.FC = () => {
  return (
    <>
      {/* 15-second Quick Facts Composition */}
      <Composition
        id="SpaceFacts"
        component={SpaceFacts}
        durationInFrames={450} // 15 seconds at 30fps
        fps={30}
        width={1080}
        height={1920}
      />

      {/* 60-second Story Video Composition */}
      <Composition
        id="StoryVideo"
        component={StoryVideo}
        durationInFrames={1800} // 60 seconds at 30fps
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};
