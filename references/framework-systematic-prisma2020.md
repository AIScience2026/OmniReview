# 系统综述框架卡：Cochrane/JBI + PRISMA 2020

依据：Cochrane Handbook v6+ / JBI Manual；报告规范 PRISMA 2020（Page et al., BMJ 2021, 27 条目，CC BY 4.0）。执行逻辑参考 keemanxp/slr-prisma 的六阶段结构（Interview → 分节起草 → 流程图 → 引用 → 成稿 → 清单审计），本工作流以 AI 辅助执行并保留用户为第二筛选人。

## Phase 1 — 问题与方案（Protocol）
- PICO 构题；建议注册 PROSPERO（注册号写入 PRISMA 第 27 条）
- 预设纳入/排除标准（PICOS 各维 + 时间 + 语种 + 设计类型）
- 产出：`protocol-systematic.md`

## Phase 2 — 穷尽检索
- ≥3 数据库（本工作流主干三库 + DeepXiv 补充 + 建议用户补充 WoS/Scopus/Embase 导出文件，脚本可解析 CSV）
- 完整检索式逐库留档；补充灰色文献 + 滚雪球

## Phase 3 — 双人筛选
- 标题/摘要级 → 全文级；AI 预筛 + 用户复核（C3）；分歧讨论/第三人裁决
- 全程计数，供 PRISMA 流程图（identification → screening → eligibility → included）

## Phase 4 — 质量评价（必须做）
- RCT → Cochrane RoB 2；观察性 → ROBINS-I / NOS；横断面 → JBI checklist
- 评价结果决定敏感性分析，不作单一纳入依据（除非预设）

## Phase 5 — 数据提取与综合
- 标准化提取表 + 预试验（C4 关卡）
- 定性综合：叙述 + 表格；定量综合（若做 meta-analysis）：效应量选取、异质性 I²、固定/随机效应模型、亚组与敏感性分析、发表偏倚（漏斗图 + Egger）
- 混合效应量或数据不足时，如实降级为叙述综合并在审计中对应条目如实标注

## Phase 6 — 成稿与审计
- 结构：Title → Abstract → Introduction → Methods → Results → Discussion → Conclusions → Declarations → References → 图表
- PRISMA 2020 流程图必须包含；27 条目清单审计（checklist-prisma-2020.json）
- Methods 必须如实披露 AI 参与；报告注册与方案偏差

## 关键纪律
- AI 编码/提取的数据必须抽查核实（数字字段抽查率 ≥10% 或全部关键效应量）
- 检索、筛选、提取的每个计数都要能与 CSV 对账
