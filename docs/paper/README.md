# 论文原文（本地放一份，不进 Git）

## 已下载的版本

| 项 | 内容 |
|---|---|
| 文件 | `Ahsan2023_arXiv2310.08645.pdf`（8.8 MB，20 页） |
| 来源 | arXiv 预印本 · <https://arxiv.org/abs/2310.08645> · PDF: <https://arxiv.org/pdf/2310.08645> |
| 题目 | *Defect Analysis of 3D Printed Cylinder Object Using Transfer Learning Approaches* |
| 作者 | Md Manjurul Ahsan, Shivakumar Raman, Zahed Siddique（University of Oklahoma） |
| 版本 | arXiv v1，提交于 2023-10-12（正文标注 A PREPRINT, October 16, 2023） |
| 许可 | **CC-BY 4.0**（可自由下载/引用，需署名） |
| 抽取的纯文本 | `preprint_text.txt`（同样不进 Git，便于 grep） |

> 两个文件都在 `.gitignore` 里：体积大、且属于第三方版权材料，不随仓库分发。
> 重新下载：`curl -L -o docs/paper/Ahsan2023_arXiv2310.08645.pdf https://arxiv.org/pdf/2310.08645`

## ⚠️ 这不是 ESWA 正式发表版

正式版是：*Expert Systems with Applications*, vol. 253, p. 124293, Nov. 2024, DOI `10.1016/j.eswa.2024.124293`
（作者名单在预印本 3 人基础上增加 Ying-Tao Liu）。**两者内容范围差别很大**，引用时必须区分：

| 维度 | arXiv 预印本（本文件） | ESWA 正式版（我们复现的对象） |
|---|---|---|
| 数据集 | **2 个**（Study One / Study Two） | **3 个**（第三个 1,557 张，未公开） |
| 骨干 | **6 个**（VGG16、VGG19、ResNet50、ResNet101、InceptionResNetV2、MobileNetV2） | **11 个**（另加 Xception、NASNetLarge、EfficientNet-B0/B7/V2-M） |
| 优化器 | **2 个**（Adam、SGD） | **3 个**（Adam、SGD、RMSprop） |
| 指标 | 4 个（accuracy / precision / recall / F1） | **10 个**（另加 MCC、kappa、AUC、mAP、sensitivity、specificity） |
| 可解释性 | **没有**（全文 0 处 LIME / Grad-CAM） | 作者 notebook 里有 LIME + Grad-CAM（见 `docs/AUTHOR_CODE.md`） |
| baseline 对照 | 没有 | Study Three 含 MLP / 简单 CNN / 双流 CNN |

**含义**：
- 预印本**不能**用来判断正式版"有没有可解释性/baseline"——它太早期。
- 我们报告里的对标数字**不是**从这份 PDF 抄的，而是从作者公开的 xlsx 抽取，存在
  `docs/paper_results.csv`（297 行）与 `docs/PAPER_RESULTS.md`。
- 如果组员要引用"论文说了什么"，请以 `docs/paper_results.csv` + `docs/AUTHOR_CODE.md` 为准。

## 怎么拿到正式版（Elsevier 付费墙）

| 途径 | 说明 |
|---|---|
| **HKU 图书馆**（推荐） | 登录 <https://www.sciencedirect.com/science/article/pii/S0957417424011595> 或经 HKU VPN / EZproxy，可直接下 PDF（机构订阅） |
| 作者主页 / 代码仓库 | 作者有公开 GitHub（见 `docs/AUTHOR_CODE.md`），可邮件索取 accepted manuscript |
| 邮件问通讯作者 | 第一作者 Ahsan: `ahsan@ou.edu`（OU SMIS Lab） |
| 不要用 | Sci-Hub 之类盗版站点（学术不端风险，且 Turnitin/学校网络会记录） |

> 目前我们**没有**正式版 PDF。所有 66 格对标用的作者报告值来自作者 xlsx，不是 PDF 正文，所以不影响实验与结论。

## 引用格式（IEEE）

**正式版（报告 References 用这条）**

```text
[1] M. M. Ahsan, S. Raman, Y.-T. Liu, and Z. Siddique, "Defect analysis of 3D printed object using
    transfer learning approaches," Expert Systems with Applications, vol. 253, p. 124293, Nov. 2024,
    doi: 10.1016/j.eswa.2024.124293.
```

**预印本（只在引用"早期版本"时使用）**

```text
[2] M. M. Ahsan, S. Raman, and Z. Siddique, "Defect analysis of 3D printed cylinder object using
    transfer learning approaches," arXiv:2310.08645 [cs.CV], Oct. 2023. [Online].
    Available: https://arxiv.org/abs/2310.08645
```

## 用这份 PDF 能做什么

| 用途 | 是否可用 |
|---|---|
| 写 Introduction / Background 的文献综述 | ✅ 可用（引言、相关工作部分在正式版里基本保留） |
| 引用方法描述（迁移学习 + 冻结 + 分类头） | ✅ 可用（该部分两版一致：VGG16(ImageNet, include_top=False) + AvgPool + Dense(64)） |
| 引用"论文有 11 个骨干 / 3 个数据集 / 10 个指标" | ❌ 不能用预印本，要引正式版 |
| 引用"论文的 LIME/Grad-CAM 结论" | ❌ 预印本没有；正式版需核对原文 |
| 复现实验 | ⚠️ 不够，详见 `docs/AUTHOR_CODE.md`（作者 notebook 才是唯一高保真来源） |
