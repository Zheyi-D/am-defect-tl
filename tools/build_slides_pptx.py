# Author: Kenneth + agent | Task: 16-slide deck — data preparation, model training, results on the dataset
"""Build the group deck.

Scope agreed with the team: one short background slide, then only
    (a) how the data is prepared,
    (b) how the model is trained,
    (c) the results on the dataset,
and one placeholder page for the live demo.

Every content slide carries 60-90 words of plain factual text plus its figure.
No WHAT/WHY/RESULT labels, no methodology caveats, no process commentary.
Numbers come from the repository; figures from reports/assets/.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from tools.deck_style import (
    ACCENT,
    AMBER,
    BORDER,
    CARD,
    CARD_2,
    CYAN_LIGHT,
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


def para(slide, x, y, w, s, size=BODY, colour=None, spacing=1.32):
    text(slide, x, y, w, 3.2, s, size=size, color=colour or INK, spacing=spacing)


def pic(slide, name, x, y, w, h, caption=None):
    image_card(slide, ASSETS / name, x, y, w, h, caption=caption)


# ------------------------------------------------------------------ pages
def s01(prs, page, total):
    cover(prs,
          "Python-Based Transfer Learning\nfor 3D Printed Object Defect Detection",
          "Reproduction of Ahsan et al., Expert Systems with Applications 253 (2024) 124293",
          ["Group 【GROUP NO.】  ·  【MEMBER NAMES】",
           "IDAT7215 Computer Programming for Product Development and Applications",
           "【DATE】"])


def s02(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 1, "INTRODUCTION", "Background and objective", page, total)
    box(slide, M, 1.62, 5.85, 4.35, fill=CARD, line=BORDER, lw=0.8, radius=0.05)
    text(slide, M + 0.30, 1.80, 5.2, 0.34, "BACKGROUND", size=12, color=ACCENT, bold=True)
    para(slide, M + 0.30, 2.30, 5.25,
         "Fused-deposition 3D printing produces surface defects such as stringing, poor layer "
         "bonding and rough patches. Inspecting every part by eye is slow and subjective, and "
         "defect photographs are scarce: the public dataset used here contains only 271 real "
         "images.", size=17, spacing=1.55)
    box(slide, 6.95, 1.62, 5.65, 4.35, fill=CARD_2, line=BORDER, lw=0.8, radius=0.05)
    text(slide, 7.20, 1.80, 5.0, 0.34, "OBJECTIVE", size=12, color=GREEN, bold=True)
    para(slide, 7.20, 2.30, 5.05,
         "Because labels are few, a convolutional network is not trained from scratch. An "
         "ImageNet-pretrained backbone is frozen and only a small classification head is learned. "
         "The project reproduces the comparison of eleven such backbones and reports their "
         "accuracy on the dataset together with the training settings used.", size=17,
         spacing=1.55)


def s03(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 2, "DATA PREPARATION", "The two datasets", page, total)
    pic(slide, "slide_dataset_grid.png", M, 1.58, 11.88, 2.85,
        caption="D1 samples — eight defects (top) and eight clean parts (bottom)")
    box(slide, M, 4.75, 5.85, 1.95, fill=CARD, line=BORDER, lw=0.8, radius=0.05)
    text(slide, M + 0.26, 4.90, 5.3, 0.30, "D1 — REAL PHOTOGRAPHS", size=11, color=ACCENT, bold=True)
    para(slide, M + 0.26, 5.24, 5.32,
         "271 images (136 defect, 135 clean) at 5184 × 3456, all taken on the same rig. The defect "
         "appears as thin strands of extruded material around the part.", size=SMALL + 0.5)
    box(slide, 6.95, 4.75, 5.65, 1.95, fill=CARD_2, line=BORDER, lw=0.8, radius=0.05)
    text(slide, 7.20, 4.90, 5.2, 0.30, "D2 — AUGMENTED COPIES", size=11, color=AMBER, bold=True)
    para(slide, 7.20, 5.24, 5.12,
         "3,017 images (947 defect, 2,070 clean) at 128 × 128, generated from the 271 D1 photographs "
         "by rotation, flip and brightness changes.", size=SMALL + 0.5)


def s04(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 2, "DATA PREPARATION", "How the augmented set is generated", page, total)
    pic(slide, "slide_augmentation.png", M, 1.58, 8.10, 2.95,
        caption="One source image and four of its eleven augmented views")
    text(slide, 8.90, 1.66, 3.60, 0.32, "AUGMENTATION SETTINGS", size=11, color=ACCENT, bold=True)
    para(slide, 8.90, 2.02, 3.60,
         "Each source image is rotated by up to ±15°, mirrored horizontally, and brightened or "
         "darkened slightly. Eleven copies are produced per image, which turns 271 real photographs "
         "into 3,017 training images. The copies are stored at 128 × 128 and read back at 224 × 224 "
         "during training.", size=SMALL + 0.5)


def s05(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 3, "DATA PREPARATION", "Preprocessing and the train / val / test split", page, total)
    pic(slide, "slide_pipeline.png", M, 1.56, 11.88, 1.75)
    pic(slide, "slide_split.png", M, 3.45, 11.88, 1.95,
        caption="The same three splits are used by all 66 runs — 70 / 10 / 20, seed 42")
    para(slide, M, 5.95, 11.88,
         "Every image is resized to 224 × 224, normalised with the ImageNet mean and standard "
         "deviation, and written to a cache of small JPEG files, because decoding a 5184 × 3456 "
         "photograph costs about 80 seconds per epoch. The data is then split 70 / 10 / 20 with a "
         "fixed seed: D1 gives 189 / 28 / 54 images, D2 gives 2,112 / 302 / 603.", size=BODY)


def s06(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 4, "MODEL TRAINING", "Transfer learning: a frozen backbone and a new head", page, total)
    rows = [["", "from scratch", "our setting"],
            ["initialisation", "random", "ImageNet weights"],
            ["conv layers", "all updated", "frozen"],
            ["trainable parameters", "2,305,986", "82,114"],
            ["test accuracy on D2", "0.995", "0.995"]]
    table_block(slide, rows, M, 1.62, 6.45, [2.2, 2.0, 2.0], size=13, row_h=0.54)
    para(slide, 7.30, 1.68, 5.25,
         "The backbone keeps the weights it learned on ImageNet; every convolutional layer is "
         "frozen, so no gradient reaches it. A new head is added on top of the final feature map: "
         "4 × 4 average pooling, flatten, a fully connected layer with 64 units and ReLU, dropout "
         "0.5, and a two-unit softmax. Only those 82,114 parameters are trained. On D2 the frozen "
         "model matches a fully trained one while using 28 times fewer parameters.", size=12.5)


def s07(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 4, "MODEL TRAINING", "The network", page, total)
    image_card(slide, ASSETS / "slide_network.png", M, 1.60, 11.88, 3.20, caption=None)
    para(slide, M, 5.05, 11.88,
         "A 224 × 224 RGB image enters the frozen backbone and comes out as a 7 × 7 feature map with "
         "C channels (C depends on the backbone: 512 for VGG16, 2,048 for ResNet50). Average pooling "
         "reduces it to 1 × 1 × C, the map is flattened to a vector, and two fully connected layers "
         "produce the two class scores. The blue blocks are frozen and the green blocks are trained.",
         size=BODY)


def s08(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 4, "MODEL TRAINING", "Algorithm 1 — one training run", page, total)
    pic(slide, "slide_algorithm.png", M, 1.58, 11.55, 4.35)
    para(slide, M, 6.10, 11.88,
         "One run loads the pretrained backbone, freezes it, builds the head and then optimises the "
         "head only: the features are computed without gradients, the loss is cross-entropy, and the "
         "optimiser updates just the head parameters. Training and validation loss are recorded every "
         "epoch, and the final model is evaluated once on the held-out test split.", size=SMALL + 0.5)


def s09(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 4, "MODEL TRAINING", "Experimental setup", page, total)
    backbones = ["VGG16", "VGG19", "ResNet50", "ResNet101", "MobileNetV2", "Xception",
                 "IncResNetV2", "NASNetLarge", "EffNet-B0", "EffNet-B7", "EffNet-V2M"]
    opts = ["Ada", "SGD", "RMS"]
    x0, y0 = 2.10, 1.90
    cell, gap = 0.32, 0.11
    for d, ds in enumerate(("D1", "D2")):
        base = x0 + d * (3 * (cell + gap) + 0.55)
        text(slide, base - 0.06, y0 - 0.44, 1.2, 0.26, ds, size=12, color=ACCENT, bold=True)
        for k, o in enumerate(opts):
            text(slide, base + k * (cell + gap) - 0.04, y0 - 0.20, 0.34, 0.20, o, size=7.5,
                 color=MUTED, align=PP_ALIGN.CENTER)
    for i, b in enumerate(backbones):
        y = y0 + i * 0.365
        text(slide, M, y - 0.02, 1.24, 0.24, b, size=9, color=INK, align=PP_ALIGN.RIGHT)
        for d in range(2):
            for k in range(3):
                cx = x0 + d * (3 * (cell + gap) + 0.55) + k * (cell + gap)
                box(slide, cx, y, cell, 0.27, fill=ACCENT, radius=0.25)
    text(slide, x0 - 0.36, y0 + len(backbones) * 0.365 + 0.18, 5.8, 0.28,
         "each square = one completed run", size=10, color=MUTED)
    rows = [["setting", "value"], ["input size", "224 × 224"], ["learning rate", "1e-3"],
            ["epochs", "30 (D1) / 50 (D2)"], ["batch size", "8 (D1) / 32 (D2)"], ["seed", "42"]]
    table_block(slide, rows, 7.90, 1.60, 4.65, [1.9, 2.6], size=12.5, row_h=0.48)
    para(slide, 7.90, 5.00, 4.65,
         "Eleven backbones are combined with three optimisers on two datasets, giving 66 runs. Every "
         "run uses the same split, the same head and the same preprocessing, so the comparison between "
         "backbones is like for like.", size=SMALL + 0.5)


def s10(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 5, "TRAINING & RESULTS", "What one run looks like, epoch by epoch", page, total)
    pic(slide, "slide_train_curves.png", M, 1.58, 11.88, 3.55)
    para(slide, M, 5.30, 11.88,
         "This is MobileNetV2 on D1 with Adam. Training loss falls steadily to about 0.01 and "
         "training accuracy reaches 1.00 within ten epochs. Validation loss improves until roughly "
         "epoch 10 and then rises again, while validation accuracy stays flat between 0.96 and 1.00. "
         "The extra epochs therefore fit noise rather than adding information.", size=BODY)


def s11(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 5, "TRAINING & RESULTS", "Results: eleven backbones", page, total)
    pic(slide, "slide_backbones_d2.png", M, 1.56, 11.88, 4.05)
    para(slide, M, 5.80, 11.88,
         "On the D2 test split (603 images) the eleven backbones average 0.9849, ranging from "
         "0.920 for EfficientNet-V2M to 0.997 for Xception. VGG16, VGG19, MobileNetV2 and both "
         "EfficientNet-B variants stay above 0.990, while NASNetLarge and ResNet drop to 0.980 or "
         "below. The grey dots show the same ranking on D1, which has only 54 test images.", size=12.5)


def s12(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 5, "TRAINING & RESULTS", "Results: what tuning changes", page, total)
    pic(slide, "slide_tuning_d2.png", M, 1.56, 11.88, 4.05)
    para(slide, M, 5.80, 11.88,
         "Changing the optimiser moves test accuracy by 0 to 4 points, and the movement is visible "
         "only for the weakest backbone. For VGG16 and MobileNetV2 all three optimisers land within a "
         "fraction of a point, and the ordering of the backbones does not change. The right panel "
         "shows the validation curve of EfficientNet-V2M on D2, which oscillates between 0.86 and "
         "0.99 from epoch to epoch.", size=12.5)


def s13(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 5, "TRAINING & RESULTS", "Results compared with the reported values", page, total)
    pic(slide, "slide_delta.png", M, 1.52, 7.55, 3.70)
    rows = [["dataset", "ours", "paper", "Δ"],
            ["D1 (all 11)", "0.983", "0.788", "+0.195"],
            ["D2 (all 11)", "0.985", "0.846", "+0.139"],
            ["D1 (three bad cells out)", "0.982", "0.899", "+0.082"],
            ["D2 (three bad cells out)", "0.990", "0.911", "+0.079"]]
    table_block(slide, rows, 8.30, 1.56, 4.25, [1.75, 0.9, 0.85, 0.8], size=10, row_h=0.42)
    para(slide, 8.30, 3.60, 4.25,
         "Overall our accuracy is 19.5 points higher on D1 and 13.9 on D2. Most of that gap comes "
         "from three EfficientNet cells where the reported F1 is zero, which means the classifier "
         "predicted the majority class only. Leaving those out, the difference is +8.2 and +7.9 "
         "points, which is the fairer comparison. The remaining gap is explained by the unpublished "
         "split and by the input normalisation used in the paper.", size=SMALL)


def s14(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 6, "DEMO", "Live demo", page, total, accent=GREEN)
    box(slide, M, 1.62, 7.20, 4.35, fill=RGBColor(0x0D, 0x14, 0x1B), line=BORDER, lw=1.2, radius=0.04)
    text(slide, M + 0.28, 1.78, 6.6, 0.32, "LIVE VIEW  ·  CAM-01 · 224 × 224", size=11,
         color=CYAN_LIGHT, bold=True)
    box(slide, M + 0.28, 2.18, 6.65, 3.50, fill=RGBColor(0x06, 0x0B, 0x10), line=BORDER, lw=0.9,
        radius=0.03)
    text(slide, M + 0.50, 3.60, 6.20, 0.9, "【 demo — screen placeholder 】", size=18,
         color=RGBColor(0x8F, 0xA6, 0xBA), align=PP_ALIGN.CENTER)
    para(slide, 8.20, 1.68, 4.30,
         "The inspection interface loads a photograph, runs the frozen MobileNetV2 model on the CPU, "
         "and shows the verdict with its confidence and the time the inference took. The same screen "
         "keeps a log of every part inspected in the session, which can be exported as a CSV file. "
         "The demo runs locally without a GPU and without a network connection.", size=SMALL + 0.5)
    text(slide, M, 6.22, 11.88, 0.35, "Fallback recording: 【TBD: demo_fallback.mp4】", size=12,
         color=MUTED)


def s15(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    frame(slide, 8, "CONCLUSIONS", "Conclusions", page, total)
    bullets(slide, [
        "Frozen ImageNet features classify these parts | 66 runs, mean D2 test accuracy 0.9849, "
        "range 0.920 – 0.997 across eleven backbones",
        "Accuracy saturates | four backbones exceed 0.99 and the optimiser changes the score by at "
        "most 4 points, so the choice of backbone matters less than the data",
        "Small model for deployment | MobileNetV2 matches VGG16 at 0.995 accuracy with 2.3 M instead "
        "of 134 M parameters and 22.9 ms instead of 165 ms per image on a CPU",
    ], M, 1.68, 11.88, 3.10, size=16, gap=18)
    box(slide, M, 4.05, 11.88, 1.45, fill=CARD_2, line=BORDER, lw=0.8, radius=0.05)
    text(slide, M + 0.28, 4.20, 11.3, 0.30, "LIMITATION", size=11, color=AMBER, bold=True)
    para(slide, M + 0.28, 4.55, 11.3,
         "The D1 test split holds only 54 images, where a single mistake costs 1.85 accuracy points, "
         "and the learning rate was not swept. Both are noted so that the numbers are not over-read.",
         size=13)


def s16(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg(slide, NAVY)
    box(slide, W - 4.6, -1.4, 6.4, 6.4, fill=RGBColor(0x14, 0x30, 0x4C), radius=0.16)
    box(slide, 0, 0, 0.22, H, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
    text(slide, M + 0.15, 1.95, 8.4, 1.0, "Thank you", size=46, color=WHITE, bold=True)
    box(slide, M + 0.2, 3.10, 1.4, 0.05, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
    text(slide, M + 0.15, 3.38, 8.2, 0.5, "Questions and discussion", size=18, color=CYAN_LIGHT)
    text(slide, M + 0.15, 4.60, 8.2, 1.3,
         "Code, splits and all 66 runs:\ngithub.com/Zheyi-D/am-defect-tl",
         size=13.5, color=RGBColor(0xC7, 0xD6, 0xE4), spacing=1.3)
    text(slide, W - 2.4, 7.14, 2.0, 0.26, f"{page} / {total}", size=10,
         color=RGBColor(0x74, 0x8C, 0xA2), align=PP_ALIGN.RIGHT)


BUILDERS = [s01, s02, s03, s04, s05, s06, s07, s08,
            s09, s10, s11, s12, s13, s14, s15, s16]


NOTES = [
    "PART 1 / 8 · presenter 【NAME 1】 · budget 0:20\nTitle, the paper (ESWA 253, 124293) and one "
    "sentence on what the group did.",

    "PART 1 / 8 · presenter 【NAME 1】 · budget 0:50\nBackground: printed parts show stringing and poor "
    "layer bonding; inspection by eye is slow; only 271 real photographs exist.\nObjective: freeze an "
    "ImageNet backbone, train a small head, and reproduce the comparison of eleven backbones. Keep it "
    "short — the detail starts on the next slide.",

    "PART 2 / 8 · presenter 【NAME 2】 · budget 0:50\nPoint at the grid: eight defects on top, eight "
    "clean parts below; the defect is the thin extruded strands.\nD1: 271 real photos, 136/135, "
    "5184 × 3456. D2: 3,017 copies, 947/2,070, 128 × 128.",

    "PART 2 / 8 · presenter 【NAME 2】 · budget 0:45\nRotation ±15°, horizontal flip, brightness; "
    "eleven copies per image, so 271 photographs become 3,017 training images.\nCopies are stored at "
    "128 × 128 and read at 224 × 224.",

    "PART 3 / 8 · presenter 【NAME 3】 · budget 0:50\nWalk the five preprocessing blocks, then the "
    "split bars: resize to 224, ImageNet normalisation, cache, then 70/10/20 with seed 42.\nGive the "
    "split sizes: 189/28/54 on D1 and 2,112/302/603 on D2.",

    "PART 4 / 8 · presenter 【NAME 4】 · budget 0:50\nLeft column trains 2.3 M parameters, right "
    "column 82 k; every convolution layer is frozen.\nRead the head aloud: pooling, flatten, 64-unit "
    "layer with ReLU, dropout 0.5, two-unit softmax.\nOn D2 the frozen model matches the fully "
    "trained one.",

    "PART 4 / 8 · presenter 【NAME 4】 · budget 0:45\nWalk the diagram left to right and read the "
    "shapes: 224×224×3 → 7×7×C → 1×1×C → 64 → 2.\nBlue blocks are frozen, green blocks are trained.",

    "PART 4 / 8 · presenter 【NAME 4】 · budget 0:45\nRead Algorithm 1: freeze the backbone, build the "
    "head, compute features without gradients, update only the head, evaluate once on the test "
    "split.",

    "PART 4 / 8 · presenter 【NAME 4】 · budget 0:40\nEach square is one completed run: 11 backbones × "
    "3 optimisers × 2 datasets = 66, all with the same split and the same head.\nThen the shared "
    "settings: 224 px, lr 1e-3, 30/50 epochs, batch 8/32, seed 42.",

    "PART 5 / 8 · presenter 【NAME 5】 · budget 0:45\nMobileNetV2 on D1 with Adam: training loss falls "
    "to 0.01, accuracy reaches 1.00 in ten epochs, validation loss then rises while accuracy stays "
    "flat — the extra epochs fit noise.",

    "PART 5 / 8 · presenter 【NAME 5】 · budget 0:50\nRead the D2 numbers: mean 0.9849 over 603 test "
    "images, from 0.920 for EffNet-V2M to 0.997 for Xception; VGG16, VGG19 and MobileNetV2 are above "
    "0.990.\nThe grey dots are the same ranking on the 54-image D1 split.",

    "PART 5 / 8 · presenter 【NAME 5】 · budget 0:50\nThe optimiser moves the score by 0-4 points and "
    "only for the weakest backbone; the backbone ranking never changes.\nThe right panel shows "
    "EffNet-V2M on D2 oscillating between 0.86 and 0.99 from epoch to epoch.",

    "PART 5 / 8 · presenter 【NAME 5】 · budget 0:50\nOverall we are +19.5 on D1 and +13.9 on D2, but "
    "three EfficientNet cells report F1 = 0 in the paper, so the fair comparison is +8.2 and "
    "+7.9.\nThe rest is explained by the unpublished split and the paper's input normalisation.",

    "PART 6 / 8 · presenter 【NAME 6】, operated by 【NAME 7】 · budget 2:00\nHand over to the live demo: "
    "load a defect photo, then a clean one, show the verdict with confidence and cycle time, then the "
    "session log and the CSV export.\nIf anything fails, play the fallback recording "
    "【TBD: demo_fallback.mp4】 and keep talking.",

    "PART 8 / 8 · presenter 【NAME 8】 · budget 0:50\nThree conclusions: frozen features are enough "
    "(0.9849 on D2); accuracy saturates, so the optimiser matters less than the data; MobileNetV2 "
    "matches VGG16 with 58× fewer parameters.\nThen the limitation: 54 D1 test images and no learning-"
    "rate sweep.",

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
    ap = argparse.ArgumentParser(description="Build the 16-slide deck.")
    ap.add_argument("--out", type=Path, default=Path("reports/slides_draft.pptx"))
    args = ap.parse_args()
    path = build(args.out)
    print(f"[slides] wrote {path} ({len(BUILDERS)} slides, {path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
