import os
import shutil
from pathlib import Path

lut_mapping = {
    'teal_and_orange_blockbuster.cube': ('Dramatic_BlockBuster_33.cube', 'Teal and Orange Blockbuster Modern 2-Strip'),
    'kodak_2383_print.cube': ('koda5219.cube', 'Kodak Vision Color Print Film 2383 Emulation'),
    'sci_netone_balanced.cube': ('Nicest_709.cube', 'Sci-Netone Balanced Skin Tone Reference'),
    'vintage_film_emulation.cube': ('Vintage.cube', 'Vintage 1970s Warm 35mm Stock Emulation'),
    'golden_hour_warmth.cube': ('warm.cube', 'Golden Hour Warmth Sunset Radiance'),
    'clean_log_to_rec709.cube': ('VLog_to_V709.cube', 'Clean Arri Alexa LogC3 to Rec709 Base Transform'),
    'urban_desaturated.cube': ('SteelBlue.cube', 'Urban Desaturated Industrial Architecture'),
}

lut_dir = Path('mini_run_pipeline/luts')
scratch_lumix = Path('scratch/lumix_luts')
scratch_lumix.mkdir(parents=True, exist_ok=True)

# First pass: parse and write normalized canonical LUTs
for target_name, (src_name, title) in lut_mapping.items():
    src_path = lut_dir / src_name
    if not src_path.exists():
        src_path = scratch_lumix / src_name
    lines = src_path.read_text(encoding='utf-8', errors='ignore').splitlines()
    data = []
    for l in lines:
        parts = l.strip().split()
        if len(parts) == 3:
            try:
                r, g, b = float(parts[0]), float(parts[1]), float(parts[2])
                data.append((r, g, b))
            except ValueError:
                pass
    assert len(data) == 33 * 33 * 33, f"Expected 35937 RGB points for {src_name}, got {len(data)}"
    
    out_lines = [
        f'TITLE "{title}"',
        'LUT_3D_SIZE 33',
        'DOMAIN_MIN 0.0 0.0 0.0',
        'DOMAIN_MAX 1.0 1.0 1.0',
    ]
    for r, g, b in data:
        r_clamped = max(0.0, min(1.0, r))
        g_clamped = max(0.0, min(1.0, g))
        b_clamped = max(0.0, min(1.0, b))
        out_lines.append(f"{r_clamped:.6f} {g_clamped:.6f} {b_clamped:.6f}")
    
    target_path = lut_dir / target_name
    target_path.write_text('\n'.join(out_lines) + '\n', encoding='utf-8')
    print(f"Normalized {target_name} ({len(out_lines)} lines, {target_path.stat().st_size} bytes)")

# Move all raw downloaded LUTs to scratch/lumix_luts
raw_files = [
    'Dramatic_BlockBuster_33.cube',
    'koda5219.cube',
    'kodaRG400.cube',
    'kodaUM800.cube',
    'Nicest_709.cube',
    'SteelBlue.cube',
    'Vintage.cube',
    'VLog_to_V709.cube',
    'warm.cube',
]
for rf in raw_files:
    p = lut_dir / rf
    if p.exists():
        dest = scratch_lumix / rf
        if dest.exists():
            dest.unlink()
        shutil.move(str(p), str(dest))
        print(f"Moved {rf} -> {dest}")

print("Normalization complete.")
