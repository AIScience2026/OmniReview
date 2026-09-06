# 报告规范条目库（Checklists）

供 `scripts/audit_checklist.py` 消费的注册表。每个规范一个 JSON 文件，结构：

```json
{
  "guideline": "<id>",
  "name": "<全称>",
  "applies_to": ["<适用综述类型>"],
  "source": "<官方来源 URL>",
  "citation": "<引用格式>",
  "license": "<许可>",
  "condensed": false,            // true = 摘要版，投稿前必须对照官方文件逐条核对
  "items": [{"id": "1", "label": "...", "requirement": "...", "optional": false}]
}
```

## 当前注册状态

| 文件 | 规范 | 条目数 | 状态 |
| --- | --- | --- | --- |
| checklist-prisma-2020.json | PRISMA 2020（系统综述/元分析/伞状） | 27 | ✅ 完整（顶层条目，子项见 requirement 注记） |
| checklist-prisma-scr.json | PRISMA-ScR（范围综述） | 22（2 条可选） | ✅ 完整 |
| checklist-sanra.json | SANRA（叙述性综述） | 6（0-2 分） | ✅ 完整 |
| checklist-entreq.json | ENTREQ（定性证据综合） | 21 | ⚠️ 主体完整（条目 15-21 为摘要措辞，condensed 注记） |
| checklist-stub-registry.json | MOOSE / MARS / PRISMA-NMA / PRISMA-DTA / AMSTAR-2 / RAMESES / eMERGe / MMAT / ROBIS / GRADE-CERQual | — | 📌 桩：含条目总数与官方链接，使用前须补全条目 |

## 审计评分规则

- 每条目判定三级：`Reported`（有原文证据引用）/ `Partial`（部分满足或不明确）/ `Missing`（稿文找不到）
- 判定必须引用稿文原句作为证据；找不到证据 = Missing，不得臆断
- 可选条目（optional=true）未执行时判 `N/A` 并要求说明原因
- adapted 清单（rapid/叙述类适配版）输出时必须带 "adapted" 标记
- 评分表按 `Reported/Total` 汇总并列出修复优先级（Missing 的高影响条目优先）
