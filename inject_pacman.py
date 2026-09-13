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

    # Find the duration of the animation from the .s class
    match = re.search(r'\.s\{[^}]*animation:[^}]+(\d+ms)', svg)
    if not match:
        print("Could not find animation duration in snake SVG. Copying as-is.")
        import shutil
        shutil.copy(input_path, output_path)
        return
    dur = match.group(1)

    # Find the highest index for the snake body (the tail)
    tail_match = re.findall(r'@keyframes s(\d+)', svg)
    if not tail_match:
        print("Could not find keyframes in snake SVG. Copying as-is.")
        import shutil
        shutil.copy(input_path, output_path)
        return
    
    tail_index = max(int(i) for i in tail_match)
    
    # Extract the tail's initial x and y from its rect to align Pac-Man precisely
    # <rect class="s s3" x="3.0" y="3.0" width="9.9" height="9.9" rx="3.3" ry="3.3"/>
    rect_match = re.search(f'<rect class="s s{tail_index}" x="([^"]+)" y="([^"]+)" width="([^"]+)"', svg)
    if rect_match:
        rx = float(rect_match.group(1))
        ry = float(rect_match.group(2))
        rw = float(rect_match.group(3))
    else:
        rx, ry, rw = 3.0, 3.0, 10.0
        
    cx = rx + rw/2
    cy = ry + rw/2
    r = rw/1.8 # make pacman slightly larger than the snake body

    # Build the Pac-Man SVG group
    pacman_group = f"""
  <!-- Pac-Man following the snake tail (s{tail_index}) -->
  <g class="s s{tail_index}">
    <!-- Body -->
    <path fill="#FFD700">
      <animate attributeName="d"
        values="M{cx},{cy} L{cx+r},{cy-r*0.6} A{r},{r} 0 1,0 {cx+r},{cy+r*0.6} Z;M{cx},{cy} L{cx+r},{cy} A{r},{r} 0 1,0 {cx+r},{cy} Z;M{cx},{cy} L{cx+r},{cy-r*0.6} A{r},{r} 0 1,0 {cx+r},{cy+r*0.6} Z"
        dur="0.25s"
        repeatCount="indefinite"/>
    </path>
    <!-- Eye -->
    <circle cx="{cx+1.5}" cy="{cy-2.5}" r="1.5" fill="#1a1b27" opacity="0.85" />
  </g>
"""

    output_svg = svg.replace('</svg>', pacman_group + '\n</svg>')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_svg)

    print(f"Done! Pac-Man injected. Attached to s{tail_index} with duration {dur}.")


if __name__ == '__main__':
    inp = sys.argv[1] if len(sys.argv) > 1 else 'github-contribution-grid-snake-dark.svg'
    out = sys.argv[2] if len(sys.argv) > 2 else 'github-contribution-grid-snake-pacman-dark.svg'
    inject_pacman(inp, out)