import os
from PIL import ImageFont

font_path = 'remotion-app/public/fonts/library/antenna/antenna-a14c59300f3b.ttf'
font = ImageFont.truetype(font_path, 104)

text = "PURCHASED MORE"
bbox = font.getbbox(text)
w = bbox[2] - bbox[0]
h = bbox[3] - bbox[1]
aspect = w / (len(text) * 104)
print(f"Text '{text}' at size 104:")
print(f"  bbox: {bbox}")
print(f"  width: {w}px, height: {h}px")
print(f"  actual char aspect: {aspect:.3f}")
