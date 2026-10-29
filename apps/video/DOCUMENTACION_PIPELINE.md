# Documentación Técnica del Pipeline de Video (VideoIA)

Este documento detalla la arquitectura técnica, herramientas, pipelines de datos y especificaciones del motor de video de **VideoIA**, diseñado para la creación de motion graphics y videos verticales (9:16) en **1080x1920 a 30 FPS**.

---

## 1. Objetivo y Contenido del Video

### 1.1 Formato y Especificaciones
* **Formato**: Vertical 9:16 (1080x1920).
* **Velocidad de fotogramas**: 30 FPS constantes.
* **Duración total**: ~53.5 segundos (1605 frames).
* **Propósito**: Video de alto dinamismo, retención y motion graphics para plataformas de video corto (TikTok, Instagram Reels, YouTube Shorts).

### 1.2 Estructura Narrativa (Anders Hejlsberg)
El guion narra la trayectoria del legendario arquitecto de software **Anders Hejlsberg**:

| Escena | Rango Temporal | Tema / Hito | Mensaje Clave |
| :--- | :--- | :--- | :--- |
| **Escena 0** | 0.0s – 5.4s | *Gancho Inicial* | ¿Sabías que el creador de C# también inventó TypeScript y Turbo Pascal? |
| **Escena 1** | 5.4s – 13.0s | *Presentación* | Su nombre es Anders Hejlsberg. Un genio del software cuyo código usas a diario. |
| **Escena 2** | 13.0s – 22.8s | *Años 80: Turbo Pascal* | Creado en solitario; revolucionó la enseñanza gracias a su velocidad de compilación. |
| **Escena 3** | 22.8s – 30.9s | *Microsoft: C# y .NET* | Diseñó C# y .NET, transformando el desarrollo empresarial para siempre. |
| **Escena 4** | 30.9s – 42.2s | *Revolución Web: TypeScript* | Ante el caos de JavaScript, aportó tipado estricto y escalabilidad a la web moderna. |
| **Escena 5** | 42.2s – 53.5s | *Conclusión y Legado* | De código máquina a la web: crear herramientas elegantes que empoderen a los desarrolladores. |

---

## 2. Elementos Requeridos en la Animación

Cualquier animación o composición debe incluir e integrar armónicamente:

1. **Locución Principal**:
   - Archivo: `public/voz_masterizada.wav`.
   - Audio vocal procesado y masterizado según norma broadcast EBU R128 (-14 LUFS).

2. **Subtítulos Cinéticos Sincronizados**:
   - Marcas temporales exactas palabra por palabra definidas en `cues.js` y `src/timeline.json`.
   - Énfasis visual en términos clave (lenguajes, nombres propios, hitos).

3. **Ventanas de Código / IDE Interactivas**:
   - Efecto mecanográfico (*typewriter*) sincronizado con los tiempos de habla (`cues.typing`):
     - **Turbo Pascal** (14.0s - 18.4s): Sintaxis Pascal clásica.
     - **C#** (23.5s - 28.3s): Estructura clásica en C# / .NET.
     - **TypeScript** (31.4s - 37.0s): Interfaces y tipado en TypeScript.

4. **Recursos Visuales y Gráficos**:
   - Iconos vectoriales en `public/icons2/` (Pascal, C#, .NET, TypeScript, VS Code, GitHub, Windows).
   - Fotografías históricas de Anders Hejlsberg (`public/anders/`).
   - Fondos y clips de soporte técnico en `public/bg/` y `public/broll/`.

5. **Diseño de Sonido (SFX y Música)**:
   - SFX de tecleo (`public/sfx/keyboard.wav`), pops (`public/sfx/pop.wav`), whooshes y transiciones (`public/sfx/whoosh.wav`, `public/sfx/bell.wav`, `public/sfx/topic_transition.wav`).
   - Música de fondo (`public/music/background.mp3` o `lofi.mp3`) con ducking bajo la voz.

---

## 3. Libertad Creativa y de Diseño

> [!NOTE]
> Se han removido todas las especificaciones o restricciones rígidas de gustos personales previas (como esquemas forzados o estilos restrictivos). Quien anime el video tiene **total libertad creativa** para decidir paletas cromáticas, modos (dark/light/cyber/tech), transiciones, coreografía de movimientos con GSAP y estilos tipográficos, priorizando la máxima calidad visual, dinamismo y retención de la audiencia.

---

## 4. Pipeline Técnico y Comandos de Ejecución

### 4.1 Pila de Tecnologías
* **Gestor de Paquetes**: `pnpm` (uso estricto, no npm).
* **Motor de Animación**: **HyperFrames** (HTML5 + CSS + GSAP con playback determinista frame a frame).
* **Motor Alternativo**: **Remotion** (React 18 + Remotion CLI).
* **Procesamiento de Audio**: Python (Edge TTS + FFmpeg).

### 4.2 Flujo de Datos y Scripts
```
guion/anders_hejlsberg.txt
          │
          ▼
   pipeline_voz.py  ──────────> public/voz_masterizada.wav + src/timeline.json
          │
          ▼
    build_cues.py   ──────────> cues.js (subtítulos, typing y pops SFX)
          │
          ▼
     index.html     ──────────> Composición HyperFrames (HTML + GSAP)
          │
          ▼
   pnpm video:render ─────────> out/video.mp4 (1080x1920 @ 30fps)
```

### 4.3 Comandos Clave (desde la raíz del proyecto)

```powershell
# Instalar dependencias del monorepo
pnpm install

# Previsualizar video en navegador en tiempo real (puerto 3000)
pnpm video:preview

# Renderizar video a MP4 con HyperFrames
pnpm video:render

# Previsualizar en Remotion Studio (si se usa el stack React)
pnpm video:remotion
```
