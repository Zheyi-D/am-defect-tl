# 从 0 到 1：这个项目到底做了什么

> 读者：组内任何人（含第一次接触本仓库的同学），以及想快速理解"这套东西是怎么搭起来的"的老师/评审。
> 写法：按**实际动手顺序**讲，每一步都给命令、产物和"为什么这么做"。
> 所有数字都来自仓库产物，可以逐项核对（见 §11 速查表）。

---

## 0. 一句话与阅读路线

**一句话**：复现一篇 2024 年 Expert Systems with Applications 的论文（用**迁移学习**做 **3D 打印件的缺陷二分类**），把 66 个实验全部跑通、把论文没做的 4 个分析补上，并做成一个能演示的检测界面。

**阅读路线建议**：

| 你是 | 建议读 |
|---|---|
| 第一次看这个仓库 | §0 → §1 → §2 → §3 → §9（先建立"数据→模型→产品"的整体印象） |
| 要写报告 | §1、§3、§5、§8、§12（涉及数字与结论口径） |
| 要讲 PPT | §0–§9 通读，然后看 `reports/speaker-notes.md` |
| 要复现跑一遍 | §10 全流程 |
| 只想知道边界 | §12 |

---

## 1. 起点：论文与任务

| 项 | 内容 |
|---|---|
| 论文 | Ahsan et al., *…defect detection of additive manufacturing parts using transfer learning approaches*, **Expert Systems with Applications 253 (2024) 124293** |
| 任务 | 给一张零件照片，判断**有没有表面缺陷**（拉丝、层间粘连、表面粗糙） |
| 任务类型 | **整图二分类**。不是目标检测，不做分割，不给缺陷位置 |
| 正类定义 | **positive = 缺陷（defect）**，混淆矩阵按 `[[TN, FP], [FN, TP]]`，行=真实、列=预测 |
| 论文的实验矩阵 | 11 个骨干 × 3 个优化器 × 3 个数据集 = **99 格** |
| 我们的覆盖 | **66 格**（第三个数据集作者未公开；公开部分全部做完） |

**方法核心（论文设定，我们照做）**：不训练卷积层，**只训练一个新分类头**。

```
冻结的 ImageNet 骨干  →  7×7×C 特征图
        ↓ AvgPool2d(4,4)
      1×1×C
        ↓ Flatten
        C 维向量
        ↓ Linear(C, 64) + ReLU
        64
        ↓ Dropout(0.5)
        64
        ↓ Linear(64, 2) + Softmax
   [P(无缺陷), P(缺陷)]  →  argmax  → PASS / FAIL
```

---

## 2. 数据：从哪来、长什么样

### 2.1 两个公开数据集

| 数据集 | 规模 | 尺寸 | 说明 |
|---|---|---|---|
| **D1** | 271 张（136 缺陷 / 135 正常） | 5184 × 3456 | **真实照片**，同一批零件、同一背景与光照 |
| **D2** | 3,017 张（947 / 2,070） | 128 × 128 | **D1 的增强版**（旋转 ±15°、水平翻转、亮度抖动，每张原图 11 份） |

> ⚠️ **必须记住的事实**：D2 **不是独立数据集**，它是 D1 的增强产物。它的用途是"数据量与数据质量"的对照，**不能当成"更多证据"**。

### 2.2 数据放在哪

- 原始数据**不进 Git**（体积大）：`data/` 只有一份 README。
- Kaggle 上挂载为 Dataset（`kennethdeng/am-defect-v1`），路径 `/kaggle/input/...`；本地则放在仓库外的一个目录。
- 代码不硬编码路径，用 `src/locate_data.py` 自动搜索含 `data/D1/defect` 的目录（支持挂载延迟重试）。

### 2.3 划分（这一步决定了所有实验可比性）

```
分层抽样 70 / 10 / 20，seed = 42
D1：train 189 / val 28 / test 54
D2：train 2,112 / val 302 / test 603
```

**划分一旦生成就冻结**，写进 `splits/D1.csv`、`splits/D2.csv` 并**提交到 Git**。
原因：66 个 run 必须用同一份划分，否则模型之间不可比；任何人重跑都能得到同一批图在同一个集合里。

> 我们用 `val` 只记录曲线，**不做早停、不用它选模型**，所以 `test` 是干净的。

---

## 3. 第一步：把图片变成能训练的东西

### 3.1 为什么必须做缓存

D1 原图是 5184×3456 的 JPEG。每个 epoch 都要重新解码 189 张这种图，实测**约 80 秒/epoch**，30 个 epoch 光解码就 40 分钟。所以第一步是把所有图**缩到 224×224 存成小 JPEG**。

```bash
# 1) 找到数据目录
DATA=$(python -m src.locate_data --wait 300 --diagnose)

# 2) 建 224 缓存（幂等，已存在会跳过）
python -m src.data_prepare --data-root "$DATA" --out /kaggle/temp/cache --size 224

# 3) 生成冻结划分（只做一次！）
python -m src.splits --data-root "$DATA" --out splits --seed 42
```

| 产物 | 位置 | 说明 |
|---|---|---|
| 224 缓存 | `/kaggle/temp/cache`（本地任意目录） | **不要放 `/kaggle/working`**，否则几千张小图会被打进 kernel 输出，下载极慢 |
| 划分文件 | `splits/D1.csv`、`splits/D2.csv` | 列：`path, label, split, source_id` |

### 3.2 归一化

用 ImageNet 的均值/方差：`mean=[0.485,0.456,0.406]`、`std=[0.229,0.224,0.225]`。
**不要**用 `/255` 代替 —— 论文里很可能就是这里没对齐，导致 EfficientNet 系列崩掉（见 §8.5）。

---

## 4. 第二步：模型怎么搭

### 4.1 代码位置

| 文件 | 作用 |
|---|---|
| `src/models.py` | `BACKBONES`（11 个骨干，值是候选名列表，按序回退）+ `PaperHead`（论文同款头）+ `TransferModel`（冻结逻辑） |
| `configs/_template.yaml` | 超参与结构：`pretrained: imagenet`、`freeze: all_conv`、`dense_units: 64`、`dropout: 0.5`、`input_size: 224` |

### 4.2 冻结是怎么实现的（关键三行）

```python
if freeze == "all_conv":
    for p in self.net.parameters():
        p.requires_grad = False        # ① 梯度不回流

def forward(self, x):
    with torch.no_grad():              # ② 前向不算梯度图
        feat = self.net.forward_features(x)
    return self.head(feat)             # ③ 只有头参与训练
```

另外 `train()` 里对冻结骨干保持 `eval()` 模式 —— **BatchNorm 的统计量也不会被更新**。

### 4.3 参数量（这组数字很重要）

| 骨干 | 特征维度 C | 头的参数量 | 可训练占比 | 总参数 |
|---|---|---|---|---|
| VGG16 | 512 | **32,962** | **0.02 %** | 134,293,506 |
| ResNet50 | 2048 | 131,266 | 0.56 % | 23,639,298 |
| MobileNetV2 | 1280 | **82,114** | 3.56 % | 2,305,986 |
| Xception | 2048 | 131,266 | 0.63 % | 20,938,218 |
| InceptionResNetV2 | 1536 | 98,498 | 0.18 % | 54,404,962 |

**一句话**：VGG16 里 1.34 亿参数只有 3.3 万在训练，占 0.02%。这就是"小数据集能训出东西"的原因。

### 4.4 全网络结构图

- 报告版：`results/figures/fig_network.png`
- 幻灯片版：`reports/assets/slide_network.png`
- 生成脚本：`tools/make_network_figure.py`

---

## 5. 第三步：训练一个 run

```bash
python -m src.train \
  --config configs/_template.yaml \
  --model vgg16 --dataset D1 --optimizer adam \
  --data-root "$DATA" --cache-root /kaggle/temp/cache \
  --save-weights
```

### 5.1 超参（论文两阶段设定）

| 项 | 值 |
|---|---|
| 输入 | 224 × 224 |
| 学习率 | 1e-3（三个优化器相同） |
| epochs | D1 = 30，D2 = 50 |
| batch | D1 = 8，D2 = 32 |
| seed | 42 |
| 损失 | 交叉熵（2 类） |

### 5.2 一个 run 内部发生什么

```
读图（缓存优先） → 训练 N 个 epoch（每 epoch 记 train/val 曲线）
   → 取最后一轮的权重（无早停）
   → 在 test 上算 10 个指标 + 2×2 混淆矩阵
   → 写 results/runs/<run_id>/metrics.json + train_log.csv + 曲线图
   → （可选）保存分类头 model.pt
```

`run_id` 的命名规则 **必须** 是：

```
<model>__<dataset>__<optimizer>__s<seed>
例：mobilenet_v2__D1__adam__s42
```

目录名必须与 `metrics.json.run_id` 一致，否则汇总脚本会对不上。

### 5.3 `metrics.json` 里有什么

- 元信息：`run_id, git_commit, model, dataset, optimizer, seed, input_size, n_train/val/test, n_params_total/trainable`
- 指标：`metrics.{train,val,test}.{accuracy, precision, recall, f1, mcc, kappa, auc, map, sensitivity, specificity}`
- 混淆矩阵：`confusion.{train,val,test}`（`[[TN,FP],[FN,TP]]`）
- 训练耗时 `train_time_s`

### 5.4 checkpoint 只存头

`model.pt`（131–515 KB）里只有：`{model, num_classes, freeze, dense_units, dropout, input_size, feat_shape, head_state, run_id}`。
**不存骨干**：推理时用 timm 重新加载 ImageNet 骨干（离线缓存后不需要联网），再把 `head_state` 套上去。好处是 10 个 checkpoint 加起来不到 5 MB。

---

## 6. 第四步：跑完 66 个 run

```bash
python -m src.batch --data-root "$DATA" --out results --cache-root /kaggle/temp/cache
```

### 6.1 矩阵

```
11 个骨干 × 3 个优化器（Adam / SGD / RMSprop）× 2 个数据集 = 66 个 run
```

11 个骨干：VGG16、VGG19、ResNet50、ResNet101、MobileNetV2、Xception、InceptionResNetV2、NASNetLarge、EfficientNet-B0、EfficientNet-B7、EfficientNet-V2M。

`batch.py` 的行为：某个 run 失败**不中断**，失败清单写到 `results/batch_failures.json`，最后有失败才 `exit 1`。已存在 `metrics.json` 的 run 会**跳过**（要重跑必须 `--force`）。

### 6.2 为什么在 Kaggle 上跑

- 本机没有 GPU；Kaggle 免费 T4 足够（一个 run 几秒到几分钟）。
- 免费账号**最多 2 个并发 GPU 会话**，第 3 个会被拒。
- 整套流程用 `tools/build_kernel.py` 打成**自包含 kernel**：把 `src/*.py analysis/*.py tools/*.py configs/*.yaml splits/*.csv requirements.txt` 压成 zip → base64 内嵌进 `main.py` → 推送运行。**不需要 token、不需要 git clone**。

```bash
python tools/build_kernel.py --slug am-defect-v1 --cmd 'DATA=$(python -m src.locate_data --wait 300) && python -m src.data_prepare --data-root "$DATA" --out /kaggle/temp/cache --size 224 && python -m src.batch --data-root "$DATA" --out results --cache-root /kaggle/temp/cache'
```

产物直接从 kernel output 下载（`kaggle kernels output <slug> -p <dir>`）。

---

## 7. 第五步：汇总，并保证"数字不会错"

```bash
python -m src.aggregate            # 合并 66 个 metrics.json → results/leaderboard.csv
python -m src.aggregate --check    # 只校验完整性（应输出 66 / 66 complete）
python -m analysis.export_tables --check   # 表格数值逐格核对
```

| 产物 | 说明 |
|---|---|
| `results/leaderboard.csv` | 66 行我们的结果 + 33 行作者报告值（后者的 `delta_acc` 为空） |
| `reports/tables/table{1..6}_*.{md,tex}` | 报告用表，md + LaTeX 双份 |
| `results/figures/` + `CATALOG.md` | 23 张图，图号以 `CATALOG.md` 为准 |

**核对机制**：报告里每张表的数值都从 `leaderboard.csv` 重新生成，并逐格比对源文件。
最近一次核对：**522 个数值，0 处不一致**。这是"报告数字可信"的证据。

---

## 8. 第六步：论文没做的 4 个分析

### 8.1 数据泄漏对照（结论：阴性）

**问题**：D2 是 D1 增强来的，随机划分会让同一张原图的副本同时出现在 train 和 test，准确率可能虚高。

**做法**（`analysis/leakage.py`）：

1. 用 D1 重新生成带溯源的增强集 **D2′**（`source_id` 保留在文件名里）
2. 对同一份 D2′ 生成两种划分：`D2p_random.csv`（随机）与 `D2p_group.csv`（**按 source_id 分组**）
3. 同样超参训 3 个模型 × 2 种训练规模 = **6 个对照 run**
4. 比较 test 指标

**结果**（`results/leakage.csv`）：

| 设置 | 模型 | 随机划分 acc | 分组划分 acc | Δ |
|---|---|---|---|---|
| full | MobileNetV2 | 0.9983 | 1.0000 | −0.0017 |
| full | ResNet50 | 0.9916 | 0.9966 | −0.0050 |
| full | VGG16 | 1.0000 | 0.9882 | +0.0118 |
| small15 | MobileNetV2 | 0.9799 | 0.9949 | −0.0151 |
| small15 | ResNet50 | 0.9664 | 0.9764 | −0.0100 |
| small15 | VGG16 | 0.9698 | 0.9731 | −0.0033 |

**结论：没有泄漏效应**（|Δ| ≤ 1.5%，多数为负）—— 高准确率来自任务本身容易，不是泄漏。
这是**阴性结果**，照实报告。

### 8.2 可解释性（结论：注意力图，不是定位）

- 方法：**Grad-CAM** + **LIME**，各取 3 个 checkpoint 出图。
- 关键限制：最后一层特征图是 **7×7**（每格约 32 px），分类头还用 `AvgPool2d(4,4)` 压过一次。
- 因此它只能说"模型大概关注这一带"，**不能给边界框、掩码或面积**。
- 我们据此**删掉了 UI 里写死坐标的"缺陷红圈"**和"缺陷面积"字段 —— 那是不诚实的。

### 8.3 部署成本（结论：同精度选小模型）

| 模型 | 参数量 | GFLOPs | CPU 单张 | T4 单张 |
|---|---|---|---|---|
| MobileNetV2 | 2.30 M | 0.60 | **22.9 ms** | 5.3 ms |
| EfficientNet-B0 | 5.29 M | 0.39 | 34.6 ms | — |
| ResNet50 | 23.6 M | 8.18 | 82.8 ms | 6.1 ms |
| Xception | 20.9 M | 9.10 | 103.4 ms | 6.3 ms |
| VGG16 | 134.3 M | 30.69 | 165.3 ms | 13.3 ms |
| NASNetLarge | 88.8 M | 23.8 | **389.5 ms** | 39.9 ms |

- GPU 上 11 个骨干全部 < 40 ms；**CPU 上只有 MobileNetV2 与 EfficientNet-B0 能实时**。
- 准确率并列第一时，MobileNetV2 参数是 VGG16 的 1/58 —— 这就是产品引擎选它的原因。

### 8.4 无迁移消融（结论：预训练买的是成本，不是准确率）

12 个补充 run：2 种初始化（随机+冻结 / 随机+全参数训练）× 3 优化器 × 2 数据集。

| 配置 | D1 test acc | D2 test acc |
|---|---|---|
| ImageNet 预训练 + 冻结（主方法） | **1.0000** | 0.9950 |
| 随机初始化 + 冻结 | **0.5000**（MCC=0，只会猜多数类） | 0.7717 |
| 随机初始化 + 全参数训练（从零） | **1.0000** | 0.9950 |

**怎么读**：

1. 冻结的随机特征 = 完全没学到东西 → **"冻结"这个策略只有配预训练权重才成立**
2. 但从零端到端训练也能到 1.00 → **这个数据集太简单**，准确率已经饱和，无法用它区分方法优劣
3. 所以预训练的价值是**成本**：82k 参数 / 30 秒 vs 2.2M 参数 / 几分钟

明细：`results_ablation/ABLATION.md`；生成脚本 `tools/run_ablation.py`、`tools/summarize_ablation.py`。

### 8.5 与论文对比的诚实口径

| 口径 | D1 | D2 |
|---|---|---|
| 全部 11 个骨干 | 0.9826 vs 0.7879 → **+19.5** | 0.9849 vs 0.8464 → **+13.9** |
| 剔除论文崩掉的 3 个 EfficientNet（那 18 格 F1=0） | 0.9815 vs 0.8992 → **+8.2** | 0.9903 vs 0.9111 → **+7.9** |

**必须这样讲**：论文的 EfficientNet-B0/B7/V2-M 报告 `acc=0.4909, F1=0`（全部预测多数类），是**没跑起来**，不是模型差。所以对外说 **+8.2（fair comparison）**，不说 +19.5，也不说"我们赢了论文"。

---

## 9. 第七步：把模型变成产品（两套前端）

### 9.1 技术版：`analysis/demo_app.py`（Gradio）

给技术问答用：能选 10 个 checkpoint（5 骨干 × 2 数据集）、看 Grad-CAM、看全模型对比表。
能演示"为什么只有 D1 权重可用"（D2 权重喂原图会崩）。

```bash
python -m analysis.demo_app --warmup --mirror   # 第一次预热权重
python -m analysis.demo_app                     # http://127.0.0.1:7860
```

### 9.2 客户端版：`analysis/demo_client.py`（给客户看的形态）

单屏、无滚动、工业检测站风格：

```
上传照片 → 点 SCAN → 激光扫描动效（1.15 s）→ PASS / FAIL + 置信度 + 耗时 + 注意力叠加
        → 写入检测记录 → 可 EXPORT CSV / CLEAR 清空
```

| 设计决定 | 理由 |
|---|---|
| 固定引擎 **MobileNetV2 · D1 · Adam** | 与最强骨干同精度，2.3 M 参数、22.9 ms（笔记本 CPU 可跑） |
| 只暴露 D1 权重 | D2 权重喂 5184×3456 原图会判错（10 个缺陷只对 2–6 个） |
| 无模型选择、无数据集名、无准确率 | 客户不需要，也不需要被这些数字误导 |
| **不做缺陷定位** | 7×7 注意力图给不出框/面积；写死的红圈已删 |
| 离线优先 | 权重缓存 + `HF_HUB_OFFLINE=1`，断网也能演示 |
| REVIEW 档 | 概率落在 0.35–0.65 时给"需复检"；实测极少触发，只作异常输入兜底 |

```bash
python -m analysis.demo_client                  # http://127.0.0.1:7861
python -m analysis.demo_client --selftest       # 一次性推理，验证环境
python -m analysis.demo_client --model resnet50 # 隐藏开关（答辩被问到"能不能换更强"时用）
```

### 9.3 静态看板：`docs/index.html`

离线可投屏的结果看板（由 `tools/build_dashboard.py` 生成）。

---

## 10. 从零重跑一遍（要多久）

| 步骤 | 命令 | 耗时（参考） |
|---|---|---|
| 装依赖 | `pip install -r requirements.txt` | 2–5 分钟 |
| 找数据 | `python -m src.locate_data --wait 300` | 几秒 |
| 建 224 缓存 | `python -m src.data_prepare ...` | 271 张约 1 分钟；3,017 张约 5 分钟 |
| 生成划分 | `python -m src.splits ...` | 几秒（**已有则不要重跑**） |
| 单 run 验证 | `python -m src.train --model vgg16 --dataset D1 --optimizer adam ...` | T4 上约 30 秒 |
| 全套 66 run | 推 Kaggle kernel（`tools/build_kernel.py`） | 运行约 20–30 分钟 + 排队（不可控） |
| 汇总 | `python -m src.aggregate` | 几秒 |
| 图 + 表 | `python -m analysis.make_figures`、`python -m analysis.export_tables` | 1–2 分钟 |
| 前端 | `python -m analysis.demo_client` | 启动约 10 秒（首次加载权重更久） |

**几个必须知道的坑**：

| 现象 | 原因 | 对策 |
|---|---|---|
| 每 epoch 80 秒 | 每轮重新解码 5184×3456 JPEG | 必须先 `data_prepare` 建缓存 |
| kernel 下载卡住 | 缓存写进了 `/kaggle/working` | 缓存放 `/kaggle/temp` |
| 第 3 个 kernel 被拒 | 免费号 GPU 会话上限 2 | 排队或串行 |
| `No pretrained weights for efficientnet_b7` | timm 移除旧名默认权重 | `BACKBONES` 用候选名列表按序回退 |
| Windows 生成的 csv 在 Linux 读不到 | 路径用了 `\` | `splits.py` 统一 `as_posix()` |
| 改了 `splits/*.csv` | 全部结果不可比 | **不要改**；要改必须重跑 66 个 run |

---

## 11. 速查表

### 11.1 关键文件地图

| 想找什么 | 去哪 |
|---|---|
| 任务说明 / 课程要求 | `docs/SUBMISSION.md` |
| 给写报告同学 | `docs/START-HERE.md` |
| 给 AI agent / 新人 | `AGENTS.md` |
| 训练管线 | `src/locate_data.py` `data_prepare.py` `splits.py` `dataset.py` `models.py` `train.py` `batch.py` `aggregate.py` `evaluate.py` |
| 分析脚本 | `analysis/leakage.py` `gradcam.py` `lime_explain.py` `efficiency.py` `make_figures.py` `export_tables.py` |
| 两套前端 | `analysis/demo_app.py`（技术）、`analysis/demo_client.py`（客户） |
| 结果数字 | `results/leaderboard.csv`、`results/runs/*/metrics.json` |
| 补充实验 | `results/leakage.csv`、`results_ablation/ABLATION.md` |
| 报告图/表 | `results/figures/`（+`CATALOG.md`）、`reports/tables/` |
| PPT | `reports/slides_draft.pptx`、备注 `reports/speaker-notes.md` |
| 测试集汇总 | `testset/`（657 张，`tools/make_testset.py` 可重建） |

### 11.2 核心数字

| 项 | 值 |
|---|---|
| 正式 run | **66**（11 × 3 × 2） |
| checkpoint | **10**（5 骨干 × 2 数据集，Adam） |
| D1 平均 test 准确率 | **0.9826** |
| D2 平均 test 准确率 | **0.9849** |
| 表格数值核对 | **522 个，0 处不一致** |
| 报告图 / 表 | **23 张 / 6 张** |
| PPT | **23 页，8 个 part，23 页均有备注** |
| 补充实验 | 泄漏 6 run + 消融 12 run |

### 11.3 术语

| 术语 | 含义 |
|---|---|
| **骨干 / backbone** | ImageNet 预训练的卷积网络（我们冻结它） |
| **头 / head** | 新加的分类头（唯一被训练的部分） |
| **冻结 / frozen** | `requires_grad=False` + `no_grad` 前向 + BN 保持 eval |
| **run_id** | `<model>__<dataset>__<optimizer>__s<seed>` |
| **D1 / D2** | 真实 271 张 / 增强 3,017 张（D2 派生自 D1） |
| **检查点 / checkpoint** | 只含分类头权重的 `model.pt`（131–515 KB） |
| **delta_acc** | 我们 - 论文的值；论文未公开的数据集行为空 |

---

## 12. 边界：能说什么、不能说什么

| 结论 | 可以这样说 | 不能这样说 |
|---|---|---|
| 复现程度 | "论文公开数据覆盖的 **66/66** 全部完成；矩阵层面 66/99" | "我们 100% 复现了论文" |
| 与论文分数 | "剔除论文坏格后 **+8.2（fair comparison）**" | "我们比论文好 19 个点" |
| 1.0000 的含义 | "在 D1 的 **54 张测试图**上全部判对" | "模型完美 / 100% 可靠" |
| 泄漏实验 | "泄漏对照是**阴性结果**" | "我们证明了存在数据泄漏" |
| 可解释性 | "Grad-CAM 是**注意力图**，7×7，不给精确位置" | "模型能定位缺陷" |
| D2 | "D2 是 D1 的**增强版**，用作对照" | "我们有两个独立数据集" |
| 无迁移消融 | "预训练买的是**成本**（参数/时间），这个数据集上准确率已饱和" | "没有迁移学习就训不出来" |

**三条铁律**（仓库里也写了）：

1. 数字只认 `results/leaderboard.csv` / `reports/tables/`，不估算、不编造
2. 泄漏对照是阴性，不要反着写
3. 不要把 D2 说成独立数据集

---

## 13. 最后：这套东西的价值在哪

1. **可复现**：冻结划分 + 自包含 kernel + 一条命令重建
2. **可追溯**：66 个 `metrics.json` → `leaderboard.csv` → 报告表格，522 个数值零差异
3. **诚实**：阴性结果照报；删掉了所有"看起来很强但站不住"的东西（假红圈、假面积）
4. **完整**：从论文数字到能演示的产品，中间每一步都有产物
5. **有增量**：4 个论文没做的分析，其中 2 个结论与直觉相反（泄漏阴性、预训练不涨点）
