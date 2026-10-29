---
name: hyperframes-core
description: HyperFrames composition contract, DOM structure, data-* timing attributes, and seekable animation rules.
---

# HyperFrames Core

## 1. Composition Contract
- Top-level root: `<div id="stage" data-composition-id="anders" data-start="0" data-width="1080" data-height="1920" data-duration="53">`
- Child clips: `<div class="clip" data-start="X" data-duration="Y" data-track-index="Z">`
- Seekable GSAP timeline registered on `window.__timelines[compositionId]`.
- All CSS positioning and GSAP tweens must be deterministic and seekable.
