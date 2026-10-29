import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';

export const TypingCodeWindow: React.FC<{ startFrame: number, code: string, title: string, language?: string }> = ({ startFrame, code, title, language }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const activeFrame = Math.max(0, frame - startFrame);

  // 3D Entrance Spring
  const entrance = spring({
    frame: activeFrame,
    fps,
    config: { damping: 12, stiffness: 100, mass: 1 },
  });

  const scale = interpolate(entrance, [0, 1], [0.4, 1]);
  const rotateX = interpolate(entrance, [0, 1], [45, 0]);
  const rotateY = interpolate(entrance, [0, 1], [-30, 0]);
  const opacity = interpolate(entrance, [0, 1], [0, 1]);

  // Typing effect
  const charsPerFrame = 2;
  const typedLength = Math.max(0, Math.floor((activeFrame - 15) * charsPerFrame));
  const displayedCode = code.slice(0, typedLength);
  const isTyping = typedLength < code.length && activeFrame > 15;

  if (frame < startFrame) return null;

  // Syntax highlighting por tokens (seguro, sin HTML inyectado)
  const KEYWORDS = /^(public|static|void|class|namespace|using|interface|const|string|program|begin|end|var|writeln|readln|async|let|type|number)$/i;
  const TYPES = /^(Console|WriteLine|Main|HelloWorld|Developer|Hello|Anders|Task|Promise)$/;
  const renderCode = () => {
    const tokens = displayedCode.split(/(".*?"|'.*?'|\w+|[{}()[\];:<>=.,]|\s+)/g).filter((t) => t !== '');
    return (
      <span>
        {tokens.map((t, i) => {
          let color: string | undefined;
          if (/^["'].*["']$/.test(t)) color = '#A5D6FF';
          else if (KEYWORDS.test(t)) color = '#FF7B72';
          else if (TYPES.test(t)) color = '#D2A8FF';
          else if (/^[{}()[\];]$/.test(t)) color = '#FFD700';
          return (
            <span key={i} style={color ? { color } : undefined}>
              {t}
            </span>
          );
        })}
      </span>
    );
  };

  return (
    <div style={{
      position: 'absolute',
      top: '20%',
      left: '10%',
      width: '80%',
      backgroundColor: 'rgba(13, 17, 23, 0.95)',
      borderRadius: 16,
      border: '1px solid rgba(255,255,255,0.1)',
      boxShadow: '0 30px 80px rgba(0,0,0,0.8), 0 0 40px rgba(88, 166, 255, 0.2)',
      overflow: 'hidden',
      transform: `perspective(1000px) scale(${scale}) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
      opacity,
      fontFamily: '"Fira Code", "Consolas", monospace',
      zIndex: 60,
    }}>
      {/* Mac OS Header */}
      <div style={{
        backgroundColor: 'rgba(22, 27, 34, 1)',
        padding: '16px 20px',
        display: 'flex',
        alignItems: 'center',
        borderBottom: '1px solid rgba(255,255,255,0.05)'
      }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <div style={{ width: 14, height: 14, borderRadius: '50%', backgroundColor: '#FF5F56', boxShadow: '0 0 10px #FF5F56' }} />
          <div style={{ width: 14, height: 14, borderRadius: '50%', backgroundColor: '#FFBD2E', boxShadow: '0 0 10px #FFBD2E' }} />
          <div style={{ width: 14, height: 14, borderRadius: '50%', backgroundColor: '#27C93F', boxShadow: '0 0 10px #27C93F' }} />
        </div>
        <div style={{ flex: 1, textAlign: 'center', color: '#8b949e', fontSize: 16, fontWeight: 600, letterSpacing: 1 }}>
          {title}
        </div>
      </div>
      
      {/* Code Editor Body */}
      <div style={{ 
        padding: '30px', 
        color: '#c9d1d9', 
        fontSize: 32, 
        lineHeight: 1.6, 
        whiteSpace: 'pre-wrap',
        textShadow: '0 0 2px rgba(255,255,255,0.3)'
      }}>
        {renderCode()}
        {isTyping && <span style={{ 
            display: 'inline-block', 
            width: 14, 
            height: 34, 
            backgroundColor: '#58a6ff', 
            verticalAlign: 'middle',
            marginLeft: 4,
            boxShadow: '0 0 10px #58a6ff'
        }} />}
      </div>
    </div>
  );
};
