# Instrucciones de Desarrollo y Animación para Claude (VideoIA)

Bienvenido a **VideoIA**. Tu misión principal en este repositorio es diseñar, animar y perfeccionar la composición de video en motion graphics para alcanzar el máximo estándar visual, fluidez y retención.

---

## 🎯 Objetivo del Video

* **Formato**: Vertical 9:16 (1080x1920).
* **Frame rate**: 30 FPS constantes.
* **Duración**: Exactamente 53.5 segundos (1605 frames).
* **Salida de render**: `out/video.mp4` a través de HyperFrames.
* **Audiencia / Plataforma**: Video de alta retención para redes sociales (Reels, TikTok, Shorts).
* **Tema / Historia**: Narrativa biográfica y técnica sobre **Anders Hejlsberg**, creador de Turbo Pascal, C# / .NET y TypeScript.

---

## 📋 Qué Debe Llevar el Video (Requerimientos Esenciales)

1. **Locución Principal**:
   - `apps/video/public/voz_masterizada.wav` (duración exacta: 53.5s).
   - Audio sincronizado en la línea de tiempo.

2. **Estructura Narrativa por Escenas**:
   - **Escena 0 (0.0s – 5.4s)**: Gancho: "¿Sabías que el creador de C# también inventó TypeScript y Turbo Pascal?"
   - **Escena 1 (5.4s – 13.0s)**: "Su nombre es Anders Hejlsberg. Un genio de la ingeniería de software cuyo código probablemente usas a diario."
   - **Escena 2 (13.0s – 22.8s)**: "En los ochenta, Anders escribió Turbo Pascal casi en solitario, revolucionando cómo se enseñaba a programar gracias a su increíble velocidad de compilación."
   - **Escena 3 (22.8s – 30.9s)**: "Más tarde, se unió a Microsoft, donde diseñó C# y el framework punto net, cambiando el panorama empresarial para siempre."
   - **Escena 4 (30.9s – 42.2s)**: "Pero su legado no se detuvo ahí. Ante el caótico mundo de JavaScript, Anders lideró el desarrollo de TypeScript, añadiendo tipado estricto y escalabilidad a la web moderna."
   - **Escena 5 (42.2s – 53.5s)**: "Desde compilar código máquina puro hasta dominar la web, la visión de Anders Hejlsberg siempre ha sido la misma: crear herramientas elegantes que empoderen a los desarrolladores."

3. **Subtítulos Cinéticos**:
   - Sincronizados palabra por palabra según `apps/video/cues.js` o `apps/video/src/timeline.json`.
   - Palabras clave destacadas con énfasis visual dinámico.

4. **Ventanas de Código / IDE Interactivas**:
   - Efecto mecanográfico (*typewriter*) sincronizado con las marcas exactas en `cues.typing`:
     - **Turbo Pascal** (14.0s a 18.4s)
     - **C#** (23.5s a 28.3s)
     - **TypeScript** (31.4s a 37.0s)

5. **Iconos, Logos y Gráficos Oficiales**:
   - Disponibles en `apps/video/public/icons2/` (Pascal, C#, .NET, TypeScript, VS Code, GitHub, Windows).
   - Fotos históricas de Anders en `apps/video/public/anders/`.
   - B-roll y fondos de soporte en `apps/video/public/broll/` y `apps/video/public/bg/`.

6. **Diseño Sonoro (SFX y Música)**:
   - SFX de tecleo (`public/sfx/keyboard.wav`), pops (`public/sfx/pop.wav`), whooshes y transiciones (`public/sfx/whoosh.wav`, `public/sfx/bell.wav`).
   - Música de fondo (`public/music/background.mp3` o `lofi.mp3`) con volumen atenuado (ducking) bajo la voz.

---

## 🎨 Libertad Creativa y Dirección Estética

> [!IMPORTANT]
> **No estás atado a ningún gusto estético ni restricción visual previa del usuario.**
> Se han eliminado requerimientos rígidos de estilos anteriores (como estilo Apple obligatorio o esquemas de color fijos). Tienes **completa libertad creativa** para definir la dirección de arte, modos (dark/light/cyberpunk/editorial), transiciones cinematográficas, tipografías modernas y coreografía de animación en GSAP. Tu objetivo es crear la animación visualmente más atractiva, dinámica y profesional posible.

---

## ⚙️ Reglas de Desarrollo y Comandos

### Gestor de paquetes obligatorio
* **Usar siempre `pnpm`**. NUNCA uses `npm`.

### Comandos de ejecución
```powershell
# Instalar dependencias
pnpm install

# Previsualizar la composición HyperFrames en navegador (http://localhost:3000)
pnpm video:preview

# Renderizar composición final determinista a MP4
pnpm video:render

# Previsualizar en Remotion Studio (si decides usar el stack de React)
pnpm video:remotion
```

### Contrato HyperFrames (apps/video/index.html)
* **Animaciones Deterministas (Seekable)**:
  HyperFrames renderiza frame a frame. Todas las animaciones de GSAP deben pertenecer a una línea de tiempo pausada registrada en:
  ```javascript
  const tl = gsap.timeline({ paused: true });
  window.__timelines = window.__timelines || {};
  window.__timelines['anders-video'] = tl;
  ```
* **Estructura del DOM**:
  - Elemento raíz `#stage` con atributos `data-composition-id="anders-video"`, `data-start="0"`, `data-width="1080"`, `data-height="1920"`, `data-duration="53.5"`.
  - Elementos de medios (`<audio>`, `<video>`) controlados con atributos `data-start`, `data-duration`, `data-volume`.
* **Rutas de assets**:
  - Todas las rutas relativas en `apps/video/index.html` deben apuntar a `public/...` o `cues.js`.

### Seguridad y Privacidad
* No subas ni crees claves de API, secretos ni credenciales en el repositorio.
* No agregues archivos de video crudo o datos personales al control de versiones.
