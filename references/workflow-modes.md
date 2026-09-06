# 双模式流程机与决策记录规范

## review-state.md（阶段机）

每次运行更新。格式：

```markdown
# Review State
- mode: assisted | autonomous
- created: {date}
- topic: {主题}
- types: {类型列表}
- stage: C0 | R0-question | R1-routing | R2-search | R3-screening | R4-synthesis | R5-audit | DONE
- checkpoints:
  - [x] C0 模式=assisted (2026-09-06)
  - [ ] C1 ...
```

规则：每个关卡完成后立即更新；中断恢复时先读本文件续跑；`stage` 永远反映唯一当前阶段。

## decision-log.md（决策日志，位于 _working/）

两种模式都写；模式2 是唯一的事后追溯依据。每条决策追加：

```markdown
## {YYYY-MM-DD HH:MM} C{N} {环节名}
- 决策：{选了什么}
- 备选：{还有哪些选项}
- 理由：{为什么选它（引用数据/方法学依据）}
- 影响：{该决策影响哪些后续环节}
```

模式2 特殊规则：
- C3 筛选采用保守策略——"不确定"一律纳入并注明
- 决策粒度到"每个可分支的选择点"，而非只记结果
- 成稿时 decision-log 完整附录于审计报告之后，并在报告 Methods 披露段中给出其路径

## 待确认简报（模式1）

每个关卡输出固定结构：**当前状态 → 本次决策点与选项（含 AI 推荐+理由）→ 需要用户回复什么**。用户回复"确认"或给出修改意见后推进；修改意见回写到 review-state 并触发受影响环节重跑。
