import React from 'react';
import {
  AbsoluteFill,
  Img,
  Loop,
  OffthreadVideo,
  interpolate,
  random,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

export const FONT = '"Plus Jakarta Sans", system-ui, sans-serif';

// Duración (frames a 30fps) de cada video de fondo para hacer bucle
const BG_FRAMES: Record<string, number> = {
  'bg/9757.mp4': 628,
  'bg/41654.mp4': 213,
  'bg/46635.mp4': 339,
  'bg/14396.mp4': 622,
};

/** Video de fondo oscurecido y teñido, con zoom lento (Ken Burns). */
export const BgVideo: React.FC<{ src: string; tint: string; startFrom?: number; zoomTo?: number }> = ({
  src,
  tint,
  startFrom = 0,
  zoomTo = 1.18,
}) => {
  const frame = useCurrentFrame();
  const s = interpolate(frame, [0, 400], [1.05, zoomTo], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ overflow: 'hidden', backgroundColor: '#05060a' }}>
      <AbsoluteFill style={{ transform: `scale(${s})` }}>
        <Loop durationInFrames={(BG_FRAMES[src] ?? 200) - startFrom - 2}>
          <OffthreadVideo
            src={staticFile(src)}
            startFrom={startFrom}
            muted
            style={{ width: '100%', height: '100%', objectFit: 'cover', filter: 'saturate(1.3) contrast(1.1) brightness(0.55)' }}
          />
        </Loop>
      </AbsoluteFill>
      <AbsoluteFill style={{ background: `linear-gradient(160deg, ${tint}66 0%, #05060acc 60%, #05060aee 100%)`, mixBlendMode: 'multiply' }} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 35%, ${tint}33 0%, transparent 60%)` }} />
    </AbsoluteFill>
  );
};

/** Partículas flotantes deterministas. */
export const Particles: React.FC<{ color: string; count?: number }> = ({ color, count = 36 }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: 'none' }}>
      {Array.from({ length: count }).map((_, i) => {
        const x = random(`x${i}`) * 1080;
        const size = 4 + random(`s${i}`) * 10;
        const speed = 0.6 + random(`v${i}`) * 1.8;
        const y = 1920 - ((frame * speed * 2 + random(`y${i}`) * 2200) % 2200) + 100;
        const sway = Math.sin(frame / 20 + i) * 30;
        const op = 0.15 + random(`o${i}`) * 0.5;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x + sway,
              top: y,
              width: size,
              height: size,
              borderRadius: '50%',
              backgroundColor: color,
              opacity: op,
              boxShadow: `0 0 ${size * 3}px ${color}`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/** Grano de película animado + viñeta. */
export const FilmLook: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: 'none', zIndex: 90 }}>
      <svg width="100%" height="100%" style={{ position: 'absolute', opacity: 0.09, mixBlendMode: 'overlay' }}>
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={frame % 12} />
        </filter>
        <rect width="100%" height="100%" filter="url(#grain)" />
      </svg>
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.65) 100%)' }} />
    </AbsoluteFill>
  );
};

/** Texto con glitch RGB al entrar. */
export const GlitchText: React.FC<{ text: string; size: number; color?: string; delay?: number; accent: string }> = ({
  text,
  size,
  color = '#fff',
  delay = 0,
  accent,
}) => {
  const frame = useCurrentFrame() - delay;
  const { fps } = useVideoConfig();
  if (frame < 0) return null;
  const p = spring({ frame, fps, config: { damping: 14, stiffness: 140 } });
  const glitch = frame < 14 ? (random(`g${frame}`) - 0.5) * 40 * (1 - frame / 14) : 0;
  const base: React.CSSProperties = {
    position: 'absolute',
    inset: 0,
    fontSize: size,
    fontWeight: 900,
    letterSpacing: '-0.02em',
    textAlign: 'center',
    lineHeight: 1,
    whiteSpace: 'pre-line',
    fontFamily: FONT,
    textTransform: 'uppercase',
  };
  return (
    <div
      style={{
        position: 'relative',
        transform: `scale(${interpolate(p, [0, 1], [1.6, 1])})`,
        opacity: p,
        filter: frame < 14 ? 'none' : `drop-shadow(0 0 24px ${accent}88)`,
      }}
    >
      <div style={{ ...base, color: '#ff2d55', transform: `translateX(${glitch}px)`, mixBlendMode: 'screen', opacity: frame < 14 ? 1 : 0 }}>{text}</div>
      <div style={{ ...base, color: '#00e5ff', transform: `translateX(${-glitch}px)`, mixBlendMode: 'screen', opacity: frame < 14 ? 1 : 0 }}>{text}</div>
      <div style={{ ...base, position: 'relative', color, textShadow: `0 6px 40px ${accent}aa` }}>{text}</div>
    </div>
  );
};

/** Icono que "salta" con rebote, flota y brilla. */
export const PopIcon: React.FC<{ src: string; size: number; x: number; y: number; delay: number; accent: string; rotate?: number }> = ({
  src,
  size,
  x,
  y,
  delay,
  accent,
  rotate = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = frame - delay;
  if (f < 0) return null;
  const p = spring({ frame: f, fps, config: { damping: 9, stiffness: 160, mass: 0.7 } });
  const float = Math.sin((frame + delay * 3) / 18) * 14;
  return (
    <div
      style={{
        position: 'absolute',
        left: x - size / 2,
        top: y - size / 2 + float,
        width: size,
        height: size,
        padding: size * 0.18,
        borderRadius: size * 0.28,
        background: 'linear-gradient(145deg, rgba(255,255,255,0.18), rgba(255,255,255,0.04))',
        border: '2px solid rgba(255,255,255,0.25)',
        backdropFilter: 'blur(14px)',
        boxShadow: `0 20px 60px rgba(0,0,0,0.5), 0 0 60px ${accent}77`,
        transform: `scale(${p}) rotate(${interpolate(p, [0, 1], [-40, rotate])}deg)`,
        zIndex: 40,
      }}
    >
      <Img src={staticFile(src)} style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
    </div>
  );
};

/** Etiqueta tipo píldora que se desliza. */
export const Chip: React.FC<{ text: string; accent: string; delay?: number; top?: number }> = ({ text, accent, delay = 0, top = 130 }) => {
  const frame = useCurrentFrame() - delay;
  const { fps } = useVideoConfig();
  if (frame < 0) return null;
  const p = spring({ frame, fps, config: { damping: 16, stiffness: 150 } });
  return (
    <div style={{ position: 'absolute', top, left: 0, right: 0, display: 'flex', justifyContent: 'center', zIndex: 80 }}>
      <div
        style={{
          transform: `translateY(${interpolate(p, [0, 1], [-60, 0])}px) scale(${interpolate(p, [0, 1], [0.6, 1])})`,
          opacity: p,
          display: 'flex',
          alignItems: 'center',
          gap: 14,
          padding: '14px 38px',
          borderRadius: 100,
          backgroundColor: '#fff',
          boxShadow: `0 10px 40px ${accent}88`,
        }}
      >
        <div style={{ width: 16, height: 16, borderRadius: '50%', backgroundColor: accent, boxShadow: `0 0 12px ${accent}` }} />
        <span style={{ fontFamily: FONT, fontWeight: 800, fontSize: 30, letterSpacing: '0.1em', color: '#111', textTransform: 'uppercase' }}>{text}</span>
      </div>
    </div>
  );
};

/** Contador animado de años (rueda de números). */
export const YearCounter: React.FC<{ from: number; to: number; delay: number; accent: string; label: string; y: number }> = ({
  from,
  to,
  delay,
  accent,
  label,
  y,
}) => {
  const frame = useCurrentFrame() - delay;
  const { fps } = useVideoConfig();
  if (frame < 0) return null;
  const p = spring({ frame, fps, config: { damping: 30, stiffness: 60 }, durationInFrames: 50 });
  const value = Math.round(interpolate(p, [0, 1], [from, to]));
  const pop = spring({ frame, fps, config: { damping: 10, stiffness: 120 } });
  return (
    <div style={{ position: 'absolute', top: y, left: 0, right: 0, textAlign: 'center', transform: `scale(${pop})`, zIndex: 45 }}>
      <div
        style={{
          fontFamily: FONT,
          fontSize: 230,
          fontWeight: 900,
          lineHeight: 1,
          color: '#fff',
          textShadow: `0 0 60px ${accent}, 0 10px 50px rgba(0,0,0,0.6)`,
          WebkitTextStroke: `3px ${accent}`,
        }}
      >
        {value}
      </div>
      <div style={{ fontFamily: FONT, fontSize: 40, fontWeight: 800, color: accent, letterSpacing: '0.2em', textTransform: 'uppercase' }}>{label}</div>
    </div>
  );
};

/** Transición global: persianas de color con destello y glitch en cada corte. */
export const Transitions: React.FC<{ cuts: number[]; colors: string[] }> = ({ cuts, colors }) => {
  const frame = useCurrentFrame();
  const BARS = 8;
  return (
    <AbsoluteFill style={{ pointerEvents: 'none', zIndex: 95 }}>
      {cuts.map((cut, ci) => {
        const f = frame - (cut - 10);
        if (f < 0 || f > 24) return null;
        const color = colors[ci % colors.length];
        return (
          <React.Fragment key={cut}>
            {Array.from({ length: BARS }).map((_, i) => {
              const st = i * 0.9;
              const inP = interpolate(f, [st, st + 8], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
              const outP = interpolate(f, [10 + st * 0.6, 22], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
              const w = (inP - outP) * 1080;
              return (
                <div
                  key={i}
                  style={{
                    position: 'absolute',
                    top: (i * 1920) / BARS,
                    height: 1920 / BARS + 2,
                    left: outP > 0 ? 1080 - w : 0,
                    width: w,
                    background: i % 2 ? color : '#0a0b12',
                    boxShadow: `0 0 40px ${color}`,
                  }}
                />
              );
            })}
            <AbsoluteFill
              style={{
                backgroundColor: '#fff',
                opacity: interpolate(f, [8, 11, 16], [0, 0.55, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }),
                mixBlendMode: 'overlay',
              }}
            />
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};

/** Empuje de cámara al entrar la escena (zoom + leve sacudida). */
export const CameraPunch: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - 6, fps, config: { damping: 14, stiffness: 90 } });
  const shake = frame < 18 ? (random(`sh${frame}`) - 0.5) * 14 * (1 - frame / 18) : 0;
  return (
    <AbsoluteFill style={{ transform: `scale(${interpolate(p, [0, 1], [1.18, 1])}) translate(${shake}px, ${-shake}px)` }}>{children}</AbsoluteFill>
  );
};

/** Barra inferior-izquierda con nombre. */
export const LowerThird: React.FC<{ title: string; subtitle: string; accent: string; delay: number; top: number }> = ({
  title,
  subtitle,
  accent,
  delay,
  top,
}) => {
  const frame = useCurrentFrame() - delay;
  const { fps } = useVideoConfig();
  if (frame < 0) return null;
  const p = spring({ frame, fps, config: { damping: 18, stiffness: 120 } });
  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 70,
        right: 70,
        transform: `translateX(${interpolate(p, [0, 1], [-900, 0])}px)`,
        zIndex: 50,
      }}
    >
      <div
        style={{
          borderLeft: `10px solid ${accent}`,
          padding: '18px 30px',
          background: 'linear-gradient(90deg, rgba(0,0,0,0.75), rgba(0,0,0,0.2))',
          backdropFilter: 'blur(10px)',
          borderRadius: '0 20px 20px 0',
        }}
      >
        <div style={{ fontFamily: FONT, fontWeight: 900, fontSize: 64, color: '#fff', lineHeight: 1.05, textTransform: 'uppercase' }}>{title}</div>
        <div style={{ fontFamily: FONT, fontWeight: 600, fontSize: 32, color: accent, marginTop: 6 }}>{subtitle}</div>
      </div>
    </div>
  );
};
