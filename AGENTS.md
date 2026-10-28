# Central graph-separation package

The root `graph-separation.sty` is the only editable implementation. Preserve
the existing public macro names, meanings and original permissive licence.
Use actual AMS glyphs for squiggles; see `README.md` for endpoint derivations,
optical sizes and SVG overhang handling. Historical comparisons in `tests/` are
fixtures, not alternative packages for consumers.

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

The current v3 candidate is awaiting the lecturer's visual approval before public
GitHub upload and website deployment. Local generation and synchronization do
not publish. Do not change historical manuscript sources or immutable published
lecture releases when changing the central package.
