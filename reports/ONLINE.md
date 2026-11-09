# 在线共享文档（WPS 金山文档）

| 项 | 值 |
|---|---|
| **文档链接** | **https://www.kdocs.cn/l/cokbmUbGMYkE** |
| 文档名 | `IDAT7215 Topic4 Report.docx` |
| 类型 | WPS 文字（`.docx`） |
| 文件 ID | `aDNJSYqGRxM9ZTacoAue1xvT1kZqTrVFr` |
| 云盘 ID | `66138690` |
| 分享链接 ID | `cokbmUbGMYkE` |
| 分享范围 | `anyone`（持有链接即可访问），状态 `open` |
| 创建日期 | 2026-11-09 |

> 这是**报告正文唯一的协同编辑入口**。仓库里不放 docx，只放链接与结构源。

---

## 文档里只有两样东西

1. **封面**（全部留空待填）：课程名、题目、副标题、Group No.、Programme / Class、Group Leader、
   8 人姓名 — UID、Word Count、Repository、Date of Submission
2. **各级标题**（正文全空）：
   - `Abstract`、`List of Figures`、`List of Tables`
   - `1 Introduction` → 1.1 Background and Motivation / 1.2 Transfer Learning for Small Datasets / 1.3 Objectives and Scope
   - `2 Project Description` → 2.1 Dataset / 2.2 Network Architectures / 2.3 Training Protocol / 2.4 Evaluation Metrics
   - `3 Results and Discussion` → 3.1 Overall Model Comparison / 3.2 Optimizer Ablation /
     3.3 Comparison with the Reported Results / 3.4 Data-Leakage Control Experiment /
     3.5 Explainability: Grad-CAM and LIME / 3.6 Deployment Cost
   - `4 Conclusion`
   - `Individual Contributions`、`References`、`Appendix A Full Experimental Results`

**没有任何写作说明、图表清单或结论文字** —— 那些在仓库里（见下方"取材"），不放进文档。

---

## 谁做什么

| 角色 | 操作 |
|---|---|
| **8 位成员** | 打开链接 → 在自己负责的标题下写正文 |
| **组长** | 维护分享权限；定稿时导出 docx → 存 `reports/submission/` |
| **AI agent** | 只改仓库文件；需要改结构时重新生成 docx 并覆盖上传 |

> ⚠️ 如果打开后是**只读**：请在金山文档右上角「分享」里把权限改为**可编辑**，或把成员加为协作者。
> 链接分享的默认权限取决于账号设置，API 无法设置"编辑/只读"。

---

## 结构从哪来

标题结构定义在 **`tools/build_report_docx.py` 的 `SECTIONS`** 常量里。

要改章节（加一节、改标题措辞）：

```bash
# 1) 改 tools/build_report_docx.py 的 SECTIONS
# 2) 本地重新生成
python tools/build_report_docx.py --out report_draft.docx
# 3) 覆盖上传到同一文档（链接不变）
#    用 kdocs-cli drive upload-file，file_id = aDNJSYqGRxM9ZTacoAue1xvT1kZqTrVFr
```

⚠️ 覆盖上传会**清空正文**，只在还没人写东西时使用。

---

## 写正文时怎么取材（都在仓库里，不进文档）

| 需要 | 位置 |
|---|---|
| 所有数字 | `results/leaderboard.csv`、`results/leakage.csv`、`results/efficiency.csv` |
| 表格（可直接粘贴） | `reports/tables/table*.md` |
| 图 | `results/figures/`，图号与 caption 见 `INDEX.md` |
| 章节内容要点 / 字数预算 | `reports/WPS-REPORT-OUTLINE.md` |
| 方法细节 | `README.md`、`docs/DATA.md`、`docs/AUTHOR_CODE.md` |
| 提交要求 | `docs/SUBMISSION.md` |

---

## 定稿与备份

1. 金山文档 →「文件」→「下载」→ 选 **Word (.docx)**
2. 存到 `reports/submission/IDAT7215_Topic4_Report_Final.docx`
3. 按 [docs/SUBMISSION.md](../docs/SUBMISSION.md) 的 20 项清单逐条核对
