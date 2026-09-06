# 其他类型轻量卡（无 ✅ 完整卡的类型）

这些类型权威框架存在但流程可由通用管线覆盖，或缺少形式化执行框架。执行时以 PRISMA 管线为底，叠加下列差异点；审计用对应规范（见 checklist-stub-registry.json）。**本卡条目数与执行要点为摘要，正式投稿前必须对照官方文件逐条核对。**

## 元分析（观察性研究）— MOOSE
- 检索/筛选/提取同 systematic-prisma2020.md；差异：偏倚评价用 NOS（Newcastle-Ottawa Scale）；报告按 MOOSE 35 条目（Stroup et al., JAMA 2000；2024 有更新版，投稿前核对）
- 数据来源清单必须区分：发表/未发表、注册库

## 元分析（心理学）— MARS
- APA 元分析报告标准（Appelbaum et al., 2018）；强调效应量与异质性、检索全面性声明、方差估计模型选择

## 网络元分析（NMA）— PRISMA-NMA
- 在 SR 管线上叠加：干预网络图（geometry 描述必须）、一致性/不一致性检验（node-splitting 等）、传递性假设讨论
- Hutton et al., Ann Intern Med 2015

## 诊断试验综述（DTA）— PRISMA-DTA
- 2×2 表提取（TP/FP/FN/TN）；QUADAS-2 偏倚评价；灵敏度/特异度森林图与 SROC
- McInnes et al., PLoS Med 2018

## 元人志（meta-ethnography）— eMERGe
- 见 qes-entreq.md 附节；七阶段 + 三种综合方式（类比/回驳/包摄）；Noblit & Hare (1988)
- eMERGe (2019) 19 条报告规范（France et al., BMC Med Res Methodol）

## 快速综述（rapid review）— Cochrane RRMG
- 原则：**缩短步骤但不牺牲透明**——省什么（如单一筛选人、缩减数据库、不做灰色文献）必须在 Methods 显式披露
- 依据 Garritty et al., J Clin Epidemiol 2020（Cochrane 快速综述方法组建议）
- 审计：适配版 PRISMA + "省略项披露表"（每省略一项，说明理由与风险）

## 混合方法综述（mixed methods review）
- 定量与定性**分别**检索、评价（Cochrane RoB 2 / CASP）、提取，再整合（汇合式 convergent / 序贯式）
- 纳入研究评价用 MMAT（Hong et al., 2018）
- 报告 PRISMA 适配；整合策略（joint display 等）必须描述

## 批判性综述（critical review）
- Grant & Booth：无形式化流程；核心是概念创新——通过新视角对文献做概念分析，产出假说或理论模型
- 执行：检索照做留档；分析框架自建并明示；无形式化审计 → 定性评价表（论点原创性/证据支撑/概念贡献三维，AI 给评语不给分数）

## 映射综述（mapping review / systematic map）
- 目的：为后续 SR/primary research 立项画地图。时间/范围约束可放宽检索，但**约束本身要写明**
- 产出：研究数量与质量特征图（按设计/主题/年份/地域）；可与 scoping-jbi 卡的 Step 5 证据地图方法复用

## 系统检索与叙述综述（systematic search and review）
- 穷尽检索 + 批判评价 + 最佳证据综合；多种研究设计混合
- 执行 = systematic 检索管线 + narrative 综合结构；审计 SANRA 适配 + PRISMA 检索条目部分适配
