# S2 的提交区

| 项 | 内容 |
|---|---|
| 负责 | 现场 demo 操作 + 90 秒录屏 + 断网预案 + Q&A 卡片 |
| 目标字数 | —（以文件为准） |
| 参考素材 | `docs/DEMO.md`（§2 准备、§3 启动、§4 演示脚本、§5 断网预案、§6 八个必答题、§9 录屏步骤）、`docs/index.html`（可交互结果看板）、`analysis/demo_app.py`（Gradio 推理界面） |
| 完成标准 | demo 脚本 + 录屏完成（demo_fallback.mp4）+ 断网预案演练 + Q&A 卡片 |

## 只允许在这个目录里建这些文件

- `S2_demo_plan.md`
- `S2_recording_notes.md`
- `S2_qa_cards.md`
- `status.md`（必填：状态 / 字数 / 最后更新）

**不要改这个目录以外的任何东西。** 全局规则见 [`../README.md`](../README.md)。

## 提交方式

```bash
git add submissions/S2
git commit -m "S2: draft"
git push origin HEAD:submissions/S2
```

## 注意事项

视频文件**不要放进仓库**（太大），只在本目录写：文件名、时长、存放位置、录制日期。断网预案必须排练过一次。
