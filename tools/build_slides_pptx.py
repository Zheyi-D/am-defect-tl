# Author: Kenneth | Task: build the 15-slide presentation skeleton
"""Build a 15-slide presentation skeleton (titles, bullet placeholders, speaker notes).

Output: slides_draft.pptx  (then uploaded to the cloud document service as the shared deck)

Usage:
    python tools/build_slides_pptx.py --out slides_draft.pptx
"""

from __future__ import annotations

import argparse
from pathlib import Path

# (slide title, [bullet placeholders], speaker note with time budget)
SLIDES: list[tuple[str, list[str], str]] = [
    (
        "Python-Based Transfer Learning for 3D Printed Object Defect Detection",
        [
            "A Reproducibility Study of Ahsan et al. (2024)",
            "",
            "IDAT7215 Computer Programming for Product Development and Applications",
            "Group <number>  |  <member names>",
            "<date>",
        ],
        "Title slide. 0:00-0:20. Presenter: <name>. State the paper, the task, and the group.",
    ),
    (
        "Agenda",
        [
            "1. Motivation and objectives",
            "2. Dataset and method",
            "3. Experimental setup (66 runs)",
            "4. Results and discussion",
            "5. Our analysis: leakage, explainability, cost",
            "6. Conclusions and recommendations",
        ],
        "0:20-0:50. Presenter: <name>. One sentence per block; do not read the list.",
    ),
    (
        "1. Motivation: why inspect 3D-printed parts automatically?",
        [
            "Additive manufacturing produces defects (stringing, poor layer adhesion) that are hard to spot visually.",
            "Manual inspection does not scale; a camera plus a classifier can.",
            "Deep learning needs large labelled datasets, but defect images are scarce.",
            "Transfer learning from ImageNet is the standard answer for small datasets - but how much does it help?",
        ],
        "0:50-2:00. Presenter: <name>.",
    ),
    (
        "2. Objectives: reproduce Ahsan et al. (2024)",
        [
            "Reproduce the comparison of 11 ImageNet backbones on 3D-printed defect classification.",
            "Reproduce the optimizer ablation (Adam / SGD / RMSprop).",
            "Go beyond the paper: data-leakage control, explainability, deployment cost.",
            "Deliver a fully reproducible pipeline (code + frozen splits + readme).",
        ],
        "2:00-2:50. Presenter: <name>.",
    ),
    (
        "3. Dataset: D1 (real) and D2 (augmented)",
        [
            "D1: 271 real photographs (136 defect / 135 non-defect), 5184 x 3456.",
            "D2: 3,017 augmented images (947 / 2,070), 128 x 128 - derived from D1, not independent.",
            "Stratified split 70 / 10 / 20, seed 42, frozen in splits/*.csv.",
            "The paper's third dataset (1,557 images) is not public -> we cover 66 of 99 cells.",
        ],
        "2:50-4:00. Presenter: <name>. Refer to Table 1.",
    ),
    (
        "4. Method: transfer-learning pipeline",
        [
            "Pre-trained ImageNet CNN, all convolutional layers frozen.",
            "New head trained from scratch: AvgPool(4,4) - Flatten - Dense(64) - Dropout(0.5) - Dense(2).",
            "Same head for all 11 backbones -> comparison is fair.",
            "Images cached at 224 x 224; head-only training keeps each run under a few minutes.",
        ],
        "4:00-5:20. Presenter: <name>. Refer to Figure 1.",
    ),
    (
        "5. Method: training protocol and metrics",
        [
            "Optimizers: Adam, SGD, RMSprop (shared learning rate and epoch budget per dataset).",
            "Head-only training: backbone parameters never updated.",
            "Ten metrics reported on train / val / test (accuracy, precision, recall, F1, MCC, kappa, AUC, mAP, sensitivity, specificity).",
            "Positive class = defect.",
        ],
        "5:20-6:30. Presenter: <name>. Refer to Algorithm 1.",
    ),
    (
        "6. Experimental setup: 66 runs",
        [
            "11 backbones x 3 optimizers x 2 datasets = 66 runs.",
            "Every run stores metrics.json, confusion matrices, training curves and the trained head.",
            "All numbers reported in this talk come from results/leaderboard.csv.",
        ],
        "6:30-7:00. Presenter: <name>.",
    ),
    (
        "7. Results: model comparison",
        [
            "Xception, MobileNetV2 and InceptionResNetV2 reproduce the paper within 0.02 accuracy.",
            "ResNet50/101 and VGG16/19 are clearly better than the reported values.",
            "EfficientNet family: the paper reports F1 = 0 (majority-class collapse); we reach 0.98-1.00.",
            "D1 test set has only 54 images -> differences within ~0.02 are not meaningful.",
        ],
        "7:00-8:10. Presenter: <name>. Refer to Figures 2 and 6, Tables 2-3.",
    ),
    (
        "8. Results: optimizer ablation",
        [
            "Adam is the most consistent choice across backbones.",
            "SGD and RMSprop are close but less stable on the heaviest backbones.",
            "The ranking of backbones is stable across optimizers.",
        ],
        "8:10-8:50. Presenter: <name>. Refer to Figure 3.",
    ),
    (
        "9. Results: where we disagree with the paper",
        [
            "Overall accuracy is higher in our reproduction (mean delta per dataset).",
            "Most likely cause: the authors normalise all inputs with /255, while EfficientNet expects its own preprocessing.",
            "We therefore report deltas but do not claim to be strictly better.",
            "Numbers are given per backbone in Table 4.",
        ],
        "8:50-9:40. Presenter: <name>. Refer to Figure 5 and Table 4.",
    ),
    (
        "10. Our analysis (i): data-leakage control experiment",
        [
            "Tested whether the near-perfect accuracy is caused by leakage from augmented copies.",
            "Built D2' ourselves, keeping source provenance, and compared random vs source-grouped splits.",
            "Two training-set regimes (2,087 and 313 images) and three backbones.",
            "Result: no consistent leakage effect (|delta| <= 1.5%, mostly negative) -> the task is simply easy.",
        ],
        "9:40-10:40. Presenter: <name>. Refer to Figure 7 and Table 6.",
    ),
    (
        "11. Our analysis (ii): explainability",
        [
            "Grad-CAM shows the classifier focuses on the printed part rather than the background in most cases.",
            "Failure cases concentrate on thin struts and low-contrast regions.",
            "LIME agrees with Grad-CAM on the same samples.",
        ],
        "10:40-11:40. Presenter: <name>. Refer to Figures 8 and 9.",
    ),
    (
        "12. Our analysis (iii): deployment cost",
        [
            "On a T4 GPU all 11 models run below 40 ms per image (at least 25 FPS).",
            "On CPU only MobileNetV2 (22.9 ms) and EfficientNet-B0 (34.6 ms) stay real-time.",
            "Model choice therefore depends on the deployment hardware, not only on accuracy.",
        ],
        "11:40-12:30. Presenter: <name>. Refer to Figure 10 and Table 5.",
    ),
    (
        "13. Conclusions, recommendations and limitations",
        [
            "Transfer learning with a frozen backbone is sufficient for this task: 11 models exceed 0.92 test accuracy.",
            "Recommendation: on edge/CPU hardware use MobileNetV2 or EfficientNet-B0; with a GPU any backbone works.",
            "Limitation: the paper's third dataset is unavailable; D2 is an augmentation of D1.",
            "Full code, frozen splits and results: https://github.com/Zheyi-D/am-defect-tl",
        ],
        "12:30-14:00. Presenter: <name>. Then hand over to Q&A (5 minutes).",
    ),
]


def build(out: Path) -> Path:
    from pptx import Presentation
    from pptx.util import Inches, Pt

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    title_layout = prs.slide_layouts[0]
    content_layout = prs.slide_layouts[1]

    for index, (title, bullets, note) in enumerate(SLIDES):
        if index == 0:
            slide = prs.slides.add_slide(title_layout)
            slide.shapes.title.text = title
            slide.shapes.title.text_frame.paragraphs[0].font.size = Pt(28)
            body = slide.placeholders[1].text_frame
            body.text = bullets[0]
            for line in bullets[1:]:
                para = body.add_paragraph()
                para.text = line
                para.font.size = Pt(14)
        else:
            slide = prs.slides.add_slide(content_layout)
            slide.shapes.title.text = title
            slide.shapes.title.text_frame.paragraphs[0].font.size = Pt(26)
            body = slide.placeholders[1].text_frame
            body.text = bullets[0]
            for line in bullets[1:]:
                para = body.add_paragraph()
                para.text = line
                para.level = 0
                para.font.size = Pt(16)

        slide.notes_slide.notes_text_frame.text = note

    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the 15-slide presentation skeleton.")
    ap.add_argument("--out", type=Path, default=Path("slides_draft.pptx"))
    args = ap.parse_args()
    path = build(args.out)
    print(f"[slides] wrote {path} ({len(SLIDES)} slides, {path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
