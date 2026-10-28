"""Fast checks for local synchronization safeguards and the public API."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sync_consumers", ROOT / "tools/sync-consumers.py")
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class WorkflowTests(unittest.TestCase):
    def test_existing_public_api(self):
        expected = """nosquigno nosquigfull fullsquigno halfsquighalf halfsquigfull
        fullsquighalf fullsquigfull nostraigno nostraigfull fullstraigno
        halfstraighalf halfstraigfull fullstraighalf fullstraigfull rdedge nordedge
        ldedge noldedge bdedge nobdedge rdpath nordpath ldpath noldpath dconnarc
        nodconnarc mconnarc nomconnarc trek tconnarc notrek notconnarc confarc
        noconfarc samedist colliderconn markovblanket tconn mconn dconn confpath
        udedge noudedge uconn deltaconn muconn""".split()
        self.assertEqual(set(expected), set(sync.workflow.public_macros()))
        self.assertEqual(len(expected), len(sync.workflow.public_macros()))

    def test_course_copy_matches_central_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            course = Path(temporary)
            sync.sync_course(course)
            self.assertEqual((course / "lecture-notes/vendor/graph-separation/graph-separation.sty").read_bytes(),
                             (ROOT / "graph-separation.sty").read_bytes())
            sync.sync_course(course)  # An unchanged pin is safe to refresh.

    def test_refuse_to_replace_locally_edited_vendor(self):
        with tempfile.TemporaryDirectory() as temporary:
            course = Path(temporary)
            sync.sync_course(course)
            style = course / "lecture-notes/vendor/graph-separation/graph-separation.sty"
            style.write_text("user edit")
            with self.assertRaisesRegex(ValueError, "locally edited"):
                sync.sync_course(course)
            self.assertEqual(style.read_text(), "user edit")

    def test_refuse_unmanaged_vendor(self):
        with tempfile.TemporaryDirectory() as temporary:
            course = Path(temporary)
            style = course / "lecture-notes/vendor/graph-separation/graph-separation.sty"
            style.parent.mkdir(parents=True)
            style.write_text("user source")
            with self.assertRaisesRegex(ValueError, "Unmanaged"):
                sync.sync_course(course)

    def website_fixture(self, root):
        central = root / "central"
        for name in ["graph-separation.sty", "graph-separation.tex",
                     "tests/comparison.tex", "tools/workflow.py",
                     "build/graph-separation-example.pdf"]:
            source = central / name
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("fixture " + name)
        receipt = {key: sync.workflow.digest(central / name) for key, name in [
            ("source_sha256", "graph-separation.sty"), ("example_sha256", "graph-separation.tex"),
            ("comparison_sha256", "tests/comparison.tex"), ("generator_sha256", "tools/workflow.py")]}
        receipt["outputs"] = {"graph-separation-example.pdf": sync.workflow.digest(
            central / "build/graph-separation-example.pdf")}
        (central / "build/documents.json").write_text(json.dumps(receipt))
        website = root / "website"
        (website / "static/files").mkdir(parents=True)
        (website / "scripts").mkdir()
        return central, website

    def test_refuse_locally_edited_website_download(self):
        with tempfile.TemporaryDirectory() as temporary:
            central, website = self.website_fixture(Path(temporary))
            with patch.object(sync, "ROOT", central):
                sync.sync_website(website)
                style = website / "static/files/graph-separation.sty"
                style.write_text("user edit")
                with self.assertRaisesRegex(ValueError, "locally edited website"):
                    sync.sync_website(website)
                self.assertEqual(style.read_text(), "user edit")

    def test_refuse_stale_pdf_build(self):
        with tempfile.TemporaryDirectory() as temporary:
            central, website = self.website_fixture(Path(temporary))
            (central / "graph-separation.sty").write_text("updated source")
            with patch.object(sync, "ROOT", central):
                with self.assertRaisesRegex(ValueError, "stale"):
                    sync.sync_website(website)
            self.assertEqual(list((website / "static/files").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
