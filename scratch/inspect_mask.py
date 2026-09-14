import cv2
import numpy as np

img = cv2.imread('scratch/test_frame_22.5s.png')
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
b, g, r = cv2.split(img)
lum = 0.299 * r.astype(float) + 0.587 * g.astype(float) + 0.114 * b.astype(float)

bright_text = lum > 160.0
cyan_text = (b > 130) & (g > 130) & (r < 110)
warm_text = (r > 175) & (g > 130) & (b < 80)
mask = (bright_text | cyan_text | warm_text).astype(np.uint8) * 255

cv2.imwrite('scratch/mask_22.5s.png', mask)
print("Saved mask to scratch/mask_22.5s.png")
print("Nonzero pixels in mask:", cv2.countNonZero(mask))
