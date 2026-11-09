# submissions/ —— 6 位同学交作业的地方（就一个文件）

> **只有一个文件：[`report.md`](report.md)。** 里面已经按章节分好标题，找到你写的那一节，在它下面写。
> 仓库其它目录（代码 / 结果 / 图表 / 文档）**全部只读**，不要动。

---

## 1. 你能做什么

| 允许 | 不允许 |
|---|---|
| 在 `submissions/report.md` 你负责的那节下面写内容 | ❌ 改别人写的段落（会覆盖别人的工作） |
| 改 `submissions/README.md`（一般不需要） | ❌ 动 `src/`、`analysis/`、`tools/`、`tests/`、`results/`、`splits/`、`docs/` |
| 在 markdown 里引用图号和表格 | ❌ 往仓库里复制图片（用图号引用即可） |

> 写作分工不是死的，谁有空谁写多写少都行，**只要别互相覆盖**。

---

## 2. 绝对不能碰的地方

| 路径 | 为什么 |
|---|---|
| `src/`、`analysis/`、`tools/`、`tests/` | 代码，改了会破坏 66 个实验的可比性 |
| `results/`（`leaderboard.csv`、`runs/`、`figures/`） | 实验结果与图，**数字唯一来源**，手改即造假 |
| `splits/` | 数据划分已冻结，改了必须重跑全部 66 个 run |
| `docs/`、`README.md`、`AGENTS.md` | 项目文档，由维护者维护 |
| `reports/tables/`、`reports/WPS-REPORT-OUTLINE.md` | 脚本生成的结构文件，读可以，不要改 |

想改上面任何一项 → 群里说，由 Kenneth 改。

---

## 3. 怎么上传（3 条命令）

```bash
# 第一次
git clone https://github.com/Zheyi-D/am-defect-tl.git
cd am-defect-tl

# 以后每次：先拉最新，再改，再推
git pull
#   编辑 submissions/report.md 里你那一节
git add submissions/report.md
git commit -m "draft: 第 2 节 项目描述"
git push
```

> 如果 `git push` 提示冲突（说明别人刚改过）：先 `git pull`，解决冲突后再推。
> 解决不了就把你那段文字直接发群里 / 发给 Kenneth，由他合并 —— **不要为了推上去删别人的内容**。

---

## 4. 和在线文档的关系

| 在哪 | 用途 |
|---|---|
| **在线文档**（金山，链接见 `docs/START-HERE.md`） | 多人同时写**正式正文**，最终交付从这里导出 docx |
| **`submissions/report.md`（本文件）** | 每个人的**草稿备份**：写即时存档，方便回头查、方便 AI 复查 |

推荐：在在线文档里写正式稿；写的同时（或写完）把内容贴一份到 `report.md` 对应标题下。

---

## 5. 写作规范（3 条）

1. **数字不许自己算**：一律从 `results/leaderboard.csv` 或 `reports/tables/table*.md` 复制；查不到就写 "not available"
2. **图不复制**：正文里写 `Figure 7`（图号与英文 caption 在 `results/figures/CATALOG.md`），Word 里再插图
3. **表格从 `reports/tables/` 复制**，不要手打数字

---

## 6. 提交前 30 秒自检

- [ ] `git status` 里只有 `submissions/report.md`（或本 README）
- [ ] 没有动 `src/`、`analysis/`、`results/`、`splits/`、`docs/`
- [ ] 没有删掉或覆盖别人的段落
- [ ] 你写的每个数字都能在仓库里找到出处
