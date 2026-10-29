"""Local, standard-library-only build/test/MathJax workflow for graph-separation."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import base64
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "graph-separation.sty"
BUILD = ROOT / "build"
VERSION = re.search(r"\\ProvidesPackage\{graph-separation\}\[[^\]]* v([^\s]+)",
                    STYLE.read_text()).group(1)
DEFAULT_MACROS = ["ldpath", "rdpath", "mconnarc", "dconnarc", "trek", "colliderconn", "mconn"]
STYLES = {"display": (r"\displaystyle", 10), "text": (r"\textstyle", 10),
          "script": (r"\scriptstyle", 7), "scriptscript": (r"\scriptscriptstyle", 5)}
NOTICE = ("Copyright 2024, 2026 by Qingyuan Zhao (qyzhao@statslab.cam.ac.uk).\n"
          "These macros may be freely used, transmitted, reproduced, or modified\n"
          "provided that the copyright notice and this permission is retained.")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def executable(name):
    found = shutil.which(name)
    if not found:
        fallback = Path("/Library/TeX/texbin") / name
        if fallback.is_file():
            found = str(fallback)
    if not found:
        raise RuntimeError(f"Required executable not found: {name}")
    return found


def public_macros():
    return re.findall(r"\\newcommand\s*\{?\\([A-Za-z]+)(?=[}\s{])", STYLE.read_text())


def run(command, work):
    env = dict(os.environ, TEXINPUTS=str(ROOT) + os.pathsep + os.environ.get("TEXINPUTS", ""))
    result = subprocess.run(command, cwd=work, env=env, text=True,
                            capture_output=True, timeout=180)
    log = work / (Path(command[0]).name + "-output.txt")
    log.write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f"Command failed; inspect {log}\n{result.stdout[-2000:]}")
    return result.stdout + result.stderr


def compile_tex(source, work, engine="pdflatex"):
    work.mkdir(parents=True, exist_ok=True)
    # Keep the explicit dvisvgm driver before TikZ is loaded for DVI exports.
    document = work / "document.tex"
    document.write_text(source)
    run([executable(engine), "-no-shell-escape", "-interaction=nonstopmode",
         "-halt-on-error", "-recorder", str(document)], work)
    log = (work / "document.log").read_text()
    for marker in ["Overfull", "Missing character:", "Undefined control sequence"]:
        if marker in log:
            raise ValueError(f"{marker}: inspect {work / 'document.log'}")
    # Ensure a system-installed or stale copy never shadows the central source.
    inputs = (work / "document.fls").read_text()
    if str(STYLE) not in inputs:
        raise ValueError("TeX did not load the central graph-separation.sty")
    return log


def check(engines=None):
    report = {}
    for engine in (engines or ["pdflatex", "lualatex", "xelatex"]):
        executable(engine)  # Missing engines are explicit failures, not silent skips.
        body = [r"\documentclass{article}\usepackage{graph-separation}",
                r"\input{tests/legacy-primitives.tex}",
                r"\newsavebox{\probe}", r"\begin{document}"]
        expected = {}
        primitives = {
            "nosquigno": "nosquigno", "nosquigfull": "nosquigno",
            "fullsquigno": "nosquigno", "halfsquighalf": "nosquigno",
            "halfsquigfull": "nosquigno", "fullsquighalf": "nosquigno",
            "fullsquigfull": "nosquigno",
        }
        for size in [10, 11, 12]:
            body.append(r"\fontsize{" + str(size) + "}{14}\\selectfont")
            for style, (tex_style, _) in STYLES.items():
                for name in [*primitives, "rightsquigarrow", "leftrightsquigarrow"]:
                    key = f"{size}-{style}-{name}"
                    body.append(r"\sbox{\probe}{$" + tex_style + "\\" + name + r"$}%")
                    body.append(r"\typeout{GS " + key
                                + r": \the\wd\probe,\the\ht\probe,\the\dp\probe}")
                    if name in primitives:
                        expected[key] = f"{size}-{style}-{primitives[name]}"
                # Exercise every public command in all four styles at each size.
                for name in public_macros():
                    if size == 10:
                        body.append(r"\sbox{\probe}{$" + tex_style + " A\\" + name + " B$}")
        # Preserve the published 0.5pt straight primitive, including its box.
        for name, tips in [("nostraigno", "-"),
                           ("nostraigfull", "-{Classical TikZ Rightarrow[length=1mm]}"),
                           ("fullstraigno", "{Classical TikZ Rightarrow[length=1mm]}-")]:
            body.append("\\sbox{\\probe}{$\\" + name + r"$}%")
            body.append(r"\typeout{GS " + name + r": \the\wd\probe,\the\ht\probe,\the\dp\probe}")
            body.append(r"\sbox{\probe}{$\mathrel{\adjustbox{valign=c}{\begin{tikzpicture}"
                        + r"\draw[line width=0.5pt," + tips + r"] (0,0) -- (0.515,0);"
                        + r"\end{tikzpicture}}}$}%")
            body.append(r"\typeout{GS old-" + name + r": \the\wd\probe,\the\ht\probe,\the\dp\probe}")
            expected[name] = "old-" + name
        # All B2 endpoint variants share their complete box in every math style.
        body.append(r"\end{document}")
        work = BUILD / "checks" / engine
        log = compile_tex("\n".join(body), work, engine)
        metrics = {name: [float(v) for v in values]
                   for name, *values in re.findall(
                       r"GS ([\w-]+): (-?[\d.]+)pt,(-?[\d.]+)pt,(-?[\d.]+)pt", log)}
        for actual, reference in expected.items():
            if any(abs(a - b) > .0002 for a, b in zip(metrics[actual], metrics[reference])):
                raise AssertionError((engine, actual, metrics[actual], metrics[reference]))
        report[engine] = {"metric_comparisons": len(expected),
                          "public_macros": len(public_macros()), "metrics": metrics}
    path = BUILD / "checks" / ("report.json" if engines is None else engines[0] + "-report.json")
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(report)} engine(s), {len(public_macros())} public macros, "
          f"{sum(r['metric_comparisons'] for r in report.values())} box comparisons")
    return report


def check_all():
    with ThreadPoolExecutor(max_workers=3) as pool:
        reports = list(pool.map(lambda engine: check([engine]), ["pdflatex", "lualatex", "xelatex"]))
    report = {engine: result for entry in reports for engine, result in entry.items()}
    (BUILD / "checks/report.json").write_text(json.dumps({
        "source_sha256": digest(STYLE), "engines": report}, indent=2) + "\n")


def check_outlines():
    """The production primitives must reproduce the selected B2 experiment."""
    count = 0
    for style in STYLES:
        for name in ["nosquigno", "nosquigfull", "fullsquigno", "halfsquighalf",
                     "halfsquigfull", "fullsquighalf", "fullsquigfull"]:
            work = BUILD / "outline-checks" / style / name
            _, metric = render_glyph(name, style, work)
            reference = (r"\input{" + str(ROOT / "experiments/2026-10-29-length-weight/probes.tex")
                         + "}\n" + r"\gspSelect{1.318785236}{0.045000000}" + "\n")
            _, expected = render_glyph(name, style, work / "selected-b2", reference)
            assert metric["svg_sha256"] == expected["svg_sha256"], (style, name, "B2 drawing changed")
            count += 1
    print(f"PASS: {count} production SVGs are byte-identical to the selected B2 experiment")


def build():
    outputs = {}
    for source, name in [(ROOT / "graph-separation.tex", "example"),
                         (ROOT / "tests/comparison.tex", "comparison")]:
        work = BUILD / name
        compile_tex(source.read_text(), work)
        shutil.copy2(work / "document.pdf", BUILD / f"graph-separation-{name}.pdf")
        if name == "example":
            shutil.copy2(work / "document.pdf", ROOT / "graph-separation.pdf")
        outputs[f"graph-separation-{name}.pdf"] = digest(BUILD / f"graph-separation-{name}.pdf")
    (BUILD / "documents.json").write_text(json.dumps({
        "source_sha256": digest(STYLE), "example_sha256": digest(ROOT / "graph-separation.tex"),
        "comparison_sha256": digest(ROOT / "tests/comparison.tex"),
        "generator_sha256": digest(Path(__file__)), "outputs": outputs}, indent=2) + "\n")
    print(BUILD / "graph-separation-comparison.pdf")


def render_glyph(name, style, work, extra_preamble=""):
    tex_style, em = STYLES[style]
    log = compile_tex(
        r"\documentclass[dvisvgm,border=0pt]{standalone}" + "\n"
        r"\def\pgfsysdriver{pgfsys-dvisvgm.def}" + "\n"
        r"\usepackage{graph-separation}\newsavebox{\glyph}" + "\n" + extra_preamble
        + r"\begin{document}\sbox{\glyph}{$" + tex_style + "\\" + name + r"$}%" + "\n"
        r"\typeout{GS-BOX: \the\wd\glyph,\the\ht\glyph,\the\dp\glyph}%" + "\n"
        # Keep a small transparent top guard without changing the baseline.
        # Never tight-crop the image: that discards the measured TeX box.
        r"\noindent\rule{0pt}{\dimexpr\ht\glyph+" + f"{.06*em:.4f}pt"
        + r"\relax}\usebox{\glyph}\end{document}", work, "latex")
    match = re.search(r"GS-BOX: (-?[\d.]+)pt,(-?[\d.]+)pt,(-?[\d.]+)pt", log)
    if not match:
        raise ValueError(f"Missing native box metrics: {name}/{style}")
    width, height, depth = map(float, match.groups())
    target = work / "glyph.svg"
    run([executable("dvisvgm"), "--no-fonts", "--no-styles", "--exact",
         "--bbox=papersize", "--precision=6", f"--output={target}", "document.dvi"], work)
    data = target.read_bytes()
    svg = ET.fromstring(data)
    paper = list(map(float, svg.attrib["viewBox"].split()))
    bp_per_pt = 72 / 72.27
    image_width, image_height = paper[2] / bp_per_pt, paper[3] / bp_per_pt
    image_depth = depth
    if abs(image_width - width) > .0002:
        raise AssertionError(f"SVG advance changed: {name}/{style}: {image_width} != {width}")
    if abs(image_height - (height + depth + .06 * em)) > .0002:
        raise AssertionError(f"Unexpected SVG height: {name}/{style}")
    uri = "data:image/svg+xml;base64," + base64.b64encode(data).decode()
    token = (r'\mathrel{\mmlToken{mglyph}[src="' + uri
             + f'",width="{image_width/em:.6f}em",height="{image_height/em:.6f}em",'
             + f'valign="{-image_depth/em:.6f}em",alt="{name}"]{{}}}}')
    return token, {"native_width_pt": width, "native_height_pt": height,
                   "native_depth_pt": depth, "image_width_pt": image_width,
                   "image_height_pt": image_height, "image_depth_pt": image_depth,
                   "svg_sha256": hashlib.sha256(data).hexdigest()}


def export_mathjax(output, names, mathjax_js=None):
    unknown = set(names) - set(public_macros())
    if unknown:
        raise ValueError(f"Unknown macros: {sorted(unknown)}")
    identity = hashlib.sha256(STYLE.read_bytes() + Path(__file__).read_bytes()).hexdigest()
    work = BUILD / "mathjax" / identity[:16]
    macros, metrics = {}, {}
    for name in names:
        variants = []
        metrics[name] = {}
        for style in STYLES:
            token, metric = render_glyph(name, style, work / name / style)
            variants.append("{" + token + "}")
            metrics[name][style] = metric
        macros[name] = r"\mathchoice" + "".join(variants)
    header = ("<!-- Generated from the central graph-separation package.\n" + NOTICE
              + "\nVersion: " + VERSION + "\nStyle SHA-256: " + digest(STYLE) + "\n-->\n"
              "<script>\nwindow.MathJax = window.MathJax || {};\n"
              "window.MathJax.tex = window.MathJax.tex || {};\n"
              "window.MathJax.tex.maxBuffer = Math.max(window.MathJax.tex.maxBuffer || 0, 1048576);\n"
              "window.MathJax.tex.macros = Object.assign({}, window.MathJax.tex.macros, "
              + json.dumps(macros, indent=2) + ");\n</script>\n")
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(header)
    receipt = {"version": VERSION, "source_sha256": digest(STYLE),
               "generator_sha256": digest(Path(__file__)), "metrics": metrics,
               "output_sha256": digest(output)}
    output.with_suffix(".json").write_text(json.dumps(receipt, indent=2) + "\n")
    if mathjax_js:
        preview = BUILD / "preview"
        preview.mkdir(parents=True, exist_ok=True)
        shutil.copy2(mathjax_js, preview / "tex-svg-full.js")
        rows = "\n".join(
            "<tr><th><code>\\" + html.escape(name) + "</code></th><td>\\(V_j\\"
            + name + " V_k\\)</td><td>\\(X_{A\\" + name + " B}\\)</td>"
            "<td>\\(X_{Y_{A\\" + name + " B}}\\)</td></tr>" for name in names)
        (preview / "index.html").write_text(
            '<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>Graph separation review</title><style>'
            'body{font:18px system-ui;max-width:900px;margin:24px auto;padding:0 16px;color:#222;background:white}'
            'table{border-collapse:collapse}td,th{padding:10px;text-align:left}'
            '.scroll{overflow:auto}mjx-container{max-width:100%}'
            '</style>' + header + '<script defer src="tex-svg-full.js"></script>'
            '<h1>Graph separation: review candidate</h1>'
            '<p>AMS reference: \\(A\\rightsquigarrow B\\), '
            '\\(A\\leftrightsquigarrow B\\).</p><div class="scroll"><table>'
            '<tr><th>Command</th><th>Inline</th><th>Script</th><th>Script-script</th></tr>'
            + rows + '</table></div><p>Display:</p>\\[V_j\\mconnarc V_k'
            '\\qquad V_j\\dconnarc V_k\\qquad V_j\\trek V_k\\]</html>')
    print(json.dumps({"output": str(output), "source_sha256": digest(STYLE),
                      "macros": len(names)}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check")
    sub.add_parser("build")
    sub.add_parser("check-outlines")
    export = sub.add_parser("export-mathjax")
    export.add_argument("--output", type=Path, default=BUILD / "graph-separation.html")
    export.add_argument("--macros", nargs="+", default=DEFAULT_MACROS)
    export.add_argument("--mathjax-js", type=Path)
    args = parser.parse_args()
    if args.command == "check":
        check_all()
    elif args.command == "build":
        build()
    elif args.command == "check-outlines":
        check_outlines()
    else:
        export_mathjax(args.output, args.macros, args.mathjax_js)


if __name__ == "__main__":
    main()
