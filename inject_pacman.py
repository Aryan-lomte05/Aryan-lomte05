#!/usr/bin/env python3
"""
inject_pacman.py
Reads the snake SVG, extracts the animateMotion path, 
and injects a Pac-Man following 3 cells behind the snake head.
"""

import re
import sys
import os

def inject_pacman(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        svg = f.read()

    # ── 1. Find the snake head's animateMotion element ─────────────────────────
    # Platane/snk puts the snake head first; its motion path is in:
    #   <animateMotion path="M x,y L x,y ..." dur="Xs" .../>
    motion_match = re.search(
        r'(<animateMotion\s[^>]*path="([^"]+)"[^>]*dur="([^"]+)"[^>]*/?>)',
        svg
    )
    if not motion_match:
        print("Could not find animateMotion in snake SVG. Copying as-is.")
        import shutil
        shutil.copy(input_path, output_path)
        return

    full_tag   = motion_match.group(1)
    path_data  = motion_match.group(2)
    dur        = motion_match.group(3)   # e.g. "3.5s"

    # ── 2. Calculate delay so Pac-Man starts 3 blocks behind ──────────────────
    # Extract numeric duration
    dur_s = float(re.sub(r'[^\d.]', '', dur))

    # Count path segments to estimate "3 cells behind" as a time fraction.
    # Each "L" or "M" segment = one cell. We want ~3 cells of lag.
    segments = re.findall(r'[ML]\s*[\d.]+\s*,\s*[\d.]+', path_data)
    n_cells  = max(len(segments), 1)
    # 3 cells behind = 3/n_cells of total duration as begin offset
    # We use a negative begin (keySplines trick): begin="-Xs" to start mid-path
    lag_fraction = 3.0 / n_cells
    lag_s = dur_s * lag_fraction
    # begin = dur_s - lag_s  means Pac-Man is lag_s seconds "behind"
    begin_val = f"-{lag_s:.3f}s"

    # ── 3. Build the Pac-Man SVG group ─────────────────────────────────────────
    # Pac-Man: yellow circle with chomping mouth, 14px diameter
    pacman_group = f"""
  <!-- Pac-Man following the snake path -->
  <g id="pacman">
    <!-- Body -->
    <path fill="#FFD700" filter="url(#snk-f1)">
      <!-- Chomping mouth: alternates between open and closed -->
      <animateMotion 
        path="{path_data}" 
        dur="{dur}" 
        begin="{begin_val}" 
        repeatCount="indefinite"
        rotate="auto"/>
      <animate attributeName="d"
        values="M7,7 L14,2 A7,7 0 1,0 14,12 Z;M7,7 L14,7 A7,7 0 1,0 14,7 Z;M7,7 L14,2 A7,7 0 1,0 14,12 Z"
        dur="0.25s"
        repeatCount="indefinite"/>
    </path>
    <!-- Eye -->
    <circle cx="9" cy="4" r="1.5" fill="#1a1b27" opacity="0.85">
      <animateMotion 
        path="{path_data}" 
        dur="{dur}" 
        begin="{begin_val}" 
        repeatCount="indefinite"
        rotate="auto"/>
    </circle>
  </g>
"""

    # ── 4. Inject Pac-Man just before </svg> ───────────────────────────────────
    output_svg = svg.replace('</svg>', pacman_group + '\n</svg>')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_svg)

    print(f"Done! Pac-Man injected. Path has {n_cells} cells, lag={lag_s:.2f}s, begin={begin_val}")


if __name__ == '__main__':
    inp = sys.argv[1] if len(sys.argv) > 1 else 'github-contribution-grid-snake-dark.svg'
    out = sys.argv[2] if len(sys.argv) > 2 else 'github-contribution-grid-snake-pacman-dark.svg'
    inject_pacman(inp, out)