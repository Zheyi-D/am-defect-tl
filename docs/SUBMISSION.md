# 提交清单（SUBMISSION）

> 截止：**2026-11-30（周一）17:00 前**，Moodle + Turnitin，仅组长上传。
> 口头报告：**11/19 或 11/26（周四）**，20 分钟（15 讲 + 5 问答），全员到场。
> 本文件是定稿周的检查表，逐项打勾后再提交。

---

## 一、提交三件套

| # | 交付物 | 从哪来 | 谁负责 |
|---|---|---|---|
| 1 | 报告 `.docx` | Word Online 导出 → 存 `reports/submission/` | 统稿人 |
| 2 | 口头报告 `.pptx` | PowerPoint 导出 → 存 `reports/submission/` | PPT 负责人 |
| 3 | 源码 `.zip` + README | 本仓库 `git archive` 生成（见 §四） | 组长 |

---

## 二、数字唯一来源（防止抄错）

| 内容 | 唯一来源 |
|---|---|
| 66 个 run 的 10 个指标 | `results/leaderboard.csv` |
| 作者报告值（99 格） | `docs/paper_results.csv` |
| 效率（CPU/GPU/参数量/FLOPs） | `results/efficiency.csv` |
| 泄漏对照实验 | `results/leakage.csv` |
| 报告里的表格 | `reports/tables/table*.md`（脚本生成，禁止手改） |

> 定稿前跑一次 `python -m src.aggregate --check`，必须输出 **66/66 完整**。
> 报告里出现的每个数字都应能在上述文件中找到；对不上就是抄错了。

---

## 三、图表清单（报告引用用）

- 图：`results/figures/fig_*.png` —— 图号与英文 caption 见 `results/figures/INDEX.md`
- 表：`reports/tables/table{1..5}_*.md` —— 表号固定为 Table 1–5
- 正文交叉引用格式：`Figure 3` / `Table 2`（不要写"下图""上表"）

---

## 四、源码打包命令（组长执行）

```bash
# 只打包 Git 跟踪的文件：自动排除 data/、缓存、权重（.gitignore 已处理）
git archive --format=zip --prefix=am-defect-tl/ -o reports/submission/am-defect-tl-src.zip HEAD
```

打包后自检：
- 解压后应含 `README.md`、`AGENTS.md`、`src/`、`analysis/`、`results/`、`reports/tables/`
- **不应**含 `data/`、`*.pt`（除 `results/runs/*/model.pt`）、`__pycache__`
- 体积应在 30 MB 量级

---

## 五、提交前 20 项检查

### 报告内容

- [ ] 1. 正文词数 2,000–4,000（**上限 4,400**，超了扣 10%）
- [ ] 2. 结构齐全：封面 / 目录 / Abstract / List of Figures / List of Tables / 正文四节 / 个人贡献 / References / Appendices
- [ ] 3. 封面含：科目代码与名称、班级、组号、8 人姓名学号、**字数**
- [ ] 4. 所有图表在正文被引用且编号连续
- [ ] 5. 每个数字可追溯到 §二 的文件（抽查 10 个）
- [ ] 6. 参考文献 IEEE 格式、数量 ≥15、正文有引用标记
- [ ] 7. 8 份个人贡献报告（各 300–600 词）齐全
- [ ] 8. 明确写出"第三个数据集未公开 → 覆盖 66/99"这一限制
- [ ] 9. 明确写出"D2 是 D1 的增强版"与"我们未观察到泄漏效应"
- [ ] 10. 明确写出"代码为自己实现 + 开源组件已在 NOTICE.md 登记"

### 格式

- [ ] 11. A4 / 单倍行距 / Times New Roman 12
- [ ] 12. 页边距正常、页码存在、图表不跨页断裂
- [ ] 13. 导出的 docx 用 Word 打开一次，确认没有排版错乱

### 口头报告

- [ ] 14. PPT ≤15 页；8 人各 60–90 秒，分段写清
- [ ] 15. 完整彩排 ≥2 次，掐表 **≤15:00**
- [ ] 16. 演示录屏（90 秒）已备份，现场断网也能放
- [ ] 17. Q&A 卡片：预判 10 个问题（含"为什么只有两个数据集""为什么数字和论文不同"）

### 提交与合规

- [ ] 18. `python -m src.aggregate --check` → **66/66 完整**；`python -m unittest discover -s tests` → 全绿
- [ ] 19. 源码 zip 已解压验证一次（确认能按 README 复现到第 3 步）
- [ ] 20. Moodle + Turnitin 均上传成功（截图留档），**时间留 2 小时缓冲**

---

## 六、常见踩坑

| 现象 | 原因 | 对策 |
|---|---|---|
| 字数超限 | 正文 + 附录混算 | 附录/个人贡献/参考文献不计入，导出前用 Word 统计"正文部分" |
| 图表编号错乱 | 中途插图 | 最后统一用 Word 的"插入题注"重排一次 |
| Turnitin 相似度高 | 模板句/方法描述抄原文 | 方法与数据描述用自己话重写，引用标清楚 |
| 上传失败 | 文件过大 / 网络 | 报告转 PDF 备份；源码 zip 确认 <30 MB |
| 报告数字与仓库不一致 | 手抄旧值 | 一律从 `reports/tables/` 复制，不手打 |
