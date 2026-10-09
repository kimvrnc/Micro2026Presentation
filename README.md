# Micro2026 — Take-Home Flyer

An unfoldable, shareable version of the Micro2026 trifold flyer:

**Towards Validated SWIR Hyperspectral Methods for Small Microplastic (≤100 µm) Detection in Water Filtration Samples: Challenges and Perspectives**
M. Barbaresi, G. Gorla\*, E. Martinelli, K. Ranoco\*\*\*, J. M. Amigo, A. de Diego, J. A. Carrero, M. Mattarozzi, M. Careri

**Live:** https://kimvrnc.github.io/Micro2026Presentation/

The page shows the flyer as a real sheet of paper. The front cover swings open,
then the tucked flap unfolds, exactly as the printed trifold does. Any panel can
be opened at full resolution for reading.

* Drag sideways, scroll, or use the slider to fold and unfold
* Tap or click a panel to read it at 600 dpi, with zoom and pan
* The turn-over button shows the other side of the sheet at any fold angle
* Keyboard: `←` `→` fold · `F` turn over · `R` read · `Esc` close

## Panel map

The source is a two-slide A4 landscape deck (29.7 × 21 cm) using the standard
letter-fold imposition — equal thirds of 9.9 cm:

| Sheet | Left | Middle | Right |
|---|---|---|---|
| Slide 1 — outside | `o1` inside flap (SWIR-HSI Analysis) | `o2` back cover (Summary of Decisions) | `o3` **front cover** |
| Slide 2 — inside | `i1` One Pixel ≠ One Pure Spectrum | `i2` No Single Preprocessing Recipe | `i3` Pixel ≠ Particle |

Folded, the left third carries the front cover over the middle, and the right
third tucks the flap underneath it. That is why the cover opens first and the
flap second.

## Why the images are sharp

The panels are cut from a **600 dpi export made by PowerPoint itself**, with
automatic picture compression switched off, so the embedded figures keep their
native resolution (up to 2880 px) and the text is set in the real fonts —
Ebrima, Segoe Print, Gill Sans Nova Cond — which only exist on the authoring
machine.

A PDF exported from PowerPoint with default settings downsamples every figure to
roughly 200 dpi; that is the clarity loss this version avoids.

Each panel ships in two tiers: a light one that drives the fold animation, and a
600 dpi one loaded on demand for the reader.

## Rebuilding the assets

1. Run `export_web.ps1` (in the flyer's working folder) on the Windows machine
   that has the `.pptx`. It disables picture compression and exports
   `slide1.png` / `slide2.png` at 7016 × 4961 plus a vector PDF.
2. Run `build_assets.py` pointing at that `web_export` folder. It slices each
   sheet into equal thirds and writes the WebP tiers into `assets/panels/`.

Both scripts are kept in `tools/`.
