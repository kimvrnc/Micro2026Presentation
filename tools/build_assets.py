#!/usr/bin/env python3
"""
Slice the two trifold sheets into six panels and emit web tiers.

Source priority:
  1. web_export/slide1.png + slide2.png  (PowerPoint 600 dpi export - real fonts, native images)
  2. a vector PDF rendered at 600 dpi    (fallback: correct fonts, downsampled images)

Panel map (standard A4 letter-fold imposition):
  outside sheet, L->R:  o1 inside-flap | o2 back cover | o3 FRONT COVER
  inside  sheet, L->R:  i1             | i2            | i3
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "out"
PANELS = OUT / "assets" / "panels"
PANELS.mkdir(parents=True, exist_ok=True)

SRC_PPT = ROOT / "web_export"
SRC_PDF = ROOT / "pdfchk" / "src.pdf"
RENDER = ROOT / "render"
RENDER.mkdir(exist_ok=True)

# width in px, webp quality
TIERS = [("lo", 1100, 85), ("hi", 2340, 82)]

IDS = [["o1", "o2", "o3"], ["i1", "i2", "i3"]]


def source_sheets():
    """Return [page1, page2] as PIL images, plus a label for provenance."""
    a, b = SRC_PPT / "slide1.png", SRC_PPT / "slide2.png"
    if a.exists() and b.exists():
        return [Image.open(a), Image.open(b)], "powerpoint-600dpi"

    # fallback: rasterise the vector PDF at 600 dpi
    made = sorted(RENDER.glob("sheet-*.png"))
    if len(made) != 2:
        subprocess.run(
            ["pdftocairo", "-png", "-r", "600", "-f", "1", "-l", "2",
             str(SRC_PDF), str(RENDER / "sheet")],
            check=True,
        )
        made = sorted(RENDER.glob("sheet-*.png"))
    return [Image.open(p) for p in made], "pdf-600dpi"


def main():
    sheets, provenance = source_sheets()
    manifest = {"source": provenance, "panels": {}}

    for sheet_idx, sheet in enumerate(sheets):
        sheet = sheet.convert("RGB")
        W, H = sheet.size
        print(f"sheet {sheet_idx + 1}: {W}x{H}  ({provenance})")

        for col in range(3):
            pid = IDS[sheet_idx][col]
            x0 = round(col * W / 3)
            x1 = round((col + 1) * W / 3)
            panel = sheet.crop((x0, 0, x1, H))

            entry = {"w": panel.width, "h": panel.height, "tiers": {}}
            for name, target_w, q in TIERS:
                tw = min(target_w, panel.width)
                th = round(panel.height * tw / panel.width)
                im = panel.resize((tw, th), Image.LANCZOS)
                path = PANELS / f"{pid}-{name}.webp"
                im.save(path, "WEBP", quality=q, method=6)
                kb = path.stat().st_size / 1024
                entry["tiers"][name] = {"w": tw, "h": th, "kb": round(kb, 1)}
                print(f"  {pid}-{name}.webp  {tw}x{th}  {kb:.0f} KB")
            manifest["panels"][pid] = entry

    # social preview: front cover on a warm card
    cover = Image.open(PANELS / "o3-hi.webp").convert("RGB")
    og = Image.new("RGB", (1200, 630), (28, 26, 24))
    ch = 560
    cw = round(cover.width * ch / cover.height)
    og.paste(cover.resize((cw, ch), Image.LANCZOS), ((1200 - cw) // 2, 35))
    og.save(OUT / "assets" / "og.png", "PNG")
    print(f"og.png  {og.size}")

    (OUT / "assets" / "manifest.json").write_text(json.dumps(manifest, indent=2))
    total = sum(p.stat().st_size for p in PANELS.glob("*.webp")) / 1024 / 1024
    lo = sum(p.stat().st_size for p in PANELS.glob("*-lo.webp")) / 1024 / 1024
    print(f"\ntotal panels {total:.1f} MB   (initial load: {lo:.1f} MB)")


if __name__ == "__main__":
    main()
