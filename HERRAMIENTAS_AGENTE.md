# Manual de Herramientas, Algoritmos y Pipelines Técnicos (Guía para el Agente)

Este archivo sirve como referencia técnica directa para mí (y futuros agentes) en este entorno. Documenta las herramientas exactas, algoritmos, parámetros y mejores prácticas para procesar audio, estabilizar video, reducir ruido y generar subtítulos dinámicos sin degradar la calidad ni saturar los recursos de la máquina.

> **Estructura actual (proyecto híbrido)**: todo lo descrito aquí vive ahora en `apps/video/`. Las rutas como `pipeline/`, `public/`, `src/` y `videos/` son relativas a esa carpeta, y los scripts de Python se ejecutan desde `apps/video`. El módulo `apps/design/` es independiente y no debe importar nada de video. Lo compartido va en `packages/shared/`. Ver [README.md](README.md).

---

## 1. Supresión y Limpieza de Ruido de Audio (Studio Voice Mastering)

Para obtener un sonido de voz con calidad de estudio sin que se escuche robótico ni se supriman las pausas naturales de la persona, se utiliza un pipeline híbrido en 3 etapas (`pipeline/enhance_all_audio_studio.py`):

```
Audio Original ──> [Etapa 1: Highpass + RNNoise] ──> [Etapa 2: Spectral Gating 40%] ──> [Etapa 3: Mastering Vocal] ──> Audio MP3 Broadcast
```

### Etapa 1: Filtro Anti-Viento y Red Neuronal RNNoise
* **Herramienta**: FFmpeg con filtro `highpass` y `arnndn`.
* **Comando**:
  ```bash
  ffmpeg -i [input] -vn -af "highpass=f=120:p=1,arnndn=m=bd.rnnn" -ar 48000 -ac 1 temp_rnn.wav
  ```
* **Por qué funciona**:
  * `highpass=f=120:p=1`: Corta las ráfagas de baja frecuencia provocadas por el viento contra el micrófono (sub-graves por debajo de 120 Hz). Se usa orden 1 (`p=1`) en vez de 2 para no adelgazar los armónicos fundamentales de la voz.
  * `arnndn=m=bd.rnnn`: Modelo neuronal ligero RNNoise que aísla los componentes de voz humana del ruido ambiental exterior (tráfico, murmullo lejano) sin latencia ni carga pesada.

### Etapa 2: Spectral Gating No Estacionario Dinámico
* **Herramienta**: Python con librería `noisereduce` (`scipy.io.wavfile`).
* **Implementación**:
  ```python
  import noisereduce as nr

  reduced = nr.reduce_noise(
      y=audio_float,
      sr=sr,
      stationary=False,         # Adapta el perfil de ruido continuamente
      prop_decrease=0.40,       # CLAVE: solo 40% de atenuación para NO cortar colas de palabras
      n_fft=2048,
      hop_length=512,
      time_mask_smooth_ms=80,   # Suavizado temporal para evitar chasquidos
      freq_mask_smooth_hz=200   # Suavizado en frecuencia para evitar efecto "tubo/peine"
  )
  ```
* **Regla crítica**: NUNCA usar `prop_decrease=1.0` ni compuertas de ruido duras (*hard noise gates*), ya que cortan la respiración, eliminan consonantes suaves y generan un silencio digital artificial molesto.

### Etapa 3: Cadena de Masterización de Estudio (EBU R128)
* **Herramienta**: FFmpeg con filtros encadenados:
  ```bash
  -af "equalizer=f=300:t=q:w=1.4:g=-2.0,equalizer=f=3300:t=q:w=1.2:g=2.5,equalizer=f=8000:t=q:w=1.5:g=1.2,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=80:makeup=2.0,loudnorm=I=-14:TP=-1.0:LRA=9,afade=t=in:ss=0:d=0.05,afade=t=out:st=[dur-0.05]:d=0.05"
  ```
* **Parámetros desglosados**:
  * `equalizer 300Hz (-2dB)`: Limpia el "fango" (*mud*) o resonancias de espacio cerrado.
  * `equalizer 3300Hz (+2.5dB)`: Realza la inteligibilidad y articulación de la voz (*presence*).
  * `equalizer 8000Hz (+1.2dB)`: Aporta brillo y aire profesional (*air*).
  * `acompressor`: Nivelador transparente con ratio 2.5:1 que controla picos sin efecto de bombeo.
  * `loudnorm=I=-14:TP=-1.0`: Normalización internacional estándar de podcast/streaming para volumen uniforme.

---

## 2. Estabilización de Video (VidStab 2-Pass)

Para eliminar el temblor de cámara en mano sin perder resolución ni crear vibraciones gelatinosas:

* **Herramienta**: FFmpeg con biblioteca `libvidstab` (`pipeline/process_natural_clips.py`):
* **Paso 1 (Detección de vectores de movimiento)**:
  ```bash
  ffmpeg -y -ss [start] -t [dur] -i [vfile] -vf "fps=30,crop=1134:2016:(in_w-1134)/2:0,scale=1080:1920,vidstabdetect=stepsize=6:shakiness=7:accuracy=15:result=[clip].trf" -f null -
  ```
* **Paso 2 (Transformación y compensación)**:
  ```bash
  ffmpeg -y -ss [start] -t [dur] -i [vfile] -vf "fps=30,crop=1134:2016:(in_w-1134)/2:0,scale=1080:1920,vidstabtransform=input=[clip].trf:smoothing=30:optalgo=gauss:interpol=bilinear:crop=black:zoom=3,hqdn3d=2.5:2.0:4.0:3.0,cas=0.4" -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -an [out_mp4]
  ```
* **Detalles clave**:
  * `crop=1134:2016` + `zoom=3`: Da un 5% de margen perimetral para que el algoritmo compense el movimiento sin que los bordes negros entren al encuadre vertical.
  * `smoothing=30` + `optalgo=gauss`: Movimiento orgánico y cinemático.

---

## 3. Reducción de Ruido de Video y Nitidez 1080p

### 3.1 Denoise 3D Espacio-Temporal (`hqdn3d`)
* **Parámetros**: `hqdn3d=2.5:2.0:4.0:3.0`
  * `2.5`: Ruido espacial en luminancia (suaviza grano de sensor).
  * `2.0`: Ruido espacial en crominancia (evita manchas de color en sombras).
  * `4.0`: Ruido temporal en luminancia (elimina el parpadeo de grano entre fotogramas sucesivos).
  * `3.0`: Ruido temporal en crominancia.
* **Ventaja**: Es un filtro ultrarrápido en CPU que no satura laptops ni requiere GPU dedicada pesada.

### 3.2 Nitidez Adaptativa AMD FidelityFX CAS (`cas`)
* **Parámetros**: `cas=0.4`
* **Por qué CAS y no Unsharp**: Los filtros unsharp tradicionales crean halos blancos en bordes de alto contraste. AMD FidelityFX CAS inspecciona el gradiente local de contraste y solo afila donde hay textura real (pelo, ojos, telas), entregando una sensación cristalina en 1080p sin artefactos.

### 3.3 Regla de Colorimetría Natural
* **LECCIÓN APRENDIDA**: NO aplicar curvas forzadas de levantamiento de sombras en escenas con contraluz severo (sujeto bajo tejado y fondo soleado). Al forzar curvas lineales o contraste global, las sombras se vuelven grises/lavadas o los fondos se queman. El color debe mantenerse **100% natural y fiel** a la captura original, confiando únicamente en el denoise y el filtro CAS.

---

## 4. Subtitulado Dinámico en Remotion (React + CSS)

### 4.1 Prevención de Choque de Animaciones (Ráfagas Continuas de Voz)
* **Archivo**: [Subtitles.tsx](file:///c:/Users/tavog/Documents/Codigo/Universidad/VideoIA/src/components/Subtitles.tsx)
* **Problema resuelto**: Si la persona habla de seguido, una frase terminando hacía *fade-out* mientras la siguiente hacía *slide-up* desde abajo, produciendo un salto visual caótico.
* **Algoritmo de ráfagas**:
  ```tsx
  // ¿Viene de una pausa larga o es la primera frase?
  const isFirstInBurst = !prevPhrase || (phraseStart - prevPhrase[prevPhrase.length - 1].end_frame > 12);

  // ¿Va hacia una pausa larga o es la última frase?
  const isLastInBurst = !nextPhrase || (nextPhrase[0].start_frame - phraseLastWordEnd > 12);
  ```
  * Si la persona habla de corrido, la tarjeta blanca permanece fija en pantalla (`translateY = 0`) y el texto cambia de forma limpia.
  * La animación de entrada/salida solo se activa ante silencios reales (> 12 fotogramas).

### 4.2 Prevención de Saltos de Renglón (*Zero Layout Shifts*)
* **Problema resuelto**: En HTML/CSS, si la palabra activa cambia su `padding`, `fontWeight` o `fontSize`, el ancho acumulado empuja las palabras contiguas a una segunda línea y luego regresa a una, haciendo que el párrafo brinque.
* **Solución**:
  * Todas las palabras comparten propiedades físicas **inmutables**: `fontWeight: 800`, `padding: '6px 14px'`, `fontSize: 52px`, `whiteSpace: 'nowrap'`.
  * El resaltado dinámico solo altera propiedades visuales que no alteran el box model: `backgroundColor: highlight.bg`, `color: highlight.text`, y una micro-escala centrada `scale(1.08)`.
  * Límite estricto de frase: máximo 3 a 4 palabras (o 24 caracteres).

---

## 5. Comandos de Operación y Buenas Prácticas

### 5.1 Reglas del Usuario
* **Idioma**: Responder siempre en español.
* **Navegador**: Pedir confirmación antes de abrir el navegador.
* **Gestor de paquetes**: Utilizar exclusivamente `pnpm` (nunca `npm`).

### 5.2 Comandos Clave en Terminal
* **Previsualización interactiva**:
  ```powershell
  pnpm exec remotion studio src/index.ts --port 3000
  ```
* **Renderizado final en 1080p**:
  ```powershell
  pnpm exec remotion render src/index.ts VideoComposition out/video.mp4
  ```
* **Obtención de ruta de FFmpeg en Python**:
  ```python
  import imageio_ffmpeg
  ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
  ```

### 5.3 Política de Almacenamiento y Limpieza
* **Eliminar archivos temporales de video** tras exportar (`videos/`, `public/videos_enhanced/`, `.trf`, `.tmp.mp4`).
* **Limpiar periódicamente la caché de Remotion** en `$env:TEMP` (`remotion-assets*`) y vaciar la Papelera de Reciclaje con PowerShell para conservar espacio en disco.

---

## 6. Módulo de Diseño Gráfico e Ilustración Vectorial (`apps/design`)

### 6.1 Arquitectura y Herramientas
* **Stack**: Vite + TypeScript + OpenPencil (`@open-pencil/core`, `@open-pencil/scene-graph`, `@open-pencil/fig`, `@open-pencil/pen`).
* **Objetivo**: Creación, previsualización y exportación de piezas gráficas vectoriales (SVG editable y PNG en alta definición).
* **Servidor de desarrollo local**:
  ```bash
  pnpm run design:dev    # Inicia Vite en http://localhost:5173/
  ```

### 6.2 Flujo de Réplica de Posters y Diseños Complejos
1. **Análisis de Capas (Z-Index estricto)**:
   * **Fondo / Textura**: Parchment / papel vintage con viñeta lateral oscura generada con ruido y gradiente para realismo editorial.
   * **Tipografía de fondo**: Títulos o manifiestos en capas inferiores cuando los elementos visuales deban pasar por encima (*breakout effect*).
   * **Recortes y Máscaras SVG (`clipPath`)**: Delimitan áreas cerradas (ej. recuadro de agua o rayos angulares proyectados).
   * **Elementos Salientes / 3D Breakout**: Capas PNG con transparencia (alfa) y filtro `feDropShadow` que sobresalen del marco hacia el lienzo, pasando por encima de textos o títulos.
2. **Generación de Assets Fotográficos**:
   * Utilizar la herramienta `generate_image` con prompts cenitales/fotográficos de alta resolución.
   * Segmentación con OpenCV (`cv2.grabCut` o canal alfa con suavizado gaussiano) para extraer recortes limpios sin fondos indeseados.
3. **Exportación Autónoma en SVG**:
   * Las imágenes fotográficas se incrustan directamente dentro del SVG como `data:image/jpeg;base64` o `data:image/png;base64`.
   * Esto garantiza que el archivo `.svg` sea **100% autónomo y portable**, permitiendo abrirlo y editarlo en Illustrator, Figma o Inkscape sin enlaces rotos a imágenes locales.

### 6.3 Regla Crítica de Disco
* **Límite mínimo del usuario**: NUNCA bajar de 80 GB de espacio libre en C:. Verificar con `Get-PSDrive C` antes y después de operaciones pesadas.

---
*Manual técnico de herramientas para el proyecto VideoIA.*
