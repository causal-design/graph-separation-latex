"""Create and smoke-test a local draft distribution. Never sync or upload."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("workflow", ROOT / "tools/workflow.py")
workflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)


def main():
    receipt = json.loads((ROOT / "build/documents.json").read_text())
    for key, source in [("source_sha256", ROOT / "graph-separation.sty"),
                        ("example_sha256", ROOT / "graph-separation.tex"),
                        ("comparison_sha256", ROOT / "tests/comparison.tex"),
                        ("generator_sha256", ROOT / "tools/workflow.py")]:
        if receipt[key] != workflow.digest(source):
            raise ValueError("Guide build is stale; run tools/workflow.py build first")
    pdf = ROOT / "build/graph-separation-example.pdf"
    if workflow.digest(pdf) != receipt["outputs"][pdf.name]:
        raise ValueError("Guide PDF does not match the build receipt")
    names = ["graph-separation.sty", "graph-separation.tex", "README.md", "LICENSE",
             "examples/minimal.tex", "tools/workflow.py", "tools/sync-consumers.py",
             "tools/package-draft.py", "tests/test_workflow.py", "tests/browser.cjs",
             "tests/comparison.tex", "tests/legacy-primitives.tex",
             "experiments/2026-10-29-length-weight/probes.tex"]
    files = {name: (ROOT / name).read_bytes() for name in names}
    files["graph-separation.pdf"] = pdf.read_bytes()
    sums = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    files["SHA256SUMS.txt"] = "".join(f"{sha}  {name}\n" for name, sha in sorted(sums.items())).encode()
    folder = f"graph-separation-{workflow.VERSION}-draft"
    archive = ROOT / "build" / (folder + ".zip")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, data in files.items():
            bundle.writestr(folder + "/" + name, data)
    smoke = Path(tempfile.mkdtemp(prefix="draft-smoke-", dir=ROOT / "build"))
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(smoke)
    unpacked = smoke / folder
    env = dict(os.environ, TEXINPUTS=str(unpacked) + os.pathsep)
    # Compile the shipped example without relying on the authoring checkout.
    result = subprocess.run([workflow.executable("pdflatex"), "-no-shell-escape",
                             "-interaction=nonstopmode", "-halt-on-error", "-recorder",
                             str(unpacked / "examples/minimal.tex")],
                            cwd=unpacked, env=env, text=True, capture_output=True, timeout=120)
    (smoke / "compile-output.txt").write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f"Unpacked example failed: {smoke}")
    inputs = (unpacked / "minimal.fls").read_text()
    assert str(unpacked / "graph-separation.sty") in inputs
    for name, sha in sums.items():
        assert workflow.digest(unpacked / name) == sha
    (ROOT / "build/draft-bundle.json").write_text(json.dumps({
        "version": workflow.VERSION, "archive": archive.name,
        "archive_sha256": workflow.digest(archive), "files": sums,
        "unpacked_example_compiles": True, "uploaded": False}, indent=2) + "\n")
    print(archive)
    print("Verified all file hashes and compiled the unpacked minimal example.")


if __name__ == "__main__":
    main()
