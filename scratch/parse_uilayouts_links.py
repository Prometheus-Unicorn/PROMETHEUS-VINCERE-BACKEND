import re
from pathlib import Path

content = Path(r"C:\Users\HomePC\.gemini\antigravity-cli\brain\324a0008-10b1-47d2-91b3-5651c4d692f0\.system_generated\steps\962\content.md").read_text(encoding="utf-8", errors="ignore")
matches = re.findall(r'href="(/components/[^"#\s]+)"', content)
print(f"Total matches: {len(matches)}")
for m in sorted(set(matches)):
    print(m)
