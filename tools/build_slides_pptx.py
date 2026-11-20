# Author: Kenneth + agent | Task: 20-slide deck (brief background, deep data / training / testing, demo placeholder)
"""Build the group deck.

Focus requested by the team: say the background in one slide, then go deep on
(a) how the data is prepared, (b) how the model is trained, (c) how the results are
tested, and finish with a placeholder page for the live demo.

No timing on the slides (budgets live in the speaker notes only).
Every number comes from the repository; every figure from reports/assets/.
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
TITLE_SIZE = 28
BODY = 14
SMALL = 12


def frame(slide, part: int, group: str, title: str, page: int, total: int, accent=ACCENT) -> None:
    box(slide, 0, 0, W, 0.38, fill=NAVY, shape=MSO_SHAPE.RECTANGLE)
    box(slide, 0, 0.38, W, 0.055, fill=accent, shape=MSO_SHAPE.RECTANGLE)
    text(slide, 0.36, 0.07, 8.0, 0.27, f"PART {part} / {PARTS}   ·   {group}",
         size=12, color=WHITE, bold=True)
    text(slide, W - 3.9, 0.07, 3.5, 0.27, f"presenter 【NAME {part}】  ·  IDAT7215",
         size=10.5, color=CYAN_LIGHT, align=PP_ALIGN.RIGHT)
    text(slide, M, 0.64, W - 2 * M, 0.86, title, size=TITLE_SIZE, color=INK, bold=True, spacing=0.95)
    box(slide, M, 1.50, 1.2, 0.05, fill=accent, shape=MSO_SHAPE.RECTANGLE)
    box(slide, M, 7.06, W - 2 * M, 0.012, fill=BORDER, shape=MSO_SHAPE.RECTANGLE)
    text(slide, M, 7.14, 7.5, 0.26, REPO, size=10, color=MUTED)
    text(slide, W - 2.4, 7.14, 2.0, 0.26, f"{page} / {total}", size=10, color=MUTED,
         align=PP_ALIGN.RIGHT)


def wr(slide, x, y, kind, w=1.0, h=0.32):
    colour = ROLE_COLOUR[kind]
    box(slide, x, y, w, h, fill=WHITE, line=colour, lw=1.2, radius=0.25)
    text(slide, x, y, w, h, kind, size=10, color=colour, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def notes(slide, x, y, w, items, size=BODY, gap=0.18):
    cy = y
    for kind, body in items:
        lines = max(1, math.ceil(len(body) / max(12.0, w * 4.2)))
        h = 0.32 * lines + 0.16
        wr(slide, x, cy + 0.02, kind)
        text(slide, x + 1.16, cy, w - 1.16, h, body, size=size, color=INK, spacing=1.2)
        cy += h + gap
    return cy


def one_line(slide, y, s, size=12.5, colour=None):
    text(slide, M, y, W - 2 * M, 0.42, s, size=size, color=colour or MUTED)


def pic(slide, name, x, y, w, h, caption=None):
    image_card(slide, ASSETS / name, x, y, w, h, caption=caption)


# ------------------------------------------------------------------ pages
def s01(prs, page, total):
    cover(prs,
          "Python-Based Transfer Learning\nfor 3D Printed Object Defect Detection",
          "A reproducibility study of Ahsan et al., Expert Systems with Applications 253 (2024) 124293",
          ["Group 【GROUP NO.】  ·  【MEMBER NAMES】",
           "IDAT7215 Computer Programming for Product Development and Applications",
           "【DATE】"])


def s02(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 1, "INTRODUCTION", "Background and objective", page, total)
    box(slide, M, 1.62, 7.05, 3.05, fill=CARD, line=BORDER, lw=0.9, radius=0.05)
    text(slide, M + 0.28, 1.80, 6.5, 0.34, "BACKGROUND", size=11, color=ACCENT, bold=True)
    text(slide, M + 0.28, 2.20, 6.45, 3.20,
         "Three ways to inspect a 3D-printed part:\n"
         "① human visual inspection — cheap, slow, subjective\n"
         "② CT / ultrasound — sees inside, expensive and slow\n"
         "③ camera + machine learning — fast and repeatable, needs labelled images\n\n"
         "We take ③. Labelled defect photos are scarce (271 real images), so we reuse "
         "ImageNet features instead of training a CNN from scratch.",
         size=13, color=INK, spacing=1.30)
    box(slide, 8.00, 1.62, 4.60, 3.05, fill=CARD_2, line=BORDER, lw=0.9, radius=0.05)
    text(slide, 8.24, 1.80, 4.1, 0.34, "OBJECTIVE", size=11, color=GREEN, bold=True)
    text(slide, 8.24, 2.20, 4.10, 3.20,
         "Reproduce the paper's comparison of 11 frozen ImageNet backbones on 3D-printed "
         "defect classification, and measure what the deployment actually costs.",
         size=13, color=INK, spacing=1.30)
    stat_cards(slide, [("11", "backbones"), ("3", "optimisers"), ("2", "datasets"), ("66", "runs")],
               M, 5.00, 11.88, 1.05, value_size=24, label_size=10)


def s03(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 2, "DATA PREPARATION", "The two datasets", page, total)
    pic(slide, "slide_dataset_grid.png", M, 1.60, 11.88, 3.10,
        caption="D1 samples — eight defects (top) and eight clean parts (bottom)")
    notes(slide, M, 5.10, 11.88, [
        ("WHAT", "D1: 271 real photographs, 136 defect / 135 clean, 5184 × 3456."),
        ("WHAT", "D2: 3,017 augmented copies, 947 / 2,070, 128 × 128, generated from D1."),
    ], size=BODY)


def s04(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 2, "DATA PREPARATION", "How the augmented set is generated", page, total)
    pic(slide, "slide_augmentation.png", M, 1.58, 8.10, 2.95,
        caption="One source image and four of its eleven augmented views")
    notes(slide, 8.90, 1.64, 3.65, [
        ("WHAT", "Rotation ±15°, horizontal flip, brightness jitter — 11 copies per image."),
        ("WHY", "189 training photos are too few for a CNN."),
    ], size=SMALL)
    notes(slide, M, 4.75, 11.88, [
        ("RESULT", "271 → 3,017 images. The copies are 128 × 128 and come from the same 271 "
                   "photographs, so D2 measures robustness to those transforms, not new scenes."),
    ], size=BODY)


def s05(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 3, "DATA PREPARATION", "Preprocessing and the split", page, total)
    pic(slide, "slide_pipeline.png", M, 1.58, 11.88, 1.90)
    pic(slide, "slide_split.png", M, 3.72, 11.88, 2.20,
        caption="The same three splits are used by all 66 runs — 70 / 10 / 20, seed 42")
    one_line(slide, 6.30, "Images are cached once at 224 × 224; after that one training run takes "
                          "under a minute on a T4.", size=12.5)


def s06(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 4, "MODEL TRAINING", "Transfer learning: a frozen backbone and a small head", page, total)
    rows = [["", "train from scratch", "our setting"],
            ["initialisation", "random", "ImageNet weights"],
            ["conv layers", "all updated", "frozen (0 updated)"],
            ["trainable parameters", "2,305,986 (100 %)", "82,114 (3.56 %)"],
            ["time per run", "minutes", "under a minute"],
            ["accuracy on D1", "1.0000", "1.0000"]]
    table_block(slide, rows, M, 1.62, 6.75, [2.4, 2.1, 2.2], size=13, row_h=0.52)
    notes(slide, 7.85, 1.66, 4.60, [
        ("WHAT", "Every convolutional layer keeps its ImageNet weights and is never updated; only "
                 "the new classification head is trained."),
        ("WHY", "With 189 training images, updating millions of backbone parameters memorises the "
                "training set."),
        ("RESULT", "Frozen + pre-trained reaches 1.0000 on D1 while training 3.56 % of the parameters."),
    ], size=12)


def s07(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 4, "MODEL TRAINING", "The network", page, total)
    image_card(slide, ASSETS / "slide_network.png", M, 1.62, 11.88, 3.15, caption=None)
    box(slide, M, 5.00, 11.88, 0.60, fill=CARD, line=BORDER, lw=0.8, radius=0.05)
    text(slide, M + 0.24, 5.13, 11.4, 0.38,
         "Blue = frozen ImageNet weights.   Green = the only trained part: 82,114 parameters, "
         "3.56 % of MobileNetV2.", size=13, color=INK)


def s08(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 4, "MODEL TRAINING", "Algorithm 1 — one training run", page, total)
    pic(slide, "slide_algorithm.png", M, 1.58, 11.60, 4.60)
    one_line(slide, 6.35, "The same procedure is repeated for every cell of the experiment matrix; "
                          "only the backbone, optimiser and dataset change.", size=12.5)


def s09(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 4, "MODEL TRAINING", "The experiment matrix", page, total)
    backbones = ["VGG16", "VGG19", "ResNet50", "ResNet101", "MobileNetV2", "Xception",
                 "InceptionResNetV2", "NASNetLarge", "EffNet-B0", "EffNet-B7", "EffNet-V2M"]
    opts = ["Adam", "SGD", "RMSprop"]
    x0, y0 = 2.00, 2.12
    cell, gap = 0.34, 0.11
    for d, ds in enumerate(("D1", "D2")):
        base = x0 + d * (3 * (cell + gap) + 0.60)
        text(slide, base - 0.10, y0 - 0.48, 1.6, 0.28, ds, size=13, color=ACCENT, bold=True)
        for k, o in enumerate(opts):
            text(slide, base + k * (cell + gap), y0 - 0.22, 0.40, 0.22, o[:3], size=9,
                 color=MUTED, align=PP_ALIGN.CENTER)
    for i, b in enumerate(backbones):
        y = y0 + i * 0.34
        text(slide, M, y - 0.02, 1.20, 0.26, b, size=9.5, color=INK, align=PP_ALIGN.RIGHT)
        for d in range(2):
            for k in range(3):
                cx = x0 + d * (3 * (cell + gap) + 0.60) + k * (cell + gap)
                box(slide, cx, y, cell, 0.26, fill=ACCENT, radius=0.25)
    text(slide, x0, y0 + len(backbones) * 0.34 + 0.18, 7.0, 0.30,
         "each square = one completed run (11 × 3 × 2 = 66)", size=11, color=MUTED)
    rows = [["setting", "value"], ["input", "224 × 224"], ["learning rate", "1e-3"],
            ["epochs", "30 / 50"], ["batch", "8 / 32"], ["seed", "42"]]
    table_block(slide, rows, 8.35, 1.62, 4.25, [1.7, 2.4], size=12, row_h=0.42)


def s10(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 5, "TRAINING & TESTING", "What one run looks like, epoch by epoch", page, total)
    pic(slide, "slide_train_curves.png", M, 1.58, 11.88, 3.75)
    notes(slide, M, 5.48, 11.88, [
        ("WHAT", "MobileNetV2 · D1 · Adam, 30 epochs: training loss falls to ~0.01, validation "
                 "loss bottoms out around epoch 10 and then drifts up."),
        ("RESULT", "Accuracy saturates long before the last epoch, which is why the epoch budget only "
                   "matters for the heaviest backbones."),
    ], size=12)


def s11(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 5, "TRAINING & TESTING", "How the results are measured", page, total)
    pic(slide, "slide_confusion.png", M, 1.58, 7.55, 3.05)
    notes(slide, 8.25, 1.64, 4.30, [
        ("WHAT", "One pass over the frozen test split, then ten metrics and a 2x2 confusion matrix."),
        ("WHY", "One error on the 54-image D1 split costs 1.85 points, so accuracy alone is not enough."),
    ], size=SMALL)
    rows = [["metric", "metric"], ["accuracy", "MCC"], ["precision", "kappa"],
            ["recall", "AUC"], ["F1", "mAP"], ["sensitivity", "specificity"]]
    table_block(slide, rows, M, 4.85, 5.40, [2.6, 2.6], size=12, row_h=0.38)
    text(slide, 6.45, 4.90, 6.15, 1.90,
         "Positive class = defect; confusion rows are truth, columns are prediction.\n"
         "All 66 x 3 splits are written to results/leaderboard.csv, so every number in this deck can be"
         " traced back to one metrics.json.",
         size=12, color=INK, spacing=1.25)


def s12(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 5, "TRAINING & TESTING", "Results: eleven backbones", page, total)
    pic(slide, "slide_backbones.png", M, 1.58, 11.88, 4.40)
    one_line(slide, 6.18, "Mean test accuracy 0.9826 on D1 and 0.9849 on D2; five backbones reach "
                          "1.0000, the weakest 0.9259.", size=13)


def s13(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 5, "TRAINING & TESTING", "Results: what tuning changes", page, total)
    pic(slide, "slide_tuning.png", M, 1.56, 11.88, 4.10)
    notes(slide, M, 5.85, 11.88, [
        ("WHAT", "Left: three backbones × three optimisers. Right: validation accuracy of the "
                 "weakest backbone, epoch by epoch."),
        ("RESULT", "Optimiser choice moves the number by 0-4 points and only for the weakest "
                   "backbone; the backbone ranking never changes. Gradients were too coarse to sweep "
                   "the learning rate, which we state as a limitation."),
    ], size=12)


def s14(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 8, "RESULTS & VALIDATION", "Results against the reported values", page, total)
    pic(slide, "slide_delta.png", M, 1.52, 8.10, 4.10)
    rows = [["dataset", "ours", "paper", "Δ"],
            ["D1 (all 11)", "0.983", "0.788", "+0.195"],
            ["D2 (all 11)", "0.985", "0.846", "+0.139"],
            ["D1 (no broken EffNet)", "0.982", "0.899", "+0.082"],
            ["D2 (no broken EffNet)", "0.990", "0.911", "+0.079"]]
    table_block(slide, rows, 8.90, 1.56, 3.60, [1.55, 0.85, 0.85, 0.8], size=10, row_h=0.38)
    notes(slide, 8.90, 3.70, 3.60, [
        ("WHY", "Three EfficientNets report F1 = 0 in the paper, which inflates the overall gap. "
                "Excluding them we are +8 points ahead."),
    ], size=SMALL)


def s15(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 8, "RESULTS & VALIDATION", "Control: random split versus source-grouped split", page, total)
    pic(slide, "slide_leakage.png", M, 1.52, 8.10, 4.10)
    box(slide, 8.90, 1.58, 3.60, 0.95, fill=RGBColor(0xE8, 0xF5, 0xEE), line=GREEN, lw=1.1, radius=0.06)
    text(slide, 9.10, 1.74, 3.2, 0.32, "RESULT: NEGATIVE", size=12, color=GREEN, bold=True)
    text(slide, 9.10, 2.08, 3.2, 0.30, "no leakage effect detected", size=11, color=INK)
    notes(slide, 8.90, 2.80, 3.60, [
        ("WHAT", "The augmented set was rebuilt with source provenance, then trained twice: random "
                 "split and split grouped by source image (6 runs)."),
        ("RESULT", "|Δacc| ≤ 1.5 %, mostly negative — accuracy comes from the task, not from copies."),
    ], size=SMALL)


def s16(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 8, "RESULTS & VALIDATION", "What the model looks at", page, total)
    pic(slide, "slide_gradcam.png", M, 1.50, 8.05, 4.25)
    notes(slide, 8.85, 1.56, 3.70, [
        ("WHAT", "Grad-CAM maps of a defect sample and a clean sample, computed for the predicted class."),
        ("RESULT", "Attention sits on the printed part rather than the background. The last feature "
                   "map is 7 × 7 (≈32 px per cell) and is averaged by a 4 × 4 pool, so it indicates a "
                   "region, not a defect mask."),
    ], size=SMALL)


def s17(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 8, "RESULTS & VALIDATION", "Deployment cost", page, total)
    pic(slide, "slide_efficiency.png", M, 1.52, 7.90, 4.10)
    stat_cards(slide, [("22.9 ms", "MobileNetV2 · CPU"), ("165 ms", "VGG16 · CPU")],
               8.70, 1.58, 3.80, 1.15, value_size=24, label_size=10)
    notes(slide, 8.70, 2.95, 3.80, [
        ("WHAT", "Measured parameters, FLOPs and single-image latency on CPU and on a T4."),
        ("RESULT", "On a GPU every backbone is under 40 ms. On CPU only MobileNetV2 (22.9 ms) and "
                   "EfficientNet-B0 (34.6 ms) stay real-time at the same accuracy."),
    ], size=SMALL)


def s18(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 6, "DEMO", "Live demo", page, total, accent=GREEN)
    box(slide, M, 1.62, 7.35, 4.45, fill=RGBColor(0x0D, 0x14, 0x1B), line=BORDER, lw=1.2, radius=0.04)
    text(slide, M + 0.30, 1.78, 6.8, 0.34, "LIVE VIEW  ·  CAM-01 · 224 × 224", size=11,
         color=CYAN_LIGHT, bold=True)
    box(slide, M + 0.30, 2.20, 6.75, 3.55, fill=RGBColor(0x06, 0x0B, 0x10), line=BORDER, lw=0.9,
        radius=0.03)
    text(slide, M + 0.55, 3.70, 6.25, 0.9,
         "【 demo — screen placeholder 】", size=18, color=RGBColor(0x8F, 0xA6, 0xBA),
         align=PP_ALIGN.CENTER)
    notes(slide, 8.30, 1.70, 4.30, [
        ("WHAT", "Upload a photo, press Scan, read PASS / FAIL with confidence and cycle time."),
        ("WHAT", "Every inspection is appended to the session log and can be exported as CSV."),
        ("RESULT", "MobileNetV2 · D1 · Adam on a laptop CPU: 0.3-1.5 s per image, no GPU, no network."),
    ], size=12)
    text(slide, M, 6.30, 11.88, 0.4,
         "Fallback recording: 【TBD: demo_fallback.mp4】", size=12, color=MUTED)


def s19(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 8, "CONCLUSIONS", "Conclusions and limitations", page, total)
    box(slide, M, 1.58, 5.85, 2.00, fill=CARD, line=BORDER, lw=0.9, radius=0.05)
    text(slide, M + 0.26, 1.74, 5.3, 0.32, "CONCLUSIONS", size=11, color=GREEN, bold=True)
    bullets(slide, [
        "Frozen ImageNet features classify this task | 66 runs, mean test accuracy 0.98",
        "Deploy the small model | MobileNetV2 matches VGG16 at 1/58 the parameters",
        "Pre-training buys cost | scratch also reaches 1.00, at 27× the parameters",
    ], M + 0.26, 2.10, 5.3, 1.45, size=11.5, gap=6, marker=GREEN)
    box(slide, 6.90, 1.58, 5.70, 2.00, fill=CARD, line=BORDER, lw=0.9, radius=0.05)
    text(slide, 7.12, 1.74, 5.3, 0.32, "LIMITATIONS", size=11, color=RED, bold=True)
    bullets(slide, [
        "54 test images on D1 | one error is 1.85 points",
        "The authors' split is unpublished | we compare trends, not cell by cell",
        "Classification only | no bounding box, no mask, no area",
        "The learning rate was not swept",
    ], 7.12, 2.10, 5.3, 1.45, size=11, gap=3, marker=RED)
    stat_cards(slide, [("66", "runs"), ("0.98", "mean test accuracy"), ("2.3 M", "parameters deployed")],
               M, 3.85, 11.88, 1.15, value_size=24, label_size=10)
    box(slide, M, 5.25, 11.88, 0.95, fill=NAVY, line=None, radius=0.05)
    text(slide, M + 0.30, 5.42, 7.3, 0.62,
         "Next: segmentation or anomaly detection — the only way to report where a defect is.",
         size=12.5, color=WHITE, spacing=1.15)
    text(slide, 8.45, 5.48, 4.0, 0.5, "github.com/Zheyi-D/am-defect-tl", size=10.5,
         color=CYAN_LIGHT, align=PP_ALIGN.RIGHT)


def s20(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg(slide, NAVY)
    box(slide, W - 4.6, -1.4, 6.4, 6.4, fill=RGBColor(0x14, 0x30, 0x4C), radius=0.16)
    box(slide, 0, 0, 0.22, H, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
    text(slide, M + 0.15, 1.95, 8.4, 1.0, "Thank you", size=46, color=WHITE, bold=True)
    box(slide, M + 0.2, 3.10, 1.4, 0.05, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
    text(slide, M + 0.15, 3.38, 8.2, 0.5, "Questions and discussion", size=18, color=CYAN_LIGHT)
    text(slide, M + 0.15, 4.60, 8.2, 1.3,
         "Code, frozen splits, all 66 runs and the inspection demo:\ngithub.com/Zheyi-D/am-defect-tl",
         size=13.5, color=RGBColor(0xC7, 0xD6, 0xE4), spacing=1.3)
    text(slide, W - 2.4, 7.14, 2.0, 0.26, f"{page} / {total}", size=10,
         color=RGBColor(0x74, 0x8C, 0xA2), align=PP_ALIGN.RIGHT)


BUILDERS = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10,
            s11, s12, s13, s14, s15, s16, s17, s18, s19, s20]


NOTES = [
    "PART 1 / 8 · presenter 【NAME 1】 · budget 0:20\nTitle, the paper (ESWA 253, 124293) and one "
    "sentence on what the group built.",

    "PART 1 / 8 · presenter 【NAME 1】 · budget 0:50\nKeep this short: three ways to inspect a printed "
    "part, we take camera + ML, labels are scarce so we reuse ImageNet features.\nThen the objective: "
    "reproduce 11 backbones and measure the deployment cost. 11 × 3 × 2 = 66 runs.",

    "PART 2 / 8 · presenter 【NAME 2】 · budget 0:45\nPoint at the grid: eight defects (stringing) on "
    "top, eight clean parts below.\nNumbers: D1 271 real (136/135), 5184 × 3456; D2 3,017 augmented "
    "(947/2,070), 128 × 128.",

    "PART 2 / 8 · presenter 【NAME 2】 · budget 0:45\nRotation, flip and brightness; 11 copies per "
    "image → 271 becomes 3,017.\nBe precise: the copies are 128 px and come from the same 271 photos.",

    "PART 3 / 8 · presenter 【NAME 3】 · budget 0:50\nWalk the five preprocessing blocks, then the split "
    "bars: 189/28/54 and 2,112/302/603, seed 42, identical for all 66 runs.\nSay why the cache exists: "
    "decoding a 5184 × 3456 JPEG costs about 80 s per epoch.",

    "PART 4 / 8 · presenter 【NAME 4】 · budget 0:45\nLeft column trains 2.3 M parameters, right column "
    "82 k.\nWhy: with 189 images, updating the backbone memorises the training set.",

    "PART 4 / 8 · presenter 【NAME 4】 · budget 0:45\nRead the shapes left to right: 224×224×3 → 7×7×C → "
    "1×1×C → 64 → 64 → 2.\nBlue is frozen, green is trained: 82,114 parameters = 3.56 % of MobileNetV2.",

    "PART 4 / 8 · presenter 【NAME 4】 · budget 0:45\nRead Algorithm 1: freeze the backbone, build the "
    "head, train the head only, evaluate ten metrics on the frozen test split.\nThe same procedure ran "
    "66 times.",

    "PART 4 / 8 · presenter 【NAME 4】 · budget 0:45\nEach square is one completed run: 11 × 3 × 2 = 66.\n"
    "Then the hyper-parameters: 224 px, lr 1e-3, 30/50 epochs, batch 8/32, seed 42.",

    "PART 5 / 8 · presenter 【NAME 5】 · budget 0:45\nLeft: training loss keeps falling. Right: accuracy "
    "saturates after ~10 epochs, and validation loss drifts up after that — the epoch budget only "
    "matters for the heaviest backbones.",

    "PART 5 / 8 · presenter 【NAME 5】 · budget 0:50\nHow we test: one pass over the frozen test split, "
    "then ten metrics and a 2×2 confusion matrix; positive class is defect.\nPoint out why: on 54 test "
    "images one mistake costs 1.85 points, so accuracy alone is not enough.",

    "PART 5 / 8 · presenter 【NAME 5】 · budget 0:45\nRead the two means: 0.9826 on D1, 0.9849 on D2; "
    "five backbones at 1.0000, the weakest 0.9259.\nDo not announce a winner.",

    "PART 5 / 8 · presenter 【NAME 5】 · budget 0:50\nOptimiser choice moves the number by 0-4 points and "
    "only for the weakest backbone; the ranking never changes; curves oscillate for the heavy model.\n"
    "State the limitation: the learning rate was not swept.",

    "PART 8 / 8 · presenter 【NAME 8】 · budget 1:00\nWalk the delta chart, then the trap: three "
    "EfficientNets report F1 = 0, so the raw gap is inflated. Fair comparison: +8.2 points on D1.",

    "PART 8 / 8 · presenter 【NAME 8】 · budget 0:50\nThe augmented set was rebuilt with provenance and "
    "trained twice: random split vs split grouped by source image.\n|Δacc| ≤ 1.5 %, mostly negative — a "
    "negative control result.",

    "PART 8 / 8 · presenter 【NAME 8】 · budget 0:45\nAttention sits on the part, not the background.\n"
    "But the map is 7 × 7 with a 4 × 4 pooling step, so it marks a region, not a defect mask.",

    "PART 8 / 8 · presenter 【NAME 8】 · budget 0:45\nMobileNetV2 22.9 ms on CPU versus VGG16 165 ms; on "
    "a GPU everything is under 40 ms.\nAt equal accuracy MobileNetV2 is 58× smaller — that is the engine "
    "we deploy.",

    "PART 6 / 8 · presenter 【NAME 6】 with 【NAME 7】 operating · budget 2:00\nHand over to the live demo: "
    "load a defect photo, then a clean one, show the log, export the CSV.\nIf anything fails, play the "
    "fallback recording 【TBD: demo_fallback.mp4】 and keep talking.",

    "PART 8 / 8 · presenter 【NAME 8】 · budget 0:45\nThree conclusions and four limitations, one "
    "sentence each.\nEnd on the limitation: classification only, 54 test images, learning rate not "
    "swept.",

    "PART 8 / 8 · presenter: all eight on stage · budget 0:20\nThank the audience, point at the "
    "repository link, hand over to Q&A.",
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
    ap = argparse.ArgumentParser(description="Build the 20-slide deck.")
    ap.add_argument("--out", type=Path, default=Path("reports/slides_draft.pptx"))
    args = ap.parse_args()
    path = build(args.out)
    print(f"[slides] wrote {path} ({len(BUILDERS)} slides, {path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
