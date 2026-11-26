# Q&A 手册 — IDAT7215 Group 15（按 PPT 分工结构）

> **怎么用**：先看第 0 节的「数字速查」和「红线」，再只看自己那一 part 的问答，最后扫一遍第 9 节的通用硬问题。
> 每个问题给 **30 秒答案（英文可直接念）+ 中文对照 + 追问补充 + 出处**。
> 所有数字都能在仓库里查到，写报告和答问只认这些来源：`results/leaderboard.csv`、`results/leakage.csv`、
> `results/baselines.csv`、`results/efficiency.csv`、`results_ablation/ABLATION.md`、`docs/paper_results.csv`。
> 最后更新：2026-11-26

---

## 0. 数字速查（答辩前背这一页）

| 项 | 值 |
|---|---|
| 数据集 | D1：271 张真实照片（136 缺陷 / 135 正常），5184 × 3456；D2：3,017 张增强图（947 / 2,070），128 × 128，由 D1 生成 |
| 划分（seed 42，70/10/20，分层） | D1 189 / 28 / 54；D2 2,112 / 302 / 603 |
| 实验矩阵 | 11 骨干 × 3 优化器（Adam / SGD / RMSprop）× 2 数据集 = **66 组** |
| 分类头 | AvgPool(4,4) → Flatten → Dense(64, ReLU) → Dropout(0.5) → Dense(2, softmax) |
| 可训练参数 | VGG16/19 32,962；MobileNetV2 / EffNet-B0 / V2-M 82,114；InceptionResNetV2 98,498；ResNet50/101、Xception 131,266；EffNet-B7 164,034；NASNetLarge 258,242 |
| 超参 | 输入 224×224，lr 1e-3，D1 训 30 轮 / D2 训 50 轮，batch 8 / 32，seed 42 |
| 主结果（D2，603 张测试图） | 均值 **0.9849**，范围 **0.920**（EffNet-V2M）– **0.997**（Xception） |
| D1（54 张测试图） | 均值 0.9826，18/33 组恰好 1.0000，最低 0.9074（NASNetLarge-SGD） |
| 与论文比 | 全 11 个：+0.195（D1）/ +0.139（D2）；剔除 3 个坏格：**+0.082 / +0.079** |
| 训练成本 | 单卡 T4：D1 每组平均 40.9 s，D2 每组平均 414 s，66 组合计约 **250 分钟（≈4.2 GPU 小时）** |
| 推理成本 | MobileNetV2 22.9 ms/张（CPU）/ 5.3 ms（T4），0.599 GFLOPs，2.31 M 参数；VGG16 165 ms（CPU），134.3 M 参数 |
| 对照实验 | 泄漏对照 6 组，\|Δ\| ≤ 1.5 %；无迁移消融 12 组：D1 1.0000 / 0.5000 / 1.0000；D2 0.9950 / 0.7717 / 0.9950 |
| 基线 | 全猜正常：D1 0.5000、D2 0.6866；全猜缺陷 D2 0.3134；像素+逻辑回归 D1 测试 0.9259；冻结特征+逻辑回归 D1 测试 1.0000 |
| 交付物 | 66 个 `metrics.json`、10 个 `model.pt`（只存分类头）、23 张报告图、8 个 part 的 PPT、检测界面 |

---

## 1. PART 1 · INTRODUCTION（封面 + 背景与目标）

**Q1. What exactly is the problem you solve?**
> "Binary classification of a photograph of a 3D-printed part: does it show a defect or not. The defect here is a surface defect — extruded strings around the part, poor layer bonding, rough patches. We do not localise the defect."
> **中文**：对打印件照片做二分类 —— 有无缺陷；缺陷是表面缺陷（拉丝、层间结合差、粗糙）；不做定位。
> **追问**：为什么不定位？→ 整图分类器的输出只有一个标签；定位需要分割或检测模型（下一步工作）。

**Q2. Why transfer learning instead of training from scratch?**
> "The public dataset has only 271 real photographs. Training millions of parameters from scratch on that would memorise the training set. With ImageNet weights frozen we train 33 thousand to 258 thousand parameters, under a minute per run, and reach 0.98 accuracy."
> **中文**：只有 271 张真实照片，从零训练会记住训练集；冻结骨干后只训 3.3 万–25.8 万参数，每组不到 1 分钟，精度 0.98。
> **出处**：`results_ablation/ABLATION.md`。

**Q3. Why this paper?**
> "It is a recent systematic comparison of frozen backbones on 3D-printing defect data — Expert Systems with Applications, volume 253, 124293 (2024) — and its reported matrix is small enough to reproduce completely."
> **中文**：ESWA 253, 124293（2024），是近几年对 3D 打印缺陷数据最系统的冻结骨干对比，矩阵规模可完整复现。

**Q4. Is this your own dataset?**
> "No. It is the authors' public dataset (mahsan2/AMdataset): 271 real photographs, plus the 3,017 augmented copies they shipped. We publish the exact split files instead of the images."
> **中文**：不是，是作者公开数据集；我们发布的是划分文件而不是图片。

**Q5. What is the objective in one sentence?**
> "Reproduce the comparison of eleven ImageNet backbones under one frozen protocol, and report both accuracy and deployment cost so the result is usable, not just a number."
> **中文**：在同一冻结协议下复现 11 个骨干的对比，并同时给出准确率与部署代价。

---

## 2. PART 2 · DATA PREPARATION — 数据集

**Q6. How many images, and what is the class balance?**
> "D1 has 271 real photographs: 136 defect, 135 non-defect. D2 has 3,017: 947 defect, 2,070 non-defect. The split is 70/10/20 and stratified, so both classes keep their proportion."
> **中文**：D1 271 张（136/135）；D2 3,017 张（947/2,070）；70/10/20 分层划分。

**Q7. What does a defect actually look like?**
> "It is material that should not be there: thin extruded strands around the part, uneven layer edges, rough surface patches. The two rows on the slide are the same part type under the same lighting."
> **中文**：多余的材料 —— 拉丝、层边不齐、表面粗糙；幻灯片上下两行同零件、同光照。

**Q8. Is D2 an independent dataset?**
> "No, and we never present it as one. D2 is the authors' augmented set generated from the same 271 photographs, stored at 128 × 128. That is why we report D1 and D2 separately instead of averaging them."
> **中文**：不是。D2 是作者用同一批 271 张照片做的增强集（128×128），所以两个数据集永远分开报。
> ⚠️ **红线**：绝不能说 "we have two independent datasets"。

**Q9. How exactly was D2 generated?**
> "It is the authors' pre-built augmented set, not something we generated. Their notebook only shows the online augmentation (`rotation_range=15`), so the exact offline recipe is not published — we describe it as rotation up to ±15°, horizontal flip and brightness jitter, about eleven copies per source image."
> **中文**：D2 是作者预先做好的增强集；作者只公开了在线增强（rotation_range=15），离线配方没有完全公开，我们按"±15° 旋转、水平翻转、亮度抖动、约 11 份/张"描述。
> ⚠️ **注意**：271 × 11 = 2,981 ≠ 3,017，所以只能说 "**about** eleven copies"。被追问时就说"配方未完全公开"。

**Q10. Why 128 × 128 for D2?**
> "That is the resolution the authors shipped. We keep it as given and upscale to 224 at read time; changing it would break comparability with their reported numbers."

---

## 3. PART 3 · DATA PREPARATION — 预处理与划分

**Q11. Why resize to 224 and not keep the original resolution?**
> "224 is the input size of ImageNet backbones, and it makes all eleven backbones comparable. The original 5184 × 3456 photograph would also need 410 MiB per image if processed as float at full size."
> **中文**：224 是 ImageNet 骨干的标准输入，也让 11 个骨干可比；原图全尺寸处理单张就要 410 MiB。

**Q12. Why cache the images?**
> "Decoding a 5184 × 3456 JPEG takes about 80 seconds per epoch over the training set, which dominates training time. We decode once, write 224 × 224 JPEGs, and each run then takes under a minute."
> **中文**：原图解码每轮约 80 秒；先解码一次写成 224 缓存，之后每组训练不到 1 分钟。

**Q13. How do you guarantee the same split across 66 runs?**
> "The split is a file, not a runtime call: `splits/D1.csv` and `splits/D2.csv` are generated once with seed 42 and committed. Every run reads those files, so no run can silently re-split."

**Q14. Why 70/10/20 and not 80/10/10?**
> "With 271 images, 20 % gives a 54-image test set — already very small. A 10 % test set would be 27 images, where a single mistake moves accuracy by 3.7 points."

**Q15. Did you check for leakage between train and test?**
> "Yes. We rebuilt the augmented set keeping the source photograph ID, compared a random split against a split grouped by source image, and ran six controlled models. Accuracy moved by at most 1.5 points and mostly downward — no leakage effect detected."
> **中文**：做了。重建增强集并保留原图 ID，随机划分 vs 按原图分组划分各跑 3 个模型，精度变化 ≤1.5 点且多为负 → 未见泄漏效应。
> **出处**：`results/leakage.csv`。⚠️ **红线**：这是**阴性**结果，不能说"我们证明了存在泄漏"。

**Q16. If copies of the same photo can sit in train and test, isn't D2 leaking?**
> "That is exactly what the leakage control tested. Grouping by source image changes accuracy by at most 1.5 points, so the ranking is unaffected. We still report D1 — the real photographs — as the practical check."
> **中文**：这正是对照实验要回答的问题；按原图分组后精度变化 ≤1.5 点，排序不变；同时用 D1 真实照片作为实际检验。

---

## 4. PART 4 · MODEL TRAINING（网络 / Algorithm 1 / 实验设置）

**Q17. Which layers are frozen, and why all of them?**
> "Every convolutional layer of the backbone keeps its ImageNet weights; only the new head is trained. Freezing everything is what makes 66 runs feasible and prevents a 271-image dataset from overfitting 20 million parameters."
> **中文**：骨干全部卷积层保留 ImageNet 权重，只训新头；这样 66 组才跑得动，也不会让 271 张图过拟合两千万参数。

**Q18. Why 64 units in the head? Why dropout 0.5?**
> "Those are the paper's settings — average pooling 4 × 4, one 64-unit dense layer with ReLU, dropout 0.5, two outputs — so our numbers stay comparable to theirs. We did not tune the head."
> **中文**：照论文：AvgPool(4,4)、64 维全连接+ReLU、dropout 0.5、2 输出；没有调头。

**Q19. Why is the feature map 7 × 7?**
> "All eleven backbones reduce 224 × 224 by a factor of 32, so the last convolutional output is 7 × 7 with C channels (512 for VGG16, 2,048 for ResNet50). The 4 × 4 average pooling in the head is what reduces it to 1 × 1."
> **中文**：11 个骨干都是 32 倍下采样，末端 7×7×C（VGG16 512、ResNet50 2048）；头里 4×4 池化把它压成 1×1。

**Q20. What does `no_grad` do in Algorithm 1, and why does it matter?**
> "It stops PyTorch from building a gradient graph through the frozen backbone, so the backward pass only touches the head. BatchNorm also stays in eval mode, so its running statistics are not updated by our data."
> **中文**：不建梯度图，反向只更新头部；BatchNorm 保持 eval，不被我们的数据改统计量。

**Q21. Why three optimisers, and why not tune the learning rate?**
> "The three optimisers are part of the reproduced matrix. We deliberately did not sweep the learning rate: the protocol had to stay identical across 66 runs, and we state this as a limitation rather than hiding it."
> **中文**：三个优化器是复现矩阵的一部分；没有扫学习率，是为了 66 组协议一致，作为局限如实说明。

**Q22. Why these eleven backbones?**
> "They are the eleven in the paper, spanning three families: VGG16/19, ResNet50/101, MobileNetV2, Xception, InceptionResNetV2, NASNetLarge and three EfficientNets (B0, B7, V2-M)."
> **中文**：即论文那 11 个，覆盖 VGG / ResNet / MobileNet / Xception / InceptionResNet / NASNet / EfficientNet 三族。

**Q23. Some EfficientNets report F1 = 0 in the paper — why keep them?**
> "Because the matrix must be the paper's matrix. We keep all eleven and flag the three broken cells in the comparison, then report the fair difference with and without them."
> **中文**：矩阵必须与论文一致；保留 11 个，但在对比时标出 3 个坏格，并给出含/不含它们的两个差值。

**Q24. How long did the 66 runs take?**
> "About 41 seconds per D1 run and about seven minutes per D2 run on a single Tesla T4 — roughly 250 minutes, four GPU hours, not counting the retries."

---

## 5. PART 5 · TRAINING & RESULTS（曲线 / 骨干 / 调参 / 与论文对比）

**Q25. Why report D2 as the headline rather than D1?**
> "D2 has 603 test images against 54 on D1, so one mistake costs 0.17 points instead of 1.85. D2 also has real spread — 0.920 to 0.997 — while D1 saturates with 18 of 33 runs exactly at 1.0000. D1 is still shown as the real-photograph reference."
> **中文**：D2 测试 603 张（错一张 0.17 分），D1 只有 54 张（1.85 分）；D2 有真实区分度（0.920–0.997），D1 有 18/33 组满分。D1 作为真实照片参照保留。

**Q26. Isn't 0.98 suspiciously high?**
> "It is high because the task is easy: pixel-level logistic regression already reaches 0.926 on D1 test, and the majority class alone gives 0.687 on D2. The models are clearly better than those baselines, but we do not claim a hard problem was solved."
> **中文**：任务本身容易 —— 32×32 像素+逻辑回归在 D1 上就有 0.926，D2 全猜多数类 0.687；模型明显优于基线，但我们不夸大难度。
> **出处**：`results/baselines.csv`。

**Q27. Why does validation loss rise while accuracy stays flat?**
> "The model starts fitting noise after about ten epochs: the training loss keeps falling to 0.01, validation loss turns upward, and validation accuracy stops improving. That is the standard over-fitting signature on a tiny training set."

**Q28. Which backbone is best?**
> "On D2, Xception averages 0.997 and MobileNetV2 0.995 — a 0.2-point difference on 603 images, which is about one image. So we do not crown a winner on accuracy; the decision is made by cost."
> **中文**：D2 上 Xception 0.997、MobileNetV2 0.995，差 0.2 点约等于 1 张图，因此不靠准确率排冠军，而是看成本。

**Q29. Which backbone would you deploy?**
> "MobileNetV2 trained on D1: 2.3 M parameters, 22.9 ms per image on a CPU, same accuracy as VGG16 which needs 134 M parameters and 165 ms. That is the checkpoint inside the demo."
> **中文**：MobileNetV2（D1 训练）：2.3 M 参数、CPU 22.9 ms，与 VGG16（134 M、165 ms）同精度；演示里用的就是它。

**Q30. What does changing the optimiser do?**
> "It moves accuracy by 0 to 4 points and only for the weakest backbone; the ranking of backbones never changes. So the training recipe is not what decides the outcome here."
> **中文**：优化器只让精度变 0–4 点，且只影响最弱骨干；骨干排序不变。

**Q31. Why is your accuracy 19.5 points above the paper on D1?**
> "That raw gap is misleading: three EfficientNet cells in the paper report F1 = 0, meaning they predicted only the majority class. Excluding those cells the gap is +8.2 on D1 and +7.9 on D2. The rest is explained by their unpublished split and their input normalisation."
> **中文**：表面 +19.5 有误导性 —— 论文 3 个 EfficientNet 格 F1=0（只猜多数类）；剔除后 +8.2 / +7.9；其余差异来自未公开的划分与其输入归一化方式。

**Q32. Is it fair to compare your split with theirs?**
> "Only at the level of trends, not cell by cell — they never publish their split. That is why we compare the ordering of backbones and the size of the gap, not individual numbers."
> **中文**：只能比趋势、不能逐格比 —— 论文没公开划分；所以我们比骨干排序和差距量级。

**Q33. Why is D1 test only 54 images?**
> "271 images with a 70/10/20 stratified split gives 54 test images. Using them for training would leave no independent check; we keep the split fixed and state the statistical limitation — the 95 % interval for 54/54 is roughly 0.95 to 1.00."

**Q34. Why ten metrics instead of just accuracy?**
> "On a small, imbalanced test set accuracy hides false negatives. F1, MCC and kappa react to class imbalance; sensitivity and specificity separate the two error types. All ten come from one confusion matrix per run."
> **中文**：小样本 + 类别不平衡下 accuracy 会掩盖漏检；F1/MCC/kappa 对不平衡敏感，sensitivity/specificity 区分两类错误。

---

## 6. PART 6–7 · DEMO（检测界面）

**Q35. What does the demo actually run?**
> "The MobileNetV2 checkpoint trained on D1 with Adam, loaded from a 400 KB file that stores only the classification head. Inference runs on the laptop CPU, so no GPU and no network connection are needed."
> **中文**：D1 + Adam 训练的 MobileNetV2 头权重（约 400 KB），笔记本 CPU 推理，无需 GPU / 联网。

**Q36. How fast is it?**
> "0.3 to 1.5 seconds per image on a laptop CPU end to end, including the 224 × 224 preprocessing; the pure forward pass is 22.9 ms on CPU."

**Q37. What if the photo is from a different camera or lighting?**
> "That has not been validated, and we say so. The training photos come from one rig; a different camera is a domain shift we did not test. The honest next step is a small set of photos from the target line."
> **中文**：未验证。训练照片来自同一套拍摄装置，换相机是域偏移；下一步是采集目标产线照片。

**Q38. What happens if it misses a defect?**
> "A false negative is the expensive error, so the interface shows the confidence and keeps a log for review; the threshold can be moved toward higher sensitivity. In the report this is the sensitivity metric on the test split."

**Q39. Can it tell you where the defect is?**
> "No. It outputs one label per image. The Grad-CAM map is 7 × 7, about 32 pixels per cell, and the head averages it with a 4 × 4 pool — so it indicates a region, not a mask. Localisation needs segmentation or detection, which we did not build."
> **中文**：不能。Grad-CAM 是 7×7（每格约 32 像素）再经 4×4 池化平均，只能提示大致区域，不是掩码。

---

## 7. PART 8 · CONCLUSIONS（结论与局限）

**Q40. What are your main contributions?**
> "Three things: the full 66-run reproduction under one frozen protocol; a measured deployment profile of each backbone; and two controlled checks — a leakage control and a no-transfer ablation — that were not in the paper."
> **中文**：三项 —— 66 组完整复现、每个骨干的实测部署代价、两个对照实验（泄漏对照、无迁移消融）。

**Q41. Were you surprised by the ablation?**
> "Yes. Frozen random features collapse to 0.5000 on D1, so freezing only works because of the ImageNet weights. But end-to-end training from scratch also reaches 1.0000 — so pre-training buys cost, not accuracy, on this dataset."
> **中文**：冻结随机特征在 D1 上塌到 0.5000，说明冻结有效的前提是 ImageNet 权重；但全量从零训练也能到 1.0000 —— 预训练省的是成本，不是精度。

**Q42. What are the limitations?**
> "Four: 54 test images on D1; the authors' split is unpublished, so comparisons are trend-level; classification only, no localisation; and no learning-rate sweep."
> **中文**：四条 —— D1 只有 54 张测试图；论文划分未公开，只能比趋势；只做分类不做定位；未扫学习率。

**Q43. What would you do next?**
> "Collect photographs from the real production camera, add segmentation or anomaly detection for localisation, and run a proper learning-rate and head-size sweep on that larger set."
> **中文**：采集真实产线照片；加分割/异常检测做定位；在更大数据上扫学习率与头宽度。

---

## 8. 全组通用（任何一位都可能被问）

**Q44. Why not use the paper's reported numbers directly?**
> "Because a number without a protocol is not reproducible. We re-ran everything on one frozen split and one head, and used their numbers only as a reference column."
> **中文**：没有协议的分数不可复现；我们用同一划分、同一头重跑，只把论文数字当参照列。

**Q45. How do we know these numbers are real?**
> "Every number comes from a `metrics.json` written by the training script, aggregated into `leaderboard.csv`. The split files are committed, every run records its git commit, and a contract test verifies the file structure. `python -m src.aggregate --check` re-verifies the matrix."
> **中文**：每个数字来自训练脚本写的 `metrics.json`，汇总到 `leaderboard.csv`；划分文件入库、每次运行记录 git commit、契约测试校验结构，`--check` 可复验。

**Q46. How much of this is your own implementation?**
> "The whole pipeline is ours: data preparation, split generation, the training and batch scripts, the metrics module, the aggregator, the leakage and ablation experiments, and the two front ends. The dataset and the paper are the authors'."
> **中文**：整条流水线是我们写的（数据准备、划分、训练与批量脚本、指标模块、汇总、两个对照实验、两套前端）；数据集与论文属于作者。

**Q47. How long did the project take, and how much compute?**
> "About five weeks end to end; compute was a free Kaggle account with two concurrent T4 sessions — 66 runs plus 18 controlled runs, roughly six GPU hours in total."

**Q48. What was the hardest part?**
> "Making the comparison fair: the paper's split is unpublished, three of their cells are broken, and their preprocessing differs. Rebuilding a single frozen protocol was more work than training the models."

---

## 9. 十个最可能被追问的"硬"问题（导师向）

| # | 问题 | 30 秒答案 |
|---|---|---|
| 1 | Your test set is tiny — how robust is the ranking? | "On D2 (603 images) the top four backbones are within 0.6 points; we therefore report a range, not a winner." |
| 2 | D2 is derived from D1 — is that not double counting? | "We never combine them: D1 and D2 are reported as two separate test sets, and the leakage control quantifies the overlap effect (≤1.5 points)." |
| 3 | Why is accuracy the headline and not F1? | "Accuracy is the paper's headline; we also report F1, MCC, kappa, sensitivity and specificity, and the conclusions do not change under F1." |
| 4 | What is the novelty if you only reproduce? | "The reproduction plus three things the paper lacks: deployment cost per backbone, a leakage control, and a no-transfer ablation." |
| 5 | Your frozen backbone never adapts to the domain — isn't that a weakness? | "It is a deliberate protocol choice for a fair 11-way comparison; end-to-end fine-tuning is the natural next experiment, and our ablation shows it reaches the same accuracy at 27× the parameters." |
| 6 | Why 224 × 224 when the parts are cylinders? | "It is the ImageNet input size shared by all eleven backbones; cropping the part region is a possible improvement we did not test." |
| 7 | Could a classical method do as well? | "A pixel-level logistic regression reaches 0.926 on D1 test, clearly below 0.98 — but it shows the task is easy, which we state." |
| 8 | What if the class balance in production differs? | "Accuracy would move; that is why we report MCC, kappa, sensitivity and specificity as balance-sensitive metrics." |
| 9 | How would you deploy this in a factory? | "Wrap the MobileNetV2 head in the existing interface, run on CPU at 22.9 ms per image, log every decision, and keep a human review step for low-confidence results." |
| 10 | What would you change if you started again? | "Publish the split first, freeze the protocol, and collect a small real-world test set from the target camera before training anything." |

---

## 10. 红线：这些话不能说（说了会扣分）

| ❌ 不要说 | ✅ 应该说 |
|---|---|
| "We beat the paper by 19 points." | "Fair comparison is +8.2 points after excluding three broken cells." |
| "We proved there is data leakage." | "The leakage control was **negative**: no effect above 1.5 points." |
| "We have two independent datasets." | "D2 is the authors' augmented set derived from the same 271 photos." |
| "The model localises the defect." | "It classifies the whole image; Grad-CAM only indicates a region." |
| "1.0000 means the model is perfect." | "It means all 54 test images were correct; the interval is about [0.95, 1.00]." |
| "The paper didn't do explainability/baselines." | "The paper covers X; our additions are Y." (Never claim what the paper lacks without checking.) |
| 任何自己算/估的数字 | 只用 `leaderboard.csv` / `reports/tables/` 里的数 |

---

## 11. 兜底话术（不会答时）

| 情况 | 英文 | 中文 |
|---|---|---|
| 没做过这个实验 | "We did not run that experiment; it is a genuine limitation, and here is what we would need to do it." | 我们没做这个实验，这是真实局限，并说明要做需要什么。 |
| 数字记不清 | "I don't want to quote a number I am not sure of — the exact value is in our leaderboard, and I can follow up after the talk." | 不确定的数字我不硬说，准确值在 leaderboard 里，会后可以补。 |
| 问题超出范围 | "That is outside what we measured; what we can say from our runs is …" | 这超出我们测过的范围；从我们的实验能说的是…… |
| 被质疑方法 | "That is a fair critique. Our protocol choice was X, and the consequence is Y." | 这是合理的批评；我们的协议选择是 X，代价是 Y。 |

---

## 12. 分工（按 PPT 结构，被问"谁做了什么"时用）

| Part | 内容 | 负责人（填真实姓名） |
|---|---|---|
| 1 | Introduction / 背景与目标 | 【NAME 1】 |
| 2 | 数据集 | 【NAME 2】 |
| 3 | 数据增强、预处理与划分 | 【NAME 3】 |
| 4 | 网络、Algorithm 1、实验设置 | 【NAME 4】 |
| 5 | 训练曲线、结果、调参、与论文对比 | 【NAME 5】 |
| 6–7 | 演示界面 | 【NAME 6】/【NAME 7】 |
| 8 | 结论与局限 | 【NAME 8】 |
| — | 代码、66 组实验、对照实验 | Kenneth（Zheyi-D）、jellyfishhamburger |
| — | 报告撰写、图表核对、提交打包 | 其余成员 |

**被问到"谁写了代码"时**：
> "The pipeline and all GPU experiments were run by two members; the rest of the group owned the report, the figures, the deck and the demo recording."
