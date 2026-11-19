# Author: Kenneth | Task: shared design system for the deck (colours, type, layout helpers)
"""Small design system on top of python-pptx so every slide looks the same.

Palette is light (our matplotlib figures are white-background) with a dark navy
for the cover and the section dividers. Accent cyan matches the inspection UI.
"""

from __future__ import annotations

from pathlib import Path

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

W, H = 13.333, 7.5          # slide size in inches
M = 0.72                    # page margin

NAVY = RGBColor(0x0B, 0x22, 0x39)
NAVY_SOFT = RGBColor(0x14, 0x30, 0x4C)
INK = RGBColor(0x12, 0x26, 0x3A)
MUTED = RGBColor(0x5F, 0x74, 0x88)
ACCENT = RGBColor(0x0E, 0x8F, 0xB6)
ACCENT_DARK = RGBColor(0x0A, 0x6C, 0x8C)
GREEN = RGBColor(0x12, 0x85, 0x5A)
AMBER = RGBColor(0xB4, 0x53, 0x09)
RED = RGBColor(0xB9, 0x1C, 0x1C)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CARD = RGBColor(0xF5, 0xF8, 0xFB)
CARD_2 = RGBColor(0xEE, 0xF4, 0xF9)
BORDER = RGBColor(0xD9, 0xE3, 0xEC)
CYAN_LIGHT = RGBColor(0x9F, 0xD8, 0xE8)

FONT = "Segoe UI"
FONT_BOLD = "Segoe UI Semibold"

REPO = "github.com/Zheyi-D/am-defect-tl"
_ROOT = Path(__file__).resolve().parents[1]
_CACHE = _ROOT / "reports" / "_slide_cache"


def _small(path: Path, max_px: int = 1400) -> Path:
    """Shrink a heavy source image once, so the deck does not balloon to megabytes."""
    if path.stat().st_size <= 800_000:
        return path
    _CACHE.mkdir(parents=True, exist_ok=True)
    dst = _CACHE / f"{path.stem}_{max_px}.jpg"
    if dst.exists():
        return dst
    try:
        from PIL import Image

        with Image.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail((max_px, max_px), Image.LANCZOS)
            im.save(dst, format="JPEG", quality=88)
        return dst
    except Exception:
        return path


# ---------------------------------------------------------------- primitives
def emu(v: float) -> Emu:
    return Emu(int(round(v * 914400)))


def bg(slide, color: RGBColor) -> None:
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, emu(W), emu(H))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def box(slide, x, y, w, h, fill=None, line=None, lw=0.75, radius=0.0, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    shp = slide.shapes.add_shape(shape, emu(x), emu(y), emu(w), emu(h))
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(lw)
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE and radius:
        try:
            shp.adjustments[0] = radius
        except Exception:
            pass
    shp.shadow.inherit = False
    return shp


def text(slide, x, y, w, h, s, size=15, color=INK, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, font=None, italic=False, spacing=1.0, margins=(0, 0, 0, 0)):
    tb = slide.shapes.add_textbox(emu(x), emu(y), emu(w), emu(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = emu(margins[0])
    tf.margin_right = emu(margins[1])
    tf.margin_top = emu(margins[2])
    tf.margin_bottom = emu(margins[3])
    tf.vertical_anchor = anchor
    lines = s.split("\n")
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = spacing
    r = p.add_run()
    r.text = lines[0]
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.name = font or (FONT_BOLD if bold else FONT)
    r.font.color.rgb = color
    for line in lines[1:]:
        p = tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.name = font or (FONT_BOLD if bold else FONT)
        r.font.color.rgb = color
    return tb


def _bullet(p, char: str = "▸", color: RGBColor = ACCENT, indent: float = 0.22):
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(int(emu(indent))))
    pPr.set("indent", str(int(-emu(indent))))
    buClr = pPr.makeelement(qn("a:buClr"), {})
    srgb = pPr.makeelement(qn("a:srgbClr"), {"val": "%02X%02X%02X" % (color[0], color[1], color[2])})
    buClr.append(srgb)
    pPr.append(buClr)
    buFont = pPr.makeelement(qn("a:buFont"), {"typeface": "Arial"})
    pPr.append(buFont)
    buChar = pPr.makeelement(qn("a:buChar"), {"char": char})
    pPr.append(buChar)


def bullets(slide, items, x, y, w, h, size=15, color=INK, gap=9, spacing=1.08, marker=ACCENT):
    tb = slide.shapes.add_textbox(emu(x), emu(y), emu(w), emu(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = emu(0)
    tf.margin_right = emu(0)
    tf.margin_top = emu(0)
    tf.margin_bottom = emu(0)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = spacing
        p.space_after = Pt(gap)
        _bullet(p, color=marker)
        head, _, tail = item.partition("|")
        r = p.add_run()
        if tail:
            r.text = head.strip() + " "
            r.font.bold = True
            r.font.name = FONT_BOLD
            r.font.size = Pt(size)
            r.font.color.rgb = color
            r2 = p.add_run()
            r2.text = tail.strip()
            r2.font.name = FONT
            r2.font.size = Pt(size)
            r2.font.color.rgb = MUTED if color == INK else color
        else:
            r.text = head.strip()
            r.font.name = FONT
            r.font.size = Pt(size)
            r.font.color.rgb = color
    return tb


# ---------------------------------------------------------------- chrome
def chrome(slide, kicker: str, title: str, page: int | None = None, total: int | None = None,
           accent: RGBColor = ACCENT):
    """Top accent bar, kicker, title, hairline rule and footer."""
    box(slide, 0, 0, W, 0.10, fill=accent, shape=MSO_SHAPE.RECTANGLE)
    if kicker:
        text(slide, M, 0.40, 9.0, 0.30, kicker.upper(), size=10.5, color=accent, bold=True)
    text(slide, M, 0.66, W - 2 * M, 0.86, title, size=23, color=INK, bold=True, spacing=0.95)
    box(slide, M, 1.56 if kicker else 1.40, 1.1, 0.045, fill=accent, shape=MSO_SHAPE.RECTANGLE)
    # footer
    box(slide, M, 7.02, W - 2 * M, 0.012, fill=BORDER, shape=MSO_SHAPE.RECTANGLE)
    text(slide, M, 7.10, 7.0, 0.26, REPO, size=8.5, color=MUTED)
    if page is not None:
        text(slide, W - M - 1.2, 7.10, 1.2, 0.26, f"{page} / {total}", size=8.5,
             color=MUTED, align=PP_ALIGN.RIGHT)


def picture_fit(slide, path: Path, x, y, w, h, fit="contain", pad=0.0):
    """Place an image inside a box; fit='cover' crops it to fill the box."""
    path = Path(path)
    if not path.exists():
        return None
    from PIL import Image

    path = _small(path)
    with Image.open(path) as im:
        iw, ih = im.size
    inner_w, inner_h = w - 2 * pad, h - 2 * pad
    if fit == "cover":
        target = inner_w / inner_h
        if iw / ih > target:
            new_w = int(ih * target)
            im_c = Image.open(path).crop(((iw - new_w) // 2, 0, (iw + new_w) // 2, ih))
        else:
            new_h = int(iw / target)
            im_c = Image.open(path).crop((0, (ih - new_h) // 2, iw, (ih + new_h) // 2))
        _CACHE.mkdir(parents=True, exist_ok=True)
        dst = _CACHE / f"{path.stem}_crop{int(inner_w * 100)}x{int(inner_h * 100)}.jpg"
        if not dst.exists():
            im_c.convert("RGB").save(dst, format="JPEG", quality=90)
        return slide.shapes.add_picture(str(dst), emu(x + pad), emu(y + pad), emu(inner_w), emu(inner_h))
    scale = min(inner_w / iw, inner_h / ih)
    pw, ph = iw * scale, ih * scale
    return slide.shapes.add_picture(str(path), emu(x + pad + (inner_w - pw) / 2),
                                    emu(y + pad + (inner_h - ph) / 2), emu(pw), emu(ph))


def split_bar(slide, x, y, w, h, parts, colors, legend, caption=None):
    """Stacked proportion bar, e.g. defect vs non-defect counts."""
    total = sum(v for v, _ in parts)
    box(slide, x, y, w, h, fill=CARD_2, line=BORDER, lw=0.7, radius=0.2)
    cursor = x
    for (value, _label), colour in zip(parts, colors):
        seg = w * value / total
        box(slide, cursor, y, max(seg - 0.03, 0.06), h, fill=colour, radius=0.2)
        cursor += seg
    lx = x
    for (value, label), colour in zip(parts, colors):
        box(slide, lx, y + h + 0.09, 0.11, 0.11, fill=colour, radius=0.3)
        text(slide, lx + 0.17, y + h + 0.05, 2.3, 0.24, f"{label} {value}", size=8.5, color=MUTED)
        lx += 2.20
    if caption:
        text(slide, x, y - 0.30, w, 0.26, caption, size=9, color=MUTED, bold=True)


def image_card(slide, path: Path, x, y, w, h, caption: str | None = None, pad=0.14, fit="contain"):
    """Card with a border and an image fitted inside; optional caption strip."""
    box(slide, x, y, w, h, fill=WHITE, line=BORDER, lw=0.9, radius=0.03)
    inner_w, inner_h = w - 2 * pad, h - 2 * pad - (0.30 if caption else 0)
    px, py = x + pad, y + pad
    path = Path(path)
    if not path.exists():
        text(slide, px, py + inner_h / 2 - 0.2, inner_w, 0.4, f"【TBD image: {path.name}】",
             size=12, color=MUTED, align=PP_ALIGN.CENTER)
    else:
        try:
            picture_fit(slide, path, px, py, inner_w, inner_h, fit=fit)
        except Exception:
            text(slide, px, py + inner_h / 2 - 0.2, inner_w, 0.4, f"【image error: {path.name}】",
                 size=12, color=MUTED, align=PP_ALIGN.CENTER)
    if caption:
        text(slide, px, y + h - 0.42, inner_w, 0.28, caption, size=9.5, color=MUTED)


def stat_cards(slide, items, x, y, w, h, gap=0.18, value_size=30, label_size=9.5,
               unit_size=13, value_color=ACCENT_DARK):
    """Row of (value, label) cards; value may contain a line break for units."""
    n = len(items)
    cw = (w - gap * (n - 1)) / n
    for i, (value, label) in enumerate(items):
        cx = x + i * (cw + gap)
        box(slide, cx, y, cw, h, fill=CARD, line=BORDER, lw=0.8, radius=0.08)
        box(slide, cx, y + 0.16, 0.045, h - 0.32, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
        text(slide, cx + 0.22, y + 0.18, cw - 0.34, h * 0.52, value, size=value_size,
             color=value_color, bold=True, spacing=0.9)
        text(slide, cx + 0.22, y + h - 0.46, cw - 0.34, 0.36, label, size=label_size,
             color=MUTED, bold=True)


def chip(slide, x, y, w, h, label, fill=CARD_2, color=INK, size=11, bold=False,
         line=BORDER, radius=0.3):
    box(slide, x, y, w, h, fill=fill, line=line, lw=0.7, radius=radius)
    text(slide, x, y, w, h, label, size=size, color=color, bold=bold,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def table_block(slide, rows, x, y, w, col_widths, header=True, size=11, row_h=0.34,
                header_fill=NAVY, header_color=WHITE, highlight_col=None):
    n_rows, n_cols = len(rows), len(rows[0])
    shape = slide.shapes.add_table(n_rows, n_cols, emu(x), emu(y), emu(w), emu(row_h * n_rows))
    table = shape.table
    total = sum(col_widths)
    for j, cwj in enumerate(col_widths):
        table.columns[j].width = emu(w * cwj / total)
    for i in range(n_rows):
        table.rows[i].height = emu(row_h)
        for j in range(n_cols):
            cell = table.cell(i, j)
            cell.text = ""
            cell.margin_left = emu(0.10)
            cell.margin_right = emu(0.08)
            cell.margin_top = emu(0.02)
            cell.margin_bottom = emu(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            is_head = header and i == 0
            cell.fill.solid()
            if is_head:
                cell.fill.fore_color.rgb = header_fill
            else:
                cell.fill.fore_color.rgb = WHITE if i % 2 else CARD
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = str(rows[i][j])
            r.font.size = Pt(size if not is_head else size)
            r.font.bold = is_head
            r.font.name = FONT_BOLD if is_head else FONT
            r.font.color.rgb = header_color if is_head else INK
    return table


# ---------------------------------------------------------------- slide kinds
def cover(prs, title, subtitle, lines):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg(slide, NAVY)
    # decorative accent blocks
    box(slide, W - 3.6, -1.2, 5.2, 5.2, fill=NAVY_SOFT, radius=0.18)
    box(slide, W - 2.35, 3.15, 3.1, 3.1, fill=RGBColor(0x16, 0x3A, 0x5C), radius=0.18)
    box(slide, 0, 0, 0.22, H, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
    box(slide, M + 0.1, 1.85, 1.35, 0.05, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)

    text(slide, M + 0.1, 1.30, 8.6, 0.4, "IDAT7215  ·  GROUP PROJECT", size=11.5,
         color=CYAN_LIGHT, bold=True)
    text(slide, M + 0.1, 2.10, 8.9, 2.1, title, size=33, color=WHITE, bold=True, spacing=0.94)
    text(slide, M + 0.1, 4.30, 8.6, 0.9, subtitle, size=14, color=CYAN_LIGHT, spacing=1.15)
    for i, line in enumerate(lines):
        text(slide, M + 0.1, 5.55 + i * 0.32, 8.6, 0.3, line, size=11.5,
             color=RGBColor(0xC7, 0xD6, 0xE4))
    return slide


def divider(prs, number, title, sub, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg(slide, NAVY)
    box(slide, W - 4.1, -1.5, 6.0, 6.0, fill=NAVY_SOFT, radius=0.16)
    box(slide, 0, 0, 0.22, H, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
    text(slide, M + 0.2, 1.55, 3.0, 1.5, number, size=78, color=RGBColor(0x2A, 0x5A, 0x7E), bold=True)
    text(slide, M + 0.2, 3.15, 8.4, 1.1, title, size=30, color=WHITE, bold=True, spacing=0.95)
    box(slide, M + 0.24, 4.36, 1.3, 0.05, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
    text(slide, M + 0.2, 4.62, 8.2, 0.9, sub, size=13, color=RGBColor(0xB9, 0xCB, 0xDD), spacing=1.2)
    text(slide, W - M - 1.2, 7.10, 1.2, 0.26, f"{page} / {total}", size=8.5,
         color=RGBColor(0x74, 0x8C, 0xA2), align=PP_ALIGN.RIGHT)
    return slide
