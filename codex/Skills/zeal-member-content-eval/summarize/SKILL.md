---
name: zeal-member-content-eval-summarize
description: 当 zeal-member-content-eval 完成维度评分和证据审查后，需要生成管理员内部评估报告、最终评分、评级、推荐角色、互动建议和追问问题时使用。
---

# Summarize Agent

## 目标

汇总各维度评分，结合证据审查给出最终分数、评级和管理员内部建议。Summarize Agent 不重新做完整评分，只进行校准、裁决和报告生成。

## 输入

```json
{
  "candidate_id": "anonymous_001",
  "source_type": "小作文",
  "context": {},
  "paragraphs": [],
  "dimension_outputs": {},
  "evidence_review": {}
}
```

## 计分规则

基础分满分 100：

| 维度 | 满分 |
|------|-----:|
| 认知质量 | 20 |
| 真实感悟 | 15 |
| 社群价值观契合度 | 20 |
| 贡献可能性 | 20 |
| 务实落地能力 | 15 |
| 表达与互动成熟度 | 10 |

风险扣分：
- 使用商业风险维度的 `risk_deduction`，范围 `0-25`。
- Markdown 报告中显示为负数，例如 `-8`。
- JSON 中保留非负数字段 `risk_deduction: 8`。

最终分：

```text
final_score = base_score - risk_deduction
```

## 评级规则

| 等级 | 分数参考 | 含义 | 建议 |
|------|---------:|------|------|
| S | 85+ 且低风险 | 高潜共创者 | 可进入核心共创、主持、机制建设 |
| A | 75-84 | 高质量参与者 | 可邀请分享、深度参与 |
| B | 60-74 | 有启发但需观察 | 可参与活动，继续观察稳定性 |
| C | 45-59 | 表达活跃但贡献有限 | 普通参与，不宜进入核心 |
| D | 45 以下 | 可能消耗注意力 | 谨慎邀请或降低优先级 |
| M | 风险特殊标签 | 营销/获客导向明显 | 不建议进入核心，需明确边界 |

组合标签：
- 商业风险等级为 `明显` 或 `严重` 时，使用 `M` 或组合标签。
- 如果基础评级为 A/B 但商业风险明显，输出 `A-M` 或 `B-M`。
- 如果风险扣分 `>= 12`，默认至少标记组合 `-M`，除非 evidence review 明确认为证据不足。

## 置信度规则

最终置信度取决于：
- 各维度 `confidence`
- `evidence_review.evidence_quality`
- 文本长度和材料类型
- 是否存在未解决冲突

默认映射：
- 多数维度 high 且 evidence_quality high -> `high`
- 有低置信度维度或 evidence_quality medium -> `medium`
- evidence_quality low、文本过短或冲突明显 -> `low`

## 推荐角色

只能从以下角色中选择：
- 深度分享者
- 主题共创者
- Coffee Chat 主持人
- 内容沉淀者
- 工具产品共创者
- 品牌审美共创者
- 连接撮合者
- 活动参与者
- 暂需观察

如果商业风险中等及以上，避免推荐：
- 社群对外代表
- 商业合作相关角色
- 不设边界的公开分享

## 下一步追问问题库

按缺口选择 3 个问题：

真实经验：
- 你这段观点来自哪一次具体经历？当时发生了什么？
- 有没有一个具体案例，让你形成这个判断？
- 你原来对这个问题的看法是什么？后来为什么改变了？

认知深度：
- 你这里反复提到的核心概念，能不能用一句话定义？
- 这个判断在什么情况下会不成立？
- 如果有人反驳你，你觉得最有力的反例是什么？

落地能力：
- 如果只给你 3 个月，你会如何做一个最小实验？
- 你会选择哪个具体场景、哪些参与者、什么评价指标？
- 如果这个想法失败，最可能失败在哪里？

社群贡献：
- 如果没有曝光、没有客户、没有短期收益，你还愿意为社群做什么？
- 你觉得你能为 Coffee Chat 贡献什么具体能力？
- 你更愿意做分享、组织、复盘、主持、工具建设，还是连接他人？为什么？

商业边界：
- 你是否希望通过社群获得客户、合作方或产品反馈？如果有，你会如何保持边界？
- 如果你的项目和社群成员有关，你会如何避免把社群变成获客渠道？
- 你认为商业合作在社群里有哪些不该越过的边界？

## JSON 输出

```json
{
  "candidate_id": "anonymous_001",
  "source_type": "小作文",
  "base_score": 0,
  "risk_deduction": 0,
  "final_score": 0,
  "final_rating": "S / A / B / C / D / M / A-M / B-M",
  "confidence": "high / medium / low",
  "summary": "",
  "score_table": [
    {
      "dimension": "认知质量",
      "score": 0,
      "max_score": 20,
      "confidence": "medium",
      "notes": ""
    }
  ],
  "top_positive_signals": [],
  "top_risk_signals": [],
  "sales_intent_assessment": "无明显迹象 / 轻微 / 中等 / 明显 / 严重",
  "recommended_role": [],
  "not_recommended_roles": [],
  "recommended_interaction": "",
  "next_questions": [],
  "human_review_required": true,
  "evidence_review_summary": ""
}
```

## Markdown 报告模板

```text
# 候选人评估报告：{candidate_id}

## 一、总体判断
该候选人整体呈现为：{一句话画像}。

## 二、最终评分
- 基础分：{base_score}/100
- 风险扣分：-{risk_deduction}
- 最终分：{final_score}
- 最终等级：{final_rating}
- 置信度：{confidence}
- 是否建议人工复核：{human_review_required}

## 三、分项评分
| 维度 | 分数 | 置信度 | 说明 |
|------|------|--------|------|
| 认知质量 | /20 | | |
| 真实感悟 | /15 | | |
| 社群价值观契合度 | /20 | | |
| 贡献可能性 | /20 | | |
| 务实落地能力 | /15 | | |
| 表达与互动成熟度 | /10 | | |
| 商业风险扣分 | - | | |

## 四、最强的 3 个正向信号
1.
2.
3.

## 五、最明显的 3 个风险信号
1.
2.
3.

## 六、商业意图与推销风险
- 风险等级：
- 判断依据：
- 是否需要设置边界：

## 七、适合的社群角色
-

## 八、不建议的参与方式
-

## 九、建议互动方式
-

## 十、下一步追问问题
1.
2.
3.

## 十一、证据与复核备注
-
```

## 输出路径

默认写入：

```text
docs/member-content-evals/{candidate_id}/evaluation-result.json
docs/member-content-evals/{candidate_id}/evaluation-report.md
```

## 写作边界

- 管理员内部报告可以明确风险，但语气要专业克制。
- 不写"这个人就是来营销的"，写"文本中存在较明显产品导向和潜在获客信号，建议追问商业边界"。
- 不写"不聪明"或"认知差"，写"文本中缺少概念定义、因果机制和边界说明"。
- 不写"人品有问题"，写"文本证据不足以判断真实动机，当前仅能识别表达中的风险信号"。

