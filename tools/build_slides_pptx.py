# Author: Kenneth + agent | Task: 25-slide deck with a single design system
"""Build the group presentation (15 min talk + 5 min Q&A).

Everything visual goes through `tools/deck_style.py`, so the deck is consistent:
one palette, one type scale, one set of cards. All numbers come from the
repository; anything still missing is written as 【TBD ...】.

Usage:
    python tools/build_slides_pptx.py --out reports/slides_draft.pptx
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pptx.dml.color import RGBColor

from tools.deck_style import (
    emu,
    ACCENT,
    ACCENT_DARK,
    AMBER,
    BORDER,
    CARD,
    CARD_2,
    CYAN_LIGHT,
    FONT,
    FONT_BOLD,
    GREEN,
    H,
    INK,
    M,
    MUTED,
    NAVY,
    NAVY_SOFT,
    RED,
    W,
    WHITE,
    bullets,
    bg,
    box,
    chip,
    chrome,
    cover,
    divider,
    image_card,
    picture_fit,
    split_bar,
    stat_cards,
    table_block,
    text,
)

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Pt

FIG = ROOT / "results" / "figures"

BACKBONES = [
    "VGG16", "VGG19", "ResNet50", "ResNet101", "MobileNetV2",
    "Xception", "InceptionResNetV2", "NASNetLarge",
    "EfficientNet-B0", "EfficientNet-B7", "EfficientNet-V2M",
]

SLIDE_COUNT = 25


# ---------------------------------------------------------------- 1 cover
def s01(prs, page, total):
    cover(
        prs,
        "Python-Based Transfer Learning\nfor 3D Printed Object Defect Detection",
        "A reproducibility study of Ahsan et al., Expert Systems with Applications 253 (2024) 124293",
        [
            "Group 【GROUP NO.】  ·  【MEMBER NAMES】",
            "IDAT7215 Computer Programming for Product Development and Applications",
            "【DATE】  ·  15-minute presentation + 5-minute Q&A",
        ],
    )


# ---------------------------------------------------------------- 2 agenda
def s02(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "Agenda", "What we will cover in 15 minutes", page, total)
    items = [
        ("01", "The problem & our objectives", "0:50 – 2:30", "Why 3D-printed parts need automatic inspection."),
        ("02", "Data & method", "2:30 – 6:25", "Two public datasets, one frozen split, one head."),
        ("03", "66 experiments & results", "6:30 – 9:55", "Where we match the paper and where we differ."),
        ("04", "Three analyses the paper lacks", "10:00 – 12:45", "Leakage, explainability, deployment cost."),
        ("05", "Live demo", "12:45 – 14:10", "The inspection station, end to end."),
        ("06", "Conclusions & limitations", "14:10 – 15:00", "What we would tell a production engineer."),
    ]
    x0, y0 = M, 1.95
    cw, ch, gx, gy = 3.72, 1.95, 0.30, 0.32
    for i, (num, title, when, what) in enumerate(items):
        r, c = divmod(i, 3)
        x = x0 + c * (cw + gx)
        y = y0 + r * (ch + gy)
        box(slide, x, y, cw, ch, fill=CARD, line=BORDER, lw=0.8, radius=0.06)
        box(slide, x, y, 0.05, ch, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
        text(slide, x + 0.24, y + 0.16, 1.0, 0.4, num, size=20, color=ACCENT, bold=True)
        text(slide, x + 1.05, y + 0.20, cw - 1.25, 0.3, when, size=9.5, color=MUTED,
             align=PP_ALIGN.RIGHT)
        text(slide, x + 0.24, y + 0.70, cw - 0.45, 0.62, title, size=14, color=INK, bold=True,
             spacing=0.95)
        text(slide, x + 0.24, y + 1.38, cw - 0.45, 0.5, what, size=10.5, color=MUTED, spacing=1.05)


# ---------------------------------------------------------------- 3 divider 01
def s03(prs, page, total):
    divider(prs, "01", "The problem and our objectives",
            "Why 3D-printed parts need automatic inspection, and what exactly we set out to reproduce.",
            page, total)


# ---------------------------------------------------------------- 4 motivation
def s04(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "01 · Motivation", "Manual inspection does not scale with additive manufacturing", page, total)
    bullets(slide, [
        "Subtle defects | stringing, poor layer adhesion and rough surfaces are easy to miss by eye.",
        "High volume | every printed part needs the same check, at the same speed.",
        "Few labels | this dataset has only 271 real photographs; deep learning normally wants thousands.",
        "So we reuse ImageNet | freeze a pre-trained CNN and train only a small head.",
    ], M, 1.95, 5.75, 3.2, size=13.5, gap=12)
    image_card(slide, ROOT / "testset" / "D1" / "test" / "defect" / "IMG_9153.jpg",
               6.55, 1.80, 6.05, 3.55, fit="cover",
               caption="D1 sample — stringing around the printed part (5184 × 3456)")
    stat_cards(slide, [("271", "real photographs"), ("1,557", "images never released"), ("11", "backbones compared")],
               M, 5.45, 11.88, 1.15, value_size=24, label_size=9)


# ---------------------------------------------------------------- 5 objectives
def s05(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "01 · Objectives", "Two goals: reproduce the paper, then test what it left out", page, total)
    goals = [
        ("Reproduce", "11 ImageNet backbones on two public datasets", "11 × 2 = 22 runs"),
        ("Reproduce", "the optimizer ablation (Adam / SGD / RMSprop)", "11 × 3 × 2 = 66 runs"),
        ("Go beyond", "leakage control, explainability, deployment cost", "6 + 23 figures + table"),
        ("Ship", "a reproducible pipeline and a working UI", "code + splits + demo"),
    ]
    x0, y0, cw, ch, gx = M, 1.95, 2.82, 1.95, 0.22
    for i, (tag, what, how) in enumerate(goals):
        x = x0 + i * (cw + gx)
        box(slide, x, y0, cw, ch, fill=WHITE, line=BORDER, lw=0.9, radius=0.05)
        box(slide, x, y0, cw, 0.06, fill=ACCENT if i < 2 else GREEN, shape=MSO_SHAPE.RECTANGLE)
        text(slide, x + 0.2, y0 + 0.22, cw - 0.4, 0.28, tag.upper(), size=9, color=ACCENT if i < 2 else GREEN,
             bold=True)
        text(slide, x + 0.2, y0 + 0.60, cw - 0.4, 1.0, what, size=12.5, color=INK, bold=True, spacing=1.0)
        text(slide, x + 0.2, y0 + 1.62, cw - 0.4, 0.3, how, size=10, color=MUTED)
    box(slide, M, 4.25, 11.88, 1.05, fill=CARD_2, line=BORDER, lw=0.8, radius=0.05)
    text(slide, M + 0.25, 4.42, 11.4, 0.72,
         "Scope: 66 of the 99 cells the paper reports. The third dataset (1,557 images) is not public, "
         "so those 33 cells stay author-reported and are never presented as our own measurement.",
         size=12, color=INK, spacing=1.15)
    for i, (label, colour) in enumerate([("report", ACCENT), ("deck", ACCENT), ("source", ACCENT),
                                         ("demo", GREEN)]):
        chip(slide, M + 2.6 + i * 1.85, 5.62, 1.65, 0.44, label, size=10.5, color=colour, bold=True)
    text(slide, M + 0.6, 5.70, 2.0, 0.3, "DELIVERABLES", size=9, color=MUTED, bold=True)


# ---------------------------------------------------------------- 6 divider 02
def s06(prs, page, total):
    divider(prs, "02", "Data and method",
            "Two public datasets, one frozen split, and an identical classification head for every backbone.",
            page, total)


# ---------------------------------------------------------------- 7 datasets
def s07(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "02 · Data", "Two datasets — and a caveat that changes how you read the numbers", page, total)
    cards = [
        ("D1", "271", "real photographs", ["136 defect · 135 non-defect", "5184 × 3456 px", "split 189 / 28 / 54"], ACCENT),
        ("D2", "3,017", "augmented images", ["947 defect · 2,070 non-defect", "128 × 128 px", "split 2,112 / 302 / 603"], AMBER),
    ]
    for i, (tag, big, unit, rows, colour) in enumerate(cards):
        x = M + i * 3.05
        box(slide, x, 1.95, 2.9, 3.0, fill=CARD, line=BORDER, lw=0.9, radius=0.05)
        box(slide, x, 1.95, 2.9, 0.06, fill=colour, shape=MSO_SHAPE.RECTANGLE)
        text(slide, x + 0.24, 2.15, 1.6, 0.32, tag, size=13, color=colour, bold=True)
        text(slide, x + 0.24, 2.52, 2.4, 0.8, big, size=38, color=INK, bold=True)
        text(slide, x + 0.24, 3.28, 2.4, 0.3, unit, size=10.5, color=MUTED, bold=True)
        for j, line in enumerate(rows):
            text(slide, x + 0.24, 3.72 + j * 0.34, 2.5, 0.3, line, size=10.5, color=INK)
    rows = [["split", "D1", "D2"], ["train", "189", "2,112"], ["val", "28", "302"], ["test", "54", "603"]]
    table_block(slide, rows, M, 5.05, 6.15, [1.9, 2.1, 2.1], size=10.5, row_h=0.29)
    box(slide, 6.75, 1.95, 5.85, 2.35, fill=CARD_2, line=BORDER, lw=0.8, radius=0.05)
    text(slide, 7.0, 2.12, 5.4, 0.34, "THE CAVEAT", size=9.5, color=AMBER, bold=True)
    text(slide, 7.0, 2.50, 5.35, 1.7,
         "D2 is NOT an independent dataset — it is a 128 px augmentation of D1. "
         "Training on it and testing on D1 originals collapses: 8 of 10 checkpoints misclassify most images. "
         "We therefore treat D2 as a separate experiment, never as extra evidence.",
         size=11, color=INK, spacing=1.15)
    text(slide, 6.75, 4.45, 5.85, 0.55,
         "Frozen split: stratified 70 / 10 / 20, seed 42, committed as splits/D1.csv and splits/D2.csv.",
         size=10, color=MUTED, spacing=1.1)
    text(slide, 7.00, 5.10, 5.4, 0.26, "CLASS BALANCE — D1", size=8.5, color=MUTED, bold=True)
    split_bar(slide, 7.00, 5.42, 5.4, 0.22, [(136, "defect"), (135, "non-defect")], [AMBER, ACCENT],
              None)
    text(slide, 7.00, 5.90, 5.4, 0.26, "CLASS BALANCE — D2", size=8.5, color=MUTED, bold=True)
    split_bar(slide, 7.00, 6.22, 5.4, 0.22, [(947, "defect"), (2070, "non-defect")], [AMBER, ACCENT],
              None)


# ---------------------------------------------------------------- 8 coverage
def s08(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "02 · Scope", "We cover 66 of the 99 cells the paper reports", page, total)
    groups = [("D1", ACCENT), ("D2", ACCENT), ("D3", MUTED)]
    x0, y0 = 2.15, 2.35
    cell, gap = 0.20, 0.10
    for g, (name, colour) in enumerate(groups):
        text(slide, x0 + g * (3 * (cell + gap) + 0.28), y0 - 0.34, 1.6, 0.26, name,
             size=10, color=colour, bold=True)
    for i, backbone in enumerate(BACKBONES):
        y = y0 + i * 0.30
        text(slide, M, y - 0.02, 1.35, 0.24, backbone, size=8.5, color=INK, align=PP_ALIGN.RIGHT)
        for g in range(3):
            for k in range(3):
                public = g < 2
                cx = x0 + g * (3 * (cell + gap) + 0.28) + k * (cell + gap)
                box(slide, cx, y, cell, 0.19,
                    fill=ACCENT if public else CARD,
                    line=None if public else BORDER, lw=0.6, radius=0.25)
    legend_y = y0 + len(BACKBONES) * 0.30 + 0.14
    box(slide, x0, legend_y, 0.17, 0.17, fill=ACCENT, radius=0.2)
    text(slide, x0 + 0.25, legend_y - 0.04, 2.4, 0.26, "executed by us (66)", size=9, color=MUTED)
    box(slide, x0 + 2.65, legend_y, 0.17, 0.17, fill=WHITE, line=BORDER, lw=0.7, radius=0.2)
    text(slide, x0 + 2.90, legend_y - 0.04, 3.9, 0.26, "author-reported only — D3 not public (33)",
         size=9, color=MUTED)
    stat_cards(slide, [("66", "runs executed here"), ("33", "cells author-reported")],
               8.55, 2.25, 4.05, 1.35, value_size=26, label_size=9.5)
    box(slide, 8.55, 3.95, 4.05, 2.05, fill=CARD_2, line=BORDER, lw=0.8, radius=0.05)
    text(slide, 8.80, 4.12, 3.6, 0.32, "WHY THIS MATTERS", size=9.5, color=ACCENT, bold=True)
    text(slide, 8.80, 4.50, 3.55, 1.35,
         "A 100 % reproduction is impossible without the third dataset. "
         "We report 66/99 as coverage, and keep the author-reported cells in a "
         "separate column so the two are never confused.",
         size=10.5, color=INK, spacing=1.12)
    box(slide, M, 6.15, 11.88, 0.60, fill=CARD, line=BORDER, lw=0.7, radius=0.05)
    text(slide, M + 0.22, 6.26, 11.4, 0.4,
         "D3 (1,557 images) is referenced in the paper but has never been released — "
         "we could not run a single cell on it, so all 33 D3 cells remain author-reported.",
         size=10, color=MUTED)


# ---------------------------------------------------------------- 9 pipeline
def s09(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "02 · Method", "Frozen backbone, new head — the same recipe for all 11 models", page, total)
    bullets(slide, [
        "Freeze everything | every convolutional layer keeps its ImageNet weights and is never updated.",
        "Train a new head | AvgPool(4,4) → Flatten → Dense(64, ReLU) → Dropout(0.5) → Dense(2, softmax).",
        "One head for all | identical architecture and hyper-parameters, so the comparison is fair.",
        "Cache at 224 px | one run finishes in well under a minute on a T4.",
    ], M, 1.95, 5.55, 3.6, size=13.5, gap=12)
    image_card(slide, FIG / "fig_pipeline.png", 6.55, 1.85, 6.05, 4.85,
               caption="Figure 1 — pipeline: frozen ImageNet backbone + trained classification head")


# ---------------------------------------------------------------- 10 head
def s10(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "02 · Method", "The head is tiny: 33 k parameters for VGG16, 82 k for MobileNetV2", page, total)
    steps = [
        ("224 × 224", "input image", NAVY_SOFT),
        ("FROZEN", "ImageNet backbone", MUTED),
        ("AvgPool 4×4", "spatial average", ACCENT_DARK),
        ("Dense 64", "+ ReLU", ACCENT_DARK),
        ("Dropout 0.5", "regularisation", ACCENT_DARK),
        ("Softmax 2", "defect / ok", GREEN),
    ]
    n = len(steps)
    gap = 0.30
    cw = (W - 2 * M - (n - 1) * gap) / n
    y, ch = 2.10, 1.10
    for i, (head, sub, colour) in enumerate(steps):
        cx = M + i * (cw + gap)
        shp = box(slide, cx, y, cw, ch, fill=colour, radius=0.10)
        tf = shp.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = emu(0.05)
        tf.margin_right = emu(0.05)
        tf.margin_top = emu(0)
        tf.margin_bottom = emu(0)
        p1 = tf.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        r1 = p1.add_run()
        r1.text = head
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r1.font.name = FONT_BOLD
        r1.font.color.rgb = WHITE
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run()
        r2.text = sub
        r2.font.size = Pt(8.5)
        r2.font.name = FONT
        r2.font.color.rgb = WHITE
        if i < n - 1:
            box(slide, cx + cw + 0.055, y + ch / 2 - 0.11, gap - 0.11, 0.22,
                fill=RGBColor(0xC3, 0xD1, 0xDF), shape=MSO_SHAPE.RIGHT_ARROW)
    text(slide, M, 3.48, 11.88, 0.3,
         "only the last four blocks are trained -- everything left of AvgPool is frozen",
         size=10.5, color=MUTED, align=PP_ALIGN.CENTER)
    stat_cards(slide, [("32,962", "VGG16 head parameters"), ("82,114", "MobileNetV2 head parameters"),
                       ("100 %", "backbone frozen")],
               M, 4.05, 11.88, 1.35, value_size=26, label_size=9.5)
    box(slide, M, 5.70, 11.88, 0.95, fill=CARD, line=BORDER, lw=0.8, radius=0.05)
    text(slide, M + 0.25, 5.85, 11.4, 0.65,
         "Why this matters: with 189 training images, updating 2.2 M backbone parameters overfits immediately. "
         "Freezing turns the problem into fitting 33-82 k numbers -- that is what makes the small dataset work.",
         size=11, color=INK, spacing=1.12)


# ---------------------------------------------------------------- 11 protocol
def s11(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "02 · Protocol", "One protocol, ten metrics, deterministic evaluation", page, total)
    stat_cards(slide, [("11", "ImageNet backbones"), ("3", "Adam · SGD · RMSprop"),
                       ("2", "datasets (D1 / D2)"), ("1e-3", "learning rate")],
               M, 1.92, 11.88, 1.30, value_size=24, label_size=9)
    metrics = ["accuracy", "precision", "recall", "F1", "MCC", "kappa", "AUC", "mAP", "sensitivity", "specificity"]
    text(slide, M, 3.52, 6.0, 0.3, "TEN METRICS REPORTED ON TRAIN / VAL / TEST", size=9.5,
         color=ACCENT, bold=True)
    for i, m in enumerate(metrics):
        r, c = divmod(i, 5)
        chip(slide, M + c * 1.44, 3.88 + r * 0.52, 1.34, 0.40, m, size=10, color=INK)
    box(slide, 7.85, 3.52, 4.75, 2.35, fill=CARD_2, line=BORDER, lw=0.8, radius=0.05)
    text(slide, 8.08, 3.68, 4.3, 0.3, "PROTOCOL DETAILS", size=9.5, color=ACCENT, bold=True)
    text(slide, 8.08, 4.05, 4.3, 1.65,
         "Positive class = defect\n"
         "Confusion matrix: rows = truth, columns = prediction\n"
         "Epochs: 30 on D1, 50 on D2; batch 8 / 32\n"
         "Same seed (42) and same split for every run",
         size=10.5, color=INK, spacing=1.25)
    text(slide, M, 6.15, 11.88, 0.5,
         "Pseudo-code of one run is Algorithm 1 in the report; the evaluation script is in src/evaluate.py.",
         size=10.5, color=MUTED)


# ---------------------------------------------------------------- 12 divider 03
def s12(prs, page, total):
    divider(prs, "03", "Experiments and results",
            "66 runs on a Tesla T4, one environment, one frozen split — every number comes from the same CSV.",
            page, total)


# ---------------------------------------------------------------- 13 setup
def s13(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "03 · Setup", "66 runs, one environment — and a very narrow test set", page, total)
    stat_cards(slide, [("66", "runs completed"), ("10", "checkpoints kept"), ("54", "D1 test images"),
                       ("3,017", "D2 test+train images")],
               M, 1.95, 11.88, 1.35, value_size=26, label_size=9)
    rows = [["dataset", "train", "val", "test", "epochs", "batch"],
            ["D1", "189", "28", "54", "30", "8"],
            ["D2", "2,112", "302", "603", "50", "32"]]
    table_block(slide, rows, M, 3.65, 6.3, [1.3, 1.0, 0.9, 1.0, 1.0, 0.9], size=11, row_h=0.36)
    box(slide, 7.25, 3.60, 5.35, 1.85, fill=CARD_2, line=BORDER, lw=0.8, radius=0.05)
    text(slide, 7.50, 3.76, 4.9, 0.32, "THE HONEST LIMITATION", size=9.5, color=RED, bold=True)
    text(slide, 7.50, 4.12, 4.85, 1.20,
         "The D1 test set has 54 images, so one mistake costs 1.85 accuracy points. "
         "Any difference below ~0.02 in this deck is noise.",
         size=10.5, color=INK, spacing=1.12)
    text(slide, 7.25, 5.58, 5.35, 0.26, "ONE D1 TEST SET = 54 IMAGES (red = one error)", size=8.5,
         color=MUTED, bold=True)
    for i in range(54):
        r, c = divmod(i, 18)
        box(slide, 7.25 + c * 0.245, 5.88 + r * 0.245, 0.17, 0.17,
            fill=RED if i == 4 else RGBColor(0xC9, 0xD8, 0xE4), radius=0.2)
    text(slide, M, 6.35, 6.3, 0.4,
         "All 66 runs share configs/_template.yaml; results live in results/leaderboard.csv.",
         size=10, color=MUTED)


# ---------------------------------------------------------------- 14 backbones
def s14(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "03 · Results", "Five backbones reach 1.0000 on D1 — the weakest still reaches 0.93", page, total)
    image_card(slide, FIG / "fig_accuracy_by_model.png", M, 1.80, 7.35, 4.90,
               caption="Figure 2 — mean test accuracy over the three optimizers, per backbone")
    bullets(slide, [
        "D1 mean | 0.9826 across 33 runs",
        "D2 mean | 0.9849 across 33 runs",
        "Five at 1.0000 | VGG19, Xception, MobileNetV2, ResNet50, EfficientNet-B0",
        "Weakest | NASNetLarge 0.9259",
    ], 8.30, 2.00, 4.35, 3.0, size=12, gap=10)
    box(slide, 8.30, 4.85, 4.35, 1.65, fill=CARD_2, line=BORDER, lw=0.8, radius=0.05)
    text(slide, 8.52, 5.00, 3.95, 0.3, "READ THIS CAREFULLY", size=9, color=AMBER, bold=True)
    text(slide, 8.52, 5.32, 3.9, 1.05,
         "With 54 test images, 1.0000 and 0.9815 differ by a single photograph.",
         size=10.5, color=INK, spacing=1.12)


# ---------------------------------------------------------------- 15 optimizer
def s15(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "03 · Results", "Adam is the most consistent — and the backbone ranking does not move", page, total)
    image_card(slide, FIG / "fig_optimizer_heatmap.png", M, 1.80, 7.35, 4.90,
               caption="Figure 3 — test accuracy per backbone × optimizer")
    bullets(slide, [
        "Adam | stable across all 11 backbones and both datasets",
        "SGD | similar peaks, larger variance on heavy backbones",
        "RMSprop | sits between the two",
        "Conclusion | our comparison does not depend on the optimizer",
    ], 8.30, 2.00, 4.35, 3.2, size=12, gap=10)
    text(slide, 8.30, 5.55, 4.35, 1.0,
         "We report all three optimizers rather than cherry-picking the best column.",
         size=10.5, color=MUTED, spacing=1.15)


# ---------------------------------------------------------------- 16 errors
def s16(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "03 · Results", "Where the errors are — thin struts, low contrast, ambiguous parts", page, total)
    image_card(slide, FIG / "fig_confusion_grid.png", M, 1.80, 7.35, 4.90,
               caption="Figure 6 — confusion matrices of the ten kept checkpoints")
    bullets(slide, [
        "Most errors | one or two images per checkpoint, on ambiguous parts",
        "D2 checkpoints | collapse on D1 originals (128 px vs 5184 px) — never shipped",
        "False negatives | more expensive than false positives in production",
        "So the demo engine | uses a D1 checkpoint only",
    ], 8.30, 2.00, 4.35, 3.4, size=11.5, gap=9)


# ---------------------------------------------------------------- 17 paper
def s17(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "03 · Results", "We match most backbones and differ on the ones the paper broke", page, total)
    image_card(slide, FIG / "fig_delta_acc.png", M, 1.80, 6.55, 4.90,
               caption="Figure 5 — accuracy difference against the author-reported values")
    rows = [["dataset", "ours", "paper", "Δ"],
            ["D1 (all 11)", "0.9826", "0.7879", "+0.195"],
            ["D2 (all 11)", "0.9849", "0.8464", "+0.139"],
            ["D1 (excl. EffNet)", "0.9815", "0.8992", "+0.082"],
            ["D2 (excl. EffNet)", "0.9903", "0.9111", "+0.079"]]
    table_block(slide, rows, 7.50, 1.90, 5.10, [2.2, 1.2, 1.2, 1.0], size=10.5, row_h=0.34)
    text(slide, 7.50, 3.80, 5.10, 2.3,
         "The three EfficientNets report F1 = 0 in the paper (majority-class collapse), which inflates any "
         "overall comparison by ~11 points. Excluding those 18 cells we are +8 points ahead — a fair, modest result. "
         "Main suspect: the authors do not publish their split and normalise inputs with /255.",
         size=10.5, color=INK, spacing=1.15)
    chip(slide, 7.50, 6.15, 2.4, 0.42, "fair comparison, not a win", fill=CARD_2, color=AMBER, size=10, bold=True)


# ---------------------------------------------------------------- 18 divider 04
def s18(prs, page, total):
    divider(prs, "04", "Beyond the paper",
            "Three questions the paper never asks: is it leakage, what does the model look at, and what does it cost?",
            page, total)


# ---------------------------------------------------------------- 19 leakage
def s19(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "04 · Analysis", "Is the near-perfect accuracy just data leakage? Test says no", page, total)
    image_card(slide, FIG / "fig_leakage_combined.png", M, 1.80, 7.15, 3.85,
               caption="Figure 7 — random split vs source-grouped split, two training-set sizes")
    box(slide, 8.15, 1.85, 4.45, 0.95, fill=RGBColor(0xE8, 0xF5, 0xEE), line=GREEN, lw=1.0, radius=0.06)
    text(slide, 8.35, 2.02, 4.0, 0.34, "RESULT: NEGATIVE", size=11, color=GREEN, bold=True)
    text(slide, 8.35, 2.34, 4.0, 0.3, "no leakage effect detected", size=10, color=INK)
    bullets(slide, [
        "We rebuilt D2 | keeping source provenance for every augmented copy",
        "Two regimes | 2,087 and 313 training images",
        "Three backbones | six controlled runs",
    ], 8.15, 3.10, 4.45, 1.9, size=11, gap=9)
    box(slide, M, 5.90, 11.88, 0.62, fill=CARD, line=BORDER, lw=0.7, radius=0.05)
    text(slide, M + 0.22, 6.02, 11.4, 0.4,
         "Effect size: |Δaccuracy| ≤ 1.5 % and mostly negative, so the near-perfect scores are not explained by "
         "augmented copies leaking across the split — the task is simply easy for these features.",
         size=10, color=INK)
    text(slide, 8.15, 5.20, 4.45, 0.6,
         "A negative result, reported as such — the paper never runs this control.",
         size=10, color=MUTED, spacing=1.1)


# ---------------------------------------------------------------- 20 explainability
def s20(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "04 · Analysis", "Grad-CAM and LIME agree — but a 7 × 7 map is not a segmentation", page, total)
    image_card(slide, FIG / "gradcam_mobilenet_v2__D1__adam__s42.png", M, 1.66, 11.88, 1.72,
               caption="Grad-CAM — MobileNetV2 · D1 · Adam: defect samples (left) and correct rejections (right)")
    image_card(slide, FIG / "lime_mobilenet_v2__D1__adam__s42.png", M, 3.66, 5.55, 3.20,
               caption="LIME — same checkpoint: red supports the decision, blue contradicts it")
    box(slide, 6.55, 3.66, 6.05, 3.20, fill=CARD, line=BORDER, lw=0.8, radius=0.05)
    text(slide, 6.80, 3.82, 5.55, 0.3, "WHAT THE FIGURES DO AND DO NOT SHOW", size=9.5, color=ACCENT, bold=True)
    bullets(slide, [
        "Do show | both methods look at the printed part, not the background",
        "Do show | failures concentrate on thin struts and low-contrast regions",
        "Do not show | a mask, a box or an area — the map is 7 × 7 (≈32 px per cell)",
        "Do not show | a precise defect position, so we removed that claim from our UI",
    ], 6.80, 4.18, 5.55, 2.5, size=10.5, gap=8)


# ---------------------------------------------------------------- 21 cost
def s21(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "04 · Analysis", "Same accuracy at 1/58 the parameters — that decides the deployment", page, total)
    image_card(slide, FIG / "fig_efficiency.png", M, 1.80, 7.35, 4.55,
               caption="Figure 10 — parameters, FLOPs and measured latency (CPU and T4)")
    stat_cards(slide, [("22.9 ms", "MobileNetV2 on CPU"), ("165 ms", "VGG16 on CPU")],
               8.30, 1.90, 4.35, 1.25, value_size=22, label_size=8.5)
    bullets(slide, [
        "GPU | all 11 backbones under 40 ms per image",
        "CPU | only MobileNetV2 (22.9 ms) and EfficientNet-B0 (34.6 ms) stay real-time",
        "Size | 2.3 M vs 134 M parameters for equal accuracy",
        "Choice | MobileNetV2 powers the demo",
    ], 8.30, 3.35, 4.35, 2.5, size=11, gap=9)
    text(slide, 8.30, 5.95, 4.35, 0.7,
         "Accuracy alone would have picked VGG16 — a 134 M-parameter model for a 54-image test set.",
         size=10, color=MUTED, spacing=1.1)


# ---------------------------------------------------------------- 22 ablation
def s22(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "04 · Analysis", "What does freezing cost? The no-transfer ablation", page, total)
    stat_cards(slide, [("1.0000", "ImageNet + frozen (our method)"),
                       ("0.5000", "random init + frozen"),
                       ("1.0000", "random init, all params trained")],
               M, 1.92, 11.88, 1.45, value_size=25, label_size=9)
    text(slide, M, 3.50, 11.88, 0.28,
         "D1 test accuracy, mean over Adam / SGD / RMSprop (12 runs, same splits, same head, same epochs)",
         size=9.5, color=MUTED)
    bullets(slide, [
        "Frozen random features collapse | 0.5000 = predicting the majority class, F1 = 0.67, MCC = 0",
        "So freezing only works because of ImageNet | the weights, not the head, carry the signal",
        "But end-to-end training also hits 1.0000 | with 2.2 M trainable parameters and 30 epochs",
        "D2 shows the same pattern | 0.995 frozen, 0.772 random-frozen, 0.995 from scratch",
    ], M, 3.95, 6.05, 2.5, size=11, gap=9)
    box(slide, 7.00, 3.92, 5.60, 2.50, fill=CARD_2, line=BORDER, lw=0.8, radius=0.05)
    text(slide, 7.22, 4.06, 5.15, 0.3, "WHAT THIS MEANS FOR DEPLOYMENT", size=9.5, color=ACCENT, bold=True)
    text(slide, 7.22, 4.40, 5.15, 1.85,
         "Pre-training neither adds nor removes accuracy on this dataset — the task is easy enough that a "
         "scratch model reaches the ceiling too. What pre-training buys is cost: 33-82 k trainable parameters "
         "and about 30 s per run, instead of 2.2 M parameters and several minutes. That is why we ship the "
         "frozen variant.",
         size=10.5, color=INK, spacing=1.14)


# ---------------------------------------------------------------- 23 demo
def s23(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "04 · Demo", "The inspection station: upload → scan → verdict → log", page, total)
    bullets(slide, [
        "One action | load a part photo and press Scan",
        "Real animation | a laser sweep runs while the model infers (0.35 s on a laptop CPU)",
        "Verdict | PASS / FAIL with confidence, cycle time and an attention overlay",
        "Session | every inspection is logged; EXPORT CSV and CLEAR are one click away",
    ], M, 1.95, 5.35, 3.0, size=12.5, gap=11)
    card_x, card_y, card_w, card_h = 6.25, 1.75, 6.35, 3.95
    box(slide, card_x, card_y, card_w, card_h, fill=RGBColor(0x0D, 0x14, 0x1B), line=BORDER, lw=1.0, radius=0.03)
    text(slide, card_x + 0.3, card_y + 0.18, card_w - 0.6, 0.3, "LIVE VIEW  ·  CAM-01 · 224 × 224",
         size=9, color=CYAN_LIGHT, bold=True)
    inner = (card_x + 0.24, card_y + 0.58, card_w - 0.48, card_h - 1.05)
    box(slide, inner[0], inner[1], inner[2], inner[3], fill=RGBColor(0x06, 0x0B, 0x10),
        line=BORDER, lw=0.8, radius=0.02)
    picture_fit(slide, ROOT / "reports" / "assets" / "demo_client_ui.png",
                inner[0] + 0.02, inner[1] + 0.02, inner[2] - 0.04, inner[3] - 0.04, fit="cover")
    text(slide, card_x + 0.3, card_y + card_h - 0.42, card_w - 0.6, 0.3,
         "engine: MobileNetV2 · D1  ·  2.3 M parameters  ·  offline, no GPU", size=9, color=MUTED)
    text(slide, M, 5.95, 11.88, 0.7,
         "Live demo script: docs/DEMO.md (2:30). Fallback recording: 【TBD: demo_fallback.mp4】 if anything fails on stage.",
         size=10.5, color=MUTED, spacing=1.1)


# ---------------------------------------------------------------- 24 conclusions
def s24(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(slide, "05 · Conclusions", "What we would tell a production engineer", page, total)
    box(slide, M, 1.90, 5.80, 2.45, fill=CARD, line=BORDER, lw=0.8, radius=0.05)
    text(slide, M + 0.25, 2.05, 5.3, 0.32, "FINDINGS", size=9.5, color=GREEN, bold=True)
    bullets(slide, [
        "Frozen features are enough | 11 backbones, 66 runs, mean test accuracy 0.98",
        "Pre-training buys cost, not accuracy | from scratch also reaches 1.00 end-to-end",
        "Deploy small | MobileNetV2 matches VGG16 at 1/58 the parameters",
    ], M + 0.25, 2.42, 5.3, 1.8, size=11, gap=10, marker=GREEN)
    box(slide, 6.85, 1.90, 5.75, 2.45, fill=CARD, line=BORDER, lw=0.8, radius=0.05)
    text(slide, 7.08, 2.05, 5.3, 0.32, "LIMITATIONS", size=9.5, color=RED, bold=True)
    bullets(slide, [
        "Coverage | 66/99 cells; the third dataset is not public",
        "Independence | D2 is an augmentation of D1, not new evidence",
        "Statistics | 54 test images — one error is 1.85 points",
        "Scope | classification only; no box, no mask, no area",
    ], 7.08, 2.42, 5.3, 1.8, size=10.5, gap=6, marker=RED)
    stat_cards(slide, [("66", "runs · one environment"), ("0.98", "mean test accuracy"),
                       ("2.3 M", "parameters deployed")],
               M, 4.55, 11.88, 1.25, value_size=24, label_size=9)
    box(slide, M, 5.95, 11.88, 0.85, fill=NAVY, line=None, radius=0.05)
    text(slide, M + 0.28, 6.10, 6.4, 0.6,
         "Next: a small segmentation or anomaly-detection study — the only way to localise a defect honestly.",
         size=11, color=WHITE, spacing=1.15)
    text(slide, 8.10, 6.14, 4.3, 0.5, "github.com/Zheyi-D/am-defect-tl",
         size=10, color=CYAN_LIGHT, align=PP_ALIGN.RIGHT)


# ---------------------------------------------------------------- 25 closing
def s25(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg(slide, NAVY)
    box(slide, W - 4.6, -1.4, 6.4, 6.4, fill=NAVY_SOFT, radius=0.16)
    box(slide, 0, 0, 0.22, H, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
    text(slide, M + 0.15, 1.95, 8.4, 1.0, "Thank you", size=44, color=WHITE, bold=True)
    box(slide, M + 0.2, 3.05, 1.4, 0.05, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
    text(slide, M + 0.15, 3.32, 8.2, 0.5, "Questions and discussion", size=16, color=CYAN_LIGHT)
    text(slide, M + 0.15, 4.55, 8.2, 1.3,
         "Code, frozen splits, all 66 runs and the inspection demo:\ngithub.com/Zheyi-D/am-defect-tl",
         size=12.5, color=RGBColor(0xC7, 0xD6, 0xE4), spacing=1.3)
    text(slide, W - M - 1.2, 7.10, 1.2, 0.26, f"{page} / {total}", size=8.5,
         color=RGBColor(0x74, 0x8C, 0xA2), align=PP_ALIGN.RIGHT)


BUILDERS = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13,
            s14, s15, s16, s17, s18, s19, s20, s21, s22, s23, s24, s25]


def build(out: Path) -> Path:
    from pptx import Presentation
    from pptx.util import Inches

    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    total = len(BUILDERS)
    for i, fn in enumerate(BUILDERS, start=1):
        fn(prs, i, total)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the 25-slide presentation deck.")
    ap.add_argument("--out", type=Path, default=Path("reports/slides_draft.pptx"))
    args = ap.parse_args()
    path = build(args.out)
    print(f"[slides] wrote {path} ({len(BUILDERS)} slides, {path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
