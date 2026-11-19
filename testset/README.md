# testset/ —— 全部测试集（D1 + D2）

> 一次性汇总：**只含 test 划分**，共 **657 张**，约 **170 MB**。
> 图片本体不进 Git（`.gitignore` 只放行本 README），需要时用 `python tools/make_testset.py` 重新生成。

## 内容

| 数据集 | 类别 | 张数 | 来源 | 原始尺寸 |
|---|---|---|---|---|
| **D1** | defect | 27 | D1 测试划分 | 5184 × 3456（每张约 3.1 MB） |
| **D1** | nondefect | 27 | 同上 | 同上 |
| **D2** | defect | 189 | D2 测试划分 | 128 × 128（每张约 15 KB） |
| **D2** | nondefect | 414 | 同上 | 同上 |
| **合计** | | **657** | | 170.5 MB |

## 目录结构

```text
testset/
├── README.md                 ← 本文件（唯一进 Git 的）
├── manifest.csv              ← 每张图的 dataset / label / 文件路径 / source_id / 字节数
├── D1/
│   └── test/
│       ├── defect/          27 张
│       └── nondefect/       27 张
└── D2/
    └── test/
        ├── defect/          189 张
        └── nondefect/       414 张
```

## 来源与可追溯性

- 图片来自作者公开数据集（AMdataset），本地副本位于 `…\_kaggle-build\am-defect-v1\data\`
- **哪些图属于 test**，完全由仓库里冻结的划分文件决定：
  - `splits/D1.csv` → `split == "test"` 的 54 行
  - `splits/D2.csv` → `split == "test"` 的 603 行
- 复制脚本：`python tools/make_testset.py`（幂等，可随时重建）

## 用途

| 用途 | 怎么用 |
|---|---|
| 喂给客户端 demo 做人工验证 | 打开 demo → 上传 `D1/test/defect/` 里任意一张 → 应判 FAIL；`nondefect/` 应判 PASS |
| 复算指标 | 用 `splits/*.csv` 的 test 行跑 `src/train.py` 的评估，结果必须与 `results/leaderboard.csv` 一致 |
| 报告截图 | D1 的原图分辨率高，适合放报告/PPT；D2 只有 128px，仅作对照 |

## 注意

1. **不要**把这些图加进训练 —— 它们是测试集，泄漏会让所有指标作废
2. D2 是 D1 的**数据增强版**，不是独立采集；D1 的 54 张里可能有和 D2 同源的图（作者原始 D2 已丢失溯源）
3. D1 测试集只有 54 张：**错 1 张 = 1.85 个百分点**，不要用单张结果下结论
