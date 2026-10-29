"""Build a controlled, unpublished length/weight experiment. No server required."""

from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "build/length-weight-20261029"
spec = importlib.util.spec_from_file_location("workflow", ROOT / "tools/workflow.py")
workflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)
NAMES = ["nosquigno", "nosquigfull", "fullsquigno", "halfsquighalf",
         "halfsquigfull", "fullsquighalf", "fullsquigfull"]
BASE_PT = .515 * 72.27 / 2.54
CANDIDATES = [
    {"id": f"{letter}{column}", "length_pt": BASE_PT * factor,
     "length_em": BASE_PT * factor / 10, "weight_pt": weight, "weight_em": weight / 10}
    for letter, factor in [("A", 1), ("B", .9), ("C", .8)]
    for column, weight in [(1, .4), (2, .45), (3, .5)]
]


def selection(candidate):
    return rf"\gspSelect{{{candidate['length_em']:.9f}}}{{{candidate['weight_em']:.9f}}}"


def preamble():
    return (r"\documentclass[10pt]{article}" + "\n"
            r"\usepackage[a4paper,margin=18mm]{geometry}" + "\n"
            r"\usepackage[T1]{fontenc}\usepackage{graph-separation}" + "\n"
            + r"\input{" + str(HERE / "probes.tex") + "}\n"
            + r"\input{" + str(OUT / "old-v2.0.tex") + "}\n"
            + r"\setlength{\parindent}{0pt}\pagestyle{plain}" + "\n")


def family():
    return (r"$\nosquigno\quad\nosquigfull\quad\fullsquigno\quad\halfsquighalf$"
            + r"\par\smallskip $\halfsquigfull\quad\fullsquighalf\quad\fullsquigfull$")


def specimen():
    body = [preamble(), r"\begin{document}", r"\section*{Squiggles: length and weight}",
            r"A controlled first pass, not a release. All seven variants in each cell have",
            r"the same intended ink span and advance width. Heads retain the old TikZ",
            r"shape and 1\,mm length; wave height (0.8\,pt) and two-cycle topology are fixed.",
            r"Lengths are nominal endpoint spans, not the old file's differing bounding boxes.",
            r"\par\medskip",
            r"\textbf{Previous website v2.0, 0.5\,pt stroke:}\par\smallskip",
            r"$\oldbare\quad\oldright\quad\oldleft\quad\oldhalfhalf\quad"
            r"\oldhalffull\quad\oldfullhalf\quad\oldfullfull$",
            r"\par\medskip AMS for weight/context only: $A\rightsquigarrow B\quad "
            r"A\leftrightsquigarrow B\quad A\to B\quad A=B$.",
            r"\par\medskip Rows A/B/C retain 100\%/90\%/80\% of the old 0.515\,cm path span.",
            r"Columns 1/2/3 use 0.4/0.45/0.5\,pt stroke at the 10\,pt reference size.",
            r"\par\smallskip Each cell: no heads, right, left, half/half; then half/full, full/half, full/full.",
            r"\par\bigskip"]
    for index, candidate in enumerate(CANDIDATES):
        body.extend([r"\begin{minipage}[t]{.31\linewidth}", selection(candidate),
                     r"\textbf{" + candidate["id"] + "}: "
                     + f"{candidate['length_pt']:.2f}\\,pt / {candidate['weight_pt']:.2f}\\,pt"
                     + r"\par\medskip", family(), r"\par\medskip",
                     r"$V_j\rdpath V_k\quad V_j\mconnarc V_k$", r"\end{minipage}"])
        body.append(r"\par\vspace{16pt}" if index % 3 == 2 else r"\hfill")
    body.extend([r"\textbf{How to judge:} compare length down a column, weight across a row.",
                 r"Read at normal size first. Half and full heads should be immediately",
                 r"distinguishable without the relation overwhelming its variables.",
                 r"\par\medskip The following pages inspect the three middle-weight candidates",
                 r"in context. This does not select 0.45\,pt as the winner."])
    for candidate in CANDIDATES:
        if not candidate["id"].endswith("2"):
            continue
        body.extend([r"\newpage", selection(candidate),
                     r"\section*{" + candidate["id"] + ": "
                     + f"{candidate['length_pt']:.2f}\\,pt span, 0.45\\,pt stroke}}",
                     r"\subsection*{All seven endpoint variants}",
                     r"\begin{tabular}{lll}Endpoint & Proposed & Previous v2.0\\[7pt]"])
        for label, name, old in zip(
                ["None", "Right", "Left", "Half/half", "Half/full", "Full/half", "Full/full"],
                NAMES, ["oldbare", "oldright", "oldleft", "oldhalfhalf", "oldhalffull", "oldfullhalf", "oldfullfull"]):
            body.append(label + " & $V_j\\" + name + " V_k$ & $V_j\\" + old + r" V_k$\\[7pt]")
        body.extend([r"\end{tabular}", r"\subsection*{In text, labels and negations}",
                     r"Compare $A\rdpath B$, $A\mconnarc B$, $A\dconnarc B$ and $A\trek B$",
                     r"beside $A\to B$ and $A=B$. These symbols should remain legible in a sentence.",
                     r"\[V_j\rdpath V_k\qquad V_j\mconnarc V_k\qquad V_j\dconnarc V_k\qquad V_j\trek V_k.\]",
                     r"\[A\nordpath B\quad A\nomconnarc B\quad A\nodconnarc B\quad A\notrek B.\]",
                     r"\subsection*{Compound connections and smaller styles}",
                     r"\[A\mconn B\qquad A\dconn B\qquad A\tconn B.\]",
                     r"\[X_{A\rdpath B}\quad X_{A\mconnarc B}\quad X_{A\dconnarc B}\quad X_{A\trek B}\]",
                     r"\[X_{Y_{A\rdpath B}}\quad X_{Y_{A\mconnarc B}}\quad X_{Y_{A\dconnarc B}}\quad X_{Y_{A\trek B}}\]",
                     r"\subsection*{Enlarged shape check (not a weight judgment)}",
                     r"Old:\quad\scalebox{3}{$\oldright\quad\oldhalfhalf\quad\oldfullfull$}",
                     r"\par\bigskip New:\quad\scalebox{3}{$\nosquigfull\quad\halfsquighalf\quad\fullsquigfull$}"])
    body.append(r"\end{document}")
    return "\n".join(body)


def check_engine(engine):
    body = [preamble(), r"\newsavebox{\probe}\begin{document}"]
    for candidate in CANDIDATES:
        body.append(selection(candidate))
        for size in [10, 11, 12]:
            body.append(r"\fontsize{" + str(size) + r"}{14}\selectfont")
            for style, (tex_style, _) in workflow.STYLES.items():
                for name in NAMES:
                    key = f"{candidate['id']}-{size}-{style}-{name}"
                    body.append(r"\sbox{\probe}{$" + tex_style + "\\" + name + r"$}%")
                    body.append(r"\typeout{PROBE " + key
                                + r": \the\wd\probe,\the\ht\probe,\the\dp\probe}")
    body.append(r"\end{document}")
    log = workflow.compile_tex("\n".join(body), OUT / "checks" / engine, engine)
    metrics = {name: [float(v) for v in values] for name, *values in re.findall(
        r"PROBE ([\w-]+): (-?[\d.]+)pt,(-?[\d.]+)pt,(-?[\d.]+)pt", log)}
    assert len(metrics) == len(CANDIDATES) * 3 * 4 * len(NAMES), len(metrics)
    for candidate in CANDIDATES:
        for size in [10, 11, 12]:
            for style in workflow.STYLES:
                values = [metrics[f"{candidate['id']}-{size}-{style}-{name}"] for name in NAMES]
                assert all(max(column) - min(column) < .0002 for column in zip(*values))
    return engine, {"boxes": len(metrics), "all_seven_boxes_equal": True, "metrics": metrics}


def ink_sheet():
    body = [r"\documentclass[10pt,border=2pt,multi=probe]{standalone}",
            r"\usepackage{graph-separation}", r"\input{" + str(HERE / "probes.tex") + "}",
            r"\newenvironment{probe}{}{}\begin{document}"]
    for candidate in CANDIDATES:
        body.append(selection(candidate))
        for name in NAMES:
            body.append(r"\begin{probe}$" + "\\" + name + r"$\end{probe}")
    body.append(r"\end{document}")
    workflow.compile_tex("\n".join(body), OUT / "ink", "pdflatex")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fixture = (ROOT / "tests/legacy-primitives.tex").read_text().replace("0.4pt", "0.5pt")
    (OUT / "old-v2.0.tex").write_text(fixture)
    workflow.compile_tex(specimen(), OUT / "specimen")
    shutil.copy2(OUT / "specimen/document.pdf", OUT / "specimen.pdf")
    with ThreadPoolExecutor(max_workers=3) as pool:
        checks = dict(pool.map(check_engine, ["pdflatex", "lualatex", "xelatex"]))
    ink_sheet()
    receipt = {"candidates": CANDIDATES, "engines": checks,
               "fixed": {"wave_amplitude_pt": .8, "wave_cycles": 2,
                         "head_length_mm": 1, "endpoint_guard_pt": 3.2},
               "canonical_style_sha256": workflow.digest(ROOT / "graph-separation.sty"),
               "probe_source_sha256": workflow.digest(HERE / "probes.tex"),
               "builder_sha256": workflow.digest(Path(__file__)),
               "specimen_sha256": workflow.digest(OUT / "specimen.pdf"),
               "published": False, "consumers_changed": False}
    (OUT / "measurements.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Built {OUT / 'specimen.pdf'}")
    print(f"Verified {sum(c['boxes'] for c in checks.values())} boxes across 3 engines.")
    print("Ink sheet ready for independent raster measurement: " + str(OUT / "ink/document.pdf"))


if __name__ == "__main__":
    main()
