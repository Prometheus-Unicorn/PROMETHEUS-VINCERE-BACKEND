"""Generate an interactive HTML color grading showcase for all 12 cinematic looks.

Applies each look and optical stack via FFmpeg to a 9:16 portrait sample frame,
embeds them as high-quality base64 images into a standalone self-contained HTML
presentation file with an interactive Before/After comparison slider.
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from mini_run_pipeline import looks
SAMPLE_IMAGE = REPO_ROOT / "docs" / "mini_run_studio" / "akimbo_frame_1080p.png"
OUTPUT_DIR = REPO_ROOT / "output" / "showcase_assets"
OUTPUT_HTML = REPO_ROOT / "color_grading_showcase.html"

# Aesthetic context & cinema references for each look
CINEMA_CONTEXT = {
    "kodak_2383_print": {
        "hollywoodRef": "Oppenheimer, The Dark Knight, Titanic, Succession",
        "aesthetic": "Authentic 35mm Celluloid Release Print",
        "description": "The gold standard of Hollywood motion picture release prints. Subtractive color saturation where ruby reds stay deep and dense, shadows carry rich cyan-teal density, and highlights roll off with warm amber softness.",
        "colorScience": "3D LUT Tetrahedral + Subtractive Density + Soft Shoulder Compression + Fine 35mm Emulsion Grain",
    },
    "fuji_3513_print": {
        "hollywoodRef": "The Matrix (remaster), Amélie, The Revenant",
        "aesthetic": "Emerald Shadow Depth & Magenta Highlight Roll-Off",
        "description": "Fujifilm's signature DI release print stock. Renowned for rich emerald-teal shadows, distinct cool foliage, and delicate magenta-tinted specular highlights with high dynamic range retention.",
        "colorScience": "3D LUT Tetrahedral + Emerald Shadow Bias + Magenta Highlight Vector + Fine Grain",
    },
    "sci_netone_balanced": {
        "hollywoodRef": "The Social Network, Mindhunter, High-End Commercials",
        "aesthetic": "Natural Melanin Protection & Gentle Filmic Contrast",
        "description": "Engineered for talking-head clarity. Locks the human skin tone vector along the natural melanin line while adding subtle contrast expansion and organic texture.",
        "colorScience": "3D LUT Tetrahedral + Skin-Tone Melanin Anchor + S-Curve Pedestal + Subtle Grain",
    },
    "teal_and_orange_blockbuster": {
        "hollywoodRef": "Transformers, Mad Max: Fury Road, Top Gun: Maverick",
        "aesthetic": "Hollywood Complementary Color Contrast",
        "description": "The dominant color scheme of modern blockbusters. Pushes cool teal/cyan deep into the shadows and background while pulling warm peach and orange highlights on the human face for maximum subject isolation.",
        "colorScience": "3D LUT Tetrahedral + Complementary Split-Toning + Punchy Midtone Contrast",
    },
    "moody_dramatic_cinema": {
        "hollywoodRef": "The Batman, Chernobyl, Sicario, Blade Runner 2049",
        "aesthetic": "Crushed Pedestal & Low-Key Atmospheric Tension",
        "description": "Deep, oppressive shadows and desaturated midtones. Crushes dark regions to build dramatic weight while keeping key facial highlights cleanly legible.",
        "colorScience": "3D LUT Tetrahedral + Low-Key Shadow Crush + Gamma Compression (0.90)",
    },
    "vintage_film_emulation": {
        "hollywoodRef": "Licorice Pizza, Once Upon a Time in Hollywood, Mid90s",
        "aesthetic": "1970s Warm Tungsten Nostalgia & Analog Texture",
        "description": "Warm, sun-faded aesthetic evoking vintage 16mm/35mm Kodak Tri-X and Ektachrome stocks. Midtones are warmed with a golden-yellow bias and blacks are lifted slightly.",
        "colorScience": "3D LUT Tetrahedral + 4500K Warm Cast + Black Point Lift + Temporal Grain",
    },
    "neon_tokyo_cyberpunk": {
        "hollywoodRef": "John Wick 4, Drive, Blade Runner 2049, Enter the Void",
        "aesthetic": "Electric Magenta, Neon Cyan & High-Saturation Night",
        "description": "Hyper-stylized night palette. Channels vibrant purples, magentas, and electric cyans across reflections and ambient lighting. Perfect for creative, tech, and nightlife content.",
        "colorScience": "Color Channel Mixer + Hue Saturation Gain (1.4x) + Blue/Magenta Curve Lift",
    },
    "bleach_bypass": {
        "hollywoodRef": "Saving Private Ryan, Fight Club, Seven, Minority Report",
        "aesthetic": "Silver Retention, Harsh Contrast & Muted Saturation",
        "description": "Emulates the photochemical process where the bleaching step is skipped, retaining silver grains alongside the color dyes. Delivers piercing specular highlights and muted, desaturated tones.",
        "colorScience": "3D LUT Tetrahedral + Silver Retention Contrast (1.35x) + 40% Desaturation",
    },
    "urban_desaturated": {
        "hollywoodRef": "The Hurt Locker, The Wire, Heat, Dark Knight (Gotham B-roll)",
        "aesthetic": "Industrial Steel, Concrete & Gritty Documentary",
        "description": "Cold, desaturated street documentary grade. Strips out vibrant color pollution, highlighting architecture, industrial tones, and raw human grit.",
        "colorScience": "3D LUT Tetrahedral + Heavy Saturation Cut (35%) + Cool Steel Temperature (6200K)",
    },
    "golden_hour_warmth": {
        "hollywoodRef": "La La Land, Her, Tree of Life, Euphoria sunset scenes",
        "aesthetic": "Sun-Kissed Amber Highlights & Soft Romantic Glow",
        "description": "Infuses footage with the ethereal glow of low-angle sunset light. Warms highlights with amber and honey tones while preserving neutral, clean shadow values.",
        "colorScience": "3D LUT Tetrahedral + 4200K Highlight Shift + Soft Shoulder Roll-Off + Vignette",
    },
    "clean_log_to_rec709": {
        "hollywoodRef": "Standard Broadcast, Apple Keynote, BBC Documentary Base",
        "aesthetic": "Precision Rec.709 Technical Expansion",
        "description": "Mathematically accurate de-logging base. Expands flat camera profiles to standard Rec.709 colorimetry and contrast with zero artificial stylistic distortion.",
        "colorScience": "3D LUT Tetrahedral + Linear Contrast Expansion (1.05x) + 6500K Neutral D65",
    },
    "faded_black_and_white": {
        "hollywoodRef": "Roma, Mank, The Lighthouse, Cold War",
        "aesthetic": "High-Latitude Monochrome & Lifted Matte Black",
        "description": "Artistic high-latitude monochrome. Desaturates color completely, maps luminance with custom spectral weighting (33% R / 34% G / 33% B), lifts the black point, and adds silver emulsion grain.",
        "colorScience": "Spectral Monochrome Channel Mixer + Lifted Black Pedestal + Emulsion Grain",
    },
}


def image_to_base64(path: Path) -> str:
    with open(path, "rb") as f:
        data = f.read()
    return f"data:image/jpeg;base64,{base64.b64encode(data).decode('utf-8')}"


def main() -> None:
    if not SAMPLE_IMAGE.exists():
        raise FileNotFoundError(f"Sample image not found: {SAMPLE_IMAGE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Generate clean raw reference image (540x960 portrait preview for fast browser rendering)
    raw_preview_path = OUTPUT_DIR / "raw_reference.jpg"
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(SAMPLE_IMAGE),
            "-vf", "scale=540:960",
            "-q:v", "2",
            str(raw_preview_path),
        ],
        check=True,
    )
    print(f"Generated raw preview: {raw_preview_path}")

    # 2. Grade for each registered look
    all_looks = looks.list_looks()
    graded_data: List[Dict[str, Any]] = []

    for look_def in all_looks:
        look_id = look_def["id"]
        look_name = look_def["name"]
        print(f"Grading look: {look_name} ({look_id})...")

        plan = looks.select_look(design={"lookId": look_id})
        filter_str = looks.build_grade_filter(plan, video_width=540, video_height=960)

        out_img_path = OUTPUT_DIR / f"{look_id}.jpg"
        full_vf = f"scale=540:960,{filter_str}" if filter_str else "scale=540:960"

        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(SAMPLE_IMAGE),
            "-vf", full_vf,
            "-q:v", "2",
            str(out_img_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Warning: FFmpeg failed for {look_id}: {res.stderr}")
            continue

        b64_str = image_to_base64(out_img_path)
        context = CINEMA_CONTEXT.get(look_id, {})

        graded_data.append({
            "id": look_id,
            "name": look_name,
            "mood": look_def.get("mood", ""),
            "description": look_def.get("description", ""),
            "hollywoodRef": context.get("hollywoodRef", "Cinematic Motion Pictures"),
            "aesthetic": context.get("aesthetic", "Cinematic Color Grade"),
            "fullDescription": context.get("description", look_def.get("description", "")),
            "colorScience": context.get("colorScience", "3D LUT + Optical Finishing"),
            "filterString": filter_str,
            "policies": look_def.get("policies", {}),
            "imageBase64": b64_str,
        })

    raw_b64 = image_to_base64(raw_preview_path)
    print(f"Successfully graded {len(graded_data)} cinematic looks!")

    # 3. Build the interactive HTML file
    cards_json = json.dumps(graded_data)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Prometheus Core: Cinematic Color Grading Showcase</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #07090e;
      --card-bg: #0d121d;
      --card-border: #1e293b;
      --accent-cyan: #38bdf8;
      --accent-amber: #f59e0b;
      --accent-emerald: #10b981;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background: var(--bg);
      color: var(--text-main);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      line-height: 1.5;
      padding: 2.5rem 1.5rem 5rem;
      min-height: 100vh;
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
    }}

    /* Header */
    header {{
      text-align: center;
      margin-bottom: 3rem;
      padding-bottom: 2rem;
      border-bottom: 1px solid rgba(255,255,255,0.08);
    }}

    .badge-pill {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid rgba(56, 189, 248, 0.3);
      color: var(--accent-cyan);
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      padding: 0.4rem 1rem;
      border-radius: 9999px;
      margin-bottom: 1rem;
    }}

    h1 {{
      font-size: 2.75rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      background: linear-gradient(135deg, #ffffff 30%, #94a3b8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 0.75rem;
    }}

    .subtitle {{
      color: var(--text-muted);
      font-size: 1.15rem;
      max-width: 760px;
      margin: 0 auto;
    }}

    /* Architectural Concept Box: Stills vs Video */
    .concept-box {{
      background: linear-gradient(145deg, #0f172a 0%, #090e1a 100%);
      border: 1px solid rgba(56, 189, 248, 0.25);
      border-radius: 16px;
      padding: 1.75rem;
      margin-bottom: 3.5rem;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2rem;
      position: relative;
      overflow: hidden;
    }}

    .concept-box::before {{
      content: '';
      position: absolute;
      top: -50%;
      right: -20%;
      width: 300px;
      height: 300px;
      background: radial-gradient(circle, rgba(56, 189, 248, 0.12) 0%, transparent 70%);
      pointer-events: none;
    }}

    .concept-col h3 {{
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--accent-cyan);
      margin-bottom: 0.6rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .concept-col p {{
      color: var(--text-muted);
      font-size: 0.925rem;
      line-height: 1.6;
    }}

    /* Interactive Split Loupe Section */
    .slider-section {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 20px;
      padding: 2rem;
      margin-bottom: 4rem;
      box-shadow: 0 20px 40px -15px rgba(0,0,0,0.5);
    }}

    .slider-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
      gap: 1rem;
    }}

    .slider-header h2 {{
      font-size: 1.5rem;
      font-weight: 700;
    }}

    .look-selector-bar {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}

    .btn-look {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: var(--text-muted);
      padding: 0.45rem 0.85rem;
      border-radius: 8px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .btn-look:hover, .btn-look.active {{
      background: var(--accent-cyan);
      color: #040810;
      border-color: var(--accent-cyan);
      box-shadow: 0 0 16px rgba(56, 189, 248, 0.4);
    }}

    .slider-wrapper {{
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 1rem 0;
    }}

    .comparison-container {{
      position: relative;
      width: 440px;
      height: 782px;
      max-width: 100%;
      border-radius: 16px;
      overflow: hidden;
      border: 2px solid rgba(255, 255, 255, 0.15);
      box-shadow: 0 25px 50px -12px rgba(0,0,0,0.8);
      user-select: none;
    }}

    .comparison-img {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      pointer-events: none;
    }}

    .comparison-graded {{
      clip-path: polygon(0 0, 50% 0, 50% 100%, 0 100%);
      z-index: 2;
    }}

    .slider-handle-line {{
      position: absolute;
      top: 0;
      bottom: 0;
      left: 50%;
      width: 2px;
      background: #ffffff;
      z-index: 10;
      box-shadow: 0 0 10px rgba(0,0,0,0.8);
      transform: translateX(-50%);
      cursor: ew-resize;
    }}

    .slider-handle-button {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 42px;
      height: 42px;
      background: #ffffff;
      border-radius: 50%;
      box-shadow: 0 4px 15px rgba(0,0,0,0.6);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: ew-resize;
      color: #0f172a;
      font-weight: 800;
      font-size: 0.9rem;
    }}

    .label-tag {{
      position: absolute;
      bottom: 1.25rem;
      padding: 0.35rem 0.85rem;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      z-index: 5;
    }}

    .label-left {{
      left: 1.25rem;
      color: var(--accent-cyan);
    }}

    .label-right {{
      right: 1.25rem;
      color: var(--text-muted);
    }}

    /* Gallery Grid */
    .section-title {{
      font-size: 1.85rem;
      font-weight: 800;
      margin-bottom: 0.5rem;
      letter-spacing: -0.02em;
    }}

    .section-desc {{
      color: var(--text-muted);
      margin-bottom: 2rem;
    }}

    .looks-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 2rem;
    }}

    .look-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }}

    .look-card:hover {{
      transform: translateY(-4px);
      border-color: rgba(56, 189, 248, 0.4);
      box-shadow: 0 15px 30px -10px rgba(0,0,0,0.7);
    }}

    .card-img-wrapper {{
      width: 100%;
      height: 420px;
      overflow: hidden;
      position: relative;
      background: #000;
    }}

    .card-img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.3s ease;
    }}

    .look-card:hover .card-img {{
      transform: scale(1.03);
    }}

    .card-badge {{
      position: absolute;
      top: 1rem;
      left: 1rem;
      background: rgba(13, 18, 29, 0.85);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255,255,255,0.15);
      color: #fff;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 0.3rem 0.7rem;
      border-radius: 6px;
    }}

    .card-body {{
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      flex-grow: 1;
    }}

    .card-title {{
      font-size: 1.25rem;
      font-weight: 700;
      margin-bottom: 0.25rem;
    }}

    .card-ref {{
      font-size: 0.78rem;
      color: var(--accent-amber);
      font-weight: 600;
      margin-bottom: 0.85rem;
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }}

    .card-desc {{
      color: var(--text-muted);
      font-size: 0.875rem;
      line-height: 1.55;
      margin-bottom: 1.25rem;
      flex-grow: 1;
    }}

    .science-pill {{
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 8px;
      padding: 0.6rem 0.85rem;
      margin-bottom: 1rem;
      font-size: 0.75rem;
      color: var(--accent-cyan);
      font-family: 'JetBrains Mono', monospace;
    }}

    .cmd-box {{
      background: #050810;
      border: 1px solid #1a2333;
      border-radius: 8px;
      padding: 0.75rem;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.7rem;
      color: #94a3b8;
      overflow-x: auto;
      white-space: nowrap;
    }}

    .card-footer {{
      margin-top: 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid rgba(255,255,255,0.06);
      padding-top: 0.85rem;
      font-size: 0.75rem;
      color: var(--text-dim);
    }}

    @media (max-width: 900px) {{
      .concept-box {{
        grid-template-columns: 1fr;
      }}
      .comparison-container {{
        width: 100%;
        height: 600px;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="badge-pill">Prometheus Core • Mini-Runs Visual Lab</div>
      <h1>Cinematic Color Grading Master Showcase</h1>
      <p class="subtitle">Real 1080&times;1920 portrait talking-head plate graded through the 12 canonical film looks and the 7-pillar optical finishing stack.</p>
    </header>

    <!-- Technical Inquiry: Stills vs Video -->
    <div class="concept-box">
      <div class="concept-col">
        <h3>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
          Why Single-Image Color Grading Is 100% Mathematically Valid
        </h3>
        <p>
          You are <strong>spot on</strong>: a video frame sequence at 30 fps is mathematically a stream of spatial color tensors. 
          A 3D LUT (Look-Up Table) operates in $O(1)$ constant time per pixel via <strong>tetrahedral interpolation</strong>. 
          Because the LUT mapping matrix does not rely on motion vectors or historical frames, the spatial color transformation of a single video frame is <strong>bit-for-bit identical</strong> to applying it on the video stream.
        </p>
      </div>
      <div class="concept-col">
        <h3>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg>
          What Video Adds: The Temporal Emulsion Physics
        </h3>
        <p>
          Where stills diverge from video in cinema is <strong>time ($t$)</strong>. In real analog celluloid, silver halide crystal grains do not freeze—they dance randomly across consecutive frames (modeled via FFmpeg's temporal noise <code>allf=t</code>). Projector gate weave jitter (<code>sin(14.5*t)</code>) and organic exposure breath (<code>sin(8.8*t)</code>) only activate across motion, transforming a static grade into living film.
        </p>
      </div>
    </div>

    <!-- Interactive Comparison Slider -->
    <div class="slider-section">
      <div class="slider-header">
        <div>
          <h2>Interactive Loupe: Raw Flat Input vs Film Grade</h2>
          <p style="color: var(--text-muted); font-size: 0.85rem;">Drag the divider horizontally to inspect highlight roll-off, skin-tone preservation, and shadow density.</p>
        </div>
        <div class="look-selector-bar" id="lookSelectorBar">
          <!-- Buttons dynamically injected via JS -->
        </div>
      </div>

      <div class="slider-wrapper">
        <div class="comparison-container" id="compContainer">
          <!-- Underneath: Raw Reference -->
          <img src="{raw_b64}" alt="Raw Source Plate" class="comparison-img" id="imgRaw">
          
          <!-- Top: Graded Plate (clipped) -->
          <img src="{graded_data[0]['imageBase64']}" alt="Graded Film Plate" class="comparison-img comparison-graded" id="imgGraded">

          <!-- Divider Handle -->
          <div class="slider-handle-line" id="sliderHandle">
            <div class="slider-handle-button">&harr;</div>
          </div>

          <div class="label-tag label-left" id="activeLookTag">{graded_data[0]['name']} (Graded)</div>
          <div class="label-tag label-right">Raw Flat Source</div>
        </div>
      </div>
    </div>

    <!-- 12 Looks Gallery Grid -->
    <div style="margin-bottom: 1.5rem;">
      <h2 class="section-title">The 12 Canonical Cinematic Look Profiles</h2>
      <p class="section-desc">Every look is actively resolvable via user prompt, design metadata, or automatic aesthetic fallback in <code>mini_run_pipeline</code>.</p>
    </div>

    <div class="looks-grid">
"""

    for item in graded_data:
        policies = item.get("policies") or {}
        best_for = ", ".join(policies.get("bestFor", ["all narrative"]))
        avoid_for = ", ".join(policies.get("avoidFor", ["none"])) if policies.get("avoidFor") else "none"

        html_content += f"""
      <div class="look-card" id="card_{item['id']}">
        <div class="card-img-wrapper">
          <img src="{item['imageBase64']}" alt="{item['name']}" class="card-img" loading="lazy">
          <div class="card-badge">{item['aesthetic']}</div>
        </div>
        <div class="card-body">
          <h3 class="card-title">{item['name']}</h3>
          <div class="card-ref">&#9733; Film Reference: {item['hollywoodRef']}</div>
          <p class="card-desc">{item['fullDescription']}</p>
          
          <div class="science-pill">
            <strong>Pipeline Stack:</strong><br>{item['colorScience']}
          </div>

          <div class="cmd-box" title="FFmpeg filtergraph">
            {item['filterString']}
          </div>

          <div class="card-footer">
            <span><strong>Best:</strong> {best_for}</span>
            <span><strong>Avoid:</strong> {avoid_for}</span>
          </div>
        </div>
      </div>
"""

    html_content += f"""
    </div>
  </div>

  <script>
    const looksData = {cards_json};
    let currentLookIndex = 0;

    const compContainer = document.getElementById('compContainer');
    const imgGraded = document.getElementById('imgGraded');
    const sliderHandle = document.getElementById('sliderHandle');
    const activeLookTag = document.getElementById('activeLookTag');
    const lookSelectorBar = document.getElementById('lookSelectorBar');

    // Populate look selector buttons
    looksData.forEach((look, index) => {{
      const btn = document.createElement('button');
      btn.className = 'btn-look' + (index === 0 ? ' active' : '');
      btn.textContent = look.name;
      btn.addEventListener('click', () => selectLook(index));
      lookSelectorBar.appendChild(btn);
    }});

    function selectLook(index) {{
      currentLookIndex = index;
      const look = looksData[index];
      imgGraded.src = look.imageBase64;
      activeLookTag.textContent = look.name + ' (Graded)';

      const buttons = lookSelectorBar.querySelectorAll('.btn-look');
      buttons.forEach((b, i) => {{
        b.classList.toggle('active', i === index);
      }});
    }}

    // Split comparison slider drag logic
    let isDragging = false;

    function updateSlider(xPos) {{
      const rect = compContainer.getBoundingClientRect();
      let pos = (xPos - rect.left) / rect.width;
      pos = Math.max(0.02, Math.min(0.98, pos));
      const pct = (pos * 100).toFixed(2) + '%';
      sliderHandle.style.left = pct;
      imgGraded.style.clipPath = `polygon(0 0, ${{pct}} 0, ${{pct}} 100%, 0 100%)`;
    }}

    compContainer.addEventListener('mousedown', (e) => {{
      isDragging = true;
      updateSlider(e.clientX);
    }});

    window.addEventListener('mousemove', (e) => {{
      if (!isDragging) return;
      updateSlider(e.clientX);
    }});

    window.addEventListener('mouseup', () => {{
      isDragging = false;
    }});

    // Touch support for mobile / tablets
    compContainer.addEventListener('touchstart', (e) => {{
      isDragging = true;
      if (e.touches.length > 0) updateSlider(e.touches[0].clientX);
    }});

    window.addEventListener('touchmove', (e) => {{
      if (!isDragging || e.touches.length === 0) return;
      updateSlider(e.touches[0].clientX);
    }});

    window.addEventListener('touchend', () => {{
      isDragging = false;
    }});
  </script>
</body>
</html>
"""

    OUTPUT_HTML.write_text(html_content, encoding="utf-8")
    studio_html = REPO_ROOT / "docs" / "mini_run_studio" / "color_grading_showcase.html"
    studio_html.write_text(html_content, encoding="utf-8")
    print(f"Interactive showcase successfully compiled to:")
    print(f"1. {OUTPUT_HTML} ({OUTPUT_HTML.stat().st_size} bytes)")
    print(f"2. {studio_html} ({studio_html.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
