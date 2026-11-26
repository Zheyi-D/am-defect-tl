# 论文原文（本地两份，都不进 Git）

## 两份文件

| 文件 | 版本 | 页数 | 来源 |
|---|---|---|---|
| `Ahsan2024_ESWA124293_published.pdf` | **正式发表版（ESWA 2024）** | 23 | ScienceDirect，`1-s2.0-S095741742401159X-main.pdf`，2026-11-26 由 Kenneth 提供 |
| `Ahsan2023_arXiv2310.08645.pdf` | 预印本（arXiv v1, 2023-10） | 20 | <https://arxiv.org/abs/2310.08645>（CC-BY 4.0） |

配套的纯文本（用于检索）：`published_text.txt`（147 KB）、`preprint_text.txt`（64 KB）。

> PDF 与文本都在 `.gitignore` 里（版权 + 体积），不随仓库分发；`README.md` 入库。

**正式版引用（报告 References 用这条）**

```text
[1] M. M. Ahsan, S. Raman, Y.-T. Liu, and Z. Siddique, "Defect analysis of 3D printed object using
    transfer learning approaches," Expert Systems with Applications, vol. 253, p. 124293, Nov. 2024,
    doi: 10.1016/j.eswa.2024.124293.
```

---

## 正式版全文核验结果（2026-11-26，逐词计数）

| 维度 | 预印本（2023） | **正式版（2024，已核）** |
|---|---|---|
| 数据集 | 2 个（Study One / Two） | **3 个**（Study Three 追加，第三方公开数据，1,557 张，未随论文发布） |
| 骨干 | 6 个 | **11 个**（VGG16/19、ResNet50/101、MobileNetV2、InceptionResNetV2、Xception、NASNetLarge、EfficientNet-B0/B7/V2-M） |
| 优化器 | 2 个（Adam、SGD） | **3 个**（Adam 39 处 / SGD 34 处 / RMSprop 35 处） |
| 指标 | 4 个 | **10 个**（accuracy、precision、recall、F1、MCC、kappa、AUC、mAP、sensitivity、specificity） |
| **可解释性** | 0 处 | ✅ **只有 LIME**（全文 13 处）；**Grad-CAM 为 0 处** |
| 传统 baseline（MLP / 简单 CNN / 双流 CNN） | — | ❌ **论文正文没有**；它们只存在于作者仓库的 `base_algorithm.ipynb` 与 `baseline_one/two/three_*.xlsx` |

**结论（写报告/答问时用）**：
1. 论文的可解释性用的是 **LIME**，不是 Grad-CAM → 我们说"我们也做了 LIME + Grad-CAM"是准确的；**不能说"论文没有可解释性"**。
2. 论文**没有**传统机器学习 baseline → 我们补的 majority / 像素逻辑回归 / 冻结特征逻辑回归是**新增**对照，属于加分项，不是"补做论文缺的 baseline"。
3. 作者仓库另有 `base_algorithm.ipynb`（MLP / 简单 CNN / 双流 CNN），但**没有写进论文**；若被问"你们复现了它的 baseline 吗"，答："论文正文没有这些 baseline；作者仓库里有一份独立 notebook，我们以论文为准。"

---

## 为什么此前只有预印本

Elsevier 正式版在付费墙后，我们最初只能拿到 arXiv 预印本；2026-11-26 组员通过学校订阅下载了正式版（PII `S095741742401159X`），现已入库。预印本内容明显更早（2 数据集 / 6 骨干 / 无 LIME），**引用与对标一律以正式版为准**。
