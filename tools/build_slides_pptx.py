# Author: Kenneth + agent | Task: 24-slide deck, eight speakers, five groups, heavy on visuals
"""Build the group deck.

Structure is driven by the teacher's report outline (Sections 1-4) and by five work
groups, each covered by one or two speakers:

    INTRODUCTION        pages 3-4    speaker 1
    DATA PREPARATION    pages 5-8    speakers 2-3
    MODEL TRAINING      pages 9-15   speakers 4-5
    FRONT END           pages 16-17  speakers 6-7
    VALIDATION & DISC.  pages 18-22  speaker 8
    CONCLUSIONS         pages 23-24  speaker 8

No timing appears on the slides; budgets live in the speaker notes only.
All numbers come from the repository; figures come from reports/assets/.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Pt

from tools.deck_style import (
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
    RED,
    REPO,
    W,
    WHITE,
    bg,
    box,
    bullets,
    chip,
    cover,
    image_card,
    picture_fit,
    stat_cards,
    table_block,
    text,
)

ASSETS = ROOT / "reports" / "assets"
PARTS = 8
ROLE_COLOUR = {"WHAT": ACCENT, "WHY": AMBER, "RESULT": GREEN}


# ---------------------------------------------------------------- frame helpers
def frame(slide, part: int, group: str, title: str, page: int, total: int, accent=ACCENT) -> None:
    box(slide, 0, 0, W, 0.36, fill=NAVY, shape=MSO_SHAPE.RECTANGLE)
    box(slide, 0, 0.36, W, 0.05, fill=accent, shape=MSO_SHAPE.RECTANGLE)
    text(slide, 0.36, 0.065, 8.0, 0.26, f"PART {part} / {PARTS}   ·   {group}",
         size=10.5, color=WHITE, bold=True)
    text(slide, W - 3.6, 0.065, 3.2, 0.26, f"presenter 【NAME {part}】  ·  IDAT7215",
         size=9.5, color=CYAN_LIGHT, align=PP_ALIGN.RIGHT)
    text(slide, M, 0.62, W - 2 * M, 0.80, title, size=24, color=INK, bold=True, spacing=0.95)
    box(slide, M, 1.42, 1.1, 0.045, fill=accent, shape=MSO_SHAPE.RECTANGLE)
    box(slide, M, 7.04, W - 2 * M, 0.012, fill=BORDER, shape=MSO_SHAPE.RECTANGLE)
    text(slide, M, 7.12, 7.5, 0.26, REPO, size=8.5, color=MUTED)
    text(slide, W - 2.4, 7.12, 2.0, 0.26, f"{page} / {total}", size=9, color=MUTED,
         align=PP_ALIGN.RIGHT)


def wr(slide, x, y, kind, w=0.92, h=0.28):
    colour = ROLE_COLOUR[kind]
    box(slide, x, y, w, h, fill=WHITE, line=colour, lw=1.0, radius=0.25)
    text(slide, x, y, w, h, kind, size=8.5, color=colour, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def notes(slide, x, y, w, items, size=12.5, gap=0.16):
    cy = y
    for kind, body in items:
        lines = max(1, math.ceil(len(body) / max(12.0, w * 4.6)))
        h = 0.29 * lines + 0.14
        wr(slide, x, cy + 0.02, kind)
        text(slide, x + 1.06, cy, w - 1.06, h, body, size=size, color=INK, spacing=1.18)
        cy += h + gap
    return cy


def one_line(slide, y, s, size=11, colour=None):
    text(slide, M, y, W - 2 * M, 0.4, s, size=size, color=colour or MUTED)


def picture(slide, name, x, y, w, h, caption=None, caption_h=0.0):
    image_card(slide, ASSETS / name, x, y, w, h - caption_h, caption=caption)


# ---------------------------------------------------------------- pages
def s01(prs, page, total):
    cover(prs,
          "Python-Based Transfer Learning\nfor 3D Printed Object Defect Detection",
          "A reproducibility study of Ahsan et al., Expert Systems with Applications 253 (2024) 124293",
          ["Group 【GROUP NO.】  ·  【MEMBER NAMES】",
           "IDAT7215 Computer Programming for Product Development and Applications",
           "Eight speakers, five work groups  ·  【DATE】"])


def s02(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 1, "INTRODUCTION", "How this talk is organised", page, total)
    rows = [["part", "group", "what you will hear", "presenter"]]
    data = [
        ("1", "Introduction", "motivation, purpose, background, tools", "【NAME 1】"),
        ("2", "Data preparation", "the two datasets and why we use them", "【NAME 2】"),
        ("3", "Data preparation", "augmentation, preprocessing, the frozen split", "【NAME 3】"),
        ("4", "Model training", "transfer learning, the network, Algorithm 1", "【NAME 4】"),
        ("5", "Model training", "66 runs, results, what tuning does", "【NAME 5】"),
        ("6", "Front end", "the inspection station and its design choices", "【NAME 6】"),
        ("7", "Front end", "live demo", "【NAME 7】"),
        ("8", "Validation & conclusions", "agreement with the paper, three analyses, limitations", "【NAME 8】"),
    ]
    rows += [list(d) for d in data]
    table_block(slide, rows, M, 1.58, W - 2 * M, [0.65, 2.55, 6.6, 1.35], size=11, row_h=0.50)
    one_line(slide, 6.35, "Every part answers the same three questions: WHAT we did, WHY we did it, "
                          "and what RESULT it produced.", size=11.5)


def s03(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 1, "INTRODUCTION", "Motivation and purpose", page, total)
    picture(slide, "slide_samples.png", M, 1.58, 6.20, 3.30,
            caption="D1 — a defect (stringing) and a clean part")
    notes(slide, 7.20, 1.66, 5.25, [
        ("WHAT", "A binary classifier for 3D-printed parts: does the photo show a defect or not?"),
        ("WHY", "Manual inspection does not scale, and only 271 real photographs exist — far too few "
                "to train a CNN from scratch."),
        ("RESULT", "We reproduce a 2024 ESWA study of 11 ImageNet backbones (66 runs) and add three "
                   "analyses the paper does not report."),
    ], size=11.5)
    one_line(slide, 5.20, "Deliverables: report · this deck · source archive · a working inspection UI.",
             size=11)


def s04(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 1, "INTRODUCTION", "Background and the tools we used", page, total)
    picture(slide, "slide_timeline.png", M, 1.58, 11.88, 2.30, caption=None)
    box(slide, M, 4.10, 5.80, 2.10, fill=CARD, line=BORDER, lw=0.8, radius=0.05)
    text(slide, M + 0.24, 4.24, 5.3, 0.3, "BACKGROUND — THREE WAYS TO INSPECT", size=9.5,
         color=ACCENT, bold=True)
    text(slide, M + 0.24, 4.60, 5.3, 1.5,
         "① human visual inspection: cheap, slow, subjective\n"
         "② CT / ultrasound: accurate inside the part, expensive and slow\n"
         "③ camera + machine learning: fast and repeatable, but needs labelled images\n"
         "→ we take ③, and borrow ImageNet features because labels are scarce",
         size=10.5, color=INK, spacing=1.25)
    box(slide, 6.85, 4.10, 5.75, 2.10, fill=CARD_2, line=BORDER, lw=0.8, radius=0.05)
    text(slide, 7.08, 4.24, 5.3, 0.3, "PROPOSED TOOLS", size=9.5, color=ACCENT, bold=True)
    tools = ["Python 3.13", "PyTorch 2.11", "timm", "scikit-learn", "matplotlib",
             "Gradio", "Kaggle T4", "Git + CI"]
    for i, name in enumerate(tools):
        chip(slide, 7.08 + (i % 3) * 1.82, 4.62 + (i // 3) * 0.46, 1.70, 0.38, name,
             size=9.5, color=INK)
    one_line(slide, 6.35, "Everything runs on a free Kaggle GPU session; the demo runs on a laptop CPU.",
             size=10.5)


def s05(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 2, "DATA PREPARATION", "The two datasets we use", page, total)
    picture(slide, "slide_dataset_grid.png", M, 1.58, 11.88, 3.05,
            caption="D1 test samples — eight defects (top) and eight clean parts (bottom)")
    notes(slide, M, 5.05, 11.88, [
        ("WHAT", "D1: 271 real photographs, 136 defect / 135 clean, 5184 × 3456. "
                 "D2: 3,017 augmented copies, 947 / 2,070, 128 × 128."),
        ("WHY", "It is the public AM dataset: real parts, real defects, binary labels — and small "
                "enough that transfer learning is the only sensible approach."),
    ], size=11)


def s06(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 2, "DATA PREPARATION", "How we augment — and what it costs", page, total)
    picture(slide, "slide_augmentation.png", M, 1.56, 7.90, 2.95,
            caption="One source image → four of the eleven views used in D2")
    notes(slide, 8.70, 1.62, 3.85, [
        ("WHAT", "Rotation ±15°, horizontal flip, brightness jitter; 11 copies per source image."),
        ("WHY", "189 training photos are too few for a CNN."),
    ], size=10.5)
    notes(slide, M, 4.72, 11.88, [
        ("RESULT", "271 → 3,017 images, but D2 is downscaled to 128 × 128, its provenance was lost, "
                   "and copies are not new information — so D2 is reported separately and never "
                   "used as extra evidence."),
    ], size=11)


def s07(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 3, "DATA PREPARATION", "Preprocessing and the frozen split", page, total)
    picture(slide, "slide_pipeline.png", M, 1.54, 11.88, 1.95, caption=None)
    picture(slide, "slide_split.png", M, 3.66, 11.88, 2.20,
            caption="Every run uses exactly these three splits — 70 / 10 / 20, seed 42")


def s08(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 3, "DATA PREPARATION", "The number that limits every claim: 54", page, total)
    text(slide, M, 1.55, 6.0, 0.3, "D1 TEST SET = 54 IMAGES (red square = one mistake)",
         size=9.5, color=MUTED, bold=True)
    for i in range(54):
        r, c = divmod(i, 18)
        box(slide, M + c * 0.33, 1.92 + r * 0.33, 0.24, 0.24,
            fill=RED if i == 7 else RGBColor(0xC9, 0xD8, 0xE4), radius=0.2)
    notes(slide, 7.10, 1.62, 5.30, [
        ("WHY", "One wrong image costs 1.85 accuracy points, so differences below ~0.02 are noise."),
        ("RESULT", "1.0000 means \"all 54 correct\", not \"a perfect model\": the exact 95 % interval "
                   "for 54/54 is about [0.95, 1.00]. We never rank models on fractions of a percent."),
    ], size=11)
    one_line(slide, 5.95, "This is also why we validate against the paper by trend, not by cell-by-cell "
                          "comparison.", size=10.5)


def s09(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 4, "MODEL TRAINING", "Transfer learning: what it is and why we freeze", page, total)
    rows = [["", "train from scratch", "our setting"],
            ["initialisation", "random", "ImageNet weights"],
            ["conv layers", "all updated", "frozen (0 updated)"],
            ["trainable parameters", "2,305,986 (100 %)", "82,114 (3.56 %)"],
            ["time per run", "minutes", "under a minute"],
            ["risk on 189 images", "high", "low"]]
    table_block(slide, rows, M, 1.60, 6.55, [2.3, 2.1, 2.1], size=12, row_h=0.50)
    notes(slide, 7.55, 1.64, 4.90, [
        ("WHAT", "Keep every convolutional layer as ImageNet left it, and learn only a new "
                 "classification head on the final feature map."),
        ("WHY", "With 189 training images, updating millions of backbone parameters memorises the "
                "training set. Freezing turns the problem into fitting 82 thousand numbers."),
        ("RESULT", "Frozen + pre-trained reaches 1.0000 on D1 while training 3.56 % of the parameters."),
    ], size=11)


def s10(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 4, "MODEL TRAINING", "The whole network in one picture", page, total)
    image_card(slide, ASSETS / "slide_network.png", M, 1.60, 11.88, 3.05, caption=None)
    box(slide, M, 4.90, 11.88, 0.52, fill=CARD, line=BORDER, lw=0.7, radius=0.05)
    text(slide, M + 0.22, 5.00, 11.4, 0.32,
         "Blue = frozen ImageNet weights, never updated.   Green = the only part we train: "
         "82,114 parameters, 3.56 % of MobileNetV2.", size=10.5, color=INK)


def s11(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 4, "MODEL TRAINING", "Algorithm 1 — one training run", page, total)
    picture(slide, "slide_algorithm.png", M, 1.56, 11.55, 4.55, caption=None)
    one_line(slide, 6.30, "The same procedure runs for every one of the 66 cells: only the backbone, "
                          "the optimiser and the dataset change.", size=10.5)


def s12(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 4, "MODEL TRAINING", "The 66-run matrix", page, total)
    backbones = ["VGG16", "VGG19", "ResNet50", "ResNet101", "MobileNetV2", "Xception",
                 "InceptionResNetV2", "NASNetLarge", "EffNet-B0", "EffNet-B7", "EffNet-V2M"]
    opts = ["Adam", "SGD", "RMSprop"]
    x0, y0 = 1.95, 2.06
    cell, gap = 0.32, 0.10
    for d, ds in enumerate(("D1", "D2")):
        base = x0 + d * (3 * (cell + gap) + 0.55)
        text(slide, base - 0.10, y0 - 0.44, 1.6, 0.26, ds, size=11, color=ACCENT, bold=True)
        for k, o in enumerate(opts):
            text(slide, base + k * (cell + gap), y0 - 0.20, 0.36, 0.22, o[:3], size=8,
                 color=MUTED, align=PP_ALIGN.CENTER)
    for i, b in enumerate(backbones):
        y = y0 + i * 0.33
        text(slide, M, y - 0.02, 1.16, 0.24, b, size=8.5, color=INK, align=PP_ALIGN.RIGHT)
        for d in range(2):
            for k in range(3):
                cx = x0 + d * (3 * (cell + gap) + 0.55) + k * (cell + gap)
                box(slide, cx, y, cell, 0.24, fill=ACCENT, radius=0.25)
    text(slide, x0, y0 + len(backbones) * 0.33 + 0.16, 6.4, 0.28,
         "each square = one completed run (11 × 3 × 2 = 66)", size=9.5, color=MUTED)
    rows = [["setting", "value"], ["input", "224 × 224"], ["learning rate", "1e-3"],
            ["epochs", "30 / 50"], ["batch", "8 / 32"], ["seed", "42"]]
    table_block(slide, rows, 8.30, 1.62, 4.25, [1.7, 2.4], size=11, row_h=0.40)
    notes(slide, 8.30, 4.20, 4.25, [
        ("WHY", "Three optimisers × two datasets × eleven backbones is enough to separate the effect "
                "of the backbone from the effect of the training recipe."),
    ], size=10)


def s13(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 5, "MODEL TRAINING", "Reproducibility is part of the result", page, total)
    stat_cards(slide, [("66 / 66", "runs completed"), ("10", "checkpoints kept"),
                       ("522", "table values re-checked"), ("0", "mismatches")],
               M, 1.60, 11.88, 1.35, value_size=24, label_size=9)
    notes(slide, M, 3.30, 11.88, [
        ("WHAT", "Every run writes metrics.json, training curves, the confusion matrix and the trained "
                 "head; one script aggregates them into results/leaderboard.csv."),
        ("WHY", "Any number in the report must be traceable; every table is regenerated from the CSV "
                "and compared against the source."),
        ("RESULT", "Frozen splits, a CI job that compiles and runs the contract tests, and a "
                   "one-command rebuild of the whole matrix on Kaggle."),
    ], size=12)


def s14(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 5, "MODEL TRAINING", "Eleven backbones, one narrow band", page, total)
    picture(slide, "slide_backbones.png", M, 1.56, 11.88, 4.30, caption=None)
    notes(slide, M, 6.00, 11.88, [
        ("RESULT", "Mean test accuracy 0.9826 on D1 and 0.9849 on D2; five backbones reach 1.0000 and "
                   "the weakest still reaches 0.9259."),
    ], size=10.5)


def s15(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 5, "MODEL TRAINING", "What tuning actually does to the results", page, total)
    picture(slide, "slide_tuning.png", M, 1.54, 11.88, 3.95, caption=None)
    notes(slide, M, 5.62, 11.88, [
        ("WHY", "Optimiser choice moves the number by 0-4 points, and only for the weakest backbone; "
                "the ranking of backbones never changes. Epoch curves saturate by ~10 epochs, and the "
                "heavy model oscillates between 0.80 and 0.96 validation accuracy."),
        ("RESULT", "We did not sweep the learning rate — a limitation we state openly. What we can say "
                   "is that tuning shifts numbers, not conclusions: 0.98-1.00 is where every sensible "
                   "setting lands."),
    ], size=10.5)


def s16(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 6, "FRONT END", "From model to product: the inspection station", page, total)
    card_x, card_y, card_w, card_h = 6.05, 1.52, 6.55, 3.85
    box(slide, card_x, card_y, card_w, card_h, fill=RGBColor(0x0D, 0x14, 0x1B), line=BORDER,
        lw=1.0, radius=0.03)
    picture_fit(slide, ASSETS / "demo_client_ui.png", card_x + 0.10, card_y + 0.10,
                card_w - 0.20, card_h - 0.20, fit="cover")
    notes(slide, M, 1.58, 5.15, [
        ("WHAT", "Upload a photo, press Scan, get PASS/FAIL with confidence, cycle time and an "
                 "attention overlay; every inspection is logged and exportable."),
        ("WHY", "MobileNetV2 on D1: 2.3 M parameters, 22.9 ms on CPU, no GPU on site."),
        ("RESULT", "The engine never claims to localise a defect, hides dataset names and model "
                   "choices, and needs no network connection."),
    ], size=10.5)


def s17(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 7, "FRONT END", "Live demo — what we will show", page, total)
    steps = [
        ("1", "Load a defect photo", "PASS / FAIL appears with confidence and cycle time"),
        ("2", "Load a clean photo", "the verdict flips; the attention overlay moves"),
        ("3", "Show the log", "every inspection is recorded; export writes a CSV"),
        ("4", "Clear the session", "counters reset, the photo stays loaded"),
    ]
    for i, (num, head, body) in enumerate(steps):
        y = 1.58 + i * 0.86
        box(slide, M, y, 0.56, 0.56, fill=ACCENT, radius=0.15)
        text(slide, M, y, 0.56, 0.56, num, size=17, color=WHITE, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(slide, M + 0.80, y + 0.02, 3.6, 0.30, head, size=13, color=INK, bold=True)
        text(slide, M + 0.80, y + 0.34, 5.2, 0.30, body, size=10.5, color=MUTED)
    picture(slide, "demo_verdict.png", 6.55, 1.52, 2.85, 3.55, caption=None)
    box(slide, 9.60, 1.52, 3.00, 3.55, fill=CARD_2, line=BORDER, lw=0.8, radius=0.05)
    text(slide, 9.82, 1.68, 2.6, 0.3, "IF IT FAILS", size=9.5, color=AMBER, bold=True)
    text(slide, 9.82, 2.02, 2.60, 2.9,
         "A recorded walkthrough is kept as a fallback.\n\n"
         "The model runs offline: weights are cached, so no network request is made during inference.",
         size=10, color=INK, spacing=1.25)
    one_line(slide, 5.35, "Demo script (what to click, what to say) is in docs/DEMO.md.", size=10.5)


def s18(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 8, "VALIDATION & DISCUSSION", "Where we agree with the paper — and where we do not",
          page, total)
    picture(slide, "slide_delta.png", M, 1.50, 8.05, 4.05, caption=None)
    rows = [["dataset", "ours", "paper", "Δ"],
            ["D1 (all 11)", "0.983", "0.788", "+0.195"],
            ["D2 (all 11)", "0.985", "0.846", "+0.139"],
            ["D1 (no broken EffNet)", "0.982", "0.899", "+0.082"],
            ["D2 (no broken EffNet)", "0.990", "0.911", "+0.079"]]
    table_block(slide, rows, 8.85, 1.55, 3.65, [1.55, 0.85, 0.85, 0.8], size=9.5, row_h=0.34)
    notes(slide, 8.85, 3.45, 3.65, [
        ("WHY", "The raw gap is inflated: three EfficientNets report F1 = 0 (majority-class collapse). "
                "Excluding them we are +8 points ahead — a fair result, not a win."),
    ], size=9.5)
    one_line(slide, 5.65, "Main suspects for the rest: the authors do not publish their split, and "
                          "normalise inputs with /255 instead of per-backbone preprocessing.", size=10)


def s19(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 8, "VALIDATION & DISCUSSION", "Is the accuracy just leakage? No", page, total)
    picture(slide, "slide_leakage.png", M, 1.50, 7.85, 4.05, caption=None)
    box(slide, 8.60, 1.55, 3.90, 0.95, fill=RGBColor(0xE8, 0xF5, 0xEE), line=GREEN, lw=1.0, radius=0.06)
    text(slide, 8.82, 1.70, 3.4, 0.30, "RESULT: NEGATIVE", size=11, color=GREEN, bold=True)
    text(slide, 8.82, 2.02, 3.4, 0.30, "no leakage effect detected", size=10, color=INK)
    notes(slide, 8.60, 2.75, 3.90, [
        ("WHAT", "We rebuilt the augmented set keeping provenance, then compared a random split with "
                 "a split grouped by source image (6 controlled runs)."),
        ("WHY", "Copies of one photo must not sit on both sides of the split."),
        ("RESULT", "|Δacc| ≤ 1.5 %, mostly negative — the task is simply easy."),
    ], size=10)
    one_line(slide, 5.90, "We report this as a negative result; the paper never checks it.", size=10)


def s20(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 8, "VALIDATION & DISCUSSION", "Explainability: attention, not localisation", page, total)
    picture(slide, "slide_gradcam.png", M, 1.48, 7.95, 4.25, caption=None)
    notes(slide, 8.50, 1.55, 4.05, [
        ("WHAT", "Grad-CAM and LIME highlight the pixels that pushed the decision; both look at the "
                 "printed part, not the background."),
        ("WHY", "An operator wants to know where to look, but a whole-image classifier cannot give a mask."),
        ("RESULT", "The map is 7 × 7 (≈32 px per cell) and the head averages it with a 4 × 4 pool, so "
                   "it can only say \"around here\" — we removed the \"defect position\" marker from "
                   "our own UI for that reason."),
    ], size=10.5)


def s21(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 8, "VALIDATION & DISCUSSION", "Deployment cost decides the engine", page, total)
    picture(slide, "slide_efficiency.png", M, 1.50, 7.85, 4.10, caption=None)
    stat_cards(slide, [("22.9 ms", "MobileNetV2 · CPU"), ("165 ms", "VGG16 · CPU")],
               8.60, 1.55, 3.90, 1.10, value_size=20, label_size=8.5)
    notes(slide, 8.60, 2.85, 3.90, [
        ("WHAT", "Measured parameters, FLOPs and single-image latency on CPU and on a T4."),
        ("RESULT", "GPU: every backbone under 40 ms. CPU: only MobileNetV2 (22.9 ms) and "
                   "EfficientNet-B0 (34.6 ms) stay real-time — at the same accuracy."),
    ], size=10.5)


def s22(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 8, "VALIDATION & DISCUSSION", "How much is the pre-training worth?", page, total)
    picture(slide, "slide_ablation.png", M, 1.50, 8.05, 4.00, caption=None)
    notes(slide, 8.80, 1.58, 3.75, [
        ("WHAT", "12 extra runs: same data, same head, only the backbone initialisation changes."),
        ("RESULT", "Frozen random features collapse to 0.5000 (majority class), so freezing only works "
                   "because of the ImageNet weights."),
        ("RESULT", "But end-to-end training from scratch also reaches 1.0000 — pre-training buys cost "
                   "(82 k params, 30 s), not accuracy."),
    ], size=9.5)


def s23(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 8, "CONCLUSIONS", "What we would tell a production engineer", page, total)
    box(slide, M, 1.55, 5.80, 1.95, fill=CARD, line=BORDER, lw=0.8, radius=0.05)
    text(slide, M + 0.25, 1.70, 5.3, 0.3, "FINDINGS", size=9.5, color=GREEN, bold=True)
    bullets(slide, [
        "Frozen features are enough | 11 backbones, 66 runs, mean test accuracy 0.98",
        "Deploy small | MobileNetV2 matches VGG16 at 1/58 the parameters",
        "Pre-training buys cost | from scratch also reaches 1.00, at 27× the parameters",
    ], M + 0.25, 2.05, 5.3, 1.4, size=10, gap=6, marker=GREEN)
    box(slide, 6.85, 1.55, 5.75, 1.95, fill=CARD, line=BORDER, lw=0.8, radius=0.05)
    text(slide, 7.08, 1.70, 5.3, 0.3, "LIMITATIONS", size=9.5, color=RED, bold=True)
    bullets(slide, [
        "Statistics | 54 test images, one error is 1.85 points",
        "Splits | the authors' split is unpublished, so we compare trends",
        "Scope | classification only: no box, no mask, no area",
        "Tuning | we did not sweep the learning rate",
    ], 7.08, 2.05, 5.3, 1.4, size=9.5, gap=4, marker=RED)
    stat_cards(slide, [("66", "runs · one environment"), ("0.98", "mean test accuracy"),
                       ("2.3 M", "parameters deployed")],
               M, 3.75, 11.88, 1.10, value_size=22, label_size=9)
    box(slide, M, 5.15, 11.88, 0.90, fill=NAVY, line=None, radius=0.05)
    text(slide, M + 0.28, 5.32, 7.2, 0.58,
         "Next: a small segmentation or anomaly-detection study — the only honest way to localise a defect.",
         size=11, color=WHITE, spacing=1.15)
    text(slide, 8.40, 5.38, 4.0, 0.45, "github.com/Zheyi-D/am-defect-tl", size=10, color=CYAN_LIGHT,
         align=PP_ALIGN.RIGHT)


def s24(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg(slide, NAVY)
    box(slide, W - 4.6, -1.4, 6.4, 6.4, fill=RGBColor(0x14, 0x30, 0x4C), radius=0.16)
    box(slide, 0, 0, 0.22, H, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
    text(slide, M + 0.15, 1.95, 8.4, 1.0, "Thank you", size=44, color=WHITE, bold=True)
    box(slide, M + 0.2, 3.05, 1.4, 0.05, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
    text(slide, M + 0.15, 3.32, 8.2, 0.5, "Questions and discussion", size=16, color=CYAN_LIGHT)
    text(slide, M + 0.15, 4.55, 8.2, 1.3,
         "Code, frozen splits, all 66 runs and the inspection demo:\ngithub.com/Zheyi-D/am-defect-tl",
         size=12.5, color=RGBColor(0xC7, 0xD6, 0xE4), spacing=1.3)
    text(slide, W - 2.4, 7.12, 2.0, 0.26, f"{page} / {total}", size=9,
         color=RGBColor(0x74, 0x8C, 0xA2), align=PP_ALIGN.RIGHT)


BUILDERS = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12,
            s13, s14, s15, s16, s17, s18, s19, s20, s21, s22, s23, s24]


# ---------------------------------------------------------------- speaker notes
NOTES = [
    "PART 1 / 8 · presenter 【NAME 1】 · budget 0:20\nSay: the title, the paper (ESWA 253, 124293) "
    "and one sentence on what the group built.\nDo not read the group names or the course code aloud.",

    "PART 1 / 8 · presenter 【NAME 1】 · budget 0:35\nSay: eight parts, five work groups; every part "
    "answers WHAT / WHY / RESULT.\nDo not read the table row by row — point at the groups.",

    "PART 1 / 8 · presenter 【NAME 1】 · budget 0:50\nWHAT: binary classification of printed parts. "
    "WHY: manual inspection does not scale and only 271 real photos exist.\nRESULT: 66 runs, 0.98 mean "
    "accuracy, plus analyses the paper does not report.",

    "PART 1 / 8 · presenter 【NAME 1】 · budget 0:45\nBackground: three ways to inspect a printed part; "
    "we take camera + ML and borrow ImageNet features because labels are scarce.\nTools: PyTorch, timm, "
    "scikit-learn, matplotlib, Gradio, Kaggle T4, Git + CI.\nPoint at the timeline on the way in.",

    "PART 2 / 8 · presenter 【NAME 2】 · budget 0:45\nPoint at the grid: eight defects on top, eight "
    "clean parts below — the defect is stringing around the part.\nNumbers: D1 271 real (136/135); "
    "D2 3,017 augmented (947/2,070).\nSay explicitly that D2 is an augmentation of D1, not new data.",

    "PART 2 / 8 · presenter 【NAME 2】 · budget 0:45\nWHAT: rotation, flip, brightness, 11 copies per "
    "image. WHY: 189 training photos.\nRESULT: 271 → 3,017 but at 128 px, provenance lost, and copies "
    "are not new information.",

    "PART 3 / 8 · presenter 【NAME 3】 · budget 0:45\nWalk the five blocks, then the split bars.\nWHY: "
    "decoding a 5184 × 3456 JPEG costs ~80 s per epoch. RESULT: under a minute per run, and one frozen "
    "split for all 66 runs (189/28/54 and 2,112/302/603).",

    "PART 3 / 8 · presenter 【NAME 3】 · budget 0:45\nThis page is the caveat that limits every claim: "
    "54 test images, one mistake = 1.85 points.\n1.0000 means 'all 54 correct', and the 95 % interval "
    "for 54/54 is about [0.95, 1.00].",

    "PART 4 / 8 · presenter 【NAME 4】 · budget 0:40\nPoint at the two columns: scratch trains 2.3 M "
    "parameters, we train 82 k.\nWHY: with 189 images, updating the backbone memorises the training set.",

    "PART 4 / 8 · presenter 【NAME 4】 · budget 0:40\nWalk left to right and read the shapes under each "
    "block: 224×224×3 → 7×7×C → 1×1×C → 64 → 64 → 2.\nBlue = frozen, green = trained; 82,114 parameters "
    "= 3.56 % of MobileNetV2.",

    "PART 4 / 8 · presenter 【NAME 4】 · budget 0:40\nRead Algorithm 1 top to bottom: freeze the backbone, "
    "build the head, train the head only, evaluate 10 metrics on the frozen test split.\nStress that this "
    "exact procedure ran 66 times.",

    "PART 4 / 8 · presenter 【NAME 4】 · budget 0:40\nEach square is one completed run: 11 × 3 × 2 = 66.\n"
    "Then the hyper-parameters: 224 px, lr 1e-3, 30/50 epochs, batch 8/32, seed 42.",

    "PART 5 / 8 · presenter 【NAME 5】 · budget 0:35\n66/66 runs, 10 checkpoints, 522 table values "
    "re-checked with zero mismatches, frozen splits in the repository.\nThis is credibility, not content — "
    "keep it short.",

    "PART 5 / 8 · presenter 【NAME 5】 · budget 0:45\nRead the two means: 0.9826 on D1, 0.9849 on D2; "
    "five backbones at 1.0000, the weakest 0.9259.\nCaution: do not announce a winner.",

    "PART 5 / 8 · presenter 【NAME 5】 · budget 0:50\nOptimiser choice moves the number by 0-4 points and "
    "only for the weakest backbone; curves saturate by ~10 epochs.\nSay openly: we did not sweep the "
    "learning rate — tuning shifts numbers, not conclusions.",

    "PART 6 / 8 · presenter 【NAME 6】 · budget 0:45\nWalk the screenshot: photo in, scan, verdict with "
    "confidence and cycle time, session log.\nWHY MobileNetV2 on D1: 2.3 M parameters, 22.9 ms on CPU, "
    "offline. Never claims to localise a defect.",

    "PART 7 / 8 · presenter 【NAME 7】 · budget 2:00 (the live demo)\nFollow the four steps: defect photo → "
    "clean photo → show the log → clear.\nIf anything fails, switch to the recorded walkthrough and keep "
    "talking. Fallback: 【TBD: demo_fallback.mp4】.",

    "PART 8 / 8 · presenter 【NAME 8】 · budget 1:00\nWalk the delta chart, then explain the trap: three "
    "EfficientNets report F1 = 0, which inflates the gap.\nFair comparison: +8.2 on D1. Say 'fair "
    "comparison', never 'we beat them'.",

    "PART 8 / 8 · presenter 【NAME 8】 · budget 0:50\nWe rebuilt the augmented set with provenance and "
    "compared random vs source-grouped splits: |Δ| ≤ 1.5 %, mostly negative.\nA negative result, reported "
    "as such.",

    "PART 8 / 8 · presenter 【NAME 8】 · budget 0:45\nBoth Grad-CAM and LIME look at the part, not the "
    "background.\nBut the map is 7 × 7 and the head averages it with a 4 × 4 pool — 'around here' only, "
    "which is why we removed the marker from our UI.",

    "PART 8 / 8 · presenter 【NAME 8】 · budget 0:45\nMobileNetV2 22.9 ms on CPU versus VGG16 165 ms; on "
    "a GPU everything is under 40 ms.\nAt the same accuracy, MobileNetV2 is 58× smaller — that is the "
    "engine we ship.",

    "PART 8 / 8 · presenter 【NAME 8】 · budget 0:50\nFrozen random features collapse to 0.5000, so "
    "freezing only works because of the ImageNet weights.\nBut scratch also reaches 1.0000 — pre-training "
    "buys cost, not accuracy. Say it as a finding.",

    "PART 8 / 8 · presenter 【NAME 8】 · budget 0:45\nThree findings and four limitations, one sentence "
    "each.\nEnd on the limitation sentence and the honest next step: localisation needs segmentation or "
    "anomaly detection, which we did not do.",

    "PART 8 / 8 · presenter: all eight on stage · budget 0:20\nThank the audience, point at the repository "
    "link, and hand over to Q&A.",
]


def build(out: Path) -> Path:
    from pptx import Presentation
    from pptx.util import Inches

    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    total = len(BUILDERS)
    for i, fn in enumerate(BUILDERS, start=1):
        fn(prs, i, total)
    for note, slide in zip(NOTES, prs.slides):
        slide.notes_slide.notes_text_frame.text = note
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the 24-slide deck (8 speakers, 5 groups).")
    ap.add_argument("--out", type=Path, default=Path("reports/slides_draft.pptx"))
    args = ap.parse_args()
    path = build(args.out)
    print(f"[slides] wrote {path} ({len(BUILDERS)} slides, {path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
