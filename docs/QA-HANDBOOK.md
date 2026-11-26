# Q&A 手册（双语）— IDAT7215 Group 15

> 结构按 PPT 的八个 part；**问题与答案均为双语**。
> 数字来源：`results/leaderboard.csv`、`results/leakage.csv`、`results/baselines.csv`、`results/efficiency.csv`、`results_ablation/ABLATION.md`、`docs/paper_results.csv`。

---

## 实验总览 / Experiment overview

**本项目做的事，一句话**：把一篇 2024 年论文的「冻结骨干 + 小分类头」比较，在同一套固定数据划分与同一套协议下完整复现一遍，并在两个数据集上报告准确率与代价。

**In one sentence**: this project reproduces a 2024 paper's comparison of frozen ImageNet backbones with a small classification head, under one frozen data split and one shared protocol, and reports accuracy plus cost on two datasets.

| 项目 | 内容 |
|---|---|
| **任务** | 3D 打印件照片的二分类：有缺陷 / 无缺陷（正类 = 缺陷）；只做整图分类，不做定位 |
| **数据 D1** | 271 张真实照片（缺陷 136 / 正常 135），5184 × 3456 |
| **数据 D2** | 3,017 张增强图（缺陷 947 / 正常 2,070），128 × 128，由 D1 生成 |
| **数据划分** | 70 / 10 / 20，分层，种子 42，划分文件固定：D1 = 189 / 28 / 54，D2 = 2,112 / 302 / 603；66 组实验共用同一份 |
| **模型** | ImageNet 预训练骨干（全部卷积层冻结）+ 论文分类头：4×4 平均池化 → 展平 → 64 维全连接 + ReLU → Dropout 0.5 → 2 类 softmax；只训练分类头 |
| **实验矩阵** | 11 个骨干 × 3 个优化器（Adam / SGD / RMSprop）× 2 个数据集 = **66 组** |
| **统一设置** | 输入 224 × 224；学习率 1e-3；D1 训 30 轮、D2 训 50 轮；batch 8 / 32；种子 42 |
| **评估方式** | 在固定测试集上推理一次，计算 10 个指标（accuracy、precision、recall、F1、MCC、kappa、AUC、mAP、sensitivity、specificity）+ 2×2 混淆矩阵 |
| **主结果** | D2（603 张测试图）平均 **0.9849**，范围 **0.920–0.997**；D1（54 张）平均 **0.9826** |
| **与论文对比** | 全 11 个骨干：+0.195（D1）/ +0.139（D2）；剔除论文 3 个异常格后：**+0.082 / +0.079** |
| **两个对照实验** | 泄漏对照（6 组，\|Δ\| ≤ 1.5 %，阴性）；无迁移消融（12 组：D1 1.0000 / 0.5000 / 1.0000；D2 0.9950 / 0.7717 / 0.9950） |

**中文说明**：实验分两大步。第一步固定数据 —— 真实照片 D1 与其增强版 D2 各自按统一比例划分，划分文件一旦生成就不再改动，保证 66 组结果可比。第二步固定模型 —— 每个骨干只替换骨干本身，分类头、预处理、超参完全相同，因此骨干之间的差异不会被其它因素污染。评估只看冻结测试集，每组成员只跑一次训练、评一次分，避免在同一测试集上反复挑选结果。

**English**：the experiment has two fixed parts. First the data: the real photographs (D1) and their augmented copy set (D2) are split once, and those split files are never regenerated, so all 66 runs are comparable. Second the model: only the backbone changes between runs; the head, the preprocessing and the hyper-parameters are identical, so a difference between two backbones cannot come from anything else. Evaluation is a single pass over the frozen test split, which prevents selecting results by repeatedly looking at the test set.

---

## PART 1 · INTRODUCTION（封面 + 背景与目标）

**Q1. What exactly is the problem you solve?（你们要解决的到底是什么问题？）**
> **EN** "Binary classification of a photograph of a 3D-printed part: does it show a defect or not. The defect here is a surface defect — extruded strings around the part, poor layer bonding, rough patches. We do not localise the defect."
>
> **中文**：对 3D 打印件的照片做二分类，判断有无缺陷。缺陷指表面缺陷 —— 零件周围的拉丝、层间结合不良、表面粗糙。我们不做缺陷定位。

---

**Q2. Why transfer learning instead of training from scratch?（为什么用迁移学习而不是从零训练？）**
> **EN** "The public dataset has only 271 real photographs. Training millions of parameters from scratch on that would simply memorise the training set. With ImageNet weights frozen we only train thirty-three thousand to two hundred fifty-eight thousand parameters, under a minute per run, and still reach 0.98 accuracy."
>
> **中文**：公开数据集只有 271 张真实照片。在这么少的数据上从零训练几百万参数，模型只会记住训练集。冻结 ImageNet 权重后，我们只训练 3.3 万到 25.8 万个参数，每组训练不到一分钟，精度仍能到 0.98。

---

**Q3. Why this particular paper?（为什么选这篇论文？）**
> **EN** "It is a recent systematic comparison of frozen backbones on 3D-printing defect data — Expert Systems with Applications, volume 253, article 124293, 2024 — and its reported matrix is small enough to reproduce completely."
>
> **中文**：这是近几年对 3D 打印缺陷数据最系统的冻结骨干对比之一，发表于 2024 年《Expert Systems with Applications》第 253 卷、文章号 124293，且其报告的实验矩阵规模足以完整复现。

---

**Q4. Is this your own dataset?（数据集是你们自己做的吗？）**
> **EN** "No. It is the authors' public dataset, AMdataset: 271 real photographs plus the 3,017 augmented copies they shipped with it. We publish the exact split files rather than the images."
>
> **中文**：不是我们采集的。这是作者的公开数据集 AMdataset，包含 271 张真实照片和随数据集提供的 3,017 张增强图。我们发布的是精确的数据划分文件，而不是图片本身。

---

**Q5. What is your objective in one sentence?（一句话说你们的目标是什么？）**
> **EN** "Reproduce the comparison of eleven ImageNet backbones under one frozen protocol, and report both accuracy and deployment cost, so the result is usable rather than just a number."
>
> **中文**：在同一套冻结协议下复现 11 个 ImageNet 骨干的对比，并同时报告准确率与部署代价，使结果可用，而不只是一个数字。

---

## PART 2 · DATA PREPARATION（数据集）

**Q6. How many images are there, and what is the class balance?（有多少张图？类别平衡吗？）**
> **EN** "D1 has 271 real photographs: 136 defect and 135 non-defect. D2 has 3,017: 947 defect and 2,070 non-defect. Both are split 70/10/20 with stratification, so each class keeps its proportion in every split."
>
> **中文**：D1 有 271 张真实照片，缺陷 136 张、正常 135 张。D2 有 3,017 张，缺陷 947 张、正常 2,070 张。两者都按 70/10/20 分层划分，使每个类别在各划分中保持原有比例。

---

**Q7. What does a defect actually look like?（缺陷在照片里长什么样？）**
> **EN** "It is material that should not be there: thin extruded strands around the part, uneven layer edges, rough surface patches. On the slide, the two rows are the same part type under the same lighting — the only difference is the defect."
>
> **中文**：是那些不该存在的材料：零件周围的细拉丝、不平整的层边、粗糙的表面斑块。幻灯片上下两行是同一类零件、同样的光照，唯一区别就是有无缺陷。

---

**Q8. Is D2 an independent dataset?（D2 是独立数据集吗？）**
> **EN** "No, and we never present it as one. D2 is the authors' augmented set, generated from the same 271 photographs and stored at 128 by 128 pixels. That is why we report D1 and D2 separately instead of averaging them."
>
> **中文**：不是，我们也从不把它当作独立数据集。D2 是作者用同一批 271 张照片生成的增强集，以 128×128 存储。因此我们始终分开报告 D1 和 D2，而不做平均。

---

**Q9. How exactly was D2 generated?（D2 具体是怎么生成的？）**
> **EN** "It is a pre-built augmented set from the authors, not something we generated. Their published notebook only shows the online augmentation with a rotation range of fifteen degrees, so the exact offline recipe is not fully documented. We describe it as rotation up to fifteen degrees, horizontal flip and brightness jitter, about eleven copies per source image."
>
> **中文**：D2 是作者预先构建的增强集，不是我们生成的。作者公开的 notebook 只展示了在线增强（旋转范围 15 度），完整的离线生成配方并未完全公开。我们按「旋转最多 ±15 度、水平翻转、亮度抖动、每张原图约 11 份」来描述。

---

**Q10. Why is D2 only 128 by 128?（为什么 D2 只有 128×128？）**
> **EN** "That is the resolution the authors shipped, so we keep it as given and upscale to 224 only at read time. Changing it would break comparability with their reported numbers."
>
> **中文**：这是作者提供时的分辨率，我们保持原样，只在读取时放大到 224。若改动分辨率，就会与论文报告的数字失去可比性。

---

## PART 3 · DATA PREPARATION（增强 / 预处理 / 划分）

**Q11. Why resize to 224 and not keep the original resolution?（为什么缩到 224 而不保留原分辨率？）**
> **EN** "224 is the input size of every ImageNet backbone we use, which makes the eleven models comparable. Processing the original 5184 by 3456 image at full size would also need about 410 megabytes per image as float data."
>
> **中文**：224 是我们使用的所有 ImageNet 骨干的输入尺寸，这使 11 个模型之间可比。此外，把原始 5184×3456 的图像按全尺寸当作浮点数据处理，单张就需要约 410 MB。

---

**Q12. Why cache the images?（为什么要做图片缓存？）**
> **EN** "Decoding a 5184 by 3456 JPEG costs about 80 seconds per epoch across the training set, which dominates training time. We decode once, write 224 by 224 JPEGs to a cache, and afterwards each run takes under a minute."
>
> **中文**：在训练集上解码 5184×3456 的 JPEG，每个 epoch 约需 80 秒，会成为训练时间的主要部分。我们先解码一次，把 224×224 的 JPEG 写入缓存，之后每组训练不到一分钟。

---

**Q13. How do you guarantee the same split across all 66 runs?（怎么保证 66 组用的是同一份划分？）**
> **EN** "The split is a file, not a runtime call. D1 and D2 split files are generated once with seed 42 and committed to the repository, and every run reads those exact files, so no run can silently re-split the data."
>
> **中文**：划分是文件而不是运行时调用。D1 和 D2 的划分文件用种子 42 生成一次并提交到仓库，每次运行都读取同一份文件，因此没有任何一组会悄悄重新划分。

---

**Q14. Why 70/10/20 and not 80/10/10?（为什么是 70/10/20 而不是 80/10/10？）**
> **EN** "With 271 images, a 20 percent test split already gives only 54 images. A 10 percent test split would be 27 images, where a single mistake moves accuracy by 3.7 points."
>
> **中文**：在只有 271 张图的情况下，20% 的测试集也只有 54 张。若测试集占 10%，就只有 27 张，错一张准确率就会变动 3.7 个百分点。

---

**Q15. Did you check for leakage between training and test?（你们检查过训练集与测试集之间的泄漏吗？）**
> **EN** "Yes. We rebuilt the augmented set keeping the source photograph ID, compared a random split with a split grouped by source image, and ran six controlled models. Accuracy moved by at most 1.5 points, and mostly downward, so no leakage effect was detected."
>
> **中文**：检查过。我们重建增强集并保留原图 ID，把随机划分与按原图分组的划分做对比，跑了 6 个受控模型。准确率变化最多 1.5 个百分点，且多数为负，因此未检测到泄漏效应。

---

**Q16. If copies of the same photo can appear in both training and test, is D2 not leaking?（同一张照片的副本可能同时在训练集和测试集，这不算泄漏吗？）**
> **EN** "That is exactly what the leakage control tested. Grouping by source image changes accuracy by at most 1.5 points, so the ranking is unaffected. We still report D1, the real photographs, as the practical check."
>
> **中文**：这正是泄漏对照实验要回答的问题。按原图分组后，准确率变化最多 1.5 个百分点，骨干排序不受影响。我们同时报告 D1 真实照片，作为实际可用性的检验。

---

## PART 4 · MODEL TRAINING（网络 / Algorithm 1 / 实验设置）

**Q17. Which layers are frozen, and why freeze all of them?（哪些层被冻结？为什么全部冻结？）**
> **EN** "Every convolutional layer of the backbone keeps its ImageNet weights, and only the new classification head is trained. Freezing everything is what makes 66 runs feasible and prevents a 271-image dataset from over-fitting twenty million parameters."
>
> **中文**：骨干的每一个卷积层都保留 ImageNet 权重，只训练新的分类头。全部冻结既让 66 组实验可行，也避免 271 张图去过拟合两千万参数。

---

**Q18. Why 64 units in the head, and why dropout 0.5?（为什么分类头是 64 维？为什么 dropout 取 0.5？）**
> **EN** "Those are the paper's settings: 4 by 4 average pooling, one dense layer with 64 units and ReLU, dropout of 0.5, and two output units. We reproduce them so our numbers stay comparable, and we did not tune the head."
>
> **中文**：这些是论文的设置：4×4 平均池化、一个 64 维全连接层加 ReLU、dropout 0.5、两个输出单元。我们照此复现以保持可比，并没有调分类头。

---

**Q19. Why is the feature map 7 by 7?（为什么特征图是 7×7？）**
> **EN** "All eleven backbones downsample a 224 by 224 input by a factor of 32, so the last convolutional output is 7 by 7 with C channels — 512 for VGG16, 2,048 for ResNet50. The 4 by 4 average pooling in the head is what reduces it to a single point."
>
> **中文**：11 个骨干都把 224×224 的输入下采样 32 倍，所以最后卷积输出是 7×7、C 个通道 —— VGG16 是 512 通道，ResNet50 是 2,048 通道。是头部的 4×4 平均池化把它压成一个点。

---

**Q20. What does no_grad do in Algorithm 1, and why does it matter?（Algorithm 1 里的 no_grad 起什么作用？为什么重要？）**
> **EN** "It stops PyTorch from building a gradient graph through the frozen backbone, so the backward pass only touches the head. BatchNorm also stays in eval mode, so its running statistics are not updated by our data."
>
> **中文**：它阻止 PyTorch 在冻结骨干中构建梯度图，因此反向传播只作用于分类头。同时 BatchNorm 保持 eval 模式，其滑动统计量不会被我们的数据更新。

---

**Q21. Why three optimisers, and why no learning-rate sweep?（为什么用三个优化器？为什么不扫学习率？）**
> **EN** "The three optimisers are part of the matrix we reproduce. We deliberately did not sweep the learning rate, because the protocol had to stay identical across all 66 runs. We state this as a limitation instead of hiding it."
>
> **中文**：三种优化器是我们复现的矩阵的一部分。我们有意没有扫学习率，因为 66 组实验必须保持完全一致的协议。我们把它作为局限如实说明，而不是隐藏。

---

**Q22. Why these eleven backbones?（为什么是这 11 个骨干？）**
> **EN** "They are the eleven in the paper, spanning three families: VGG16 and VGG19, ResNet50 and ResNet101, MobileNetV2, Xception, InceptionResNetV2, NASNetLarge, and three EfficientNets — B0, B7 and V2-M."
>
> **中文**：它们就是论文里的 11 个骨干，涵盖三大类：VGG16/19、ResNet50/101、MobileNetV2、Xception、InceptionResNetV2、NASNetLarge，以及三个 EfficientNet —— B0、B7 和 V2-M。

---

**Q23. The paper has three EfficientNet cells with F1 equal to zero — why keep them?（论文里有 3 个 EfficientNet 格 F1 为 0，为什么还保留？）**
> **EN** "Because the matrix has to be the paper's matrix. We keep all eleven, flag those three broken cells in the comparison, and report the difference both with and without them."
>
> **中文**：因为我们的矩阵必须与论文的矩阵一致。我们保留全部 11 个，在对比时标出那 3 个异常的格，并同时给出包含与不包含它们的两种差值。

---

**Q24. How long did the 66 runs take?（66 组实验跑了多久？）**
> **EN** "About 41 seconds per D1 run and about seven minutes per D2 run on a single Tesla T4, so roughly 250 minutes of GPU time in total — about four GPU hours, not counting retries."
>
> **中文**：在单张 Tesla T4 上，D1 每组约 41 秒，D2 每组约 7 分钟，合计约 250 分钟 GPU 时间，约 4 个 GPU 小时，不计重跑。

---

## PART 5 · TRAINING & RESULTS（曲线 / 骨干 / 调参 / 与论文对比）

**Q25. Why report D2 as the headline rather than D1?（为什么主口径用 D2 而不是 D1？）**
> **EN** "D2 has 603 test images against 54 on D1, so one mistake costs 0.17 points instead of 1.85. D2 also shows a real spread, from 0.920 to 0.997, while D1 saturates with 18 of 33 runs exactly at 1.0000. D1 is still shown as the real-photograph reference."
>
> **中文**：D2 有 603 张测试图，D1 只有 54 张，所以错一张的代价分别是 0.17 分和 1.85 分。D2 还有真实区分度，从 0.920 到 0.997；而 D1 已饱和，33 组里有 18 组恰好 1.0000。D1 仍作为真实照片的参照保留。

---

**Q26. Is 0.98 not suspiciously high?（0.98 是不是高得可疑？）**
> **EN** "It is high because the task itself is easy. A pixel-level logistic regression already reaches 0.926 on the D1 test split, and predicting the majority class alone gives 0.687 on D2. Our models are clearly better than those baselines, but we do not claim a hard problem was solved."
>
> **中文**：高是因为任务本身容易。像素级逻辑回归在 D1 测试集上就有 0.926，而只猜多数类在 D2 上就有 0.687。我们的模型明显优于这些基线，但我们不宣称解决了一个困难问题。

---

**Q27. Why does validation loss rise while accuracy stays flat?（为什么验证损失上升而准确率不变？）**
> **EN** "After about ten epochs the model starts fitting noise: training loss keeps falling to 0.01, validation loss turns upward, and validation accuracy stops improving. That is the standard over-fitting signature on a small training set."
>
> **中文**：大约 10 轮之后模型开始拟合噪声：训练损失继续降到 0.01，验证损失转而上升，验证准确率不再提升。这在小训练集上是典型的过拟合特征。

---

**Q28. Which backbone is the best?（哪个骨干最好？）**
> **EN** "On D2, Xception averages 0.997 and MobileNetV2 averages 0.995 — a 0.2 point difference on 603 images, which is about one image. So we do not crown a winner on accuracy; the decision is made by cost."
>
> **中文**：在 D2 上，Xception 平均 0.997，MobileNetV2 平均 0.995 —— 在 603 张图上差 0.2 个百分点，大约相当于一张图。所以我们不靠准确率定冠军，而是由成本决定。

---

**Q29. Which backbone would you deploy?（你会部署哪个骨干？）**
> **EN** "MobileNetV2 trained on D1. It has 2.3 million parameters and runs at 22.9 milliseconds per image on a CPU, with the same accuracy as VGG16, which needs 134 million parameters and 165 milliseconds. That is the checkpoint inside the demo."
>
> **中文**：在 D1 上训练的 MobileNetV2。它有 230 万参数，CPU 上每张图 22.9 毫秒，精度与 VGG16 相同，而 VGG16 需要 1.34 亿参数、165 毫秒。演示里用的就是这个权重。

---

**Q30. What does changing the optimiser do?（换优化器会带来什么变化？）**
> **EN** "It moves accuracy by 0 to 4 points, and only for the weakest backbone. The ranking of backbones never changes, so the training recipe is not what decides the outcome here."
>
> **中文**：它让准确率变化 0 到 4 个百分点，而且只影响最弱的骨干。骨干之间的排序从不改变，所以在这个任务里起决定作用的不是训练配方。

---

**Q31. Why is your accuracy 19.5 points above the paper on D1?（你们的 D1 精度比论文高 19.5 分，为什么？）**
> **EN** "That raw gap is misleading. Three EfficientNet cells in the paper report an F1 of zero, which means they predicted only the majority class. Excluding those cells the gap is plus 8.2 on D1 and plus 7.9 on D2. The rest is explained by their unpublished split and their input normalisation."
>
> **中文**：表面上的 19.5 分差距有误导性。论文里有 3 个 EfficientNet 格报告 F1 为 0，意味着它们只预测了多数类。剔除这些格后，D1 上的差距是 +8.2，D2 上是 +7.9。其余差异可由论文未公开的划分方式与其输入归一化解释。

---

**Q32. Is it fair to compare your split with theirs?（用你们的划分和他们的结果比较公平吗？）**
> **EN** "Only at the level of trends, not cell by cell, because they never publish their split. That is why we compare the ordering of backbones and the size of the gap, rather than individual numbers."
>
> **中文**：只能在趋势层面比较，不能逐格比较，因为论文从未公开其划分。因此我们比较的是骨干的排序以及差距的量级，而不是单个数字。

---

**Q33. Why is the D1 test set only 54 images?（为什么 D1 测试集只有 54 张？）**
> **EN** "271 images with a 70/10/20 stratified split gives 54 test images. Using them for training would leave no independent check, so we keep the split fixed and state the statistical limitation: the 95 percent interval for 54 out of 54 is roughly 0.95 to 1.00."
>
> **中文**：271 张图按 70/10/20 分层划分，测试集就是 54 张。若把它们用于训练就没有独立检验了，所以我们固定这一划分，并如实说明统计局限：54 张全对时的 95% 区间大约是 0.95 到 1.00。

---

**Q34. Why ten metrics instead of just accuracy?（为什么用 10 个指标而不是只看准确率？）**
> **EN** "On a small and imbalanced test set, accuracy hides false negatives. F1, MCC and kappa react to class imbalance, while sensitivity and specificity separate the two error types. All ten come from one confusion matrix per run."
>
> **中文**：在小而不平衡的测试集上，准确率会掩盖漏检。F1、MCC 和 kappa 对类别不平衡敏感，敏感度和特异度则区分两类错误。这 10 个指标都由每组实验的一张混淆矩阵算出。

---

## PART 6–7 · DEMO（检测界面）

**Q35. What does the demo actually run?（演示实际跑的是什么？）**
> **EN** "The MobileNetV2 checkpoint trained on D1 with Adam, loaded from a file that stores only the classification head. Inference runs on the laptop CPU, so no GPU and no network connection are required."
>
> **中文**：用 D1 加 Adam 训练的 MobileNetV2 权重，从只保存分类头的文件中加载。推理在笔记本 CPU 上运行，不需要 GPU，也不需要联网。

---

**Q36. How fast is it?（速度多快？）**
> **EN** "End to end, 0.3 to 1.5 seconds per image on a laptop CPU, including the 224 by 224 preprocessing. The pure forward pass alone is 22.9 milliseconds on CPU."
>
> **中文**：端到端在笔记本 CPU 上每张图 0.3 到 1.5 秒，包含 224×224 的预处理。仅前向推理本身在 CPU 上是 22.9 毫秒。

---

**Q37. What if the photo comes from a different camera or lighting?（换相机或换光照还行吗？）**
> **EN** "That has not been validated, and we say so plainly. The training photographs all come from one rig, so a different camera is a domain shift we did not test. The honest next step is a small set of photographs from the target line."
>
> **中文**：这一点尚未验证，我们也直言不讳。训练照片都来自同一套拍摄装置，换相机属于我们未测试的域偏移。诚实的下一步是采集目标产线的一小批照片。

---

**Q38. What happens if it misses a defect?（如果漏检了怎么办？）**
> **EN** "A false negative is the expensive error, so the interface shows the confidence and keeps a log for review. The threshold can be moved toward higher sensitivity, and in the report this is the sensitivity metric on the test split."
>
> **中文**：漏检是代价更高的错误，所以界面显示置信度，并保留日志供复核。阈值可以朝更高敏感度方向调整；在报告中，这对应测试集上的敏感度指标。

---

**Q39. Can it tell you where the defect is?（能指出缺陷在哪里吗？）**
> **EN** "No. It outputs one label per image. The Grad-CAM map is 7 by 7, about 32 pixels per cell, and the head averages it with a 4 by 4 pool, so it indicates a region rather than a mask. Localisation needs segmentation or detection, which we did not build."
>
> **中文**：不能。它每张图只输出一个标签。Grad-CAM 图是 7×7，每格约 32 像素，且头部又用 4×4 池化做了平均，所以它提示的是一个区域，而不是掩码。定位需要分割或检测模型，我们没有做。

---

## PART 8 · CONCLUSIONS（结论与局限）

**Q40. What are your main contributions?（主要贡献是什么？）**
> **EN** "Three things: the full 66-run reproduction under one frozen protocol, a measured deployment profile for every backbone, and two controlled checks — a leakage control and a no-transfer ablation — that the paper does not report."
>
> **中文**：三点：在同一冻结协议下完成 66 组完整复现；为每个骨干测量部署代价；以及论文未报告的两个受控实验 —— 泄漏对照与无迁移消融。

---

**Q41. Were you surprised by the ablation?（消融结果意外吗？）**
> **EN** "Yes. Frozen random features collapse to 0.5000 on D1, so freezing only works because of the ImageNet weights. But end-to-end training from scratch also reaches 1.0000, so pre-training buys cost, not accuracy, on this dataset."
>
> **中文**：确实意外。冻结的随机特征在 D1 上塌到 0.5000，说明冻结之所以有效，前提是 ImageNet 权重。但从头端到端训练同样能到 1.0000，所以在这个数据集上，预训练换来的是成本，而不是精度。

---

**Q42. What are the limitations?（有哪些局限？）**
> **EN** "Four. The D1 test split holds only 54 images. The authors' split is unpublished, so comparisons are at trend level. We do classification only, without localisation. And we did not sweep the learning rate."
>
> **中文**：四条。D1 测试集只有 54 张图。论文的划分未公开，因此比较只能停留在趋势层面。我们只做分类，不做定位。此外我们没有扫学习率。

---

**Q43. What would you do next?（下一步会做什么？）**
> **EN** "Collect photographs from the real production camera, add segmentation or anomaly detection for localisation, and run a proper learning-rate and head-size sweep on that larger set."
>
> **中文**：采集真实产线相机的照片；加入分割或异常检测以实现定位；并在更大的数据上认真扫一遍学习率与分类头宽度。

---

## 全组通用

**Q44. Why not use the paper's reported numbers directly?（为什么不直接用论文报告的数值？）**
> **EN** "Because a number without a protocol is not reproducible. We re-ran everything on one frozen split with one head, and used their numbers only as a reference column."
>
> **中文**：因为没有协议的分数不可复现。我们用同一份固定划分和同一个分类头重跑了全部实验，只把论文的数字当作参照列。

---

**Q45. How do we know these numbers are real?（怎么证明这些数字是真的？）**
> **EN** "Every number comes from a metrics file written by the training script and aggregated into one leaderboard. The split files are committed, each run records its git commit, and a contract test verifies the file structure, so the whole matrix can be re-checked."
>
> **中文**：每个数字都来自训练脚本写出的指标文件，并汇总到一张总表。划分文件已入库，每次运行记录对应的 git commit，还有契约测试校验文件结构，因此整个矩阵都可以复核。

---

**Q46. How much of this is your own implementation?（有多少是你们自己实现的？）**
> **EN** "The whole pipeline is ours: data preparation, split generation, the training and batch scripts, the metrics module, the aggregator, the leakage and ablation experiments, and the two front ends. The dataset and the paper belong to the authors."
>
> **中文**：整条流水线都是我们实现的：数据准备、划分生成、训练与批量脚本、指标模块、汇总、泄漏与消融实验，以及两套前端界面。数据集与论文属于原作者。

---

**Q47. How long did the project take, and how much compute did you use?（项目做了多久？用了多少算力？）**
> **EN** "About five weeks end to end. Compute was a free Kaggle account with two concurrent T4 sessions: 66 main runs plus 18 controlled runs, roughly six GPU hours in total."
>
> **中文**：前后约五周。算力用免费 Kaggle 账号，最多两个并发的 T4 会话：66 组主实验加 18 组受控实验，总计约 6 个 GPU 小时。

---

**Q48. What was the hardest part?（最难的部分是什么？）**
> **EN** "Making the comparison fair. The paper's split is unpublished, three of their cells are broken, and their preprocessing differs. Rebuilding one frozen protocol was more work than training the models."
>
> **中文**：最难的是让比较公平。论文的划分未公开，其中有 3 个格是坏的，而且预处理方式也不同。重建一套统一的冻结协议，比训练模型本身更费功夫。
