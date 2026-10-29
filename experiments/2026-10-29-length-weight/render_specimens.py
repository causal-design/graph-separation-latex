"""Inspect experiment PDFs with PyMuPDF; produce preview images and ink metrics."""

import importlib.util
import json
from pathlib import Path

import fitz

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("probe_build", HERE / "build.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
OUT = builder.OUT


def main():
    document = fitz.open(OUT / "ink/document.pdf")
    assert len(document) == len(builder.CANDIDATES) * len(builder.NAMES)
    rows = []
    scale = 20
    pt_per_pixel = 72.27 / 72 / scale
    for i, candidate in enumerate(builder.CANDIDATES):
        glyphs = {}
        common_body = document[i * 7].get_drawings()[0]["items"]
        for j, name in enumerate(builder.NAMES):
            page = document[i * 7 + j]
            assert page.get_drawings()[0]["items"] == common_body, (candidate["id"], name)
            pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=True)
            alpha = pixmap.samples[3::4]
            visible = [k for k, a in enumerate(alpha) if a >= 128]
            left, right = min(k % pixmap.width for k in visible), max(k % pixmap.width for k in visible)
            top, bottom = min(k // pixmap.width for k in visible), max(k // pixmap.width for k in visible)
            assert left > 0 and right < pixmap.width - 1
            assert top > 0 and bottom < pixmap.height - 1
            glyphs[name] = {"ink_width_pt": (right - left + 1) * pt_per_pixel,
                            "ink_area_pt2": sum(alpha) / 255 * pt_per_pixel ** 2}
        widths = [glyph["ink_width_pt"] for glyph in glyphs.values()]
        spread = max(widths) - min(widths)
        assert spread <= pt_per_pixel + .00001, (candidate["id"], spread)
        assert all(abs(width - candidate["length_pt"]) <= pt_per_pixel for width in widths)
        rows.append({**candidate, "glyphs": glyphs, "width_spread_pt": spread,
                     "same_vector_body": True, "ink_not_cropped": True})
    # This verifies that weight really changes ink coverage; it is not an
    # aesthetic score and does not decide the winner.
    for offset in [0, 3, 6]:
        for name in builder.NAMES:
            areas = [r["glyphs"][name]["ink_area_pt2"] for r in rows[offset:offset + 3]]
            assert areas[0] < areas[1] < areas[2], (name, areas)
    (OUT / "ink-measurements.json").write_text(json.dumps({
        "raster_pixels_per_bp": scale, "alpha_threshold": 128,
        "width_tolerance_pt": pt_per_pixel, "increasing_ink_area_with_weight": True,
        "candidates": rows}, indent=2) + "\n")
    specimen = fitz.open(OUT / "specimen.pdf")
    assert len(specimen) == 4
    for i, page in enumerate(specimen):
        page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(OUT / f"specimen-{i+1}.png")
    page = specimen[0]
    first = page.search_for("A1:")[0]
    end = page.search_for("How to judge:")[0]
    page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5),
                   clip=fitz.Rect(49, first.y0 - 6, 548, end.y0 - 8),
                   alpha=False).save(OUT / "grid.png")
    old = page.search_for("Previous website v2.0")[0]
    reference = page.search_for("AMS for weight/context")[0]
    page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5),
                   clip=fitz.Rect(49, old.y0 - 4, 548, reference.y0 - 6),
                   alpha=False).save(OUT / "old-v2.0.png")
    print(f"Verified {len(document)} glyphs: common vector bodies and ink spans within "
          f"{pt_per_pixel:.4f} pt (one raster pixel); no crop-boundary contact.")
    print(OUT / "grid.png")


if __name__ == "__main__":
    main()
