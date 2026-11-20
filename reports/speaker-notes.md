# Speaker notes — eight parts

> Exported from `slides_draft.pptx`; the same text sits in each slide's notes pane.
> Timing appears here only — never on the slides.

## Slide 1 — Python-Based Transfer Learning

**PART 1 / 8 · presenter 【NAME 1】 · budget 0:20**
- Title, the paper (ESWA 253, 124293) and one sentence on what the group built.

## Slide 2 — Background and objective

**PART 1 / 8 · presenter 【NAME 1】 · budget 0:50**
- Keep this short: three ways to inspect a printed part, we take camera + ML, labels are scarce so we reuse ImageNet features.
- Then the objective: reproduce 11 backbones and measure the deployment cost. 11 × 3 × 2 = 66 runs.

## Slide 3 — The two datasets

**PART 2 / 8 · presenter 【NAME 2】 · budget 0:45**
- Point at the grid: eight defects (stringing) on top, eight clean parts below.
- Numbers: D1 271 real (136/135), 5184 × 3456; D2 3,017 augmented (947/2,070), 128 × 128.

## Slide 4 — How the augmented set is generated

**PART 2 / 8 · presenter 【NAME 2】 · budget 0:45**
- Rotation, flip and brightness; 11 copies per image → 271 becomes 3,017.
- Be precise: the copies are 128 px and come from the same 271 photos.

## Slide 5 — Preprocessing and the split

**PART 3 / 8 · presenter 【NAME 3】 · budget 0:50**
- Walk the five preprocessing blocks, then the split bars: 189/28/54 and 2,112/302/603, seed 42, identical for all 66 runs.
- Say why the cache exists: decoding a 5184 × 3456 JPEG costs about 80 s per epoch.

## Slide 6 — Transfer learning: a frozen backbone and a small head

**PART 4 / 8 · presenter 【NAME 4】 · budget 0:45**
- Left column trains 2.3 M parameters, right column 82 k.
- Why: with 189 images, updating the backbone memorises the training set.
- On D2 both settings reach 0.995 — freezing costs nothing in accuracy and saves 27x the parameters.

## Slide 7 — The network

**PART 4 / 8 · presenter 【NAME 4】 · budget 0:45**
- Read the shapes left to right: 224×224×3 → 7×7×C → 1×1×C → 64 → 64 → 2.
- Blue is frozen, green is trained: 82,114 parameters = 3.56 % of MobileNetV2.

## Slide 8 — Algorithm 1 — one training run

**PART 4 / 8 · presenter 【NAME 4】 · budget 0:45**
- Read Algorithm 1: freeze the backbone, build the head, train the head only, evaluate ten metrics on the frozen test split.
- The same procedure ran 66 times.

## Slide 9 — The experiment matrix

**PART 4 / 8 · presenter 【NAME 4】 · budget 0:45**
- Each square is one completed run: 11 × 3 × 2 = 66.
- Then the hyper-parameters: 224 px, lr 1e-3, 30/50 epochs, batch 8/32, seed 42.

## Slide 10 — What one run looks like, epoch by epoch

**PART 5 / 8 · presenter 【NAME 5】 · budget 0:45**
- Left: training loss keeps falling. Right: accuracy saturates after ~10 epochs, and validation loss drifts up after that — the epoch budget only matters for the heaviest backbones.

## Slide 11 — How the results are measured

**PART 5 / 8 · presenter 【NAME 5】 · budget 0:50**
- How we test: one pass over the frozen test split, then ten metrics and a 2×2 confusion matrix; positive class is defect.
- Point out why: on 54 test images one mistake costs 1.85 points, so accuracy alone is not enough.

## Slide 12 — Results: eleven backbones

**PART 5 / 8 · presenter 【NAME 5】 · budget 0:45**
- Read the D2 numbers: mean 0.9849 over 603 test images, from 0.920 (EffNet-V2M) to 0.997 (Xception); the D1 dots show the same ranking.
- Do not announce a winner.

## Slide 13 — Results: what tuning changes

**PART 5 / 8 · presenter 【NAME 5】 · budget 0:50**
- All on D2: the optimiser moves the number by 0-4 points and only for the weakest backbone; the ranking never changes.
- State the limitation: the learning rate was not swept.

## Slide 14 — Results against the reported values

**PART 8 / 8 · presenter 【NAME 8】 · budget 1:00**
- Walk the delta chart, then the trap: three EfficientNets report F1 = 0, so the raw gap is inflated. Fair comparison: +8.2 points on D1.

## Slide 15 — Control: random split versus source-grouped split

**PART 8 / 8 · presenter 【NAME 8】 · budget 0:50**
- The augmented set was rebuilt with provenance and trained twice: random split vs split grouped by source image.
- |Δacc| ≤ 1.5 %, mostly negative — a negative control result.

## Slide 16 — What the model looks at

**PART 8 / 8 · presenter 【NAME 8】 · budget 0:45**
- Attention sits on the part, not the background.
- But the map is 7 × 7 with a 4 × 4 pooling step, so it marks a region, not a defect mask.

## Slide 17 — Deployment cost

**PART 8 / 8 · presenter 【NAME 8】 · budget 0:45**
- MobileNetV2 22.9 ms on CPU versus VGG16 165 ms; on a GPU everything is under 40 ms.
- At equal accuracy MobileNetV2 is 58× smaller — that is the engine we deploy.

## Slide 18 — Live demo

**PART 6 / 8 · presenter 【NAME 6】 with 【NAME 7】 operating · budget 2:00**
- Hand over to the live demo: load a defect photo, then a clean one, show the log, export the CSV.
- If anything fails, play the fallback recording 【TBD: demo_fallback.mp4】 and keep talking.

## Slide 19 — Conclusions and limitations

**PART 8 / 8 · presenter 【NAME 8】 · budget 0:45**
- Three conclusions and four limitations, one sentence each.
- End on the limitation: classification only, 54 test images, learning rate not swept.

## Slide 20 — Thank you

**PART 8 / 8 · presenter: all eight on stage · budget 0:20**
- Thank the audience, point at the repository link, hand over to Q&A.
