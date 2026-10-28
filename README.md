# graph-separation

LaTeX notation for graph edges, walks, connections and separations, by Qingyuan
Zhao. The package name and all 46 existing public commands are unchanged.

**Current version: 3.0.0-rc.1, for visual review.** Nothing in the local workflow
uploads files, updates a live website or changes an existing lecture release.

## Install

Put `graph-separation.sty` beside your document and use:

```tex
\usepackage{graph-separation}
```

Dependencies: `amsmath`, `amssymb`, TikZ/PGF, `adjustbox`, `centernot`. These are
available in standard TeX Live and MiKTeX installations. This candidate is tested
with pdfLaTeX, LuaLaTeX and XeLaTeX using traditional AMS math fonts. It does not
claim support for `unicode-math` or replacement AMS symbol fonts.

## What changed

- Full right and bidirectional squiggles **are** `\rightsquigarrow` and
  `\leftrightsquigarrow`; the left squiggle reflects the former.
- Half arrowheads are clipped from the same AMS glyphs, preserving the original
  half-head orientations. The unheaded variant removes the head and extends the
  native horizontal stem without changing its thickness.
- One-ended/unheaded squiggles have the one-ended AMS width. Two-ended squiggles
  have the two-ended AMS width. At 10 pt these are 10 pt and about 13.9 pt.
- Script and script-script use the AMS optical sizes, not a scaled 10 pt picture.
- Straight relations retain the published website/course v2.0 drawing, including
  its 0.5 pt stroke. The research v2.1 copy's 0.4 pt change is not applied to them.
- Labels, negations, aliases and compound-relation names are retained.

See `graph-separation.tex` for the complete command table and
`tests/comparison.tex` for AMS comparisons and archival v2.1 squiggles.

## Reproduce locally

Requires Python 3.9+, TeX Live (including `standalone`, `geometry`, and the package
dependencies above), and `dvisvgm`. No paid models, shell escape or cloud service
are used. On macOS the workflow also checks `/Library/TeX/texbin` for executables.

```sh
python3 tools/workflow.py check
python3 tools/workflow.py check-outlines
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/workflow.py build
python3 tools/workflow.py export-mathjax
```

`check` compiles every command in all four math styles at 10, 11 and 12 pt with
each engine, checks 252 primitive/native AMS and nine legacy-straight box
comparisons, and fails if the
central source was not actually loaded. Missing engines are failures, not skips.
`build` writes the example and two-page comparison PDFs to `build/`.
`check-outlines` verifies 28 native AMS outline comparisons, including eight
byte-identical full-arrow SVGs. The fast unit tests cover API compatibility and
safe consumer synchronization.
Generated files and machine-specific logs are not source files.

### Native SVGs for MathJax

```sh
python3 tools/workflow.py export-mathjax \
  --output build/graph-separation.html \
  --mathjax-js /path/to/local/tex-svg-full.js
python3 -m http.server 8766 --bind 127.0.0.1 --directory build
```

Open `http://127.0.0.1:8766/preview/`. The MathJax script is copied only into the
ignored build directory; the preview then works offline. The generated header is
self-contained and uses native LaTeX/dvisvgm SVGs in `mglyph` tokens. A
`\mathchoice` selects the appropriate optical size. `--macros NAME ...` selects
additional commands; the default covers the seven current course relations.

The exporter preserves native advance widths, sidebearings and baselines. It
adds a transparent top guard of 0.06 of the design size because AMS arrowhead ink
protrudes beyond its declared TFM height. It records native and image metrics
separately and rejects an unexpected width/height. Tight cropping is deliberately
not used: it loses sidebearings and is unreliable for reflected/clipped TeX boxes.

Optional browser checks need an external Playwright installation and Chromium:

```sh
node tests/browser.cjs
```

Use `PLAYWRIGHT_MODULE` for a non-default installation and `CHROME_EXECUTABLE`
or `CHROME_CHANNEL` for an existing browser. The test checks desktop/mobile
layout, MathJax errors, successful SVG-image loads and print output. The test page
must be running at the address above (override with `REVIEW_URL`).

## One source, pinned consumers

Edit the root `.sty`, never a website download or course vendor copy. Update local
consumers deliberately:

```sh
python3 tools/sync-consumers.py --course /path/to/causal-inference
python3 /path/to/causal-inference/tools/build-graph-macros.py
python3 /path/to/causal-inference/tools/build-graph-macros.py --check

python3 tools/workflow.py build
python3 tools/sync-consumers.py --website /path/to/website
```

The course gets an offline, hash-pinned distribution of the central source,
licence and SVG generator, not a separate maintained implementation. Its lock
file records the version and all hashes; locally edited vendor files cannot be
silently overwritten. The collection builder rejects stale/mismatched headers.
The historical book reference copy, canonical teaching text and immutable released
notes remain unchanged. New private renders use the pinned central symbols.

The website gets generated `.sty`, `.tex` and example `.pdf` downloads plus a
release manifest outside its published tree. Synchronization does **not** publish.
After visual approval, publish this repository first, update its release pins,
then deploy the reviewed website changes using the website's normal safeguards.
Already published lecture releases require a separate release action.

## Licence

The original permissive notice is retained in `LICENSE` and the package.
AMS glyphs come from the installed AMSFonts, licensed under SIL OFL 1.1; the font
files themselves are not redistributed here.
