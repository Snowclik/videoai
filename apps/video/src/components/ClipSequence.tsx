import React from 'react';
import {
  OffthreadVideo,
  Audio,
  staticFile,
  useCurrentFrame,
  interpolate,
} from 'remotion';
import { ClipData } from '../types';
import { Subtitles } from './Subtitles';
import { TypingCodeWindow } from './CodeWindow';
import { SourcesList } from './SourcesList';
import { DynamicBackground } from './DynamicBackground';

interface ClipSequenceProps {
  clip: ClipData;
  isFirst: boolean;
  totalFrames: number;
}

export const ClipSequence: React.FC<ClipSequenceProps> = ({
  clip,
}) => {
  const frame = useCurrentFrame();

  // Gentle continuous zoom-in for clips >= 5s to keep viewer retention
  const zoomScale = clip.has_zoom
    ? interpolate(frame, [0, clip.duration_frames], [1.0, 1.10], {
        extrapolateRight: 'clamp',
      })
    : 1.0;

  // Subtle clean flash/glimmer on theme transitions (first 6 frames)
  const themeFlashOpacity = clip.is_theme_transition
    ? interpolate(frame, [0, 2, 8], [0, 0.22, 0], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      })
    : 0;

  return (
    <div
      style={{
        position: 'relative',
        width: 1080,
        height: 1920,
        backgroundColor: '#000000',
        overflow: 'hidden',
      }}
    >
      {/* 3D Animated Grid Background */}
      <DynamicBackground />

      {/* Stabilized Video Centered in Vertical 9:16 Frame, but smaller with rounded corners to float on the background */}
      <div
        style={{
          position: 'absolute',
          top: '15%',
          left: '5%',
          width: '90%',
          height: '65%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          transform: `scale(${zoomScale})`,
          transformOrigin: 'center center',
          borderRadius: 32,
          overflow: 'hidden',
          boxShadow: '0 25px 60px rgba(0,0,0,0.6)',
          zIndex: 20
        }}
      >
        <OffthreadVideo
          src={staticFile(clip.video_source)}
          startFrom={clip.source_start_frame}
          muted
          style={{
            height: '100%',
            width: '100%',
            objectFit: 'cover',
          }}
        />
      </div>

      {/* Clean Audio for this clip */}
      <Audio src={staticFile(clip.clean_audio)} volume={1.0} />

      {/* Thematic Transition Sound Effect (only plays at the start of a new topic) */}
      {clip.is_theme_transition && (
        <Audio src={staticFile('sfx/topic_transition.wav')} volume={0.45} />
      )}

      {/* Subtle visual transition accent for topic change */}
      {clip.is_theme_transition && themeFlashOpacity > 0 && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: '#ffffff',
            opacity: themeFlashOpacity,
            pointerEvents: 'none',
            mixBlendMode: 'overlay',
          }}
        />
      )}

      {clip.id === 'clip_csharp' && (
        <TypingCodeWindow startFrame={45} title="Program.cs" code={`using System;\n\nnamespace Anders {\n  class HelloWorld {\n    static void Main() {\n      Console.WriteLine("Hello C#!");\n    }\n  }\n}`} />
      )}
      {clip.id === 'clip_anders' && (
        <TypingCodeWindow startFrame={30} title="index.ts" code={`interface Developer {\n  name: string;\n  languages: string[];\n}\n\nconst creator: Developer = {\n  name: 'Anders Hejlsberg',\n  languages: ['C#', 'TypeScript', 'Pascal']\n};`} />
      )}
      
      {clip.id === 'clip_sources' && (
        <SourcesList startFrame={30} />
      )}

      {/* Dynamic Subtitles con tag de tema y estilos rotativos */}
      <Subtitles
        words={clip.words}
        clipTag={clip.tag}
        isThemeTransition={clip.is_theme_transition}
      />
    </div>
  );
};
