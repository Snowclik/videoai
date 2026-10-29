---
name: hyperframes
description: Entry point for HyperFrames HTML video and motion graphics compositions.
---

# HyperFrames entry point

HyperFrames renders video from HTML. A composition is an HTML file whose DOM declares timing with `data-*` attributes, whose animation runtime is seekable, and whose media playback is owned by the framework.

- Root composition: `<div id="stage" data-composition-id="[id]" data-start="0" data-width="1080" data-height="1920" data-duration="[seconds]">`
- Clips: elements with `class="clip"`, `data-start="[seconds]"`, `data-duration="[seconds]"`, and `data-track-index="[number]"`.
- Seekable GSAP Timeline:
```javascript
const tl = gsap.timeline({ paused: true });
window.__timelines = window.__timelines || {};
window.__timelines[id] = tl;
```
