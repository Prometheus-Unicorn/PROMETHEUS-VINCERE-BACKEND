import urllib.request
from pathlib import Path

files = [
    ("liquid-glass.tsx", "https://raw.githubusercontent.com/ui-layouts/uilayouts/main/apps/ui-layout/components/ui/liquid-glass.tsx"),
    ("blur-vignette.tsx", "https://raw.githubusercontent.com/ui-layouts/uilayouts/main/apps/ui-layout/components/ui/blur-vignette.tsx"),
    ("liquid-gradient.tsx", "https://raw.githubusercontent.com/ui-layouts/uilayouts/main/apps/ui-layout/components/ui/liquid-gradient.tsx"),
    ("ripple-shaders.txt", "https://raw.githubusercontent.com/ui-layouts/uilayouts/main/apps/ui-layout/registry/components/external/image-ripple-effect/shaders.txt"),
    ("ripple-scene.txt", "https://raw.githubusercontent.com/ui-layouts/uilayouts/main/apps/ui-layout/registry/components/external/image-ripple-effect/scene.txt"),
    ("mesh-gradient.txt", "https://raw.githubusercontent.com/ui-layouts/uilayouts/main/apps/ui-layout/registry/components/external/mesh-gradient-background.txt"),
    ("section-noise.tsx", "https://raw.githubusercontent.com/ui-layouts/uilayouts/main/apps/ui-layout/registry/components/noise-effect/section-noise.tsx"),
    ("motion-number.mdx", "https://raw.githubusercontent.com/ui-layouts/uilayouts/main/apps/ui-layout/content/components/motion-number.mdx"),
]

out_dir = Path("scratch/uilayouts_sources")
out_dir.mkdir(parents=True, exist_ok=True)

for name, url in files:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            (out_dir / name).write_text(content, encoding="utf-8")
            print(f"Downloaded {name} ({len(content)} bytes)")
    except Exception as e:
        print(f"Failed {name}: {e}")
