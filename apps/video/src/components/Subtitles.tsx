import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { WordTimestamp } from '../types';

interface SubtitlesProps {
  words: WordTimestamp[];
  clipTag?: string;
  isThemeTransition?: boolean;
}

// Paleta de highlight vibrante y moderna que rota por frase
const HIGHLIGHT_PALETTE = [
  { bg: '#FFDE00', text: '#111111' },  // Amarillo neon
  { bg: '#00E5FF', text: '#001020' },  // Cyan eléctrico
  { bg: '#FF385C', text: '#FFFFFF' },  // Coral vivo
  { bg: '#00E676', text: '#002B11' },  // Verde menta
  { bg: '#FF9100', text: '#111111' },  // Naranja
  { bg: '#E040FB', text: '#FFFFFF' },  // Magenta
];

export const Subtitles: React.FC<SubtitlesProps> = ({ words, clipTag, isThemeTransition }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!words || words.length === 0) return null;

  // ── 1. Agrupar palabras en frases legibles de 3 a 4 palabras (máx 26 caracteres) ──
  const phrases: WordTimestamp[][] = [];
  let current: WordTimestamp[] = [];
  let currentLen = 0;

  for (let i = 0; i < words.length; i++) {
    const w = words[i];
    current.push(w);
    currentLen += w.word.length;
    const endsWithPunct = /[.,?!;:…]$/.test(w.word);

    if (current.length >= 4 || currentLen >= 24 || endsWithPunct || i === words.length - 1) {
      phrases.push(current);
      current = [];
      currentLen = 0;
    }
  }

  // ── 2. Encontrar frase activa y calcular continuidad ────────────────────────
  let activePhraseIdx = -1;

  for (let i = 0; i < phrases.length; i++) {
    const p = phrases[i];
    const pStart = p[0].start_frame;
    const nextPhrase = phrases[i + 1];

    // Si la siguiente frase empieza pronto, la frase actual permanece hasta que empiece la siguiente
    // Si hay una pausa larga (> 12 frames), la frase se mantiene visible 10 frames después de hablar
    const pEnd = nextPhrase
      ? Math.min(p[p.length - 1].end_frame + 10, nextPhrase[0].start_frame)
      : p[p.length - 1].end_frame + 12;

    if (frame >= pStart && frame < pEnd) {
      activePhraseIdx = i;
      break;
    }
  }

  // Si no está dentro de ningún rango activo, no renderizar
  if (activePhraseIdx === -1) return null;

  const activePhrase = phrases[activePhraseIdx];
  const highlight = HIGHLIGHT_PALETTE[activePhraseIdx % HIGHLIGHT_PALETTE.length];

  const phraseStart = activePhrase[0].start_frame;
  const phraseLastWordEnd = activePhrase[activePhrase.length - 1].end_frame;
  const nextPhrase = phrases[activePhraseIdx + 1];
  const prevPhrase = phrases[activePhraseIdx - 1];

  // ¿Viene de una pausa larga o es la primera? (Si viene pegada a la anterior, NO hace slide-in brusco)
  const isFirstInBurst = !prevPhrase || (phraseStart - prevPhrase[prevPhrase.length - 1].end_frame > 12);

  // ¿Va hacia una pausa larga o es la última? (Si va pegada a la siguiente, NO hace fade-out que choque)
  const isLastInBurst = !nextPhrase || (nextPhrase[0].start_frame - phraseLastWordEnd > 12);

  // ── 3. Animación limpia y sin choques ─────────────────────────────────────────
  let opacity = 1;
  let translateY = 0;

  if (isFirstInBurst) {
    // Solo hace entrada si venía de un silencio
    const framesSinceStart = Math.max(0, frame - phraseStart);
    const entrance = spring({
      frame: framesSinceStart,
      fps,
      config: { damping: 20, stiffness: 300, mass: 0.5 },
    });
    translateY = interpolate(entrance, [0, 1], [25, 0]);
    opacity = interpolate(entrance, [0, 0.4], [0, 1], { extrapolateRight: 'clamp' });
  }

  if (isLastInBurst && frame > phraseLastWordEnd) {
    // Solo hace fade-out si va hacia un silencio
    const fadeOut = interpolate(
      frame,
      [phraseLastWordEnd + 2, phraseLastWordEnd + 12],
      [1, 0],
      { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
    );
    opacity = opacity * fadeOut;
  }

  // ── 4. Tag del tema (solo en transición de tema) ──────────────────────────────
  const tagVisible = isThemeTransition && frame < 65;
  const tagAlpha = tagVisible
    ? interpolate(frame, [0, 8, 50, 65], [0, 1, 1, 0], { extrapolateRight: 'clamp' })
    : 0;

  return (
    <>
      {/* TAG DEL TEMA */}
      {tagAlpha > 0 && clipTag && (
        <div
          style={{
            position: 'absolute',
            top: 130,
            left: 0,
            right: 0,
            display: 'flex',
            justifyContent: 'center',
            zIndex: 80,
            pointerEvents: 'none',
            opacity: tagAlpha,
          }}
        >
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 12,
              backgroundColor: '#FFFFFF',
              borderRadius: 100,
              paddingLeft: 30,
              paddingRight: 36,
              paddingTop: 12,
              paddingBottom: 12,
              boxShadow: '0 8px 30px rgba(0,0,0,0.25)',
            }}
          >
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                backgroundColor: highlight.bg,
              }}
            />
            <span
              style={{
                fontFamily: '"Plus Jakarta Sans", sans-serif',
                fontSize: 28,
                fontWeight: 800,
                color: '#111111',
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
              }}
            >
              {clipTag}
            </span>
          </div>
        </div>
      )}

      {/* BLOQUE DE SUBTÍTULOS CON FONDO BLANCO ESTABLE */}
      <div
        style={{
          position: 'absolute',
          bottom: 210,
          left: 40,
          right: 40,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 70,
          pointerEvents: 'none',
          opacity,
          transform: `translateY(${translateY}px)`,
        }}
      >
        <div
          style={{
            backgroundColor: '#FFFFFF',
            borderRadius: 24,
            padding: '22px 34px',
            boxShadow: '0 14px 45px rgba(0,0,0,0.32), 0 3px 12px rgba(0,0,0,0.18)',
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'center',
            alignItems: 'center',
            rowGap: 8,
            columnGap: 4,
            maxWidth: 1000,
          }}
        >
          {activePhrase.map((w, idx) => {
            const isSpoken = frame >= w.start_frame && frame <= w.end_frame + 2;
            const isPast = frame > w.end_frame + 2;

            // Micro animación de escala sin desplazar a las demás palabras
            const wordElapsed = Math.max(0, frame - w.start_frame);
            const bounce = spring({
              frame: wordElapsed,
              fps,
              config: { damping: 12, stiffness: 380, mass: 0.25 },
            });
            const wordScale = isSpoken ? interpolate(bounce, [0, 1], [1.0, 1.08]) : 1.0;

            return (
              <span
                key={`${w.word}-${idx}`}
                style={{
                  display: 'inline-flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  // Dimensiones, paddings y font-weight 100% constantes para que NUNCA salte de 1 a 2 líneas
                  padding: '6px 14px',
                  borderRadius: 14,
                  fontSize: 52,
                  fontWeight: 800,
                  fontFamily: '"Plus Jakarta Sans", sans-serif',
                  letterSpacing: '-0.02em',
                  lineHeight: 1.2,
                  whiteSpace: 'nowrap',
                  // Highlight visual limpio
                  color: isSpoken ? highlight.text : isPast ? '#666666' : '#151515',
                  backgroundColor: isSpoken ? highlight.bg : 'transparent',
                  transform: `scale(${wordScale})`,
                  transformOrigin: 'center center',
                  transition: 'background-color 0.08s ease, color 0.08s ease',
                }}
              >
                {w.word}
              </span>
            );
          })}
        </div>
      </div>
    </>
  );
};

