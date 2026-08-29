#!/usr/bin/env python3
"""
Generate images/og-card.jpg — the 1200x630 social card.

og:image was the square 999x999 logo, which every platform centre-crops to a
letterbox, so the card arrived as a meaningless crop of a circle. This draws a
real 1.91:1 card carrying the one fact worth putting in front of someone
scrolling: what the franchise costs.

    python3 build/make-og-card.py

Needs Pillow and one download of each face (cached in build/.fonts/).

The card carries the same pairing as the page: Fraunces speaks, Inter labels.
Drawing every line in the display face made the small print shout.
"""
import os
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS  = os.path.join(ROOT, 'build', '.fonts')
DISPLAY = os.path.join(FONTS, 'fraunces-extrabold.ttf')
BODY    = os.path.join(FONTS, 'inter-semibold.ttf')
PHOTO  = os.path.join(ROOT, 'images', 'chai-4.jpeg')
OUT    = os.path.join(ROOT, 'images', 'og-card.jpg')

W, H    = 1200, 630
INK     = (16, 32, 30)
STEAM   = (244, 239, 228)
JAGGERY = (230, 169, 60)
BRASS   = (192, 138, 62)

def fetch(path, family):
    """Google serves a static instance for a single-value axis request, which is
    what Pillow needs — it cannot pick a weight out of a variable font."""
    if os.path.exists(path):
        return
    os.makedirs(FONTS, exist_ok=True)
    css = subprocess.check_output([
        'curl', '-sSA', 'Mozilla/5.0',
        'https://fonts.googleapis.com/css2?family=' + family
    ]).decode()
    url = css.split('url(')[1].split(')')[0]
    subprocess.check_call(['curl', '-sS', '-o', path, url])

fetch(DISPLAY, 'Fraunces:opsz,wght@144,800')
fetch(BODY,    'Inter:wght@600')

f = lambda size: ImageFont.truetype(DISPLAY, size)   # the voice
b = lambda size: ImageFont.truetype(BODY, size)      # the labels

card = Image.new('RGB', (W, H), INK)

# --- photograph, right third, feathered into the ink ------------------------
PW = 470
photo = Image.open(PHOTO).convert('RGB')
side  = min(photo.size)
photo = photo.crop(((photo.width - side) // 2, (photo.height - side) // 2,
                    (photo.width + side) // 2, (photo.height + side) // 2))
photo = photo.resize((max(PW, H), max(PW, H)), Image.LANCZOS)
photo = photo.crop((0, (photo.height - H) // 2, PW, (photo.height - H) // 2 + H))

# A horizontal alpha ramp, held wide enough that the photo dissolves into the
# background over ~150px instead of butting against it with a seam.
mask = Image.linear_gradient('L').rotate(-90, expand=True).resize((PW, H))
mask = mask.point(lambda v: min(255, int(v * 3.2)))
card.paste(photo, (W - PW, 0), mask)

# --- type, left --------------------------------------------------------------
d = ImageDraw.Draw(card)
X    = 72
RULE = 640          # every rule and line of type stays left of the feather

d.text((X, 96), 'CHAI WORTH COMING BACK FOR', font=b(20), fill=JAGGERY)
d.rectangle([X, 136, X + 56, 139], fill=BRASS)

d.text((X, 172), 'A chai franchise',  font=f(74), fill=STEAM)
d.text((X, 254), 'from \u20b91 lakh',      font=f(74), fill=JAGGERY)

d.text((X, 362), 'Hyderabadi Amruttulya', font=f(34), fill=STEAM)

d.rectangle([X, 456, RULE, 457], fill=(58, 74, 70))
d.text((X, 484), '40%\u201350% margin  \u00b7  100\u2013200 sq ft', font=b(23), fill=(163, 178, 174))
d.text((X, 520), 'Jaggery, not refined sugar',        font=b(23), fill=(163, 178, 174))

card.save(OUT, 'JPEG', quality=88, optimize=True, progressive=True)
print('wrote %s (%d bytes)' % (OUT, os.path.getsize(OUT)))
