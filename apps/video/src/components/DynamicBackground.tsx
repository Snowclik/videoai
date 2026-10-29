import React from 'react';
import { useCurrentFrame, useVideoConfig } from 'remotion';

export const DynamicBackground: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  // Create a cool animated grid/matrix style background using CSS
  const offset = (frame * 2) % 100;

  return (
    <div style={{
      position: 'absolute',
      width: '100%',
      height: '100%',
      backgroundColor: '#050505',
      zIndex: 10,
      overflow: 'hidden'
    }}>
      {/* Animated Grid */}
      <div style={{
        position: 'absolute',
        width: '200%',
        height: '200%',
        top: '-50%',
        left: '-50%',
        backgroundImage: `
          linear-gradient(rgba(0, 229, 255, 0.15) 2px, transparent 2px),
          linear-gradient(90deg, rgba(0, 229, 255, 0.15) 2px, transparent 2px)
        `,
        backgroundSize: '100px 100px',
        transform: `perspective(500px) rotateX(60deg) translateY(${offset}px)`,
        transformOrigin: 'center center'
      }} />
      
      {/* Glowing Orb */}
      <div style={{
        position: 'absolute',
        top: '20%',
        left: '50%',
        width: 600,
        height: 600,
        transform: 'translate(-50%, -50%)',
        background: 'radial-gradient(circle, rgba(0,229,255,0.15) 0%, rgba(0,0,0,0) 70%)',
        filter: 'blur(40px)'
      }} />
    </div>
  );
};
