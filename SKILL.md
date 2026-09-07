---
name: omnireview
display_name: OmniReview 全能综述工作台
display_name_en: OmniReview All-Type Literature Review Workbench
description: 全类型学术综述工作流技能。当用户要做文献综述（literature review）、系统综述（systematic review）、范围综述（scoping review）、伞状综述（umbrella review）、元分析框架、定性证据综合（QES）、现实主义综述（realist review）、叙述性综述（narrative review）等任意类型综述，或要求打磨研究问题、多源检索文献、批量下载论文、按 PRISMA/JBI/PRISMA-ScR/ENTREQ/SANRA 等权威规范产出并审计评分时使用。覆盖问题打磨→多源检索（OpenAlex/Semantic Scholar/Crossref/DeepXiv）→分层阅读与下载→类型路由→报告规范审计评分全流程，支持逐关确认与全自动托管两种模式。
description_zh: 把你的 AI 变成一支综述团队：将粗略研究想法打磨成可证伪的问题，自动检索 OpenAlex、Semantic Scholar、Crossref、DeepXiv 四大学术库，逐篇筛选去重，覆盖系统综述、范围综述、元分析等 16 种综述类型，成稿后按 PRISMA/JBI/ENTREQ/SANRA 权威清单逐条审计评分。每个决策留档可溯，经得起审稿人追问。重要综述逐关确认，日常调研全自动托管。
description_en: All-type literature review workbench with question refinement, multi-source search (OpenAlex/Semantic Scholar/Crossref/DeepXiv), tiered reading and download, review-type routing (16 types), and checklist-based auditing, in assisted or autonomous mode.
category: research
version: 1.2.1
author: boss
agent_created: true
---

# OmniReview · 全能综述工作台

以权威方法论（Cochrane、JBI、PRISMA 家族、SANRA、RAMESES、ENTREQ 等）为骨架，端到端完成从粗略研究想法到可投稿综述初稿的全流程。核心理念：**类型先行、分层阅读、全程可溯、双模式可控**。

## 0. 执行总览

收到综述类或文献调研类请求后，**先判车道**：

- **L0 快速脉络扫描（轻量车道）**：请求形如"帮我检索 X 主题的论文 / 看看脉络和最新进展 / 做个快速调研"——用户要的是**研究地图，不是综述成稿**。走 §0.1 的 L0 流程，不进入类型路由与审计。
- **增量更新车道**：已有综述项目存在（目录内有 review-state.md / included.csv），用户要求"补跑某数据源 / 更新检索 / 纳入新文献"——走 §0.2 的增量流程，不重跑全流程。
- **全流程（完整综述车道）**：请求要产出 protocol/成稿/审计级综述，或 L0 / 增量结束后用户表示要继续深化。走完整流程：

```
C0 模式选择 → 环节0 问题打磨 → 环节1 类型路由 → 环节2 检索与存储
→ 环节3 筛选（Tier 1 摘要级） → 环节4 框架化综合（Tier 2 精读）
→ 环节5 清单审计评分 → 交付（Markdown + HTML + 全套追溯文件）
```

所有环节的输出落在项目目录（见 §7 存储规范），任何一步都可回溯。

### 0.1 L0 快速脉络扫描规则（禁止自由发挥）

L0 仍是本技能的正式流程，同样禁止跳过以下步骤（简但不可省）：

1. **问题澄清（压缩版问题打磨）**：把用户的粗问题复述为 1 个明确检索问题（主题概念 + 边界条件 + 时间范围），加载 `references/question-refinement.md` 选取其中"概念澄清 + 可证伪边界"两步即可；有歧义（同义词、近义概念如 agency/autonomy）时列出并说明取舍。
2. **检索方案预告**：开始检索前，用 2-3 句话告知用户将用的检索式、数据源、时间窗——这是 L0 唯一的"预告关卡"（信息性，不强制等待确认，用户可随时打断纠正）。
3. **脚本检索 + 落盘**：与全流程共用环节2 的脚本与 §7 存储规范（逐库 CSV + merged_dedup.csv + 检索式留档进根目录 `文献检索报告.md`），保证可回溯。
4. **结构化输出**：脉络扫描报告必须包含：检索概况表（来源/数量/去重/噪音说明）、时间分布、按主题聚类的文献地图（每主题列代表文献+年份+被引）、与用户研究定位相关的发现（若用户背景已知）。**必须注明这是标题/摘要级扫描，不构成综述结论。**
5. **升级出口**：报告结尾提示——若需产出正式综述（protocol + 系统筛选 + 审计），可从本扫描结果升级进入全流程（检索结果直接复用）。

**为什么需要这条车道**：轻量请求若不走 L0，就会退化为不落盘、不留检索式、不做问题澄清的"自由发挥"，违背本技能"全程可溯"的核心理念（2026-09-06 端到端试跑中暴露此漏洞，已修复）。

### 0.2 增量更新车道规则（已有项目的数据源/检索补充）

触发：项目目录已有 review-state.md，用户要求补跑数据源、追加检索式或纳入新文献。流程（简但不可省）：

1. **读状态**：加载 review-state.md 与 decision-log.md，确认已有检索式、筛选裁决与成稿版本，**旧裁决一律保留、只裁决新增记录**（按 doi+title 键对齐）
2. **预告增量**：告知新增检索式/数据源与预期影响，用户可打断
3. **脚本检索 + 落盘**：新增 CSV 遵循 §7 命名；合并去重后**只对新增记录**做筛选（分桶→逐条人工复核→裁决索引必须与打印清单同一基准，推荐把裁决写成显式 JSON 文件再应用）
4. **跨源重复清理**：DOI 去重识别不了"预印本×正式版"配对（arXiv DOI ≠ 期刊 DOI）——合并后必须追加**标题规范化去重**（去标点小写取前 90 字符），重复时保留正式版/有摘要版
5. **成稿同步**：更新报告的 Abstract / §2.3 / §2.4 / §3.1 流程图 / §3.2 特征表 / 受影响的主题叙述 / §4.2 局限，重跑审计并把偏离记入 protocol 偏离记录与 decision-log
6. **结论回归检查**：新数据可能推翻旧结论（实例：RAPS 2024 入池推翻"PA 无专用量表"）——逐条核对核心结论是否仍成立，不成立必须改写而非保留

**为什么需要这条车道**：增量更新若不走固定流程，最容易出现"新数据进了池子但报告数字/结论没同步"的半更新状态（2026-09-06 DeepXiv 增量实操中暴露，已修复）。

## 1. C0 关卡：确认模式（必须首先询问）

用户提出综述需求后、开始任何工作前，先向用户确认工作模式（这是唯一不可跳过的询问）：

- **模式1 逐关确认**：在 C1-C6 每个关卡暂停，提交"待确认简报"（含 AI 建议与理由），用户确认后推进。适合方法学重要、准备投稿的综述。
- **模式2 全自动托管**：跳过所有确认，AI 在每个关卡自行决策。所有决策（选项、理由、时间戳）实时追加到 `{project}/_working/decision-log.md`，成稿时随审计报告一并完整呈现，供事后追溯与修改。

模式确定后写入 `_working/review-state.md`。模式2 下筛选采用**保守策略**：标注"不确定"的文献一律纳入并在 decision-log 中说明。低风险可逆操作（检索、去重、CSV 落盘、格式化）在两种模式下均自动执行，不询问。

## 2. 关卡机制（模式1 生效）

| 关卡 | 时机 | 确认内容 |
| --- | --- | --- |
| C1 | 问题打磨后 | 研究问题定稿 + 综述类型（单选或多选） |
| C2 | 检索前 | 检索式、数据源、时间范围、纳入/排除标准、**每库数量上限（`--limit`：穷尽型=0、叙述型=80~150）** |
| C3 | AI 预筛后 | 复核"不确定"类 + 抽查高/低置信样本 |
| C4 | 数据提取前 | 提取字段定义 + 预试验（前 5-10 篇）校准结果 |
| C5 | 综合成稿前 | 主题聚类 / 证据地图 / 核心发现 |
| C6 | 审计后 | 评分表与修改优先级（可选确认） |

阶段机记录于 `_working/review-state.md`（当前环节、已完成关卡、待办）。每次关卡暂停时输出简报并明确等待用户回复"确认 / 修改意见"。

## 3. 环节0：问题打磨

加载 `references/question-refinement.md`（源自 good-question 方法：竞争性假设、假设挑战、Heilmeier Catechism、可证伪性）。产出 1-3 个候选研究问题，各附：为什么重要、什么证据能检验、什么结果会推翻它。最后通过三项 litmus test：Advisor Test（2 分钟能说服导师）、Paper Test（能预想论文标题+图1）、Null Result Test（假设错了是否仍值得报告）。粗方向的检索随打磨同步进行（用环节2脚本小规模试搜），以便用文献实况校准问题。

## 4. 环节1：类型路由

加载 `references/type-registry.md`，按决策树推荐类型：研究目的（画地图/答问题/合并效应量/解释机制）→ 证据形态（定量/定性/混合）→ 时间与团队约束 → 推荐。用户可单选指定，也可**多选**（如 scoping + 描述性统计地图，或 systematic + meta-analysis）；多选时共享环节2 的检索结果，各类型分别综合，最终输出多报告页签的单一 HTML + 多清单合并审计。类型对应的框架卡在 `references/framework/`，报告规范在 `references/checklists/`。

## 5. 环节2：多源检索与存储

依次运行（脚本均零第三方依赖，用系统 Python 直接执行）：

```bash
# 穷尽型综述（systematic/scoping/umbrella/QES/meta 等绝大多数类型）：--limit 0 = 取全部匹配
python scripts/search_openalex.py --query "..." --since 2015 --limit 0 --out _working/search/openalex_q1.csv
python scripts/search_semanticscholar.py --query "..." --limit 0 --out _working/search/s2_q1.csv
python scripts/search_crossref.py --query "..." --limit 0 --out _working/search/crossref_q1.csv
python scripts/search_deepxiv.py --query "..." --since 2023 --limit 0 --out _working/search/deepxiv_q1.csv

# 选择性抽样型（仅叙述性综述 narrative）：推荐每库 80-150，例如 --limit 120
python scripts/search_openalex.py --query "..." --since 2015 --limit 120 --out _working/search/openalex_q1.csv
python scripts/search_semanticscholar.py --query "..." --limit 120 --out _working/search/s2_q1.csv
python scripts/search_crossref.py --query "..." --limit 120 --out _working/search/crossref_q1.csv
python scripts/search_deepxiv.py --query "..." --since 2023 --limit 120 --out _working/search/deepxiv_q1.csv

python scripts/dedup_merge.py --inputs _working/search/*.csv --out _working/merged/merged_dedup.csv
```

**每库上限 `--limit` 的取值规则（关键）**：
- 四个脚本参数名现已统一为 `--limit`；`--limit 0`（默认值）表示取全部匹配记录，硬上限 `MAX_SAFE=10000` 仅防失控。
- **穷尽型（绝大多数类型）用 `--limit 0`**：systematic / meta-analysis(全) / NMA / DTA / scoping / umbrella / QES / meta-ethnography / mixed methods / integrative / SOTA / mapping / systematic search and review。不设上限，取全部。
- **选择性抽样型（仅叙述性综述）用具体值**：推荐每库 `--limit 80~150`，并在 `文献检索报告.md` 与 Methods 声明"选择性检索、非穷尽"。
- **理论/时间抽样型**（realist / meta-narrative / critical / rapid）：默认 `--limit 0`，按 CMO 理论饱和或时间窗截断；rapid 须披露时间限制。
- **跨库一致性**：同一项目多库须用相同上限策略（都 0 或都同一数值），否则合并去重后样本偏库。
- 各脚本运行后打印 `[stats] source=... retrieved=N total_available=M capped=...`：**`total_available` 是数据库真实命中总数（取自 API 返回总量），须原样抄入 `文献检索报告.md`**（PRISMA 第 6/7 条证据）。若 `capped=true` 说明真实命中超 10000，需拆分检索式覆盖全量。
- 详细类型→上限映射见 `references/type-registry.md` 的「检索数量策略」专节。

统一 schema：`doi,title,authors,year,venue,type,cited_by,abstract,oa_url,source,query,retrieved_at`。要点：

- 每次检索的原始结果**逐次落盘 CSV**，永不覆盖；`query` 与 `retrieved_at` 列保证可复现
- 同时把检索式（各库的完整 query 串 + 过滤条件 + 命中数）写入项目根目录 `文献检索报告.md` —— 这是 PRISMA 第 7 条的核心证据
- 多组检索词时逐一执行并合并；DeepXiv 补充检索（脚本 `search_deepxiv.py`）用于 arXiv/预印本覆盖；无令牌或失败时记录并跳过，不阻塞三库
- **DeepXiv 令牌未配置时**：向用户展示一句话指引（注册 https://data.rag.ac.cn/register → 令牌写入 `~/.env` 一行 `DEEPXIV_TOKEN=xxx`），完整步骤见 `references/deepxiv-setup.md`；用户拿到令牌后可直接发给 AI 代写入 `~/.env`。**写入必须用 bash `printf`，禁用 PS5.1 `Add-Content -Encoding UTF8`（会加 BOM 使键名失配）；用户声称已有令牌时优先排查编码/键名问题而非怀疑用户**。脚本已内置 BOM 容错与注册表兜底（2026-09-06 修复）
- **合并去重后追加标题规范化跨源去重**（去标点小写取前 90 字符）：DOI 键识别不了"预印本×正式版"配对（arXiv DOI ≠ 期刊 DOI）；重复时保留正式版/有摘要版，剔除数记入流程图
- API 失败或限流时重试并降级（详见 `references/data-sources.md`；S2 的 429=限流可重试，403=key 被全局拒绝应跳过并提示核对），任何单库失败不阻塞流程，但须记录到 `文献检索报告.md`
- **集成新 SDK 前先用 `inspect.signature()` 核实方法签名与响应字段名，再写解析代码**——凭文档/猜测写的解析是实测中最常见故障源（2026-09-06 DeepXiv 教训：search_mode 参数、result 键名、date/citation_count 字段均与猜测不符）

## 6. 环节3：筛选与分层阅读

**Tier 1（默认，任何情况下可完成）**：基于标题+摘要+元数据筛选。AI 按纳入/排除标准逐篇判定，输出 `_working/screening/included.csv` / `excluded.csv`（含排除原因与置信度 高/中/低）。摘要缺失时以 venue/year/type 等元数据补足判断依据。模式1 下 C3 关卡交用户复核"不确定"类；模式2 下存疑一律纳入并记录。

**Tier 2（仅对纳入子集，可选精读）**：优先用 DeepXiv 渐进式阅读（brief→head→section，无需 PDF）；arXiv/PMC 未覆盖的论文再走 PDF 下载：

```bash
python scripts/download.py --included _working/screening/included.csv --merged _working/merged/merged_dedup.csv --out _working/pdfs/
```

下载调度链：scansci-pdf（若已安装）→ auto-paper-harvester（若已安装）→ 脚本内置 OpenAlex oa_url + Unpaywall 直链。**下载失败不是阻塞条件**：Tier 1 已能完成综述，未获取全文的论文单独列清单报告。

## 7. 存储规范（交付物上浮，过程数据下沉）

**原则：根目录只放给人看的最终交付物（≤4 个），一切过程痕迹进 `_working/`。**

```
{project}/
├── 综述报告.html               # 最终交付：证据地图+统计图+全文（多类型多页签），打开即看
├── 综述报告.md                 # 综述全文 Markdown（与 HTML 同源）
├── 文献汇总表.csv               # 数据提取/汇总总表（即 JBI charting 产出的落地文件）
├── 文献检索报告.md              # 检索式留档：各库完整 query+过滤条件+命中数+去重统计（PRISMA 第7条证据，原 search-strategy.md）
└── _working/                   # 过程数据，供复盘与追溯，不作为交付物
    ├── search/{source}_{queryslug}_{YYYYMMDD}.csv   # 原始检索，逐次落盘永不覆盖
    ├── merged/merged_dedup.csv                       # 归并去重
    ├── screening/{included,excluded}.csv             # 筛选结果+排除原因（included.csv 是最终文献集）
    ├── pdfs/{FirstAuthor}_{Year}_{TitleShort}_{DOItail}.pdf
    ├── protocol-{type}.md                            # 综述方案（投稿/注册用）
    ├── audit.md + audit_judgments.json               # 清单审计
    ├── review-state.md                               # 阶段机 + 关卡记录
    └── decision-log.md                               # 模式2 决策日志（模式1 也记录重大判断）
```

- L0 车道的脉络扫描报告同样落根目录，命名 `{主题}脉络扫描报告.md`，与全流程的 `文献检索报告.md` 角色不同、不混用
- 禁止再把交付物放进 `reports/{type}/` 之类的深层目录（历史教训：最重要的东西埋得最深，主次不分）
- "charting" 只是 JBI 对数据提取阶段的行话，**落盘文件名一律用 `文献汇总表.csv`**，不再用 charting.csv

## 8. 环节4：框架化综合

按所选类型加载对应框架卡执行（如 scoping：JBI 六阶段 PCC→三步检索→双人筛选→结构化提取→证据地图；systematic：PICO→PRISMA 流程→质量评价→综合）。数据提取表经预试验校准（C4 关卡），**最终落盘为项目根目录 `文献汇总表.csv`**（这是给用户看的主数据表，字段命名须可读，不得用 charting 等术语黑话命名）。成稿用 `templates/report/{type}.md` 骨架，方案用 `templates/protocol/{type}.md`，方案落 `_working/protocol-{type}.md`。Methods 部分必须包含 AI 参与披露段落（模板已内置占位）。

## 9. 环节5：清单审计评分

```bash
python scripts/audit_checklist.py --list
python scripts/audit_checklist.py --checklist prisma-scr --scaffold --out _working/audit.md
```

审计引擎按 `references/checklist-*.json` 注册表驱动：逐条目在稿文中定位证据（引用原文句）→ 判定 Reported / Partial / Missing → 给出优先级修复建议 → 汇总评分表。判定由 AI 依据稿文做出，脚本负责登记表与一致性检查。特殊处理：umbrella 追加 AMSTAR-2 评纳入的系统性综述；mixed methods 追加 MMAT；无形式化清单的类型用 SANRA 适配版并显式标注 "adapted"。多类型产出时输出合并审计报告。

## 10. 交付物（全部在项目根目录）

- `综述报告.html`：单文件 HTML（证据地图 + 描述性统计图 + 全文，多类型多页签）——**首要交付物**
- `综述报告.md`：综述全文 Markdown（与 HTML 同源）
- `文献汇总表.csv`：数据提取/汇总总表（最终文献集的逐篇特征，源自 `_working/screening/included.csv` + 提取字段）
- `文献检索报告.md`：检索式、数据源、命中数与去重统计（PRISMA 第 7 条证据）
- 追溯材料在 `_working/`：protocol、audit、原始 CSV 系列、review-state、decision-log——交付时向用户说明位置，不混入根目录

## 11. 边界与披露

- AI 是第一筛选人与写作助手，**用户是第二筛选人**；模式2 下必须在报告中显著披露 AI 全程托管及决策日志位置
- 审计只依据稿文文本证据判定，不臆断；adapted 清单必须显式标注
- PRISMA 系清单遵循 CC BY 4.0；引用规范原文出处见 checklist JSON 内 source 字段
- 数据源以 OpenAlex + Semantic Scholar + Crossref 为主干（免费无 key），DeepXiv 补充（日配额约 500 次，需容错）；外部下载工具全部可选
