# 综述类型注册表（Type Registry）

以 Grant & Booth (2009) 14 类型谱系（Health Info Libr J 26:91-108, doi:10.1111/j.1471.1842.2009.00848.x）及后续发展为底。只对**有权威流程框架**的类型提供完整框架卡；无权威流程的类型提供轻量卡并明示局限。每类的报告规范条目库见 `checklist-*.json`。

## 注册表总表

| 类型 | 英文 | 执行框架 | 报告规范 | 审计工具 | 检索策略 | 推荐每库上限 | 框架卡 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 范围综述 | scoping review | JBI 六阶段 + PCC（Arksey & O'Malley 2005 → Levac 2010 → JBI） | PRISMA-ScR (22条) | PRISMA-ScR 审计 | 穷尽 | 不限（取全部） | scoping-jbi.md ✅完整 |
| 系统综述 | systematic review | Cochrane Handbook / JBI；问题用 PICO | PRISMA 2020 (27条) | PRISMA 2020 审计 | 穷尽 | 不限（取全部） | systematic-prisma2020.md ✅完整 |
| 伞状综述 | umbrella review | JBI Manual（对 SR/MA 的再综述） | PRISMA 2020 | PRISMA 审计 + AMSTAR-2/ROBIS 评纳入 SR | 穷尽（限定 SR/MA 类型） | 不限（取全部） | umbrella-jbi.md ✅完整 |
| 元分析(RCT类) | meta-analysis | Cochrane 定量综合 | PRISMA 2020 | PRISMA 审计 + 效应量一致性检查 | 穷尽 | 不限（取全部） | systematic-prisma2020.md（综合章扩展） |
| 元分析(观察性) | meta-analysis (observational) | — | MOOSE (35条) | MOOSE 审计 | 穷尽 | 不限（取全部） | other-types.md 轻量 |
| 元分析(心理学) | — | — | MARS (APA) | MARS 审计 | 穷尽 | 不限（取全部） | other-types.md 轻量 |
| 网络元分析 | NMA | Cochrane | PRISMA-NMA (Hutton 2015) | PRISMA-NMA 审计 | 穷尽 | 不限（取全部） | other-types.md 轻量 |
| 诊断试验综述 | DTA review | Cochrane DTA | PRISMA-DTA (McInnes 2018) | PRISMA-DTA 审计 | 穷尽 | 不限（取全部） | other-types.md 轻量 |
| 定性证据综合 | QES | JBI QES 章 / Thomas & Harden 主题综合 | ENTREQ (21条) | ENTREQ 审计 + GRADE-CERQual | 穷尽 | 不限（取全部） | qes-entreq.md ✅完整 |
| 元人志 | meta-ethnography | Noblit & Hare 七阶段 | eMERGe (2019) | eMERGe 审计 | 穷尽 | 不限（取全部） | other-types.md 轻量 |
| 现实主义综述 | realist review | Pawson 循环（理论→检索→CMO 配置→精炼） | RAMESES 出版标准 (2013) | RAMESES 质量标准 (2014) | 理论抽样（默认取全部，按 CMO 饱和截断） | 不限（可设上限提速） | realist-rameses.md ✅完整 |
| 元叙事综述 | meta-narrative review | Greenhalgh 多传统叙事 | RAMESES 元叙事标准 | RAMESES 质量标准 | 理论抽样（默认取全部，按传统饱和截断） | 不限（可设上限提速） | realist-rameses.md（附节） |
| 快速综述 | rapid review | Cochrane RRMG 建议 (Garritty 2020)：缩短但不省略透明度 | PRISMA 2020 适配 + 时间限制披露 | 适配版 PRISMA（标注 adapted） | 时间受限抽样（默认取全部，按时间窗截断） | 不限（可设上限提速） | other-types.md 轻量 |
| 混合方法综述 | mixed methods review | 定量+定性分别检索与评价 | PRISMA 适配（无专用规范） | PRISMA 审计 + MMAT (Hong 2018) 评纳入研究 | 穷尽 | 不限（取全部） | other-types.md 轻量 |
| 叙述性综述 | narrative / literature review | 无严格规定；结构化叙述 | — | SANRA (6条, 0-2分, 满分12; Baethge 2019) | 选择性抽样 | 推荐 80–150/库 | narrative-sanra.md ✅完整 |
| 整合性综述 | integrative review | Whittemore & Knafl (2005) 五阶段 | — | SANRA 适配版（标注 adapted） | 穷尽 | 不限（取全部） | narrative-sanra.md（附节） |
| SOTA 综述 | state-of-the-art review | 聚焦最新进展的全面检索 | — | SANRA 适配版（标注 adapted） | 穷尽（按时间截断） | 不限（取全部） | narrative-sanra.md（附节） |
| 批判性综述 | critical review | Grant & Booth：概念创新导向 | — | 无形式化工具→定性评价 | 理论抽样 | 不限（可设上限提速） | other-types.md 轻量 |
| 映射综述 | mapping review / systematic map | 时间/范围约束下成图 | — | 无形式化工具→PRISMA 流程图适配 | 穷尽 | 不限（取全部） | other-types.md 轻量 |
| 系统检索叙述综述 | systematic search and review | 穷尽检索 + 批判评价 + 最佳证据综合 | — | SANRA 适配 / PRISMA 部分适配 | 穷尽 | 不限（取全部） | other-types.md 轻量 |

## 检索数量策略（按综述类型）

**总原则**：方法学不规定具体数字，而是规定"穷尽 vs 抽样"这一性质。

- **穷尽型（绝大多数类型）**：systematic / meta-analysis(全) / NMA / DTA / scoping / umbrella / QES / meta-ethnography / mixed methods / integrative / SOTA / mapping / systematic search and review。**不设每库上限，取全部匹配记录** → 脚本传 `--limit 0`（默认值即 0）。PRISMA 第 6/7 条要求报告"各库识别到的真实总数"，脚本已打印 `total_available`（取自 API 返回的命中总量），须原样抄入 `文献检索报告.md`。
- **选择性抽样型（仅叙述性综述）**：narrative / literature review 允许多数抽样、按主题/影响力选取代表性文献，**推荐每库 80–150 条** → 脚本传 `--limit 120` 之类；必须在 `文献检索报告.md` 与正文 Methods 显式声明"选择性检索、非穷尽"（SANRA 不要求穷尽，但须透明）。
- **理论/时间抽样型（realist / meta-narrative / critical / rapid）**：默认也取全部（`--limit 0`），但按"CMO 理论饱和"或"时间窗"人为截断；rapid 须额外披露时间限制。若想提速，可主动设 `--limit`（如 150）并在报告中说明截断规则。

**跨库一致性要求**：同一项目的多库检索须使用**相同上限策略**（要么都穷尽、要么都设同一数值），否则合并去重后样本会偏向某库，违背公平抽样。穷尽型各库均用 `--limit 0`；叙述型各库统一用同一 `--limit` 值。

> 注：脚本硬上限 `MAX_SAFE=10000` 仅防粗放 query 失控；`--limit 0` 取全部时若真实命中超过 10000，脚本会停在该上限并 `[stats]` 中 `capped=true`，此时应拆分检索式（加年份/类型过滤）以覆盖全量。

## 类型路由决策树

按序回答，命中即推荐（用户始终可以覆盖）：

1. **目的 = 对现有 SR/MA 做再综述？** → umbrella
2. **目的 = 合并效应量，且纳入研究统计同质？**
   - 纳入 RCT/干预研究 → systematic + meta-analysis
   - 纳入观察性研究 → MOOSE 路线；心理学领域 → MARS 路线
   - 多干预比较网络 → NMA；诊断试验 → DTA
3. **目的 = 回答高度聚焦的问题、需要质量评价与偏倚控制？** → systematic（定量）/ QES（定性）/ mixed methods（两者兼有）
4. **目的 = 绘制新领域研究地图、识别概念与空白、文献杂且散？** → scoping（团队小/时间紧 → rapid 变体）
5. **目的 = 解释"什么机制在什么情境下对谁起作用"？** → realist；多个研究传统冲突 → meta-narrative
6. **目的 = 深度理论综合、翻译概念间关系？** → meta-ethnography；批判与理论建构 → critical
7. **目的 = 领域概览、梳理脉络、教学或学位论文背景？** → narrative / integrative / SOTA / mapping / systematic search and review（按检索穷尽度降序选）

补充约束：时间 ≤6 个月 → rapid；单人 → 叙述类；期刊要求注册方案 → systematic/scoping 优先。

## 多选产出模式

用户可多选类型（如 `scoping + descriptive map`、`systematic + meta-analysis`）。执行规则：

- 环节2 检索**只做一次**，全部类型共享 merged_dedup.csv
- 各类型独立的筛选标准与提取表（可能有重叠子集，分别落盘）
- 各类型独立产出 report + 对应清单审计
- 最终 HTML 报告多页签呈现 + 多清单合并审计表
- decision-log 中记录类型间共享与分叉点
