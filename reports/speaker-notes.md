# Speaker notes — eight parts

> Exported from `slides_draft_v8.pptx`; the same text sits in each slide's notes pane.
> Timing appears here only — never on the slides.

## Slide 1 — Python-Based Transfer Learning

**PART 1 / 8 · presenter 【NAME 1】 · budget 0:20**
- Say: the title, the paper (ESWA 253, 124293) and one sentence on what the group built.
- Do not read the group names or the course code aloud.

## Slide 2 — How this talk is organised

**PART 1 / 8 · presenter 【NAME 1】 · budget 0:35**
- Say: eight parts, five work groups; every part answers WHAT / WHY / RESULT.
- Do not read the table row by row — point at the groups.

## Slide 3 — Motivation and purpose

**PART 1 / 8 · presenter 【NAME 1】 · budget 0:50**
- WHAT: binary classification of printed parts. WHY: manual inspection does not scale and only 271 real photos exist.
- RESULT: 66 runs, 0.98 mean accuracy, plus analyses the paper does not report.

## Slide 4 — Background and the tools we used

**PART 1 / 8 · presenter 【NAME 1】 · budget 0:45**
- Background: three ways to inspect a printed part; we take camera + ML and borrow ImageNet features because labels are scarce.
- Tools: PyTorch, timm, scikit-learn, matplotlib, Gradio, Kaggle T4, Git + CI.
- Point at the timeline on the way in.

## Slide 5 — The two datasets we use

**PART 2 / 8 · presenter 【NAME 2】 · budget 0:45**
- Point at the grid: eight defects on top, eight clean parts below — the defect is stringing around the part.
- Numbers: D1 271 real (136/135); D2 3,017 augmented (947/2,070).
- Say explicitly that D2 is an augmentation of D1, not new data.

## Slide 6 — How we augment — and what it costs

**PART 2 / 8 · presenter 【NAME 2】 · budget 0:45**
- WHAT: rotation, flip, brightness, 11 copies per image. WHY: 189 training photos.
- RESULT: 271 → 3,017 but at 128 px, provenance lost, and copies are not new information.

## Slide 7 — Preprocessing and the frozen split

**PART 3 / 8 · presenter 【NAME 3】 · budget 0:45**
- Walk the five blocks, then the split bars.
- WHY: decoding a 5184 × 3456 JPEG costs ~80 s per epoch. RESULT: under a minute per run, and one frozen split for all 66 runs (189/28/54 and 2,112/302/603).

## Slide 8 — The number that limits every claim: 54

**PART 3 / 8 · presenter 【NAME 3】 · budget 0:45**
- This page is the caveat that limits every claim: 54 test images, one mistake = 1.85 points.
- 1.0000 means 'all 54 correct', and the 95 % interval for 54/54 is about [0.95, 1.00].

## Slide 9 — Transfer learning: what it is and why we freeze

**PART 4 / 8 · presenter 【NAME 4】 · budget 0:40**
- Point at the two columns: scratch trains 2.3 M parameters, we train 82 k.
- WHY: with 189 images, updating the backbone memorises the training set.

## Slide 10 — The whole network in one picture

**PART 4 / 8 · presenter 【NAME 4】 · budget 0:40**
- Walk left to right and read the shapes under each block: 224×224×3 → 7×7×C → 1×1×C → 64 → 64 → 2.
- Blue = frozen, green = trained; 82,114 parameters = 3.56 % of MobileNetV2.

## Slide 11 — Algorithm 1 — one training run

**PART 4 / 8 · presenter 【NAME 4】 · budget 0:40**
- Read Algorithm 1 top to bottom: freeze the backbone, build the head, train the head only, evaluate 10 metrics on the frozen test split.
- Stress that this exact procedure ran 66 times.

## Slide 12 — The 66-run matrix

**PART 4 / 8 · presenter 【NAME 4】 · budget 0:40**
- Each square is one completed run: 11 × 3 × 2 = 66.
- Then the hyper-parameters: 224 px, lr 1e-3, 30/50 epochs, batch 8/32, seed 42.

## Slide 13 — Reproducibility is part of the result

**PART 5 / 8 · presenter 【NAME 5】 · budget 0:35**
- 66/66 runs, 10 checkpoints, 522 table values re-checked with zero mismatches, frozen splits in the repository.
- This is credibility, not content — keep it short.

## Slide 14 — Eleven backbones, one narrow band

**PART 5 / 8 · presenter 【NAME 5】 · budget 0:45**
- Read the two means: 0.9826 on D1, 0.9849 on D2; five backbones at 1.0000, the weakest 0.9259.
- Caution: do not announce a winner.

## Slide 15 — What tuning actually does to the results

**PART 5 / 8 · presenter 【NAME 5】 · budget 0:50**
- Optimiser choice moves the number by 0-4 points and only for the weakest backbone; curves saturate by ~10 epochs.
- Say openly: we did not sweep the learning rate — tuning shifts numbers, not conclusions.

## Slide 16 — From model to product: the inspection station

**PART 6 / 8 · presenter 【NAME 6】 · budget 0:45**
- Walk the screenshot: photo in, scan, verdict with confidence and cycle time, session log.
- WHY MobileNetV2 on D1: 2.3 M parameters, 22.9 ms on CPU, offline. Never claims to localise a defect.

## Slide 17 — Live demo — what we will show

**PART 7 / 8 · presenter 【NAME 7】 · budget 2:00 (the live demo)**
- Follow the four steps: defect photo → clean photo → show the log → clear.
- If anything fails, switch to the recorded walkthrough and keep talking. Fallback: 【TBD: demo_fallback.mp4】.

## Slide 18 — Where we agree with the paper — and where we do not

**PART 8 / 8 · presenter 【NAME 8】 · budget 1:00**
- Walk the delta chart, then explain the trap: three EfficientNets report F1 = 0, which inflates the gap.
- Fair comparison: +8.2 on D1. Say 'fair comparison', never 'we beat them'.

## Slide 19 — Is the accuracy just leakage? No

**PART 8 / 8 · presenter 【NAME 8】 · budget 0:50**
- We rebuilt the augmented set with provenance and compared random vs source-grouped splits: |Δ| ≤ 1.5 %, mostly negative.
- A negative result, reported as such.

## Slide 20 — Explainability: attention, not localisation

**PART 8 / 8 · presenter 【NAME 8】 · budget 0:45**
- Both Grad-CAM and LIME look at the part, not the background.
- But the map is 7 × 7 and the head averages it with a 4 × 4 pool — 'around here' only, which is why we removed the marker from our UI.

## Slide 21 — Deployment cost decides the engine

**PART 8 / 8 · presenter 【NAME 8】 · budget 0:45**
- MobileNetV2 22.9 ms on CPU versus VGG16 165 ms; on a GPU everything is under 40 ms.
- At the same accuracy, MobileNetV2 is 58× smaller — that is the engine we ship.

## Slide 22 — How much is the pre-training worth?

**PART 8 / 8 · presenter 【NAME 8】 · budget 0:50**
- Frozen random features collapse to 0.5000, so freezing only works because of the ImageNet weights.
- But scratch also reaches 1.0000 — pre-training buys cost, not accuracy. Say it as a finding.

## Slide 23 — What we would tell a production engineer

**PART 8 / 8 · presenter 【NAME 8】 · budget 0:45**
- Three findings and four limitations, one sentence each.
- End on the limitation sentence and the honest next step: localisation needs segmentation or anomaly detection, which we did not do.

## Slide 24 — Thank you

**PART 8 / 8 · presenter: all eight on stage · budget 0:20**
- Thank the audience, point at the repository link, and hand over to Q&A.
