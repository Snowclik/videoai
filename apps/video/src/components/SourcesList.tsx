import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';

export const SourcesList: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (frame < startFrame) return null;

  const entrance = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 20, stiffness: 200, mass: 1 },
  });

  const translateY = interpolate(entrance, [0, 1], [50, 0]);
  const opacity = interpolate(entrance, [0, 1], [0, 1]);

  const sources = [
    "Microsoft Docs - Historia de C#",
    "Entrevista a Anders Hejlsberg (Channel 9)",
    "Documentación de TypeScript",
    "Museo de Historia de la Computación",
  ];

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      backgroundColor: 'rgba(0,0,0,0.85)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 100,
      opacity,
      transform: `translateY(${translateY}px)`,
    }}>
      <h2 style={{
        color: '#FFFFFF',
        fontSize: 64,
        fontWeight: 800,
        marginBottom: 60,
        fontFamily: '"Plus Jakarta Sans", sans-serif',
      }}>Fuentes de Investigación</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 30 }}>
        {sources.map((src, i) => {
          const itemSpring = spring({
            frame: Math.max(0, frame - startFrame - (i * 10)),
            fps,
            config: { damping: 15, stiffness: 150 },
          });
          const itemY = interpolate(itemSpring, [0, 1], [30, 0]);
          const itemOp = interpolate(itemSpring, [0, 1], [0, 1]);
          return (
            <div key={i} style={{
              backgroundColor: '#1E1E1E',
              padding: '24px 40px',
              borderRadius: 16,
              color: '#A0A0A0',
              fontSize: 32,
              fontFamily: '"Plus Jakarta Sans", sans-serif',
              transform: `translateY(${itemY}px)`,
              opacity: itemOp,
              boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
              borderLeft: '8px solid #00E5FF'
            }}>
              {src}
            </div>
          );
        })}
      </div>
    </div>
  );
};
