# 在线共享文档（WPS 金山文档）

| 项 | 值 |
|---|---|
| **文档链接** | **https://www.kdocs.cn/l/cokbmUbGMYkE** |
| 文档名 | `IDAT7215 Topic4 Report (Draft).docx` |
| 类型 | WPS 文字（`.docx`） |
| 文件 ID | `aDNJSYqGRxM9ZTacoAue1xvT1kZqTrVFr` |
| 云盘 ID | `66138690` |
| 分享链接 ID | `cokbmUbGMYkE` |
| 分享范围 | `anyone`（持有链接即可访问），状态 `open` |
| 创建日期 | 2026-11-09 |

> 这是**报告正文唯一的协同编辑入口**。仓库里不放 docx，只放链接与结构源
> （[WPS-REPORT-OUTLINE.md](WPS-REPORT-OUTLINE.md)）。

---

## 谁做什么

| 角色 | 操作 |
|---|---|
| **8 位成员** | 打开链接 → 在线编辑自己负责的章节（见文档里的 Table of Contents） |
| **组长** | 维护分享权限；定稿时导出 docx → 存 `reports/submission/` |
| **AI agent** | 只改仓库文件（结构、图表、数字），不直接改正文文字 |

> ⚠️ 如果打开后是**只读**：请组长在金山文档右上角「分享」里把权限改为**可编辑**，
> 或把成员加为协作者。链接分享的默认权限取决于账号设置，API 无法设置"编辑/只读"。

---

## 文档里已经写好的内容

1. **封面**：课程名、题目、副标题、组号/班级/组长/8 人姓名 UID（占位）、字数、仓库链接、提交日期
2. **Table of Contents**：4 大节 + 3.1–3.6 小节，每节标注**目标字数 / 负责人 / 状态**
3. **List of Figures**：Fig. 1–10，含仓库文件名与英文 caption
4. **List of Tables**：Table 1–6，含仓库文件名与英文 caption
5. **三条必须写进去的结论**（数字固定，不许改）
6. **写作规则**（数字唯一来源、图的取法、格式要求；**定稿前删除该节**）

---

## 更新方式

| 改什么 | 怎么做 |
|---|---|
| 只改文字 | 直接在金山文档改（不需要动仓库） |
| 改章节结构 / 字数预算 / 图表编号 | **先改 [WPS-REPORT-OUTLINE.md](WPS-REPORT-OUTLINE.md)** 并提 PR，再同步到金山文档 |
| 图/表内容 | 图由 `results/figures/` 生成，表由 `analysis/export_tables.py` 生成；**不要手改文档里的数字** |

---

## 定稿与备份

1. 金山文档 → 「文件」→「下载」→ 选 **Word (.docx)**
2. 存到 `reports/submission/IDAT7215_Topic4_Report_Final.docx`
3. 按 [docs/SUBMISSION.md](../docs/SUBMISSION.md) 的 20 项清单逐条核对
