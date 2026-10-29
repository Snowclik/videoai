import base64
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
public_dir = os.path.join(base_dir, "public")

water_path = os.path.join(public_dir, "canoe_water.jpg")
cutout_path = os.path.join(public_dir, "canoe_cutout.png")
paper_path = os.path.join(public_dir, "paper_texture.jpg")
output_path = os.path.join(public_dir, "poster_the_edge.svg")

with open(water_path, "rb") as f:
    water_b64 = base64.b64encode(f.read()).decode("utf-8")

with open(cutout_path, "rb") as f:
    cutout_b64 = base64.b64encode(f.read()).decode("utf-8")

with open(paper_path, "rb") as f:
    paper_b64 = base64.b64encode(f.read()).decode("utf-8")

# Coordinate setup:
# Canoe image is 896x1200.
# We map canoe to SVG:
# Width in SVG: 700 px, centered at X = 500 -> x = 150.
# Height in SVG: 700 * (1200/896) = 937.5 px.
# We place top of canoe at Y = 295:
# So image y = 295 - (0.08 * 937.5) = 220.
img_x = 150
img_y = 220
img_w = 700
img_h = 937.5

# Water box:
water_x = 92
water_y = 485
water_w = 816
water_h = 745

svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1350" width="1000" height="1350">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&amp;family=Space+Grotesk:wght@600;700&amp;display=swap');
      .title {{
        font-family: 'Bebas Neue', 'Impact', sans-serif;
        font-size: 285px;
        fill: #f36821;
        letter-spacing: 0.04em;
      }}
      .meta {{
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 13.5px;
        letter-spacing: 0.32em;
        fill: #1d333b;
      }}
      .quote {{
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 13.5px;
        letter-spacing: 0.16em;
        fill: #1d333b;
        text-anchor: middle;
      }}
      .bottom-tag {{
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 13.5px;
        letter-spacing: 0.22em;
        fill: #1d333b;
      }}
    </style>

    <!-- Drop Shadow for Upper Canoe Bow on the Parchment Canvas -->
    <filter id="canoe-shadow" x="-40%" y="-40%" width="180%" height="180%">
      <feDropShadow dx="0" dy="6" stdDeviation="9" flood-color="#0a1920" flood-opacity="0.5" />
    </filter>

    <!-- Water Box Clipping Path (The sea stays strictly inside this box) -->
    <clipPath id="water-box-clip">
      <rect x="{water_x}" y="{water_y}" width="{water_w}" height="{water_h}" />
    </clipPath>

    <!-- Upper Canoe Clipping Path (Canoe bow protruding OUT of the water onto paper) -->
    <clipPath id="upper-canoe-clip">
      <rect x="300" y="270" width="400" height="{water_y - 268}" />
    </clipPath>
  </defs>

  <!-- 1. BASE BACKGROUND: Textured vintage paper with dark distressed sides -->
  <image href="data:image/jpeg;base64,{paper_b64}" x="0" y="0" width="1000" height="1350" preserveAspectRatio="none" />

  <!-- 2. TOP METADATA HEADER -->
  <g id="header" transform="translate(500, 56)" text-anchor="middle">
    <text class="meta">FIELD NOTES   <tspan fill="#647b84">|</tspan>   04.16.2026   <tspan fill="#647b84">|</tspan>   EDITION 1</text>
  </g>

  <!-- 3. GIANT TITLE: THE EDGE (Split to let the canoe tip rise right through the middle) -->
  <g id="title-group">
    <!-- "THE" on the left -->
    <text x="260" y="380" class="title" text-anchor="middle">THE</text>
    <!-- "EDGE" on the right -->
    <text x="685" y="380" class="title" text-anchor="middle">EDGE</text>
  </g>

  <!-- 4. QUOTE STATEMENT (Rendered BEHIND the canoe, so the boat covers the middle) -->
  <g id="quote-group" transform="translate(500, 420)">
    <text y="0" class="quote">THERE'S A MOMENT WHERE EVERYTHING SHIFTS—WHERE</text>
    <text y="20" class="quote">HESITATION FADES AND CONVICTION TAKES OVER. THE WATER</text>
    <text y="40" class="quote">STEADIES. THE PATH NARROWS. ALL THAT'S LEFT IS FORWARD.</text>
  </g>

  <!-- 5. WATER RECTANGLE: Bottom half of the poster with sea, paddler and water ripples -->
  <g id="sea-rectangle" clip-path="url(#water-box-clip)">
    <image href="data:image/jpeg;base64,{water_b64}" x="{img_x}" y="{img_y}" width="{img_w}" height="{img_h}" preserveAspectRatio="xMidYMid meet" />
  </g>

  <!-- 6. CANOE BREAKOUT: Upper half of the boat rising ON TOP of the canvas and OVER the text -->
  <g id="canoe-breakout-layer" filter="url(#canoe-shadow)" clip-path="url(#upper-canoe-clip)">
    <image href="data:image/png;base64,{cutout_b64}" x="{img_x}" y="{img_y}" width="{img_w}" height="{img_h}" preserveAspectRatio="xMidYMid meet" />
  </g>

  <!-- 7. BOTTOM BAR: STEP INTO IT | BARCODE | GO ALL IN -->
  <g id="footer" transform="translate(0, 1285)">
    <!-- Left text -->
    <text x="260" y="16" class="bottom-tag" text-anchor="end">STEP INTO IT</text>

    <!-- High-detail Vector Barcode -->
    <g id="barcode" transform="translate(382, -8)">
      <rect x="0" y="0" width="4" height="34" fill="#1d333b" />
      <rect x="7" y="0" width="2" height="34" fill="#1d333b" />
      <rect x="12" y="0" width="6" height="34" fill="#1d333b" />
      <rect x="22" y="0" width="2" height="34" fill="#1d333b" />
      <rect x="27" y="0" width="5" height="34" fill="#1d333b" />
      <rect x="36" y="0" width="2" height="34" fill="#1d333b" />
      <rect x="41" y="0" width="8" height="34" fill="#1d333b" />
      <rect x="52" y="0" width="3" height="34" fill="#1d333b" />
      <rect x="58" y="0" width="2" height="34" fill="#1d333b" />
      <rect x="63" y="0" width="5" height="34" fill="#1d333b" />
      <rect x="71" y="0" width="2" height="34" fill="#1d333b" />
      <rect x="76" y="0" width="6" height="34" fill="#1d333b" />
      <rect x="86" y="0" width="3" height="34" fill="#1d333b" />
      <rect x="92" y="0" width="2" height="34" fill="#1d333b" />
      <rect x="97" y="0" width="7" height="34" fill="#1d333b" />
      <rect x="108" y="0" width="3" height="34" fill="#1d333b" />
      <rect x="114" y="0" width="2" height="34" fill="#1d333b" />
      <rect x="119" y="0" width="5" height="34" fill="#1d333b" />
      <rect x="128" y="0" width="4" height="34" fill="#1d333b" />
      <rect x="136" y="0" width="2" height="34" fill="#1d333b" />
      <rect x="141" y="0" width="6" height="34" fill="#1d333b" />
      <rect x="150" y="0" width="2" height="34" fill="#1d333b" />
      <rect x="155" y="0" width="5" height="34" fill="#1d333b" />
      <rect x="164" y="0" width="3" height="34" fill="#1d333b" />
      <rect x="170" y="0" width="2" height="34" fill="#1d333b" />
      <rect x="175" y="0" width="7" height="34" fill="#1d333b" />
      <rect x="186" y="0" width="3" height="34" fill="#1d333b" />
      <rect x="192" y="0" width="2" height="34" fill="#1d333b" />
      <rect x="197" y="0" width="5" height="34" fill="#1d333b" />
      <rect x="206" y="0" width="4" height="34" fill="#1d333b" />
      <rect x="214" y="0" width="2" height="34" fill="#1d333b" />
      <rect x="219" y="0" width="6" height="34" fill="#1d333b" />
      <rect x="228" y="0" width="3" height="34" fill="#1d333b" />
      <rect x="234" y="0" width="2" height="34" fill="#1d333b" />
    </g>

    <!-- Right text -->
    <text x="740" y="16" class="bottom-tag" text-anchor="start">GO ALL IN</text>
  </g>
</svg>'''

with open(output_path, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"SVG regenerado con exito: {output_path}")
