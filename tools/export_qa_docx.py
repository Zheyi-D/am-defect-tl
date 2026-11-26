# Author: Kenneth + agent | Task: export docs/QA-HANDBOOK.md to a printable Word document
"""Convert the bilingual Q&A handbook into a formatted .docx.

Usage:
    python tools/export_qa_docx.py
    python tools/export_qa_docx.py --src docs/QA-HANDBOOK.md --out docs/QA-HANDBOOK.docx

Layout: A4, 2.2 cm margins, Calibri/微软雅黑 mix, part headings as Heading 1,
questions bold, English answers indented and quoted, Chinese answers plain.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

LATIN = "Calibri"
CJK = "微软雅黑"
INK = RGBColor(0x12, 0x26, 0x3A)
MUTED = RGBColor(0x5F, 0x74, 0x88)
ACCENT = RGBColor(0x0E, 0x8F, 0xB6)


def _font(run, size=10.5, bold=False, colour=None, latin=LATIN, cjk=CJK) -> None:
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = latin
    run.font.color.rgb = colour if colour is not None else INK
    rpr = run._element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.append(fonts)
    fonts.set(qn("w:ascii"), latin)
    fonts.set(qn("w:hAnsi"), latin)
    fonts.set(qn("w:eastAsia"), cjk)


def _rich(paragraph, text: str, size=10.5, bold=False, colour=None) -> None:
    """Write text with **bold** and code markers resolved into runs."""
    text = text.replace("**", "\u0001").replace("", "\u0002")
    for chunk in text.split("\u0001"):
        if not chunk:
            continue
        for k, piece in enumerate(chunk.split("\u0002")):
            if not piece:
                continue
            _font(paragraph.add_run(piece), size, bold=bold or (k % 2 == 1), colour=colour)


def _para(doc, space_before=0, space_after=4, line=1.28, left=0.0, first=0.0,
          align=None, keep=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line
    if left:
        pf.left_indent = Cm(left)
    if first:
        pf.first_line_indent = Cm(first)
    if align is not None:
        p.alignment = align
    if keep:
        pf.keep_with_next = True
    return p


def _shade(paragraph, hex_fill: str) -> None:
    ppr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    ppr.append(shd)


def _left_border(paragraph, hex_colour: str, size=12) -> None:
    ppr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), str(size))
    left.set(qn("w:space"), "6")
    left.set(qn("w:color"), hex_colour)
    borders.append(left)
    ppr.append(borders)


def _field(paragraph, instr: str, size=9) -> None:
    run = paragraph.add_run()
    _font(run, size, colour=MUTED)
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = instr
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr_el)
    run._r.append(fld_end)


def _page_setup(doc) -> None:
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(1.9)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)

    # running header
    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = header.add_run("IDAT7215 Group 15  ·  Q&A Handbook")
    _font(run, 8.5, colour=MUTED)

    # footer: page number
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("— ")
    _font(run, 9, colour=MUTED)
    _field(footer, "PAGE")
    run = footer.add_run(" —")
    _font(run, 9, colour=MUTED)


def _table(doc, rows: list[list[str]], widths_cm: list[float] | None = None) -> None:
    cols = len(rows[0])
    table = doc.add_table(rows=0, cols=cols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        cells = table.add_row().cells
        for j, value in enumerate(row[:cols]):
            cell = cells[j]
            cell.text = ""
            para = cell.paragraphs[0]
            para.paragraph_format.space_after = Pt(2)
            para.paragraph_format.space_before = Pt(2)
            _rich(para, value, 9.5, bold=(i == 0))
            if widths_cm:
                cell.width = Cm(widths_cm[j])
            if i == 0:
                _shade(para, "E8EEF4")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def build(src: Path, out: Path) -> Path:
    lines = src.read_text(encoding="utf-8").splitlines()
    doc = Document()
    _page_setup(doc)

    # default style
    normal = doc.styles["Normal"]
    normal.font.name = LATIN
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), CJK)

    i = 0
    pending_table: list[list[str]] = []
    seen_heading = False

    def flush_table():
        nonlocal pending_table
        if pending_table:
            cols = len(pending_table[0])
            widths = [3.6, 12.8] if cols == 2 else [16.4 / cols] * cols
            _table(doc, pending_table, widths)
            pending_table = []

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        if line.startswith("|"):
            safe = line.replace("\\|", "@PIPE@")
            cells = [c.strip().replace("@PIPE@", "|") for c in safe.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                i += 1
                continue
            pending_table.append(cells)
            i += 1
            continue
        flush_table()

        if not line:
            i += 1
            continue

        if line.startswith("# "):
            p = _para(doc, space_before=0, space_after=2, line=1.1)
            _font(p.add_run("Q&A 手册（双语）"), 26, bold=True, colour=INK)
            p = _para(doc, space_after=2)
            _font(p.add_run("IDAT7215 Group 15  ·  Python-Based Transfer Learning for "
                            "3D Printed Object Defect Detection"), 12, colour=ACCENT)
            p = _para(doc, space_after=10)
            _font(p.add_run("按 PPT 八个 part 组织的双语问答；问题与答案均为中英对照。"), 9.5, colour=MUTED)
            i += 1
            continue

        if line.startswith("## "):
            seen_heading = True
            title = line[3:].strip()
            p = _para(doc, space_before=14, space_after=6, line=1.15, keep=True)
            _font(p.add_run(title), 15, bold=True, colour=ACCENT)
            _left_border(p, "0E8FB6", 18)
            i += 1
            continue

        if line == "---":
            i += 1
            continue

        m = re.match(r"^\*\*(Q\d+\..*?)\*\*$", line)
        if m:
            p = _para(doc, space_before=9, space_after=2, keep=True)
            _font(p.add_run(m.group(1)), 11, bold=True, colour=INK)
            i += 1
            continue

        if line.startswith(">"):
            if not seen_heading:
                i += 1
                continue
            body = line[1:].strip()
            if not body:
                i += 1
                continue
            if body.startswith("**EN**"):
                text = body[len("**EN**"):].strip()
                p = _para(doc, space_before=0, space_after=2, left=0.45, line=1.28,
                           align=WD_ALIGN_PARAGRAPH.LEFT)
                _font(p.add_run("EN  "), 9, bold=True, colour=GREY_EN)
                _font(p.add_run(text), 10, colour=INK)
                _shade(p, "F4F8FB")
                _left_border(p, "7CC6DE", 12)
            elif body.startswith("**中文**"):
                text = body[len("**中文**"):].strip().lstrip("：:").strip()
                p = _para(doc, space_before=0, space_after=3, left=0.45, line=1.28,
                           align=WD_ALIGN_PARAGRAPH.LEFT)
                _font(p.add_run("中文  "), 9, bold=True, colour=ACCENT)
                _font(p.add_run(text), 10, colour=INK)
            else:
                if not body.strip("> ").strip():
                    i += 1
                    continue
                p = _para(doc, space_before=0, space_after=3, left=0.45, line=1.25,
                           align=WD_ALIGN_PARAGRAPH.LEFT)
                _rich(p, body, 9.5, colour=MUTED)
            i += 1
            continue

        # plain paragraph (intro note, section prose, etc.)
        p = _para(doc, space_before=2, space_after=4, line=1.3, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        text = line
        if text.startswith("**") and text.endswith("**") and len(text) > 4:
            _font(p.add_run(text[2:-2]), 10.5, bold=True)
        else:
            # inline **bold** support
            _rich(p, text, 10.5)
        i += 1

    flush_table()
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    return out


GREY_EN = RGBColor(0x2E, 0x6C, 0x8A)


def main() -> None:
    ap = argparse.ArgumentParser(description="Export the Q&A handbook to .docx")
    ap.add_argument("--src", type=Path, default=ROOT / "docs" / "QA-HANDBOOK.md")
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "QA-HANDBOOK.docx")
    args = ap.parse_args()
    path = build(args.src, args.out)
    print(f"[docx] wrote {path} ({path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
