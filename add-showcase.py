"""
SHOWCASE IMAGES  (the "Made by hand" section)
=============================================

The portfolio grid uses square tiles - that's what add-logos.py produces.
This script handles the WIDE images used in the "Made by hand" section
instead, keeping their original shape.

HOW TO USE

    1. Put the image in  _originals/showcase/
    2. Run:   python add-showcase.py
    3. Commit and push

Output goes to  assets/img/process/  and is referenced by filename in
index.html, so replacing an image means keeping the same filename.

WATERMARKING

Finished artwork gets the tiled watermark, same as the portfolio.
Screenshots of work-in-progress do NOT - the whole point of that image
is to be believable evidence of real work, and covering it in text
undercuts that. A filename starting with "raw-" skips the watermark.

    furnace-smp-poster.jpg      -> watermarked (finished artwork)
    raw-furnace-smp-psd.jpg     -> not watermarked (process screenshot)

FIRST TIME ONLY
    pip install Pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "_originals", "showcase")
DST = os.path.join(HERE, "assets", "img", "process")

MARK = "SMURFCAT"
ALPHA = 62            # slightly lighter than the portfolio - these are big
WIDTH = 1200          # output width; height follows the original ratio
QUALITY = 82
ANGLE = -30

FONT_CANDIDATES = [
    r"C:/Windows/Fonts/arialbd.ttf",
    r"C:/Windows/Fonts/arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def load_font(px):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, px)
    print("  ! No TrueType font found - using a basic font.")
    return ImageFont.load_default()


def watermark(img):
    """Tile MARK diagonally across an image of any shape."""
    w, h = img.size
    font = load_font(30)
    pad = int(max(w, h) * 1.6)
    layer = Image.new("RGBA", (pad, pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    bbox = d.textbbox((0, 0), MARK, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    step_x, step_y = tw + 90, th + 78

    row, y = 0, 0
    while y < pad:
        x = -tw + (step_x // 2 if row % 2 else 0)
        while x < pad:
            d.text((x, y), MARK, font=font,
                   fill=(255, 255, 255, ALPHA),
                   stroke_width=2, stroke_fill=(0, 0, 0, ALPHA // 2))
            x += step_x
        y += step_y
        row += 1

    layer = layer.rotate(ANGLE, resample=Image.BICUBIC)
    left, top = (pad - w) // 2, (pad - h) // 2
    layer = layer.crop((left, top, left + w, top + h))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def slugify(name):
    base = os.path.splitext(os.path.basename(name))[0]
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()
    return re.sub(r"-{2,}", "-", base)


def main():
    if not os.path.isdir(SRC):
        os.makedirs(SRC, exist_ok=True)
        print("Created " + SRC)
        print("Put the wide showcase images in there, then run this again.")
        return 0

    names = sorted(f for f in os.listdir(SRC)
                   if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")))
    if not names:
        print("No images found in " + SRC)
        return 0

    os.makedirs(DST, exist_ok=True)
    for name in names:
        im = Image.open(os.path.join(SRC, name)).convert("RGB")
        w, h = im.size
        im = im.resize((WIDTH, round(h * WIDTH / w)), Image.LANCZOS)

        slug = slugify(name)
        skip_mark = slug.startswith("raw-")
        if not skip_mark:
            im = watermark(im)

        out = os.path.join(DST, slug + ".jpg")
        im.save(out, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        print("  %-30s %sx%s  %4d KB  %s" % (
            slug + ".jpg", im.size[0], im.size[1],
            os.path.getsize(out) // 1024,
            "(no watermark)" if skip_mark else "watermarked"))

    print("\nDone. These are referenced by filename in index.html.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
