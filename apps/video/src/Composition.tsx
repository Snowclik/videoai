import React from 'react';
import { AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { TimelineData } from './types';
import timelineRaw from './timeline.json';
import { Subtitles } from './components/Subtitles';
import { TypingCodeWindow } from './components/CodeWindow';
import { SourcesList } from './components/SourcesList';
import { DynamicBackground } from './components/DynamicBackground';
import {
  BgVideo,
  CameraPunch,
  Chip,
  FONT,
  FilmLook,
  GlitchText,
  LowerThird,
  Particles,
  PopIcon,
  Transitions,
  YearCounter,
} from './components/Fx';

const timeline = timelineRaw as unknown as TimelineData & {
  words: TimelineData['clips'][number]['words'];
  scenes: { index: number; start_frame: number; end_frame: number; duration_frames: number; text: string }[];
};

export const OUTRO_FRAMES = 210;
export const TOTAL_FRAMES = timeline.total_frames + OUTRO_FRAMES;

const COLORS = ['#00E5FF', '#FFDE00', '#B388FF', '#00E676', '#FF6D00', '#FF385C'];

/** Foto real con entrada 3D, Ken Burns y marco brillante. */
const PhotoCard: React.FC<{ src: string; x: number; y: number; w: number; h: number; accent: string; delay?: number; round?: boolean; pos?: string }> = ({
  src, x, y, w, h, accent, delay = 0, round = false, pos = 'center 20%',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = Math.max(0, frame - delay);
  const p = spring({ frame: f, fps, config: { damping: 13, stiffness: 90 } });
  if (frame < delay) return null;
  const kb = interpolate(frame, [0, 400], [1.0, 1.22], { extrapolateRight: 'clamp' });
  return (
    <div
      style={{
        position: 'absolute', left: x, top: y, width: w, height: h,
        borderRadius: round ? '50%' : 40, overflow: 'hidden',
        border: `6px solid ${accent}`,
        boxShadow: `0 40px 100px rgba(0,0,0,0.7), 0 0 90px ${accent}88`,
        transform: `perspective(1200px) rotateY(${interpolate(p, [0, 1], [-60, 0])}deg) rotateX(${interpolate(p, [0, 1], [20, 0])}deg) scale(${interpolate(p, [0, 1], [0.5, 1])}) translateY(${Math.sin(frame / 25) * 8}px)`,
        opacity: p, zIndex: 30,
      }}
    >
      <Img src={staticFile(src)} style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: pos, transform: `scale(${kb})` }} />
      <AbsoluteFill style={{ background: `linear-gradient(180deg, transparent 60%, ${accent}55 100%)` }} />
    </div>
  );
};

const Headline: React.FC<{ text: string; accent: string; top: number; size?: number; delay?: number }> = ({ text, accent, top, size = 110, delay = 4 }) => (
  <div style={{ position: 'absolute', top, left: 40, right: 40, display: 'flex', justifyContent: 'center', zIndex: 60 }}>
    <GlitchText text={text} size={size} accent={accent} delay={delay} />
  </div>
);

/* ───────── Escenas ───────── */

const Scene0: React.FC = () => {
  const a = COLORS[0];
  return (
    <>
      <BgVideo src="bg/9757.mp4" tint="#0066ff" />
      <Particles color={a} />
      <CameraPunch>
        <Chip text="Historia de la programación" accent={a} />
        <Headline text={'¿LO\nSABÍAS?'} accent={a} top={300} size={190} />
        <PopIcon src="icons/csharp.svg" size={330} x={300} y={1000} delay={26} accent="#9B4F96" rotate={-8} />
        <PopIcon src="icons/typescript.svg" size={330} x={780} y={1140} delay={40} accent="#3178C6" rotate={8} />
        <PopIcon src="icons/dotnetcore.svg" size={250} x={540} y={1380} delay={54} accent="#512BD4" />
      </CameraPunch>
    </>
  );
};

const Scene1: React.FC = () => {
  const a = COLORS[1];
  return (
    <>
      <BgVideo src="bg/41654.mp4" tint="#ffb300" />
      <Particles color={a} />
      <CameraPunch>
        <Chip text="El genio detrás del código" accent={a} />
        <PhotoCard src="anders/portrait.jpg" x={190} y={250} w={700} h={950} accent={a} delay={6} />
        <LowerThird title="Anders Hejlsberg" subtitle="Copenhague, 1960 · Microsoft Technical Fellow" accent={a} delay={30} top={1230} />
        <PopIcon src="icons/csharp.svg" size={190} x={900} y={350} delay={44} accent="#9B4F96" rotate={10} />
        <PopIcon src="icons/typescript.svg" size={190} x={170} y={1050} delay={56} accent="#3178C6" rotate={-10} />
      </CameraPunch>
    </>
  );
};

const PASCAL = `program Turbo;\nbegin\n  writeln('Compilado en\n   segundos!');\nend.`;
const Scene2: React.FC = () => {
  const a = COLORS[4];
  return (
    <>
      <BgVideo src="bg/14396.mp4" tint="#ff6d00" />
      <Particles color={a} />
      <CameraPunch>
        <Chip text="Turbo Pascal · Borland" accent={a} />
        <Headline text="Años 80" accent={a} top={230} size={120} />
        <TypingCodeWindow startFrame={20} title="TURBO.PAS" code={PASCAL} />
        <YearCounter from={1975} to={1983} delay={30} accent={a} label="Nace Turbo Pascal" y={1020} />
        <PhotoCard src="anders/speaking.jpg" x={780} y={190} w={230} h={230} accent={a} delay={60} round />
      </CameraPunch>
    </>
  );
};

const CSHARP = `using System;\n\nclass Hola {\n  static void Main() {\n    Console.WriteLine("C#");\n  }\n}`;
const Scene3: React.FC = () => {
  const a = COLORS[2];
  return (
    <>
      <BgVideo src="bg/46635.mp4" tint="#7c4dff" />
      <DynamicBackgroundLite />
      <Particles color={a} />
      <CameraPunch>
        <Chip text="Microsoft · C# y .NET" accent={a} />
        <Headline text="Nace C#" accent={a} top={230} size={120} />
        <TypingCodeWindow startFrame={24} title="Program.cs" code={CSHARP} />
        <YearCounter from={1990} to={2000} delay={34} accent={a} label="Anuncio de C#" y={1020} />
        <PopIcon src="icons/csharp.svg" size={220} x={170} y={470} delay={14} accent="#9B4F96" rotate={-12} />
        <PopIcon src="icons/dotnetcore.svg" size={190} x={920} y={430} delay={26} accent="#512BD4" rotate={12} />
        <PopIcon src="icons/visualstudio.svg" size={170} x={900} y={1420} delay={80} accent="#5C2D91" rotate={8} />
      </CameraPunch>
    </>
  );
};

const TS = `interface Dev {\n  name: string;\n  typed: boolean;\n}\n\nconst a: Dev = {\n  name: 'Anders',\n  typed: true\n};`;
const Scene4: React.FC = () => {
  const a = COLORS[3];
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sw = spring({ frame: frame - 70, fps, config: { damping: 12, stiffness: 100 } });
  return (
    <>
      <BgVideo src="bg/41654.mp4" tint="#00c853" startFrom={120} />
      <Particles color={a} />
      <CameraPunch>
        <Chip text="TypeScript · JavaScript con superpoderes" accent={a} />
        <Headline text="TypeScript" accent={a} top={230} size={120} />
        <TypingCodeWindow startFrame={20} title="index.ts" code={TS} />
        <PopIcon src="icons/javascript.svg" size={220} x={310} y={1250} delay={30} accent="#F7DF1E" rotate={-6} />
        <div style={{ position: 'absolute', left: 0, right: 0, top: 1190, textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 110, color: a, opacity: sw, transform: `scale(${sw})`, textShadow: `0 0 40px ${a}` }}>→</div>
        <PopIcon src="icons/typescript.svg" size={260} x={780} y={1250} delay={70} accent="#3178C6" rotate={6} />
        <YearCounter from={2008} to={2012} delay={100} accent={a} label="Nace TypeScript" y={1380} />
      </CameraPunch>
    </>
  );
};

const Scene5: React.FC = () => {
  const a = COLORS[5];
  return (
    <>
      <BgVideo src="bg/9757.mp4" tint="#ff385c" startFrom={60} />
      <Particles color={a} count={50} />
      <CameraPunch>
        <Chip text="Su legado" accent={a} />
        <PhotoCard src="anders/pdc2008.jpg" x={140} y={240} w={800} h={960} accent={a} delay={4} pos="center 25%" />
        <PopIcon src="icons/csharp.svg" size={170} x={120} y={300} delay={30} accent="#9B4F96" rotate={-14} />
        <PopIcon src="icons/typescript.svg" size={170} x={960} y={420} delay={42} accent="#3178C6" rotate={12} />
        <PopIcon src="icons/dotnetcore.svg" size={150} x={950} y={1130} delay={54} accent="#512BD4" rotate={8} />
        <PopIcon src="icons/vscode.svg" size={150} x={120} y={1100} delay={66} accent="#007ACC" rotate={-8} />
        <LowerThird title="Herramientas elegantes" subtitle="que empoderan a los desarrolladores" accent={a} delay={40} top={1250} />
      </CameraPunch>
    </>
  );
};

/** Rejilla 3D sutil encima del video (profundidad). */
const DynamicBackgroundLite: React.FC = () => (
  <AbsoluteFill style={{ opacity: 0.22, mixBlendMode: 'screen' }}>
    <DynamicBackground />
  </AbsoluteFill>
);

const SCENES = [Scene0, Scene1, Scene2, Scene3, Scene4, Scene5];

export const MainComposition: React.FC = () => {
  const cuts = timeline.scenes.slice(1).map((s) => s.start_frame);
  cuts.push(timeline.total_frames);
  return (
    <AbsoluteFill style={{ backgroundColor: '#000', fontFamily: FONT }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800;900&family=Fira+Code:wght@500&display=swap');`}</style>

      <Audio src={staticFile('music/lofi.mp3')} volume={(f) => interpolate(f, [0, 20, TOTAL_FRAMES - 40, TOTAL_FRAMES], [0, 0.08, 0.08, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })} loop />
      <Audio src={staticFile('voz_masterizada.wav')} volume={1} />

      {timeline.scenes.map((s, i) => {
        const Scene = SCENES[i];
        const dur = s.duration_frames + (i === timeline.scenes.length - 1 ? OUTRO_FRAMES : 0);
        return (
          <Sequence key={i} from={s.start_frame} durationInFrames={dur} name={`Escena ${i + 1}`}>
            <Scene />
          </Sequence>
        );
      })}

      {/* Sonidos de corte */}
      {cuts.map((c) => (
        <Sequence key={c} from={Math.max(0, c - 10)} durationInFrames={45}>
          <Audio src={staticFile('sfx/whoosh.wav')} volume={0.5} />
        </Sequence>
      ))}

      {/* Créditos / fuentes */}
      <Sequence from={timeline.total_frames} durationInFrames={OUTRO_FRAMES}>
        <SourcesList startFrame={8} />
      </Sequence>

      <FilmLook />
      <Transitions cuts={cuts.slice(0, -1).concat([timeline.total_frames - 4])} colors={COLORS} />
      <Subtitles words={timeline.words} />
    </AbsoluteFill>
  );
};
