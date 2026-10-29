# VideoIA — Generador y Productor de Video Motion Graphics & Diseño

VideoIA es una plataforma monorepo diseñada para la generación y renderizado programable de **videos verticales (9:16) en 1080x1920 a 30 FPS** y diseño gráfico vectorial, utilizando pipelines de audio con IA, sincronización de marcas temporales y renderizado frame a frame con **HyperFrames** y **Remotion**.

---

## 📁 Arquitectura del Monorepo

```
VideoIA/
├── apps/
│   ├── video/              # Composición de video motion graphics (HyperFrames + GSAP / Remotion)
│   │   ├── guion/          # Guiones y textos fuente (anders_hejlsberg.txt)
│   │   ├── public/         # Assets multimedia (audio masterizado, música, SFX, imágenes e iconos)
│   │   ├── src/            # Implementación en Remotion (React + TypeScript)
│   │   ├── cues.js         # Marcas de tiempo de subtítulos, tipeo de código y SFX
│   │   ├── index.html      # Composición principal con HyperFrames + GSAP
│   │   ├── pipeline_voz.py # Generación y masterización de audio vocal con FFmpeg
│   │   └── build_cues.py   # Compilación de cues sincronizados
│   └── design/             # Editor y generador de gráficos vectoriales (OpenPencil + Vite)
├── packages/
│   └── shared/             # Assets, paletas y recursos compartidos
├── .agents/
│   └── skills/             # Skills oficiales de HyperFrames para asistentes y agentes
├── CLAUDE.md               # Guía e instrucciones para desarrollo y animación con Claude
├── pnpm-workspace.yaml     # Configuración de workspaces de pnpm
└── package.json            # Scripts centrales del monorepo
```

---

## 🎬 Especificaciones del Video a Animar

### 1. Qué debe hacer el video
* **Formato**: Vertical 9:16 (1080x1920 px).
* **Frame rate**: 30 FPS constantes.
* **Duración**: ~53.5 segundos (1605 frames).
* **Objetivo**: Video de alta retención para redes sociales (TikTok, Instagram Reels, YouTube Shorts).
* **Historia / Narrativa**: Trayectoria y contribución del arquitecto de software **Anders Hejlsberg**:
  1. **Hook**: "¿Sabías que el creador de C# también inventó TypeScript y Turbo Pascal?"
  2. **Presentación**: Genio del software cuyo código usamos a diario.
  3. **Años 80**: Turbo Pascal desarrollado casi en solitario; velocidad de compilación que transformó la enseñanza.
  4. **Era Microsoft**: C# y la plataforma .NET; impacto empresarial global.
  5. **Revolución Web**: TypeScript; tipado estricto y orden ante el caos de JavaScript.
  6. **Cierre / Legado**: De código máquina a la web: herramientas elegantes que empoderan a los desarrolladores.

### 2. Qué debe llevar obligatoriamente
* **Locución Vocal**: `apps/video/public/voz_masterizada.wav` (audio masterizado con loudness broadcast a -14 LUFS).
* **Subtítulos Cinéticos**: Sincronizados palabra por palabra según las marcas de tiempo en `apps/video/cues.js` / `src/timeline.json`.
* **Ventanas de Código Interactivas**: Animación mecanográfica (*typewriter effect*) mostrando fragmentos reales de código en Pascal, C# y TypeScript en los momentos exactos de la narración.
* **Identidad y Recursos Técnicos**: Iconos y logotipos oficiales de Pascal, C#, .NET, TypeScript, VS Code, GitHub y Windows (disponibles en `apps/video/public/icons2/`).
* **Diseño Sonoro**: SFX de tecleo, pops, whooshes y campanas de transición sincronizados con los eventos visuales (`apps/video/public/sfx/`).
* **Música de Fondo**: Track de fondo (`apps/video/public/music/`) con volumen atenuado (ducking) bajo la voz.

### 3. Libertad Creativa y Estética
No existen restricciones rígidas de estilo o gustos personales anteriores. Quien desarrolle la animación tiene **completa libertad creativa** para definir la dirección visual, paleta cromática, ritmo de animación con GSAP, efectos cinéticos y tipografía moderna que optimicen el impacto y la calidad visual.

---

## 🚀 Comandos de Operación

> **Regla de entorno**: Usar exclusivamente **`pnpm`** (nunca `npm`).

```powershell
# 1. Instalar todas las dependencias
pnpm install

# 2. Previsualizar el video en el navegador en tiempo real (puerto 3000)
pnpm video:preview

# 3. Renderizar el video a MP4 determinista con HyperFrames
pnpm video:render

# 4. Previsualizar composición con Remotion (si se usa el stack React)
pnpm video:remotion

# 5. Levantar el entorno de diseño gráfico (apps/design)
pnpm design:dev
```

---

## 🛠️ Pipeline de Audio y Generación de Cues

Si se modifica el guion o se requiere regenerar el audio y sus marcas temporales:

```powershell
cd apps/video

# Generar la locución masterizada con Edge TTS y FFmpeg
python pipeline_voz.py

# Compilar los eventos y marcas temporales de subtítulos, tecleo y SFX
python build_cues.py
```
