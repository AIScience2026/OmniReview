<div align="center">

# OmniReview · All-Type Literature Review Workbench / 全能综述工作台

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Format](https://img.shields.io/badge/format-agent--skills-purple)](https://agentskills.io)
[![Platform](https://img.shields.io/badge/platform-WorkBuddy%20%7C%20Claude%20%7C%20skills.sh-green)](#installation)

**Turn a vague research idea into a submission-ready review draft — end to end.**
**从一个模糊的研究想法，到可投稿的综述初稿，端到端完成。**

</div>

---

## English

### What it does

OmniReview is an AI agent skill that runs a full academic literature-review pipeline: question refinement → multi-database search → screening → tiered reading → type-specific synthesis → reporting-guideline audit. Every step leaves an auditable trail.

**Key features**

- **16 review types covered** — systematic review, scoping review, umbrella review, meta-analysis framework, qualitative evidence synthesis (QES), realist review, narrative review, and more. Types are auto-routed by decision tree; multiple types can run in parallel on one search.
- **Four academic APIs out of the box** — OpenAlex, Semantic Scholar, Crossref, and DeepXiv (arXiv/preprint supplement). No API keys required for the main pipeline.
- **Reporting-guideline audit with scores** — complete item banks for PRISMA 2020, PRISMA-ScR, SANRA, and ENTREQ; every item is judged (Reported / Partial / Missing) with quoted evidence from your draft. Ten more guidelines (MOOSE, AMSTAR-2, RAMESES, MMAT…) ship as stubs ready to extend.
- **Fully traceable** — search strings archived, raw hits saved per query, screening decisions carry confidence labels, autonomous-mode decisions logged in real time. Survives reviewer scrutiny.
- **Two control modes** — gate-by-gate confirmation (C0–C6) for submission-grade reviews, or fully autonomous mode with a conservative inclusion policy.
- **Lightweight lanes** — L0 quick landscape scan (research map, not a full review) and incremental updates to existing projects, without re-running the whole pipeline.

### Installation

**WorkBuddy** — search "OmniReview" in the skill marketplace, or upload via the [WorkBuddy Open Platform](https://open.workbuddy.cn).

**Claude Code / Claude Desktop**

```bash
git clone https://github.com/AIScience2026/OmniReview.git
mkdir -p ~/.claude/skills
cp -r OmniReview ~/.claude/skills/omnireview
```

Or drop it into a project's `.claude/skills/omnireview/`.

**skills.sh (any supported agent — Cursor, Codex, Gemini CLI, …)**

```bash
npx skills add AIScience2026/OmniReview
```

### Usage

| Scenario | Example prompt |
| --- | --- |
| Quick landscape scan | "Scan the literature on perceived agency in robotics from the last five years" |
| Full review | "I need a systematic review on X, targeted at a journal submission" |
| Incremental update | "Re-run the DeepXiv search and add 2025 papers to my existing review" |

**Deliverables** (project root): `综述报告.html` (evidence map + charts + full text), `综述报告.md`, `文献汇总表.csv`, `文献检索报告.md`; process data (protocol, audit, raw CSVs, decision log) under `_working/`.

### Requirements

- Python 3.8+ (scripts are stdlib-only, zero dependencies)
- Optional: DeepXiv token ([register here](https://data.rag.ac.cn/register), then add `DEEPXIV_TOKEN=xxx` to `~/.env`) for preprint coverage and progressive reading
- Optional: scansci-pdf / auto-paper-harvester for enhanced full-text download (auto-fallback if absent)

## 中文

### 它做什么

OmniReview 是一个 AI Agent 技能，端到端执行学术综述全流程：**问题打磨 → 多库检索 → 逐篇筛选 → 分层精读 → 分类成稿 → 权威规范审计评分**，每一步都留下可审计的痕迹。

**核心特性**

- **16 种综述类型全覆盖**：系统综述、范围综述、伞状综述、元分析框架、定性证据综合（QES）、现实主义综述、叙述性综述等，按决策树自动路由，支持多类型共享同一检索结果并行产出
- **四大学术库开箱即用**：OpenAlex、Semantic Scholar、Crossref、DeepXiv（arXiv/预印本补充），主干流程零 API key
- **权威规范审计评分**：内置 PRISMA 2020 / PRISMA-ScR / SANRA / ENTREQ 完整条目库，逐条引用稿文原句判定 Reported / Partial / Missing；MOOSE、AMSTAR-2、RAMESES、MMAT 等 10 个规范以桩形式内置、随时可扩展
- **全程可追溯**：检索式留档、原始检索逐次落盘、筛选裁决带置信度、托管模式决策实时记日志——经得起审稿人追问
- **双模式可控**：投稿级综述走 C0–C6 逐关确认；日常调研可全自动托管（保守纳入策略 + 事后审计）
- **轻量车道**：L0 快速脉络扫描（只要研究地图，不写综述）与已有项目的增量更新，均不重跑全流程

### 安装

**WorkBuddy**：在技能市场搜索 "OmniReview"，或经 [WorkBuddy 开放平台](https://open.workbuddy.cn) 上传安装。

**Claude Code / Claude Desktop**

```bash
git clone https://github.com/AIScience2026/OmniReview.git
mkdir -p ~/.claude/skills
cp -r OmniReview ~/.claude/skills/omnireview
```

或放入项目 `.claude/skills/omnireview/`。

**skills.sh（任意支持的 agent——Cursor、Codex、Gemini CLI 等）**

```bash
npx skills add AIScience2026/OmniReview
```

### 使用

| 场景 | 示例说法 |
| --- | --- |
| 快速调研 | "帮我检索机器人感知自主性近五年的论文，看看脉络" |
| 完整综述 | "我要写一篇 XX 的系统综述，准备投稿" |
| 增量更新 | "补跑一下 DeepXiv 检索，把 2025 年的新文献纳进我已有的综述" |

**产出物**（项目根目录）：`综述报告.html`（证据地图 + 统计图 + 全文）、`综述报告.md`、`文献汇总表.csv`、`文献检索报告.md`；过程数据（protocol、审计、原始 CSV、决策日志）在 `_working/`。

### 环境要求

- Python 3.8+（脚本零第三方依赖）
- 可选：DeepXiv 令牌（[在此注册](https://data.rag.ac.cn/register)，写入 `~/.env` 的 `DEEPXIV_TOKEN=xxx`），用于预印本覆盖与渐进式阅读
- 可选：scansci-pdf / auto-paper-harvester 全文下载增强（缺失时自动降级）

## License / 许可

Code and docs: [MIT](LICENSE). Bundled reporting-guideline items (PRISMA 2020, PRISMA-ScR, SANRA, ENTREQ) are redistributed under their original licenses (CC BY 4.0) — see the `source` field in each checklist JSON.

代码与文档采用 MIT 许可；内置报告规范条目（PRISMA 2020、PRISMA-ScR、SANRA、ENTREQ）遵循原始许可（CC BY 4.0），各清单 JSON 的 `source` 字段标注官方出处。
