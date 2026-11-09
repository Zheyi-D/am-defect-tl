# Author: Kenneth | Task: generate the report skeleton docx (cover page + headings)
"""Generate the report skeleton .docx: only the **cover page** and the **headings** (body left empty).

Purpose:
    1. Starting point for collaborative editing in WPS / Kdocs (see reports/ONLINE.md)
    2. Regenerate locally when the structure changes -> `kdocs-cli drive upload-file` overwrites the same document

Usage:
    python tools/build_report_docx.py --out report_draft.docx

Conventions:
    - A4 page, top/bottom margins 2.54 cm, left/right margins 3.17 cm
    - Body text Times New Roman 12 pt, single line spacing, 6 pt space after
    - H1 16 pt bold / H2 14 pt bold, both black
    - An empty paragraph follows each heading to make writing easier
"""

from __future__ import annotations

import argparse
from pathlib import Path

MEMBERS = 8

SECTIONS: list[tuple[str, int]] = [
    ("Abstract", 1),
    ("List of Figures", 1),
    ("List of Tables", 1),
    ("1  Introduction", 1),
    ("1.1  Motivation", 2),
    ("1.2  Objectives", 2),
    ("1.3  Background", 2),
    ("1.4  Tools and Environment", 2),
    ("2  Project Description", 1),
    ("2.1  Main Objectives", 2),
    ("2.2  Dataset and Problem Formulation", 2),
    ("2.3  Techniques and Algorithms", 2),
    ("2.4  Training Protocol and Evaluation Metrics", 2),
    ("3  Results and Discussion", 1),
    ("3.1  Overall Model Comparison", 2),
    ("3.2  Optimizer Ablation", 2),
    ("3.3  Comparison with the Reported Results", 2),
    ("3.4  Data-Leakage Control Experiment", 2),
    ("3.5  Explainability: Grad-CAM and LIME", 2),
    ("3.6  Deployment Cost", 2),
    ("4  Conclusion and Recommendations", 1),
    ("Individual Contributions", 1),
    ("References", 1),
    ("Appendix A  Full Experimental Results", 1),
    ("Appendix B  Reproduction Commands", 1),
]


def build(out: Path) -> Path:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor

    doc = Document()

    # Page: A4 with standard margins
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(2.54)
    sec.left_margin = sec.right_margin = Cm(3.17)

    # Body style
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "SimSun")
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.0

    # Heading styles
    for name, size in (("Heading 1", 16), ("Heading 2", 14)):
        st = doc.styles[name]
        st.font.name = "Times New Roman"
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.paragraph_format.space_before = Pt(12)
        st.paragraph_format.space_after = Pt(6)

    def center(text: str, size: int = 12, bold: bool = False,
               space_after: int = 6, space_before: int = 0) -> None:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        run = p.add_run(text)
        run.font.size = Pt(size)
        run.bold = bold

    def left(text: str, indent_cm: float = 0.0, space_after: int = 6) -> None:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        if indent_cm:
            p.paragraph_format.left_indent = Cm(indent_cm)
        p.add_run(text).font.size = Pt(12)

    # ---------------- Cover page ----------------
    for _ in range(5):
        doc.add_paragraph()

    center("IDAT7215 Computer Programming for", size=14, bold=True, space_after=2)
    center("Product Development and Applications", size=14, bold=True, space_after=24)
    center("Group Project (25%)", space_after=36)
    center("Python-Based Transfer Learning for", size=18, bold=True, space_after=2)
    center("3D Printed Object Defect Detection", size=18, bold=True, space_after=18)
    center("A Reproducibility Study of Ahsan et al. (2024)", space_after=60)

    for _ in range(4):
        doc.add_paragraph()

    for line in ("Group No.: ____________________",
                 "Programme / Class: ____________________",
                 "Group Leader: ____________________"):
        left(line)

    left("Members (Name — UID):")
    for i in range(1, MEMBERS + 1):
        left(f"{i}. ____________________  ____________________", indent_cm=0.75, space_after=2)

    for _ in range(2):
        doc.add_paragraph()

    for line in ("Word Count (body): ____________________",
                 "Repository: https://github.com/Zheyi-D/am-defect-tl",
                 "Date of Submission: ____________________"):
        left(line)

    doc.add_page_break()

    # ---------------- Headings (body left empty) ----------------
    for title, level in SECTIONS:
        doc.add_heading(title, level=level)
        doc.add_paragraph()

    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("report_draft.docx"))
    args = ap.parse_args()
    path = build(args.out)
    print(f"[report-docx] wrote {path} ({path.stat().st_size} bytes, {1 + len(SECTIONS)} heading blocks)")


if __name__ == "__main__":
    main()
