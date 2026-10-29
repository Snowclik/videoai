import React from 'react';
import { Composition } from 'remotion';
import { MainComposition, TOTAL_FRAMES } from './Composition';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="VideoComposition"
        component={MainComposition}
        durationInFrames={TOTAL_FRAMES}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{}}
      />
    </>
  );
};
