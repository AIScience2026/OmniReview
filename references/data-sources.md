# 数据源与脚本用法

## 主干三库（免费、无 key）

### 1. OpenAlex — 首选，覆盖最广
- 端点：`https://api.openalex.org/works?search={query}&per-page=100&mailto={email}`
- 过滤：`filter=from_publication_date:2015-01-01,type:article`
- 摘要以倒排索引返回（`abstract_inverted_index`），脚本已实现重建
- 附加 polite pool（mailto 参数）即获更高速率（约 10 req/s）
- `open_access.oa_url` 直接给出 OA 全文链接（download.py 的兜底数据源）

### 2. Semantic Scholar — 引文与 TLDR 好
- 端点：`https://api.semanticscholar.org/graph/v1/paper/search?query={q}&fields=externalIds,title,authors,year,venue,publicationTypes,citationCount,abstract,openAccessPdf&limit=100`
- 免费共享池限流严重（实测常 429）：脚本已内置退避重试，**持续 429 时优雅降级为空结果**（不阻塞流程，但须在 文献检索报告.md 记录该库失败）
- **API key（推荐）**：脚本自动探测 `SEMANTIC_SCHOLAR_API_KEY` / `S2_API_KEY` / `semantic_api_key` 环境变量或 Windows 注册表（HKCU\Environment 兜底），以 `x-api-key` 头发送；有 key 时间隔降为 1.1s（官方 1 req/s 限制）
- **S2 状态码诊断**（实测 2026-09-06）：429 = 限流（等待重试即可）；**403 Forbidden = key 被全局拒绝**（search 与 paper 详情端点均拒）——原因通常是 key 未激活（部分申请需按邮件确认）、已被吊销、或 key 实际属于其他服务。403 时不应重试，直接降级跳过并提示用户核对 key 来源邮件
- `externalIds.DOI` 用于合并去重；`openAccessPdf.url` 为 OA 链接

### 3. Crossref — DOI 元数据权威
- 端点：`https://api.crossref.org/works?query={q}&rows=100&mailto={email}`
- 摘要仅部分出版商提供（JATS XML，脚本做标签剥离）；subject/type 字段完整
- 适合做 DOI 校验与元数据补全
- **数量参数已统一为 `--limit`**（与另三库一致）；`--limit 0` = 取全部匹配，脚本内部 `rows` 分页至 `total-results` 或 `MAX_SAFE=10000` 上限，并打印 `total_available`

## 补充源：DeepXiv（智源研究院开源）
- 安装（隔离 venv）：`pip install deepxiv-sdk`；CLI `deepxiv`，SDK `from deepxiv_sdk import Reader`
- **令牌必须手动注册**（安装不会自动注册）：https://data.rag.ac.cn/register 免费，1000 请求/天
- 令牌配置三选一（脚本 `search_deepxiv.py` 自动探测）：环境变量 `DEEPXIV_TOKEN` / 当前目录 `.env` / 家目录 `~/.env` 写一行 `DEEPXIV_TOKEN=xxx`。**完整分步指引（注册→配置→验证→安全）见 `deepxiv-setup.md`**
- 覆盖：arXiv 全量 T+1 + PMC，混合检索（BM25+向量），每日增量更新
- 用途一（补充检索，脚本化）：`python search_deepxiv.py --query "..." --since 2023 --limit 100 --out _working/search/deepxiv_q1.csv`；无令牌时脚本 exit 2 并给出注册指引，不阻塞其他库
- 用途二（Tier 2 精读层，无 PDF 依赖）：
  - `deepxiv paper {arxiv_id} --brief`（标题/TLDR/关键词/引用数，token 极低）
  - `deepxiv paper {arxiv_id} --head`（章节分布）
  - `deepxiv paper {arxiv_id} --section "Methods"`（定点精读）
  - 免鉴权测试论文：2409.05591、2504.21776（可用于验证阅读链路）
- 限制：人文社科覆盖弱（arXiv 为主）；令牌耗尽时记录并跳过；DOI 统一映射为 `10.48550/arXiv.{id}` 以便与三库去重合并

## Tier 2 下载调度链（download.py）

按优先级自动降级，全部可选：

1. **scansci-pdf**（若 `shutil.which("scansci-pdf")`）：最强——20+ 源竞速、WebVPN/CARSI 付费墙、批量队列。调用：`scansci-pdf get {doi}`
2. **auto-paper-harvester**（若已安装）：出版商 TDM API（Wiley/Elsevier/Springer）→ OA 回退 → Playwright 机构 cookie 兜底
3. **内置兜底**：OpenAlex `oa_url` → Unpaywall API（`https://api.unpaywall.org/v2/{doi}?email={email}`，任意邮箱即可）→ arXiv DOI 直映（10.48550/arXiv.*）

PDF 命名：`{第一作者姓}_{年份}_{标题前6词缩略}_{DOI尾段}.pdf`。失败论文输出 `pdfs/unavailable.csv`（含元数据），供人工走机构馆际互借（ILL）。

## 通用注意

- 所有请求必须带 `mailto` / `User-Agent`（polite pool 礼仪）
- 检索式逐字留档到项目根目录 `文献检索报告.md`（PRISMA 第 7 条证据）
- 单库失败不阻塞：记录失败原因后继续，报告中披露覆盖范围
