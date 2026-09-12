# 期刊枚举（venue sweep）与高影响力期刊 ISSN 清单

> 用途：解决"主题式检索可能漏掉旗舰期刊/付费墙期刊"的担忧。
> JBI Step2 的第三步（补充检索）要求做"引文追溯 + 灰色文献"，**按期刊枚举**是最可靠的一种补充。

## 1. 为什么需要它

主题式检索（关键词）依赖数据库的相关性排序，低被引或术语独特的好文章可能被排到很后面。
**按刊枚举 = 把某刊 2019 年以来的全部作品拉下来，再在本地做精确 AND 过滤**，可保证"旗舰期刊一篇不漏"。

## 2. 实测结论（2026-09-12，消费级人形机器人 HRI 综述）

Crossref 与 OpenAlex 的**期刊覆盖几乎完全一致**（因为 OpenAlex 会 ingest Crossref 元数据），
但 **OpenAlex 的摘要完整度普遍更高**：

| 期刊 | Crossref 收录数 | OpenAlex 收录数 | Crossref 摘要率 | OpenAlex 摘要率 |
| --- | --- | --- | --- | --- |
| ACM Trans. HRI (THRI) | 449 | 451 | 93% | 100% |
| Int. J. Social Robotics | 923 | 929 | 40% | 56% |
| IEEE RA-L | 10,401 | 10,296 | **0%** | **100%** |
| Science Robotics | 825 | 825 | 100% | 100% |
| Frontiers in Robotics & AI | 2,170 | 2,170 | 60% | 100% |
| Robotics and Autonomous Systems | 1,842 | 1,793 | **0%** | 20% |
| Int. J. Human-Computer Studies | 1,148 | 1,067 | **0%** | 52% |
| Autonomous Robots | 440 | 442 | 46% | 32% |

**结论**：不存在"不用 Crossref 就丢掉高价期刊题摘"的问题 —— OpenAlex 已覆盖同一批记录，
且摘要在 IEEE/Elsevier 系刊上明显更好（Crossref 因出版商不提交摘要而为 0%）。
**Crossref 的正确用法是"期刊枚举"**，而非主题模糊检索（其 `query.bibliographic` 单次可返回百万级
无意义命中）。

## 3. 用法

```bash
# 枚举某刊 2019 以来全部作品
python scripts/search_crossref.py --issn "2573-9522" --since 2019 --limit 0 \
    --out _working/search/crossref_thri.csv

# 多刊枚举 + 本地精确 AND（推荐）
python scripts/search_crossref.py --issn "2573-9522,1875-4791,2470-9476" \
    --terms "robot|trust" --since 2019 --max-scan 6000 \
    --out _working/search/crossref_journals.csv

# OpenAlex 侧等价做法（更推荐，摘要更全）
python scripts/search_openalex.py \
    --filter "primary_location.source.issn:2573-9522,from_publication_date:2019-01-01" \
    --limit 0 --out _working/search/openalex_thri.csv
```

## 4. 推荐 ISSN 清单（HRI / 机器人）

| 期刊 | ISSN |
| --- | --- |
| ACM Transactions on Human-Robot Interaction (THRI) | 2573-9522 |
| International Journal of Social Robotics (IJSR) | 1875-4791；电子 1875-4805 |
| IEEE Robotics and Automation Letters (RA-L) | 2377-3766 |
| IEEE Transactions on Robotics (T-RO) | 1552-3098；1941-0468 |
| Science Robotics | 2470-9476 |
| Frontiers in Robotics and AI | 2296-9144 |
| Robotics and Autonomous Systems | 0921-8890 |
| Autonomous Robots | 0929-5593 |
| IEEE Transactions on Human-Machine Systems | 2168-2291 |
| International Journal of Human-Computer Studies | 1071-5819 |
| International Journal of Humanoid Robotics | 0219-8436 |
| Advanced Robotics | 0169-1864 |
| Paladyn, Journal of Behavioral Robotics | 2081-4836 |
| Robotics (MDPI) | 2218-6581 |
| Interaction Studies | 1572-0373 |
| Computers in Human Behavior（信任/接受度） | 0747-5632 |
| Human Factors（人因/安全） | 0018-7208 |
| Journal of Intelligent & Robotic Systems | 0921-0296 |

**会议**（无 ISSN，改用 OpenAlex `primary_location.source.id` 或按 venue 名过滤）：
ACM/IEEE HRI、IEEE RO-MAN、ICRA、IROS、RSS、CoRL、CHI、CSCW、UIST、AAMAS。

## 5. 注意事项

- Crossref `/journals/{issn}/works` 对未知 ISSN 返回 404，脚本会告警并跳过，不阻塞其他刊。
- Crossref 分页较慢且会限流；一次枚举 1–2 个刊、配合 `--max-scan` 控制扫描量。
- 若同时用 Crossref 与 OpenAlex 做同一批刊的枚举，**合并去重后务必追加标题规范化去重**
  （两库 DOI 相同，普通 DOI 去重即可，但预印本×正式版仍需标题兜底）。
