#!/usr/bin/env python3
"""
Turn the talk's 3840 px slide renders into web tiers.

  thumb  320 px  - the strip along the bottom
  view  1920 px  - what you look at
  hi    3840 px  - native, loaded only when someone zooms

Also copies the slides-only PDF and writes a manifest with the slide titles.
"""
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "out"
SRC = ROOT / "web_export" / "talk"
DST = OUT / "assets" / "talk"
DST.mkdir(parents=True, exist_ok=True)

TIERS = [("th", 320, 76), ("view", 1920, 82), ("hi", 3840, 80)]


def main():
    slides = sorted(SRC.glob("slide*.png"))
    if not slides:
        sys.exit(f"no slide renders in {SRC}")

    titles = {}
    tf = ROOT / "web_export" / "slide_titles.json"
    if tf.exists():
        titles = {int(r["n"]): r["title"] for r in json.loads(tf.read_text())}

    manifest = {"count": len(slides), "slides": []}
    total = 0

    for idx, p in enumerate(slides, 1):
        im = Image.open(p).convert("RGB")
        entry = {"n": idx, "title": titles.get(idx, ""), "w": im.width, "h": im.height}
        for name, target_w, q in TIERS:
            tw = min(target_w, im.width)
            th = round(im.height * tw / im.width)
            out = DST / f"s{idx:02d}-{name}.webp"
            im.resize((tw, th), Image.LANCZOS).save(out, "WEBP", quality=q, method=5)
            kb = out.stat().st_size / 1024
            total += kb
            entry[name] = round(kb, 1)
        manifest["slides"].append(entry)
        print(f"  s{idx:02d}  {im.width}x{im.height}  "
              f"th {entry['th']:.0f}K  view {entry['view']:.0f}K  hi {entry['hi']:.0f}K  "
              f"{entry['title'][:46]}")

    pdf = ROOT / "web_export" / "Micro2026_talk.pdf"
    if pdf.exists():
        shutil.copy(pdf, DST / "Micro2026_talk.pdf")
        manifest["pdf_mb"] = round(pdf.stat().st_size / 1048576, 1)
        print(f"\n  Micro2026_talk.pdf  {manifest['pdf_mb']} MB")
    else:
        print("\n  (no talk PDF found)")

    (DST / "manifest.json").write_text(json.dumps(manifest, indent=1))

    th = sum(s["th"] for s in manifest["slides"]) / 1024
    view = sum(s["view"] for s in manifest["slides"]) / 1024
    hi = sum(s["hi"] for s in manifest["slides"]) / 1024
    print(f"\n  thumbs {th:.1f} MB | view {view:.1f} MB | hi {hi:.1f} MB "
          f"| total {total/1024:.1f} MB")

    # JS literal for the page, so the deck needs no extra fetch
    js = ",".join(
        json.dumps([s["n"], s["title"]], ensure_ascii=False)
        for s in manifest["slides"]
    )
    (OUT / "assets" / "talk" / "titles.js").write_text(
        "window.__TALK=[" + js + "];\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
