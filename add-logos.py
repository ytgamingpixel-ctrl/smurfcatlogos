"""
ADD LOGOS TO THE PORTFOLIO
==========================

How to add a new logo to the website:

    1. Drop the clean image into the  _originals/  folder
    2. Run:   python add-logos.py
    3. Commit and push

That's it. This script does the rest:

  * watermarks every image in _originals/ (the watermark is burned into
    the pixels, so a downloaded copy still carries it)
  * centre-crops to a square and resizes, so the grid stays tidy
  * writes them into assets/img/work/ as .jpg
  * rebuilds assets/js/work.js so the new logo shows on the site

Existing logos keep the name and order you gave them. New ones are added
at the end with a name guessed from the filename - rename them in
assets/js/work.js if the guess is wrong, and the script will respect that
from then on.

FIRST TIME ONLY
---------------
    pip install Pillow

WHY THE CLEAN FILES STAY IN _originals/
---------------------------------------
Anything inside assets/ is published with the website and can be downloaded
by anyone. _originals/ is git-ignored, so the unmarked files never leave
your machine. Don't move them.
"""

from PIL import Image, ImageDraw, ImageFont
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "_originals")
IMG_DIR = os.path.join(HERE, "assets", "img", "work")
WORK_JS = os.path.join(HERE, "assets", "js", "work.js")

# ── Watermark settings ────────────────────────────────────────────────
MARK = "SMURFCAT"     # the text stamped across each image
ALPHA = 70            # strength, 0-255. ~95 = heavier, ~50 = subtler
SIZE = 800            # output width/height in pixels
QUALITY = 82          # JPEG quality
ANGLE = -30           # tilt of the watermark text

DEFAULT_TYPE = "Server logo"

# Words that shouldn't be title-cased when guessing a name from a filename
CASING = {
    "pvp": "PvP", "smp": "SMP", "mc": "MC", "uhc": "UHC",
    "kitpvp": "KitPvP", "rpg": "RPG", "ctf": "CTF", "pve": "PvE",
}

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
    print("  ! No TrueType font found - watermark will use a basic font.")
    return ImageFont.load_default()


def watermark(img):
    """Tile MARK diagonally across the image and burn it in."""
    font = load_font(26)
    pad = int(SIZE * 1.5)                    # room to rotate without bald corners
    layer = Image.new("RGBA", (pad, pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    bbox = d.textbbox((0, 0), MARK, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    step_x, step_y = tw + 70, th + 62

    row, y = 0, 0
    while y < pad:
        # stagger alternate rows so marks interlock instead of forming columns
        x = -tw + (step_x // 2 if row % 2 else 0)
        while x < pad:
            d.text((x, y), MARK, font=font,
                   fill=(255, 255, 255, ALPHA),
                   stroke_width=2, stroke_fill=(0, 0, 0, ALPHA // 2))
            x += step_x
        y += step_y
        row += 1

    layer = layer.rotate(ANGLE, resample=Image.BICUBIC)
    off = (pad - SIZE) // 2
    layer = layer.crop((off, off, off + SIZE, off + SIZE))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def slugify(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()
    return re.sub(r"-{2,}", "-", base)


def guess_name(slug):
    words = []
    for w in slug.split("-"):
        words.append(CASING.get(w.lower(), w.capitalize()))
    return " ".join(words)


def read_existing():
    """Pull {name, type, img} out of the current work.js so manual edits
    to names, types and ordering survive a rebuild."""
    if not os.path.exists(WORK_JS):
        return []
    text = io.open(WORK_JS, encoding="utf-8").read()
    body = text.split("const WORK", 1)[-1]
    entries = []
    pattern = re.compile(
        r"name:\s*'([^']*)'\s*,\s*type:\s*'([^']*)'\s*,\s*img:\s*'([^']*)'",
        re.S)
    for name, typ, img in pattern.findall(body):
        entries.append({"name": name, "type": typ, "img": img})
    return entries


def write_work_js(entries):
    lines = [
        "/* ===================================================================",
        "   THE PORTFOLIO",
        "   ===================================================================",
        "   This file is rebuilt by add-logos.py, but it is safe to edit by hand.",
        "",
        "   TO ADD A LOGO",
        "     1. Put the image in  _originals/",
        "     2. Run:  python add-logos.py",
        "",
        "   Editing here is fine too - change a name, change a type, or drag a",
        "   block up and down to reorder the grid. add-logos.py keeps whatever",
        "   you set the next time it runs.",
        "",
        "   name  - the server name, shown when someone hovers the tile",
        "   type  - the category. If every logo shares one type, the filter",
        "           buttons hide themselves automatically.",
        "   img   - a file in assets/img/work/, or a full https:// link",
        "",
        "   Note: images added by hand to assets/img/work/ are NOT watermarked.",
        "   Only files put through _originals/ and add-logos.py are.",
        "   =================================================================== */",
        "",
        "const WORK = [",
    ]
    for i, e in enumerate(entries):
        lines.append("  {")
        lines.append("    name: '%s'," % e["name"].replace("'", "\\'"))
        lines.append("    type: '%s'," % e["type"].replace("'", "\\'"))
        lines.append("    img:  '%s'" % e["img"].replace("'", "\\'"))
        lines.append("  }" + ("," if i < len(entries) - 1 else ""))
    lines.append("];")
    lines.append("")
    io.open(WORK_JS, "w", encoding="utf-8", newline="\n").write("\n".join(lines))


def main():
    if not os.path.isdir(SRC):
        os.makedirs(SRC, exist_ok=True)
        print("Created " + SRC)
        print("Put your clean logo files in there, then run this again.")
        return 0

    sources = sorted(f for f in os.listdir(SRC)
                     if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")))
    os.makedirs(IMG_DIR, exist_ok=True)

    print("Watermarking %d image(s) from _originals/\n" % len(sources))
    produced = []
    for name in sources:
        try:
            im = Image.open(os.path.join(SRC, name)).convert("RGB")
        except Exception as err:
            print("  ! Skipped %s (%s)" % (name, err))
            continue

        # centre-crop square so every tile in the grid matches
        w, h = im.size
        s = min(w, h)
        im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
        im = im.resize((SIZE, SIZE), Image.LANCZOS)

        out_name = slugify(name) + ".jpg"
        path = os.path.join(IMG_DIR, out_name)
        watermark(im).save(path, "JPEG", quality=QUALITY,
                           optimize=True, progressive=True)
        produced.append(out_name)
        print("  %-28s %4d KB" % (out_name, os.path.getsize(path) // 1024))

    # Rebuild work.js, preserving names/types/order already set by hand
    existing = read_existing()
    kept, seen = [], set()
    for e in existing:
        is_link = e["img"].startswith("http")
        if is_link or os.path.exists(os.path.join(IMG_DIR, e["img"])):
            kept.append(e)
            seen.add(e["img"])

    added = []
    for out_name in produced:
        if out_name not in seen:
            entry = {"name": guess_name(slugify(out_name)),
                     "type": DEFAULT_TYPE, "img": out_name}
            kept.append(entry)
            added.append(entry)

    write_work_js(kept)

    print("\nassets/js/work.js rebuilt - %d logo(s) on the site." % len(kept))
    if added:
        print("\nNew:")
        for e in added:
            print("  + %-24s (named \"%s\")" % (e["img"], e["name"]))
        print("\nIf a name is wrong, edit it in assets/js/work.js - it will stick.")
    print("\nCheck it locally with:  python -m http.server 4321")
    return 0


if __name__ == "__main__":
    sys.exit(main())
