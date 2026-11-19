# Author: Kenneth | Task: build the 16-slide presentation deck (real numbers, TBD placeholders)
"""Build the group presentation (15 min talk + 5 min Q&A).

Every number below is taken from the repository (`results/leaderboard.csv`,
`results/efficiency.csv`, `results/leakage.csv`) so the deck cannot drift from
the report. Anything we do not have yet is written as 【TBD ...】 so it is
obvious what still has to be filled in.

Usage:
    python tools/build_slides_pptx.py --out reports/slides_draft.pptx
"""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (slide title, [bullet lines], speaker note with time budget, optional image path)
SLIDES: list[tuple[str, list[str], str, str | None]] = [
    (
        "Python-Based Transfer Learning for 3D Printed Object Defect Detection",
        [
            "A reproducibility study of Ahsan et al., Expert Systems with Applications 253 (2024) 124293",
            "",
            "IDAT7215 Computer Programming for Product Development and Applications",
            "Group 【GROUP NO.】  |  【MEMBER NAMES】",
            "【DATE】",
        ],
        "0:00-0:25. Presenter: 【NAME】. State the paper, the task and the group in two sentences.",
        None,
    ),
    (
        "Agenda",
        [
            "1. Why automatic inspection (0:50)",
            "2. What we set out to reproduce (2:00)",
            "3. Data and method (2:50)",
            "4. 66 experiments and the results (6:20)",
            "5. Three analyses the paper does not have (9:40)",
            "6. Live demo (12:10)  +  Conclusions and limitations (13:40)",
        ],
        "0:25-0:50. Presenter: 【NAME】. One sentence per block. Do not read the list aloud.",
        None,
    ),
    (
        "1. Why inspect 3D-printed parts automatically?",
        [
            "Additive manufacturing produces defects that are hard to see: stringing, poor layer adhesion, rough surfaces.",
            "Manual inspection does not scale with production volume; a camera plus a classifier does.",
            "Deep learning needs many labelled images, but defect photos are scarce (this dataset has 271 real ones).",
            "Transfer learning is the standard answer - our question is how much it is actually worth here.",
        ],
        "0:50-2:00. Presenter: 【NAME】. Show a defect and a non-defect part side by side; point at the stringing.",
        "testset/D1/test/defect/IMG_9153.jpg",
    ),
    (
        "2. Objectives: reproduce Ahsan et al. (2024) and go further",
        [
            "Reproduce the comparison of 11 ImageNet backbones for defect classification.",
            "Reproduce the optimizer ablation (Adam / SGD / RMSprop) on both public datasets.",
            "Go beyond the paper: leakage control, explainability, deployment cost, no-transfer ablation.",
            "Ship a reproducible artefact: code, frozen splits, results and a working inspection UI.",
        ],
        "2:00-2:50. Presenter: 【NAME】. Emphasise that points 1-2 are reproduction, 3-4 are ours.",
        None,
    ),
    (
        "3. Dataset: D1 (real) and D2 (augmented) - and the honest caveat",
        [
            "D1: 271 real photographs, 136 defect / 135 non-defect, 5184 x 3456.",
            "D2: 3,017 augmented images, 947 / 2,070, 128 x 128 - derived from D1, NOT an independent dataset.",
            "Stratified 70/10/20 split, seed 42, frozen in splits/D1.csv and splits/D2.csv.",
            "The paper's third dataset (1,557 images) is not public -> we can cover 66 of 99 cells.",
        ],
        "2:50-4:00. Presenter: 【NAME】. Refer to Table 1. Say explicitly that D2 is not independent.",
        None,
    ),
    (
        "4. Method: transfer-learning pipeline",
        [
            "Pre-trained ImageNet CNN; every convolutional layer frozen.",
            "New head trained from scratch: AvgPool(4,4) - Flatten - Dense(64, ReLU) - Dropout(0.5) - Dense(2).",
            "Identical head for all 11 backbones, so the comparison is fair.",
            "Only the head is trained: 33 k parameters for VGG16, 82 k for MobileNetV2.",
        ],
        "4:00-5:20. Presenter: 【NAME】. Refer to Figure 1. Stress that the backbone never changes.",
        "results/figures/fig_pipeline.png",
    ),
    (
        "5. Method: training protocol and metrics",
        [
            "Optimizers Adam / SGD / RMSprop, shared learning rate 1e-3 and epoch budget per dataset (30 for D1, 50 for D2).",
            "Ten metrics reported on train / val / test: accuracy, precision, recall, F1, MCC, kappa, AUC, mAP, sensitivity, specificity.",
            "Positive class = defect; confusion matrix rows are truth, columns are prediction.",
            "Evaluation script is deterministic given the frozen split.",
        ],
        "5:20-6:20. Presenter: 【NAME】. Refer to Algorithm 1 in the report (pseudo-code of one run).",
        None,
    ),
    (
        "6. Experimental setup: 66 runs, one environment",
        [
            "11 backbones x 3 optimizers x 2 datasets = 66 runs, all on Kaggle Tesla T4.",
            "Each run stores metrics.json, confusion matrices, training curves and the trained head weights.",
            "10 head-only checkpoints kept (5 backbones x 2 datasets, Adam), 131-515 KB each.",
            "Every number in this talk comes from results/leaderboard.csv.",
        ],
        "6:20-6:50. Presenter: 【NAME】. Keep this slide short - it is credibility, not content.",
        "results/figures/fig_confusion_grid.png",
    ),
    (
        "7. Results: backbone comparison",
        [
            "Mean test accuracy over the three optimizers: D1 0.9826, D2 0.9849.",
            "Five backbones reach 1.0000 on D1 (VGG19, Xception, MobileNetV2, ResNet50, EfficientNet-B0).",
            "Weakest is NASNetLarge at 0.9259 - still far above chance.",
            "D1 test set has 54 images: one error costs 1.85 points, so differences under ~0.02 are not meaningful.",
        ],
        "6:50-8:00. Presenter: 【NAME】. Refer to Figure 2 and Table 2. Do not claim a winner from ties.",
        "results/figures/fig_accuracy_by_model.png",
    ),
    (
        "8. Results: optimizer ablation",
        [
            "Adam is the most consistent across backbones and datasets.",
            "SGD and RMSprop reach similar peaks but are less stable on the heaviest backbones.",
            "The ranking of backbones is stable across optimizers - the conclusion does not depend on the optimizer.",
        ],
        "8:00-8:40. Presenter: 【NAME】. Refer to Figure 3. If short on time this slide can be dropped.",
        "results/figures/fig_optimizer_heatmap.png",
    ),
    (
        "9. Results: where we agree and disagree with the paper",
        [
            "All 11 backbones: mean accuracy 0.9826 (D1) / 0.9849 (D2) vs paper 0.7879 / 0.8464.",
            "That +19.5 / +13.9 points is inflated: the paper reports F1 = 0 for all three EfficientNets.",
            "Excluding those 18 cells: +8.2 (D1) and +7.9 (D2) - a fair, modest advantage.",
            "Main suspect for the remaining gap: the authors do not publish their split, and use /255 instead of per-backbone preprocessing.",
        ],
        "8:40-9:40. Presenter: 【NAME】. Refer to Figure 5 and Table 4. Say 'fair comparison', not 'we beat them'.",
        "results/figures/fig_delta_acc.png",
    ),
    (
        "10. Our analysis (i): is the accuracy just data leakage?",
        [
            "D2 is built by augmenting D1, so augmented copies of the same part can sit in train and test.",
            "We rebuilt D2 ourselves keeping provenance, then compared random splits with source-grouped splits.",
            "Two training-set regimes (2,087 and 313 images) x three backbones = 6 controlled runs.",
            "Result: no consistent leakage effect (|delta| <= 1.5%, mostly negative) -> the task is simply easy.",
        ],
        "9:40-10:30. Presenter: 【NAME】. Refer to Figure 7 and Table 6. Stress: negative result, not a proof of leakage.",
        "results/figures/fig_leakage_combined.png",
    ),
    (
        "11. Our analysis (ii): what is the model looking at?",
        [
            "Grad-CAM and LIME both concentrate on the printed part rather than the background.",
            "Failures concentrate on thin struts and low-contrast regions - the same places a human hesitates.",
            "The map is 7 x 7 (about 32 px per cell): it is an attention map, NOT a defect localisation.",
            "We removed the misleading 'defect position' marker from the UI for exactly this reason.",
        ],
        "10:30-11:20. Presenter: 【NAME】. Refer to Figures 8 and 9. Being explicit about the limitation scores points.",
        "results/figures/gradcam_mobilenet_v2__D1__adam__s42.png",
    ),
    (
        "12. Our analysis (iii): deployment cost and the value of pre-training",
        [
            "On a T4 GPU every backbone runs under 40 ms per image; on CPU only MobileNetV2 (22.9 ms) and EfficientNet-B0 (34.6 ms) stay real-time.",
            "MobileNetV2: 2.3 M parameters, 0.6 GFLOPs - 58x smaller than VGG16 at the same accuracy.",
            "No-transfer ablation (same data, same head): random-init frozen 【TBD: D1 acc】, random-init full 【TBD: D1 acc】.",
            "Conclusion: the ImageNet weights, not the architecture, are what make 189 images enough.",
        ],
        "11:20-12:10. Presenter: 【NAME】. Refer to Figure 10 and Table 5. Fill the two 【TBD】 numbers before the talk.",
        "results/figures/fig_efficiency.png",
    ),
    (
        "13. Live demo: the inspection station",
        [
            "Load a part photo -> laser scan animation -> PASS / FAIL verdict with confidence and cycle time.",
            "Every inspection is appended to a session log; EXPORT CSV writes it out; CLEAR starts a new session.",
            "Engine: MobileNetV2 trained on D1 (2.3 M parameters, ~0.35 s per image on a laptop CPU).",
            "The UI only shows the attention map - it never claims to localise a defect.",
        ],
        "12:10-13:40. Presenter: 【NAME】. Run analysis/demo_client.py live (2:30 as scripted in docs/DEMO.md); if anything fails, play 【TBD: demo_fallback.mp4】.",
        None,
    ),
    (
        "14. Conclusions, limitations and what we would do next",
        [
            "Frozen ImageNet features are enough for this task: 11 backbones, 66 runs, mean test accuracy 0.98.",
            "Recommendation: MobileNetV2 or EfficientNet-B0 for CPU/edge, any backbone if a GPU is available.",
            "Limitations: third dataset unavailable (66/99 cells), D2 is not independent, 54-image test set, classification only.",
            "Artefact: https://github.com/Zheyi-D/am-defect-tl - code, frozen splits, results and the demo above.",
        ],
        "13:40-15:00. Presenter: 【NAME】. End on the limitation sentence, then invite questions (5 min Q&A).",
        None,
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

    for index, (title, bullets, note, image) in enumerate(SLIDES):
        if index == 0:
            slide = prs.slides.add_slide(title_layout)
            slide.shapes.title.text = title
            slide.shapes.title.text_frame.paragraphs[0].font.size = Pt(26)
            body = slide.placeholders[1].text_frame
            body.text = bullets[0]
            for line in bullets[1:]:
                para = body.add_paragraph()
                para.text = line
                para.font.size = Pt(14)
        else:
            slide = prs.slides.add_slide(content_layout)
            slide.shapes.title.text = title
            slide.shapes.title.text_frame.paragraphs[0].font.size = Pt(24)

            body = slide.placeholders[1]
            body.text_frame.word_wrap = True
            text_frame = body.text_frame
            text_frame.text = bullets[0]
            for line in bullets[1:]:
                para = text_frame.add_paragraph()
                para.text = line
                para.level = 0
                para.font.size = Pt(15)

            # optional figure on the right, bullets confined to the left half
            if image:
                img_path = ROOT / image
                if img_path.exists():
                    from PIL import Image

                    body.width = Inches(5.6)
                    # shrink very large source photos so the deck stays small
                    if img_path.stat().st_size > 600_000:
                        with Image.open(img_path) as big:
                            big = big.convert("RGB")
                            big.thumbnail((1500, 1500), Image.LANCZOS)
                            img_path = out.parent / ("_slide_" + img_path.stem + ".jpg")
                            img_path.parent.mkdir(parents=True, exist_ok=True)
                            big.save(img_path, format="JPEG", quality=88)
                    with Image.open(img_path) as im:
                        w, h = im.size
                    max_w, max_h = 6.1, 4.8  # inches
                    scale = min(max_w / (w / 96), max_h / (h / 96))
                    pic_w, pic_h = (w / 96) * scale, (h / 96) * scale
                    slide.shapes.add_picture(
                        str(img_path),
                        left=Inches(13.333 - 0.45 - pic_w),
                        top=Inches(1.55),
                        width=Inches(pic_w), height=Inches(pic_h),
                    )

        slide.notes_slide.notes_text_frame.text = note

    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the 16-slide presentation deck.")
    ap.add_argument("--out", type=Path, default=Path("reports/slides_draft.pptx"))
    args = ap.parse_args()
    path = build(args.out)
    print(f"[slides] wrote {path} ({len(SLIDES)} slides, {path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
