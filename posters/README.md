# @docbeyondthebarbell — wall posters (A3)

Seven A3 posters (297 × 420 mm), alternating light and dark.

| # | File | Theme | Image |
|---|------|-------|-------|
| 01 | `01-tyson` | light | Mike Tyson illustration |
| 02 | `02-strength-is-medicine` | dark | none (vector ECG → barbell artwork) |
| 03 | `03-goggins` | light | David Goggins studio portrait |
| 04 | `04-form-over-comfort` | dark | Arnold, scratchboard art, with anatomy index |
| 05 | `05-bannister` | light | Roger Bannister, 6 May 1954 finish |
| 06 | `06-doctors-orders` | dark | none (prescription pad, signed) |
| 07 | `07-bruce-lee` | light | Bruce Lee ink drawing |

## Files
- `NN-name.svg` — editable source. Images are linked from `images/`, fonts are embedded.
- `export/NN-name.pdf` — print master, A3. **Send these to the print shop.**
- `export/NN-name.png` — 3509 × 4963 px (A3 at 300 dpi). **Open these in Photoshop.**

## Photoshop
- **Retouch / colour-grade:** open the PNG. It is already A3 at 300 ppi.
- **Rebuild from scratch:** File → Open the PDF, choose 300 ppi, Mode RGB (or CMYK if the printer asks).
- Photoshop rasterises SVG and may drop linked images, so use the PNG or PDF, not the SVG.
- For layer-level edits (move text, swap photo), open the SVG in Illustrator or Inkscape. The
  groups are named `photo`, `type`, `header`, `footer`.
- To edit text in Illustrator/Photoshop, first install the free Google Fonts **Anton**, **Inter**
  and **Playfair Display**.

## Printing
- A3, 300 dpi, matte or satin paper. Ask for **no scaling ("actual size")**.
- Keep 16 mm safe margins (already built in). No bleed is included. If the shop wants 3 mm
  bleed, ask them to "fit to bleed", or tell Claude and it will add bleed.

## Rebuilding
```
python3 build.py     # regenerate the SVGs (needs Pillow)
node render.js       # export PDF + PNG (needs Playwright)
```
To swap a photo, replace the file in `images/` with the same name and re-run `node render.js`.

## Image sources (all belong to their creators; for this wall only, do not sell or repost as own work)
- Tyson: pinterest.com/pin/1041950063808316498 (original upload, 2304×4096)
- Goggins: i.pinimg.com/originals/4d/66/e8/4d66e8bbc7c8b5621b4aa9dd62e8a89e.webp (frame cropped)
- Arnold: i.pinimg.com/originals/42/6a/4c/426a4cc15d020ec5f5ce488dcbc51a30.jpg (border cropped)
- Bannister: i.pinimg.com/originals/15/80/1e/15801ee0cabf9e83f5a3599b2455525e.jpg
- Bruce Lee: i.pinimg.com/originals/2f/43/95/2f43950435d1d204b0b8e3a5b9b435db.jpg

## Facts on poster 02 (please have Mohan double-check before printing)
1. Leong DP et al., *The Lancet*, 2015 — PURE study: grip strength vs. all-cause mortality and systolic BP.
2. DeFronzo RA et al., *Diabetes*, 1981 — skeletal muscle takes up most insulin-stimulated glucose.
3. Edwards JJ et al., *Br J Sports Med*, 2023 — network meta-analysis of exercise and resting BP.
