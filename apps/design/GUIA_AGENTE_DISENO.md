# Guía Técnica del Agente: Módulo de Diseño Gráfico (`apps/design`)

Este documento instruye a cualquier agente o nodo que continúe el trabajo en este repositorio sobre cómo operar el subsistema de diseño gráfico.

---

## 1. Reglas Inmutables del Entorno
1. **Idioma**: Responder ÚNICAMENTE en español.
2. **Navegador**: SIEMPRE pedir permiso antes de abrir el navegador o automatizar navegación.
3. **Gestor de paquetes**: Usar EXCLUSIVAMENTE `pnpm` (nunca `npm`).
4. **Espacio en Disco**: La laptop del usuario DEBE mantener al menos **80 GB de espacio libre en C:** en todo momento. Verificar con `Get-PSDrive C` y limpiar archivos temporales tras generar assets.

---

## 2. Estructura del Monorepo
* `/apps/video`: Pipeline de video, Remotion, FFmpeg, estabilización y subtítulos.
* `/apps/design`: Motor de diseño vectorial con OpenPencil, Vite, scripts de generación SVG y visor web.
* `/packages/shared`: Tokens, paletas de colores y assets comunes.

---

## 3. Comandos de Ejecución
```bash
# Iniciar servidor web de previsualización en apps/design
pnpm run design:dev      # Corre en http://localhost:5173/

# Regenerar archivo SVG desde Python/TypeScript
python apps/design/generate_svg.py
```

---

## 4. Pipeline de Creación y Réplica de Posters
1. **Generación de Assets de Alta Fidelidad**:
   * Usar `generate_image` con descripciones cenitales/fotográficas precisas.
   * Procesar con `cv2.grabCut` o máscaras alfa para aislar elementos salientes (*breakout elements*).
2. **Composición Vectorial SVG**:
   * Mantener el orden estricto de capas (fondo -> tipografías base -> recuadros/máscaras de recorte -> elementos salientes con sombra proyectada -> textos frontales).
   * Incrustar imágenes con `base64` para que el archivo SVG sea 100% portable y autónomo para Illustrator, Figma o Inkscape.
3. **Visor Interactivo en Navegador**:
   * El archivo `apps/design/index.html` sirve como interfaz de visualización interactiva y proporciona descargas directas en formato **SVG editable** y **PNG en alta resolución (2000x2700 px)**.
