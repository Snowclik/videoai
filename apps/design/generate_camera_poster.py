import base64
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
public_dir = os.path.join(base_dir, "public")
assets_dir = os.path.join(public_dir, "camera_poster")

highres_path = os.path.join(assets_dir, "artwork_highres.jpg")
output_path = os.path.join(public_dir, "poster_camera_landscapes.svg")

with open(highres_path, "rb") as f:
    art_b64 = base64.b64encode(f.read()).decode("utf-8")

# 1152 x 2048 coordinate space
ox = 548
oy = 1488

svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1152 2048" width="1152" height="2048">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&amp;family=Inter:wght@500;600;700&amp;display=swap');
      .angled-text {{
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif;
        font-weight: 800;
        font-size: 38px;
        fill: #111417;
        letter-spacing: -0.02em;
      }}
      .manifesto-text {{
        font-family: 'Inter', sans-serif;
        font-size: 20px;
        font-weight: 600;
        line-height: 1.35;
        fill: #22262a;
        letter-spacing: -0.015em;
      }}
    </style>

    <!-- Ray 1 Clip: Left Canyon & Yellow Plane -->
    <clipPath id="clip-wedge-1">
      <polygon points="{ox},{oy} -20,450 -20,-20 280,-20" />
    </clipPath>

    <!-- Ray 2 Clip: Mountain Ridge & Hikers -->
    <clipPath id="clip-wedge-2">
      <polygon points="{ox},{oy} 280,-20 524,-20" />
    </clipPath>

    <!-- Ray 3 Clip: Deep Turquoise Sea & White Boat -->
    <clipPath id="clip-wedge-3">
      <polygon points="{ox},{oy} 524,-20 1088,-20" />
    </clipPath>

    <!-- Ray 4 Clip: Shallow Tropical Water & Orange Paddleboard -->
    <clipPath id="clip-wedge-4">
      <polygon points="{ox},{oy} 1088,-20 1172,-20 1172,960" />
    </clipPath>

    <!-- Camera & Hands Cutout Area (Bottom) -->
    <clipPath id="clip-camera-area">
      <rect x="0" y="1450" width="1152" height="598" />
    </clipPath>
  </defs>

  <!-- ========================================== -->
  <!-- LAYER 1: BASE HIGH-RESOLUTION ARTWORK     -->
  <!-- ========================================== -->
  <g id="base-artwork">
    <image href="data:image/jpeg;base64,{art_b64}" x="0" y="0" width="1152" height="2048" preserveAspectRatio="none" />
  </g>

  <!-- ========================================== -->
  <!-- LAYER 2: VECTOR CLIPPING SLICES (EDITABLE) -->
  <!-- ========================================== -->
  <g id="editable-slices" opacity="0.001">
    <!-- Slice 1: Canyon -->
    <g id="slice-1-canyon" clip-path="url(#clip-wedge-1)">
      <rect x="0" y="0" width="1152" height="2048" fill="#1b3a2a" />
    </g>
    <!-- Slice 2: Mountain Ridge -->
    <g id="slice-2-mountain" clip-path="url(#clip-wedge-2)">
      <rect x="0" y="0" width="1152" height="2048" fill="#2d4a2a" />
    </g>
    <!-- Slice 3: Sea & Boat -->
    <g id="slice-3-sea" clip-path="url(#clip-wedge-3)">
      <rect x="0" y="0" width="1152" height="2048" fill="#0f4552" />
    </g>
    <!-- Slice 4: Beach & Paddleboard -->
    <g id="slice-4-beach" clip-path="url(#clip-wedge-4)">
      <rect x="0" y="0" width="1152" height="2048" fill="#2ea8b8" />
    </g>
  </g>

  <!-- ========================================== -->
  <!-- LAYER 3: VECTOR RAY DIVIDER LINES          -->
  <!-- ========================================== -->
  <g id="divider-lines" stroke="#ffffff" stroke-width="4" stroke-linecap="round" opacity="0.85">
    <!-- Center divider between mountain and sea -->
    <line x1="{ox}" y1="{oy}" x2="524" y2="0" />
    <!-- Divider between sea and paddleboard -->
    <line x1="{ox}" y1="{oy}" x2="1088" y2="0" />
  </g>

  <!-- ========================================== -->
  <!-- LAYER 4: EDITABLE VECTOR TYPOGRAPHY        -->
  <!-- ========================================== -->
  <!-- Left Ray Text: "some landscapes are walked." -->
  <g id="text-left-ray" transform="translate(235, 1020) rotate(58.8)">
    <text x="0" y="0" class="angled-text" text-anchor="middle">some landscapes are walked.</text>
  </g>

  <!-- Right Ray Text: "some are created. crafted." -->
  <g id="text-right-ray" transform="translate(865, 1140) rotate(-53.2)">
    <text x="0" y="0" class="angled-text" text-anchor="middle">some are created. crafted.</text>
  </g>

  <!-- Bottom Left Manifesto Block -->
  <g id="text-manifesto" transform="translate(35, 1680)">
    <text y="0" class="manifesto-text">looking enough</text>
    <text y="28" class="manifesto-text">out there, and you</text>
    <text y="56" class="manifesto-text" dx="95">some</text>
    <text y="84" class="manifesto-text">landscapes feel</text>
    <text y="112" class="manifesto-text">less like stories</text>
    <text y="140" class="manifesto-text">unfolding</text>
    <text y="168" class="manifesto-text">beneath your feet</text>
  </g>
</svg>'''

with open(output_path, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"Poster vectorial generado exitosamente en: {output_path}")
