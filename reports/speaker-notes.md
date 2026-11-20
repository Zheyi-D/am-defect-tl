# Speaker notes — eight parts

> Exported from `slides_draft.pptx`; the same text sits in each slide's notes pane.
> Timing appears here only — never on the slides.

## Slide 1 — Python-Based Transfer Learning

**PART 1 / 8 · presenter 【NAME 1】 · budget 0:20**
- Title, the paper (ESWA 253, 124293) and one sentence on what the group did.

## Slide 2 — Background and objective

**PART 1 / 8 · presenter 【NAME 1】 · budget 0:50**
- Background: printed parts show stringing and poor layer bonding; inspection by eye is slow; only 271 real photographs exist.
- Objective: freeze an ImageNet backbone, train a small head, and reproduce the comparison of eleven backbones. Keep it short — the detail starts on the next slide.

## Slide 3 — The two datasets

**PART 2 / 8 · presenter 【NAME 2】 · budget 0:50**
- Point at the grid: eight defects on top, eight clean parts below; the defect is the thin extruded strands.
- D1: 271 real photos, 136/135, 5184 × 3456. D2: 3,017 copies, 947/2,070, 128 × 128.

## Slide 4 — How the augmented set is generated

**PART 2 / 8 · presenter 【NAME 2】 · budget 0:45**
- Rotation ±15°, horizontal flip, brightness; eleven copies per image, so 271 photographs become 3,017 training images.
- Copies are stored at 128 × 128 and read at 224 × 224.

## Slide 5 — Preprocessing and the train / val / test split

**PART 3 / 8 · presenter 【NAME 3】 · budget 0:50**
- Walk the five preprocessing blocks, then the split bars: resize to 224, ImageNet normalisation, cache, then 70/10/20 with seed 42.
- Give the split sizes: 189/28/54 on D1 and 2,112/302/603 on D2.

## Slide 6 — Transfer learning: a frozen backbone and a new head

**PART 4 / 8 · presenter 【NAME 4】 · budget 0:50**
- Left column trains 2.3 M parameters, right column 82 k; every convolution layer is frozen.
- Read the head aloud: pooling, flatten, 64-unit layer with ReLU, dropout 0.5, two-unit softmax.
- On D2 the frozen model matches the fully trained one.

## Slide 7 — The network

**PART 4 / 8 · presenter 【NAME 4】 · budget 0:45**
- Walk the diagram left to right and read the shapes: 224×224×3 → 7×7×C → 1×1×C → 64 → 2.
- Blue blocks are frozen, green blocks are trained.

## Slide 8 — Algorithm 1 — one training run

**PART 4 / 8 · presenter 【NAME 4】 · budget 0:45**
- Read Algorithm 1: freeze the backbone, build the head, compute features without gradients, update only the head, evaluate once on the test split.

## Slide 9 — Experimental setup

**PART 4 / 8 · presenter 【NAME 4】 · budget 0:40**
- Each square is one completed run: 11 backbones × 3 optimisers × 2 datasets = 66, all with the same split and the same head.
- Then the shared settings: 224 px, lr 1e-3, 30/50 epochs, batch 8/32, seed 42.

## Slide 10 — What one run looks like, epoch by epoch

**PART 5 / 8 · presenter 【NAME 5】 · budget 0:45**
- MobileNetV2 on D1 with Adam: training loss falls to 0.01, accuracy reaches 1.00 in ten epochs, validation loss then rises while accuracy stays flat — the extra epochs fit noise.

## Slide 11 — Results: eleven backbones

**PART 5 / 8 · presenter 【NAME 5】 · budget 0:50**
- Read the D2 numbers: mean 0.9849 over 603 test images, from 0.920 for EffNet-V2M to 0.997 for Xception; VGG16, VGG19 and MobileNetV2 are above 0.990.
- The grey dots are the same ranking on the 54-image D1 split.

## Slide 12 — Results: what tuning changes

**PART 5 / 8 · presenter 【NAME 5】 · budget 0:50**
- The optimiser moves the score by 0-4 points and only for the weakest backbone; the backbone ranking never changes.
- The right panel shows EffNet-V2M on D2 oscillating between 0.86 and 0.99 from epoch to epoch.

## Slide 13 — Results compared with the reported values

**PART 5 / 8 · presenter 【NAME 5】 · budget 0:50**
- Overall we are +19.5 on D1 and +13.9 on D2, but three EfficientNet cells report F1 = 0 in the paper, so the fair comparison is +8.2 and +7.9.
- The rest is explained by the unpublished split and the paper's input normalisation.

## Slide 14 — Live demo

**PART 6 / 8 · presenter 【NAME 6】, operated by 【NAME 7】 · budget 2:00**
- Hand over to the live demo: load a defect photo, then a clean one, show the verdict with confidence and cycle time, then the session log and the CSV export.
- If anything fails, play the fallback recording 【TBD: demo_fallback.mp4】 and keep talking.

## Slide 15 — Conclusions

**PART 8 / 8 · presenter 【NAME 8】 · budget 0:50**
- Three conclusions: frozen features are enough (0.9849 on D2); accuracy saturates, so the optimiser matters less than the data; MobileNetV2 matches VGG16 with 58× fewer parameters.
- Then the limitation: 54 D1 test images and no learning-rate sweep.

## Slide 16 — Thank you

**PART 8 / 8 · presenter: all eight on stage · budget 0:20**
- Thank the audience, point at the repository link, hand over to Q&A.
