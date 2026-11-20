# Speaker notes — eight parts

> Exported from `slides_draft_v7.pptx`; the same text sits in each slide's notes pane.
> Timing appears here only — never on the slides.

## Slide 1 — Python-Based Transfer Learning

**PART 1 / 8 · presenter: 【NAME 1】 · budget 0:20 (Part 1 total 1:45)**
- Say: the title, the paper we reproduce (ESWA 253, 124293) and one sentence on what the group built.
- Do not read the group names or the course code aloud — they are on the slide.

## Slide 2 — Eight parts, eight speakers

**PART 1 / 8 · presenter: 【NAME 1】 · budget 0:35**
- Say: eight parts, eight speakers, and every part answers the same three questions — what we did, why, and what result it produced.
- Do not read the table row by row; point at the eight rows and hand over to Part 2.

## Slide 3 — Defect detection on printed parts — what and why

**PART 1 / 8 · presenter: 【NAME 1】 · budget 0:50**
- WHAT: a binary classifier for printed parts — defect or no defect. WHY: manual inspection does not scale and only 271 real images exist, so we freeze ImageNet features and train a small head.
- RESULT: 66 runs, mean test accuracy 0.98, plus four analyses the paper does not have.
- Caution: say 'reproduce and extend', never 'we beat the paper'.

## Slide 4 — The two datasets we use

**PART 2 / 8 · presenter: 【NAME 2】 · budget 0:45 (Part 2 total 2:00)**
- Point at the pair of photos: defect (stringing) on the left, no defect on the right.
- State the numbers: D1 = 271 real photos (136/135), 5184 × 3456; D2 = 3,017 augmented copies (947/2,070), 128 × 128.
- Say explicitly that D2 is an augmentation of D1, not an independent dataset.

## Slide 5 — How we augment — and what it costs

**PART 2 / 8 · presenter: 【NAME 2】 · budget 0:50**
- WHAT: rotation ±15°, horizontal flip, brightness jitter, 11 copies per source image.
- WHY: 189 training photos are too few for a CNN. RESULT: 271 → 3,017, but at the cost of 128 px resolution and lost provenance.
- This is why D2 is reported separately and never used as extra evidence.

## Slide 6 — How we preprocess and split

**PART 2 / 8 · presenter: 【NAME 2】 · budget 0:35**
- Walk the five blocks left to right, then the split table.
- WHY the cache: decoding a 5184 × 3456 JPEG costs about 80 s per epoch. RESULT: under a minute per run and the same frozen split for all 66 runs.
- Mention the split sizes: D1 189/28/54 and D2 2,112/302/603.

## Slide 7 — Transfer learning: what it is and why we freeze

**PART 3 / 8 · presenter: 【NAME 3】 · budget 0:40 (Part 3 total 2:00)**
- Point at the two columns: scratch trains 2.3 M parameters, we train 82 k.
- WHY: with 189 images, updating the backbone memorises the training set; freezing turns the problem into fitting a small head.
- If asked: the backbone is also kept in eval mode so BatchNorm statistics never update.

## Slide 8 — The whole network in one picture

**PART 3 / 8 · presenter: 【NAME 3】 · budget 0:40**
- Walk left to right and read the shapes under each block: 224×224×3 → 7×7×C → 1×1×C → 64 → 64 → 2.
- Blue band = frozen ImageNet weights; green band = the only part we train.
- Say the number: 82,114 trainable parameters = 3.56 % of MobileNetV2.

## Slide 9 — 32,962

**PART 3 / 8 · presenter: 【NAME 3】 · budget 0:35**
- 32,962 parameters for VGG16 is 0.02 % of the model.
- The head is identical for all 11 backbones — only the channel count changes — so the comparison is fair.
- Checkpoint size 131-515 KB because we save the head only and rebuild the frozen backbone.

## Slide 10 — The 66-run matrix

**PART 4 / 8 · presenter: 【NAME 4】 · budget 0:45 (Part 4 total 1:30)**
- Each square is one completed run: 11 backbones × 3 optimisers × 2 datasets = 66.
- WHY three optimisers and two datasets: to separate the effect of the backbone from the effect of the training recipe.
- Then the hyper-parameter table: 224 px, lr 1e-3, 30/50 epochs, batch 8/32, seed 42.

## Slide 11 — Reproducibility is part of the result

**PART 4 / 8 · presenter: 【NAME 4】 · budget 0:40**
- 66/66 runs completed, 10 checkpoints kept, 522 table values re-checked with 0 mismatches.
- WHY it matters: every number in the report is regenerated from leaderboard.csv, and the splits are frozen in the repository.
- RESULT: a one-command rebuild on Kaggle plus a CI job that compiles and runs the contract tests.

## Slide 12 — Eleven backbones, one narrow band

**PART 5 / 8 · presenter: 【NAME 5】 · budget 0:45 (Part 5 total 2:00)**
- Read the two means: 0.9826 on D1, 0.9849 on D2. Five backbones reach 1.0000, the weakest 0.9259.
- Point out that the bars are a very narrow band — the choice of backbone barely matters.
- Caution: do not announce a winner; see the next-next slide for why.

## Slide 13 — Optimiser choice moves nothing much

**PART 5 / 8 · presenter: 【NAME 5】 · budget 0:40**
- Adam is the most consistent; the row order does not change between optimisers.
- Say the implication: our conclusions do not depend on the optimiser, so we never cherry-pick a column.

## Slide 14 — 7 × 7

**PART 5 / 8 · presenter: 【NAME 5】 · budget 0:35**
- 54 test images → one mistake costs 1.85 accuracy points; anything below ~0.02 is a single photograph.
- 1.0000 means 'all 54 correct', not 'perfect model' — the 95 % interval for 54/54 is about [0.95, 1.00].
- And the model is a whole-image classifier: no box, no mask, no area.

## Slide 15 — Where we agree with the paper — and where we do not

**PART 6 / 8 · presenter: 【NAME 6】 · budget 1:00 (Part 6 total 1:50)**
- Walk the delta chart: most backbones are positive. Then explain the trap: the paper reports F1 = 0 for three EfficientNets, which inflates the overall gap.
- Fair comparison: +8.2 points on D1, +7.9 on D2.
- Main suspects for the rest: the authors do not publish their split and normalise with /255. Say 'fair comparison', never 'we beat them'.

## Slide 16 — Is the accuracy just leakage? No

**PART 6 / 8 · presenter: 【NAME 6】 · budget 0:50**
- WHAT: we rebuilt the augmented set keeping provenance and compared a random split with a split grouped by source image (6 controlled runs).
- WHY: copies of one photo must not sit on both sides of the split.
- RESULT: |Δ| ≤ 1.5 %, mostly negative → a negative result, reported as such. The high accuracy is not leakage; the task is simply easy.

## Slide 17 — Explainability: attention, not localisation

**PART 7 / 8 · presenter: 【NAME 7】 · budget 0:45 (Part 7 total 2:15)**
- Point at the middle column: the map looks at the part, not the background. LIME agrees.
- But the map is 7 × 7 (≈32 px per cell) and the head averages it with a 4 × 4 pool.
- So it can only say 'around here' — we removed the 'defect position' marker from our own UI for that reason.

## Slide 18 — Deployment cost decides the engine

**PART 7 / 8 · presenter: 【NAME 7】 · budget 0:45**
- Measured numbers: MobileNetV2 22.9 ms on CPU, VGG16 165 ms; on a GPU everything is under 40 ms.
- RESULT: at the same accuracy, MobileNetV2 is 58× smaller — that is why it is the deployed engine.

## Slide 19 — 1.0000

**PART 7 / 8 · presenter: 【NAME 7】 · budget 0:45**
- Three numbers: 1.0000 frozen pretrained, 0.5000 random frozen, 1.0000 random fully trained.
- Read them: frozen random features collapse to the majority class, so freezing only works because of the ImageNet weights.
- But end-to-end training from scratch also reaches 1.0000 — on this dataset pre-training buys cost (82 k parameters, 30 s), not accuracy. Say it as a finding, not as a failure.

## Slide 20 — From model to product: the inspection station

**PART 8 / 8 · presenter: 【NAME 8】 · budget 0:40 (Part 8 total 2:40, including the live demo)**
- Walk the screenshot: photo in, scan, verdict with confidence and cycle time, session log.
- WHY MobileNetV2 on D1: 2.3 M parameters, 22.9 ms on CPU, no GPU on site, and D2 weights are never shipped because they collapse on full-resolution photos.
- State the honesty constraint: the UI shows an attention overlay, never a defect marker.

## Slide 21 — Live demo — what we will show

**PART 8 / 8 · presenter: 【NAME 8】 · budget 2:00 for the live demo**
- Follow the four steps: defect photo → no-defect photo → show the log → clear the session.
- Say the numbers while it runs: 0.3-1.5 s per image, offline, weights cached.
- If anything fails, switch to the recorded walkthrough immediately and keep talking — do not debug on stage. Fallback file: 【TBD: demo_fallback.mp4】.

## Slide 22 — What we would tell a production engineer

**PART 8 / 8 · presenter: 【NAME 8】 · budget 0:40**
- Three findings and four limitations, one sentence each.
- End on the limitation sentence and the honest next step: localisation needs segmentation or anomaly detection, which we did not do.
- Then invite questions.

## Slide 23 — Thank you

**PART 8 / 8 · presenter: all eight on stage · budget 0:20**
- Thank the audience, point at the repository link, and hand over to Q&A.
- Keep this page short — the whole group should be visible for questions.
