# DeepXiv 令牌配置指引（setup guide）

DeepXiv（智源研究院开源）是 omnireview 的补充检索源 + Tier 2 精读层：arXiv 全量 T+1 + PMC，混合检索（BM25+向量）。**阅读链路（brief/head/section）免鉴权可用；检索链路需要免费令牌**（1000 请求/天）。

## 配置三步走

### 第 1 步：注册并获取令牌

1. 打开 **https://data.rag.ac.cn/register** （免费，学术用途）
2. 注册/登录后，在个人中心（API Keys / 令牌页）复制你的令牌（一串长字符串）

### 第 2 步：配置令牌（三选一，脚本自动探测，优先级从高到低）

| 方式 | 操作 | 生效范围 |
|---|---|---|
| **A. 家目录 `.env`（推荐）** | 在 `C:\Users\<用户名>\.env`（即 `~/.env`）写入一行：`DEEPXIV_TOKEN=你的令牌` | 所有项目永久可用，推荐 |
| **B. 用户环境变量** | PowerShell 执行：`setx DEEPXIV_TOKEN "你的令牌"`，然后**重开终端** | 所有终端永久可用 |
| **C. 当前目录 `.env`** | 在综述项目根目录建 `.env` 写 `DEEPXIV_TOKEN=你的令牌` | 仅本项目，适合隔离多个令牌 |

注意事项：
- `.env` 文件为 **UTF-8 无 BOM** 编码，`=` 两边**不要加空格**，值若含特殊字符可用英文双引号包裹
- **AI 代写 `.env` 的安全命令**（BOM 事故教训 2026-09-06）：用 bash 写入 `printf 'DEEPXIV_TOKEN=%s\n' "令牌" > ~/.env`；**禁止**用 Windows PowerShell 5.1 的 `Add-Content -Encoding UTF8` 新建该文件（PS5.1 会自动加 BOM，使键名变成 `\ufeffDEEPXIV_TOKEN`，grep 与脚本的 startswith 均失配）。PS7 的 `utf8NoBOM` 或 `Out-File -Encoding ascii` 可以
- **验证令牌是否可读**：`od -c ~/.env | head -2` 看首行是否以 `D` 开头（而非 `357 273 277` 即 EF BB BF）；或直接跑一次第 3 步的真实检索
- 方式 B 用 `setx` 后当前终端不生效，需新开一个终端（或重启 WorkBuddy 会话）
- 配好后可删除其他方式的重复配置，保持单一来源

### 第 3 步：验证

```bash
# 1. 确认 SDK 已装入隔离 venv（首次使用才需要；路径以你的 Python/venv 为准）
python -m pip install deepxiv-sdk

# 2. 跑一次真实检索验证
cd <技能目录>/scripts
python search_deepxiv.py \
    --query "perceived agency robot" --since 2023 --limit 10 \
    --out ./deepxiv_test.csv

# 预期输出: [ok] DeepXiv 命中 N 条 -> ./deepxiv_test.csv
```

若输出 `[err] 未找到 DeepXiv 令牌` → 检查第 2 步的文件路径与行格式；若输出检索失败（非令牌类错误）→ 检查网络或配额（1000 请求/天耗尽会报错，次日自动恢复）。

> **排障分离原则**（2026-09-06 教训）："未安装 SDK"和"无令牌"是两个独立故障，报错信息已分开，不要把前者当成终点——装好 SDK 后必须立即重跑一次验证令牌链路；反之亦然。用户声称"令牌已在环境变量"时，优先怀疑**文件编码/键名匹配**问题（BOM、行首空格、大小写），而不是怀疑用户。

## 脚本行为约定（供 AI 参考）

- `search_deepxiv.py` 自动探测顺序：环境变量 `DEEPXIV_TOKEN` → 当前目录 `.env` → 家目录 `~/.env`
- 无令牌/无 SDK 时 **exit 2 并打印注册指引**，不阻塞其他库——检索编排照常继续，只需在 文献检索报告.md 记录"DeepXiv 未配置"
- DOI 统一映射为 `10.48550/arXiv.{id}`，与 OpenAlex/S2/Crossref 可直接去重合并
- Tier 2 精读（免鉴权，无需令牌）：`deepxiv paper {arxiv_id} --brief / --head / --section "Methods"`；测试论文 `2409.05591`、`2504.21776`

## 令牌安全

- 令牌等价于免费配额凭证，不要提交到 git 仓库或写入会分享的文档
- 泄露后到注册平台重置即可
