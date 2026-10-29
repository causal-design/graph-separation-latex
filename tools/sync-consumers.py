"""Copy hash-pinned, generated distributions to local consumers. Never upload."""

import argparse
import importlib.util
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("workflow", ROOT / "tools/workflow.py")
workflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)
REPOSITORY = "https://github.com/causal-design/graph-separation-latex"


def sync_course(course):
    vendor = course / "lecture-notes/vendor/graph-separation"
    lockfile = course / "lecture-notes/graph-separation.lock.json"
    names = ["graph-separation.sty", "LICENSE", "tools/workflow.py"]
    if lockfile.exists():
        old = json.loads(lockfile.read_text())
        for name in names:
            target = vendor / name
            if target.exists() and workflow.digest(target) != old["files"].get(name):
                raise ValueError(f"Refusing to replace a locally edited vendor file: {target}")
    elif vendor.exists() and any(vendor.rglob("*.sty")):
        raise ValueError(f"Unmanaged vendor directory: {vendor}")
    for name in names:
        target = vendor / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    lock = {"repository": REPOSITORY, "version": workflow.VERSION,
            "status": "review-candidate", "vendor": "lecture-notes/vendor/graph-separation",
            "files": {name: workflow.digest(ROOT / name) for name in names},
            "macros": workflow.DEFAULT_MACROS}
    lockfile.write_text(json.dumps(lock, indent=2) + "\n")
    print(f"Pinned {workflow.VERSION} for {course}; regenerate the course header next.")


def sync_website(website):
    target = website / "scripts/graph-separation-release.json"
    if target.exists():
        previous = json.loads(target.read_text())
        for name, expected in previous["files"].items():
            destination = website / name
            if not destination.resolve().is_relative_to(website / "static/files"):
                raise ValueError("Invalid website graph-package manifest path")
            if destination.exists() and workflow.digest(destination) != expected:
                raise ValueError(f"Refusing to replace a locally edited website download: {destination}")
    receipt = json.loads((ROOT / "build/documents.json").read_text())
    for key, source in [("source_sha256", ROOT / "graph-separation.sty"),
                        ("example_sha256", ROOT / "graph-separation.tex"),
                        ("comparison_sha256", ROOT / "tests/comparison.tex"),
                        ("generator_sha256", ROOT / "tools/workflow.py")]:
        if receipt[key] != workflow.digest(source):
            raise ValueError("Document build is stale; run tools/workflow.py build first")
    pdf = ROOT / "build/graph-separation-example.pdf"
    if workflow.digest(pdf) != receipt["outputs"][pdf.name]:
        raise ValueError("Example PDF does not match its build receipt")
    files = {"graph-separation.sty": ROOT / "graph-separation.sty",
             "graph-separation.tex": ROOT / "graph-separation.tex",
             "graph-separation.pdf": pdf}
    for name, source in files.items():
        shutil.copy2(source, website / "static/files" / name)
    target.write_text(json.dumps({
        "repository": REPOSITORY, "version": workflow.VERSION, "status": "review-candidate",
        "files": {"static/files/" + name: workflow.digest(source)
                  for name, source in files.items()}}, indent=2) + "\n")
    print(f"Staged {len(files)} website downloads. Nothing has been uploaded.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--course", type=Path)
    parser.add_argument("--website", type=Path)
    args = parser.parse_args()
    if not args.course and not args.website:
        parser.error("Choose --course and/or --website")
    if args.course:
        sync_course(args.course.resolve())
    if args.website:
        sync_website(args.website.resolve())


if __name__ == "__main__":
    main()
