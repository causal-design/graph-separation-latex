# Length and stroke-weight investigation

This is a separate, unpublished experiment following the lecturer's 29 October
rejection of direct AMS glyph reuse. It does not replace the canonical `.sty`,
lecture-note pins or website downloads.

## Controlled variables

| Row | Endpoint span at 10 pt | Compared with the old 0.515 cm path |
| --- | --- | --- |
| A | 14.65 pt | 100% |
| B | 13.19 pt | 90% |
| C | 11.72 pt | 80% |

Columns 1, 2 and 3 use 0.4, 0.45 and 0.5 pt stroke respectively. At each setting
all seven squiggle variants have a common body, intended ink span and TeX box.
The old package's boxes themselves were not identical across endpoint types;
the row percentages refer to its nominal path span, not every old ink extent.

Hold these fixed for this first pass:

- Two complete triangular waves with 0.8 pt amplitude at the reference size.
- Original `Classical TikZ Rightarrow` full/half-head construction, with 1 mm
  head length. Its native arrow pen follows the chosen stroke weight.
- A 3.2 pt straight clearance at each end. Heads are placed on those stubs;
  adding them cannot shorten or rephase the common wave.
- Mathematical-axis alignment, with proportional text/script/script-script sizing.

Changing length compresses the same wave horizontally. Wavelength therefore
changes, but amplitude, cycle count and head dimensions do not. This is deliberate:
it avoids a decoration algorithm silently adding/removing bends between probes.
The subsequent shape pass can adjust cycle count, amplitude and clearances.

## Build and inspect

From the repository root:

```sh
python3 experiments/2026-10-29-length-weight/build.py
python3 experiments/2026-10-29-length-weight/render_specimens.py
```

The first command uses the existing standard-library workflow and TeX installation.
The second requires PyMuPDF (`fitz`) in the Python environment; it renders files,
not a web server. Outputs are under `build/length-weight-20261029/`:

- `specimen.pdf`: overview plus three middle-weight context pages (A2/B2/C2).
- `grid.png`: native-LaTeX overview for chat; no invented browser-drawn symbols.
- `measurements.json`: 2,268 primitive boxes checked across three engines,
  three text sizes and four math styles. All seven boxes must agree per setting.
- `ink-measurements.json`: independent PDF raster measurements of all 63
  reference-size glyphs, including arrowhead ink; widths agree within one
  raster pixel, approximately 0.05 pt. The common vector body is also checked.

The context pages include labels, negations, compound connections and subscripts,
alongside the old v2.0 glyphs and enlarged shape comparisons. Inspect at normal
print size first; enlarged views are for shape, not for choosing stroke weight.
The 0.45 pt pages are a controlled cross-length comparison, not a selected winner.

## Initial visual assessment

B2 (13.19 pt, 0.45 pt) is a provisional starting point: it is less expansive than
the old span, with clear original-style half-heads. C is visibly more compressed
between the fixed-size heads; A keeps more room but takes more inline space.
The weight decision remains open: compare B1/B2/B3 at reading size before
choosing. These judgments are not consequences of the dimensional checks.

The lecturer subsequently selected B2 and its rotational symmetry. The root
package now implements it as v3.0.0-rc.2, with a draft illustrated guide and local
ZIP. This investigation remains the regression reference. No consumer has been
synchronized to rc.2. The draft source and reproducible workflow are published
separately in `causal-design/graph-separation-latex`; website deployment is separate.
