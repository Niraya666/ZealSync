---
name: zeal-member-content-eval-review
description: 当 zeal-member-content-eval 完成各维度评分后，需要审查证据质量、评分一致性、过度推断、无依据判断和人工复核需求时使用。
---

# Evidence Review Agent

## 目标

审查各维度 subagent 的评分是否可靠。Review Agent 不重新评价候选人，而是评价评估过程本身是否有证据、是否一致、是否过度推断。

## 输入

```json
{
  "candidate_id": "anonymous_001",
  "paragraphs": [],
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

## 审查规则

逐项检查：
1. 每个关键判断是否引用了有效 `P#`。
2. 引用片段是否真的支持该判断。
3. 是否把候选人的身份、行业、title 当作加分依据。
4. 是否把"可能"、"倾向"、"风险信号"写成确定动机。
5. 是否存在高分与风险同时成立但未解释的情况。
6. 是否存在同一证据被不同维度作出相反解释。
7. 是否存在文本太短、材料类型不足或上下文缺失导致的低置信度。

## 调整建议

Review Agent 可以给出调整建议，但不要直接覆盖原分数：
- `score_adjustment_suggestions` 中写明建议调整哪个维度、理由和建议范围。
- 对证据不足的高分，建议降低分数或降低置信度。
- 对证据不足的风险判断，建议降低风险等级或改为人工追问。
- 对商业风险中等及以上，但正向分数较高的情况，建议保守参与层级。

## 人工复核触发

任一情况成立时，`human_review_required = true`：
- `evidence_quality = low`
- 任一维度 `confidence = low`
- 商业风险等级为 `中等`、`明显` 或 `严重`
- 存在无法消解的评分冲突
- 文本少于 300 字且给出了较高分
- 关键建议会影响是否进入核心共创、公开分享或商业合作

## 输出 JSON

```json
{
  "dimension": "证据与一致性审查",
  "evidence_quality": "high / medium / low",
  "unsupported_claims": [
    {
      "dimension": "认知质量",
      "claim": "",
      "reason": ""
    }
  ],
  "over_inferences": [
    {
      "dimension": "商业意图与推销风险",
      "claim": "",
      "safer_wording": ""
    }
  ],
  "contradictions": [
    {
      "dimensions": ["贡献可能性", "商业意图与推销风险"],
      "description": "",
      "recommended_handling": ""
    }
  ],
  "score_adjustment_suggestions": [
    {
      "dimension": "",
      "current_score": "",
      "suggested_adjustment": "",
      "reason": ""
    }
  ],
  "confidence_adjustments": [],
  "human_review_required": true,
  "review_summary": ""
}
```

## 输出路径

默认写入：

```text
docs/member-content-evals/{candidate_id}/evidence-review.json
```

## 禁止事项

- 不要新增没有文本证据的人格判断。
- 不要把商业风险写成道德审判。
- 不要因为候选人有高学历、大厂 title、创业者或投资人身份而提高可信度。
- 不要因为文字普通就否定潜在贡献。

