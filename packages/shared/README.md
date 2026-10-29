# Shared (packages/shared)

Único punto de contacto entre `apps/video` y `apps/design`.

## Qué va aquí
- Tokens de marca: colores, tipografías, espaciados.
- Assets comunes: logos, imágenes, fuentes.

## Qué NO va aquí
- Lógica de video (Remotion, FFmpeg, audio).
- Lógica de diseño (lienzo, exportación de imágenes).
- Dependencias pesadas de cualquiera de las dos apps.

Estado: vacío, se llena cuando se defina el módulo de diseño.
