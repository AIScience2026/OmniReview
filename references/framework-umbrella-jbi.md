# 伞状综述框架卡：JBI

依据：JBI Manual for Evidence Synthesis（Umbrella Reviews 章，Aromataris 等）。对象：对现有**系统性综述/元分析**的再综述——证据金字塔顶层，服务政策制定。报告：PRISMA 2020 适配；附加审计：AMSTAR-2 / ROBIS 评每个纳入 SR 的方法学质量。

## 流程

1. **问题构建**：umbrella 问题必须是"某主题下现有 SR 说了什么"，比 SR 问题更宽一层
2. **检索**：穷尽检索专为找到 SR/MA（filter 文献类型 = review/meta-analysis；主干三库 + 建议用户补 Cochrane Library 的 SR 热线）
3. **筛选与去重叠**：
   - 纳入标准：明确 SR 的质量门槛（如必须报告检索式）
   - **重叠校正是伞状综述的独有难点**：多个 SR 必然覆盖相同 primary studies。记录每个 SR 的纳入研究数，计算跨 SR 重叠（如 corrected covered area, CCA）
   - 处理策略：重叠度高时取质量最高/最新 SR 的数据为主，其余佐证
4. **质量评价（必做，区别于 scoping）**：AMSTAR-2（16 条目，2 大项+14 条）或 ROBIS 逐篇评纳入 SR；结果用于解释证据可信度而非一票否决
5. **提取与综合**：
   - 提取：SR 覆盖的 PICO、检索年限、纳入 primary studies 数、主要效应量结论、AMSTAR-2 评级
   - 综合：按结局/亚组归纳各 SR 结论的**一致/冲突/缺失**矩阵；冲突时优先高 AMSTAR-2 结果
   - 呈现：证据总表（SR × 结局 × 结论 × 质量）+ 叙述总结
6. **报告**：PRISMA 2020 审计 + 附加 AMSTAR-2 子报告；明确"结论的证据底部是 SR 质量而非 primary studies 质量"

## 与本工作流的衔接
- 检索脚本无需改动（同库）；dedup_merge 对 SR 记录额外保留 `referenced_study_count`（若源数据含）
- 审计：`--checklist prisma-2020` + `--checklist amstar-2`（见 checklist-stub-registry.json）
