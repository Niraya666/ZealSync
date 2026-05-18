---
name: zeal-member-content-eval-evaluate
description: 当 zeal-member-content-eval 需要按认知质量、真实感悟、社群契合、贡献潜力、落地能力、商业风险、表达成熟度等维度隔离评分时使用。
---

# Evaluate Agents

## 目标

为每个评估维度提供独立 rubric 和 prompt。每个 subagent 只评价一个维度，避免被其他维度、最终评级或商业风险结论带偏。

## 全局上下文

每个 subagent 都可以读取：
- 候选人段落 `P1/P2/...`
- `source_type`
- `context.activity_name`
- `context.topic`
- `context.known_background`

每个 subagent 不应读取：
- 其他维度 subagent 的输出
- 最终评级规则
- Main-agent 的汇总判断
- 与当前维度无关的扣分表

## 证据规则

每个评分判断必须引用段落编号：

```json
{
  "paragraph_id": "P2",
  "quote": "不超过 60 字的原文片段",
  "supports": "这个证据支持什么判断"
}
```

引用只取必要短句，不长篇复制原文。证据不足时写"无法判断"，不要脑补。

## 维度 A1：认知质量 `/20`

评估候选人是否具备真实的问题识别能力、概念定义能力、因果推理能力和边界意识。

子项：
- `problem_identification` `/5`：是否抓住问题本质，而不是停留在现象。
- `concept_clarity` `/5`：是否定义核心概念，避免混用热词。
- `causal_reasoning` `/5`：是否解释"为什么"和"如何发生"。
- `boundary_awareness` `/5`：是否知道观点的限制、反例和失败条件。

高分信号：定义核心词，区分现象/原因/机制/结果，有问题链条，说明成立条件，承认不确定性。

低分信号：热词密集但不定义，只有愿景没有机制，只有类比没有因果，判断绝对，压缩后没有明确观点。

输出：

```json
{
  "dimension": "认知质量",
  "score": 0,
  "max_score": 20,
  "subscores": {
    "problem_identification": 0,
    "concept_clarity": 0,
    "causal_reasoning": 0,
    "boundary_awareness": 0
  },
  "evidence": [],
  "positive_signals": [],
  "risk_signals": [],
  "confidence": "high / medium / low"
}
```

## 维度 A2：真实感悟 `/15`

判断文本是否来自真实经验、真实观察和真实反思，而不是概念拼贴、表演式深刻或二手观点复述。

子项：
- `experience_density` `/5`：是否有具体场景、人物、事件、行业、冲突。
- `reflection_authenticity` `/5`：是否体现认知变化、困惑、修正和复盘。
- `non_performativity` `/5`：是否克制、朴素、可信，而不是为了显得高级。

高分信号：具体场景，真实冲突，"我原来以为...后来发现..."，失败、犹豫、修正，细节而非空泛判断。

低分信号：没有具体经验，像文章读后总结，每句话都很大但没有个人观察，只表达正确立场。

输出：

```json
{
  "dimension": "真实感悟",
  "score": 0,
  "max_score": 15,
  "subscores": {
    "experience_density": 0,
    "reflection_authenticity": 0,
    "non_performativity": 0
  },
  "evidence": [],
  "positive_signals": [],
  "risk_signals": [],
  "confidence": "high / medium / low"
}
```

## 维度 A3：社群价值观契合度 `/20`

评估候选人是否符合 ZChat 的社群气质：中短期务实、长期探索、真实连接、反内卷、审美底线、长期主义、克制商业化、组织能力产品化和工具化。

子项：
- `pragmatism` `/4`：是否关注机制、流程、沉淀，而不只是愿景。
- `authentic_connection` `/4`：是否重视真实互动，而非功利链接。
- `aesthetic_fit` `/4`：表达是否克制、舒服、有分寸。
- `anti_involution_energy` `/4`：是否减少焦虑，鼓励创造。
- `long_term_trust` `/4`：是否重视长期关系、边界和信任资产。

高分信号：尊重社群氛围，愿意共创而非索取，不急于交易化，表达有分寸，理解小组织可持续机制。

低分信号：把社群当人脉场，强调资源/客户/曝光/转化，制造焦虑，成功学味重，过度包装，短期套利明显。

输出：

```json
{
  "dimension": "社群价值观契合度",
  "score": 0,
  "max_score": 20,
  "subscores": {
    "pragmatism": 0,
    "authentic_connection": 0,
    "aesthetic_fit": 0,
    "anti_involution_energy": 0,
    "long_term_trust": 0
  },
  "evidence": [],
  "positive_signals": [],
  "risk_signals": [],
  "confidence": "high / medium / low"
}
```

## 维度 A4：贡献可能性 `/20`

评估候选人未来可能给社群带来的具体贡献，而不是只看表达能力或资源规模。

子项：
- `content_contribution` `/5`：是否能输出观点、案例、复盘、方法论。
- `activity_contribution` `/5`：是否适合分享、主持、控场、破冰。
- `organization_contribution` `/5`：是否愿意做流程、反馈、沉淀等慢活。
- `connection_contribution` `/5`：是否能连接合适的人和问题，而不是乱拉资源。

推荐角色只能从以下列表选择：
- 深度分享者
- 主题共创者
- Coffee Chat 主持人
- 内容沉淀者
- 工具产品共创者
- 品牌审美共创者
- 连接撮合者
- 暂需观察

输出：

```json
{
  "dimension": "贡献可能性",
  "score": 0,
  "max_score": 20,
  "subscores": {
    "content_contribution": 0,
    "activity_contribution": 0,
    "organization_contribution": 0,
    "connection_contribution": 0
  },
  "possible_roles": [],
  "evidence": [],
  "positive_signals": [],
  "risk_signals": [],
  "confidence": "high / medium / low"
}
```

## 维度 A5：务实落地能力 `/15`

评估候选人是否能从愿景进入行动，从想法进入机制，从讨论进入小实验。

子项：
- `constraint_awareness` `/5`：是否理解成本、组织、流程、数据、利益相关方。
- `small_experiment_design` `/5`：是否能提出 MVP、试点、指标、反馈闭环。
- `process_tooling_ability` `/5`：是否能把经验沉淀成流程、工具、Agent、小程序。

高分信号：具体行动、先后顺序、试点意识、反馈机制、运营成本、流程化或工具化沉淀。

低分信号：只讲未来不讲今天，只讲平台不讲最小场景，只讲技术不讲组织，没有指标、路径和约束。

输出：

```json
{
  "dimension": "务实落地能力",
  "score": 0,
  "max_score": 15,
  "subscores": {
    "constraint_awareness": 0,
    "small_experiment_design": 0,
    "process_tooling_ability": 0
  },
  "evidence": [],
  "positive_signals": [],
  "risk_signals": [],
  "confidence": "high / medium / low"
}
```

## 维度 A6：商业意图与推销风险 `0-25`

专门识别隐性推销、自我包装、获客、引流、资源索取或工具化社群的倾向。这个维度不参与基础加分，只输出风险扣分建议。

风险项：
- `hidden_sales`：分享是否导向自己的产品、服务、课程、平台。
- `self_branding`：是否大量强调 title、资源、成就、项目，实质内容少。
- `resource_extraction`：是否强调想认识谁、链接谁、获取什么。
- `commercial_boundary_unclear`：是否有商业目的但包装成纯分享。
- `community_instrumentalization`：是否把社群当潜在客户池、流量池或资源池。
- `anxiety_marketing`：是否制造焦虑或内卷叙事。

风险等级：
- 无明显迹象
- 轻微
- 中等
- 明显
- 严重

注意：
- 商业诉求本身不是问题。
- 不透明、不克制、不尊重社群边界才是问题。
- 如果证据不足，写"无明显迹象"或"无法判断"，不要脑补。

输出：

```json
{
  "dimension": "商业意图与推销风险",
  "risk_deduction": 0,
  "max_deduction": 25,
  "risk_items": {
    "hidden_sales": 0,
    "self_branding": 0,
    "resource_extraction": 0,
    "commercial_boundary_unclear": 0,
    "community_instrumentalization": 0,
    "anxiety_marketing": 0
  },
  "sales_intent_level": "无明显迹象 / 轻微 / 中等 / 明显 / 严重",
  "evidence": [],
  "risk_summary": "",
  "boundary_questions": [],
  "human_review_required": false,
  "confidence": "high / medium / low"
}
```

## 维度 A7：表达与互动成熟度 `/10`

评估候选人的表达是否清晰、克制、有讨论空间，以及是否适合社群公共表达。

子项：
- `clarity_and_restraint` `/5`：是否能让人理解，是否不过度包装。
- `openness_and_co_creation` `/5`：是否愿意被质疑、邀请讨论、共同探索。

高分信号：观点清楚，语言有分寸，有问题意识，愿意开放讨论，不用身份和术语制造压迫感。

低分信号：表达晦涩，术语密集，只有结论没有论证，强势输出，不留讨论空间，像演讲稿或融资路演。

输出：

```json
{
  "dimension": "表达与互动成熟度",
  "score": 0,
  "max_score": 10,
  "subscores": {
    "clarity_and_restraint": 0,
    "openness_and_co_creation": 0
  },
  "evidence": [],
  "positive_signals": [],
  "risk_signals": [],
  "discussion_impact": "",
  "confidence": "high / medium / low"
}
```

## 汇总输出

所有维度完成后写入：

```json
{
  "candidate_id": "anonymous_001",
  "dimension_outputs": {
    "cognitive_quality": {},
    "authentic_reflection": {},
    "community_fit": {},
    "contribution_potential": {},
    "practical_execution": {},
    "commercial_risk": {},
    "expression_maturity": {}
  }
}
```

默认路径：

```text
docs/member-content-evals/{candidate_id}/dimension-evals.json
```

