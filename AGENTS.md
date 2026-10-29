# Central graph-separation package

The root `graph-separation.sty` is the only editable implementation. Preserve
the existing public macro names and meanings. The lecturer selected the MIT
License for the package, documentation and workflow on 29 October 2026; retain
its full copyright/permission notice and the historical fixture notices.
The direct-AMS candidate was rejected on 29 October: the lecturer now wants a
consistent length across all seven endpoint variants and more visible original-
style half arrowheads. B2 and its 180-degree rotational symmetry were selected.
The root v3.0.0-rc.2 draft now implements that design. Keep the controlled
`experiments/2026-10-29-length-weight/` specimens as regression references;
the lecturer subsequently authorized the webpage and all released lecture notes
to use this package. AMS is an optical reference, not a
required glyph source. Historical comparisons in `tests/` are fixtures, not
alternative packages for consumers.

Before handover run:

```sh
python3 tools/workflow.py check
python3 tools/workflow.py check-outlines
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/workflow.py build
```

Check native PDFs and the MathJax preview at reading size, enlarged, in scripts
and in print. Use `tools/sync-consumers.py` for hash-pinned course distributions
and generated website downloads. Never hand-edit a consumer's vendor copy.
Read the consumer's instructions and preserve unrelated work before updating it.

The lecturer authorized publishing this draft source and workflow as the public
GitHub repository `causal-design/graph-separation-latex` and placing the local
checkout at `/Users/agents/Workspace/research/graphical-models/graph-separation-latex`.
The package name remains `graph-separation`. Website deployment and lecture-pin
updates are separate from source publication. The direct-AMS candidate is not
accepted. Local generation and synchronization do
not publish. Do not change historical manuscript sources or immutable published
lecture releases when changing the central package.
