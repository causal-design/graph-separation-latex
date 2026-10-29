# graph-separation

LaTeX notation for graph edges, walks, connections and separations, by Qingyuan
Zhao. **Draft version 3.0.0-rc.2, 29 October 2026.** The lecturer selected design
B2 and its 180-degree rotational symmetry. The former direct-AMS draft is
superseded. The source and local workflow are maintained at
[causal-design/graph-separation-latex](https://github.com/causal-design/graph-separation-latex).
Website downloads and lecture consumers use deliberately generated, hash-pinned
copies of this source; they are not independently maintained implementations.

## Installation and usage

Place `graph-separation.sty` beside your `.tex` file (or upload it into your
Overleaf project), then add:

```tex
\usepackage{graph-separation}
```

Use commands in math mode:

```tex
V_j\rdpath V_k \qquad V_j\mconnarc V_k
\qquad V_j\dconnarc V_k \qquad V_j\trek V_k
```

The illustrated **[installation, design and usage guide](graph-separation.pdf)**
is included in the repository and draft bundle; its editable source is
`graph-separation.tex`. It includes
all 46 public commands, negations, aliases, compound relations, small styles,
shared TEXMF installation and compatibility limits. A standalone test document
is `examples/minimal.tex`.

Dependencies: `amsmath`, `amssymb`, TikZ/PGF, `adjustbox`, `centernot`. Standard
TeX Live/MiKTeX distributions provide these. No shell escape or paid service is
needed. The draft targets pdfLaTeX, LuaLaTeX and XeLaTeX with traditional LaTeX
math; `unicode-math`, arbitrary replacement math fonts and automatic bold-symbol
behaviour are not qualified.

## B2 design

At a 10 pt reference math size, all seven squiggle variants have a 13.18785 pt
span and a 0.45 pt body stroke. Two triangular cycles have 0.8 pt amplitude, and
the original-style full/half heads retain a 1 mm length. Separate 3.2 pt endpoint
stubs prevent arrowheads from changing the wave. Dimensions scale with the
active math-symbol font quad and align to its mathematical axis.

The body is rotationally, not mirror, symmetric. Unheaded, full/full and half/half
glyphs rotate into themselves; right/left and half/full versus full/half rotate
into their counterparts. Labels remain upright. Straight primitives retain the
published v2.0 length, 0.5 pt stroke and fixed-size behaviour. They are not changed
to the new squiggle length. All public names and mathematical meanings are kept.

## Local workflow

Requires Python 3.9+ and TeX Live; documentation uses `geometry`, `longtable` and
`hyperref`, and native SVG export additionally uses `standalone` and `dvisvgm`.
On macOS the tools also check `/Library/TeX/texbin`.

```sh
python3 tools/workflow.py check
python3 tools/workflow.py check-outlines
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/workflow.py build
python3 tools/workflow.py export-mathjax
python3 tools/package-draft.py
```

`check` exercises all 46 commands in all four styles at 10 pt with three engines,
and checks common primitive box dimensions at 10, 11 and 12 pt. Straight relations
are checked against their legacy drawing. `check-outlines` verifies that 28
production SVGs exactly reproduce the selected B2 specimen across four styles.
The archived investigation also independently checked reference-size ink extents.
These checks supplement reading-size and print inspection; they are not an
automatic aesthetic score.

`build` creates the illustrated guide and comparison PDFs under ignored `build/`.
`export-mathjax` creates self-contained SVG macros with measured advances and
baselines, using a separate render for each math style. Original macro names stay
in editable equations. The optional browser tests in `tests/browser.cjs` use an
external Playwright installation. Preview servers are optional and should be
stopped after use.

`package-draft.py` builds a local ZIP with the style file, guide/source, minimal
example, licence, reproducible workflow and regression sources. It does not upload.

## One implementation, deliberate consumer updates

The root `.sty` is canonical. Do not edit website downloads or course vendor
copies independently. After review, use `tools/sync-consumers.py --course PATH`
and the course's header builder to update its hash-pinned offline distribution;
use `--website PATH` for generated website downloads. These are separate actions,
not part of drafting. Preserve immutable published lecture releases.

Webpage deployment and lecture-consumer updates remain separate actions.

## Licence

The package, documentation and local workflow are released under the
[MIT License](LICENSE), copyright Qingyuan Zhao. Retain the copyright and
permission notice when redistributing. Historical comparison fixtures retain
their original notices.
