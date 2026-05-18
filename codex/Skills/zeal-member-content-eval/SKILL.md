---
name: zeal-member-content-eval
description: 当用户需要评估 ZChat/ZealSync 成员小作文、报名问卷、活动复盘、分享申请、社群发言或候选人内容质量时触发本 Skill，尤其是提到"评估成员内容"、"小作文评分"、"候选人评估"、"社群价值观契合"、"推销风险"或"内容审核"时。
---

# zeal-member-content-eval

## 触发条件

当用户需要以下操作时触发本 Skill：
- "评估成员内容" / "评估小作文"
- "给候选人做社群评估"
- "判断是否适合进入 ZChat"
- "看这段报名问卷是否有推销风险"
- "根据小作文生成管理员内部评估报告"
- "评估认知质量、真实感悟、贡献潜力或社群契合度"

## 概述

本 Skill 面向管理员内部使用，用于评估候选人在小作文、报名问卷、活动复盘、分享申请、社群发言等文本中呈现出的可观察信号。

核心原则：
- 只评估文本信号，不评价人格、智商、阶层、身份或真实动机。
- 所有判断必须有文本证据；证据不足时写"无法判断"。
- 不奖励身份光环、术语密度、宏大叙事或自我包装。
- 不因表达朴素而低估真实经验、稳定贡献和组织建设能力。
- 商业诉求本身不是问题；不透明、不克制、不尊重边界才是风险。

## 默认输入

优先接收 JSON；如果用户只给原文，Agent 需要补齐缺省字段。

```json
{
  "candidate_id": "anonymous_001",
  "source_type": "小作文",
  "text": "候选人原文",
  "context": {
    "activity_name": "",
    "topic": "",
    "known_background": ""
  }
}
```

## 默认输出

默认生成管理员内部报告，不直接写入成员档案：

```text
docs/member-content-evals/{candidate_id}/evaluation-report.md
docs/member-content-evals/{candidate_id}/evaluation-result.json
```

允许在同一目录保存中间产物：

```text
preprocessed.json
dimension-evals.json
evidence-review.json
```

## 状态机

```text
[INIT] -> [PREPROCESS] -> [DIMENSION_EVAL] -> [EVIDENCE_REVIEW] -> [MAIN_SUMMARY] -> [REPORT] -> [DONE]
```

| 状态 | 说明 | 输出 |
|------|------|------|
| INIT | 确定 candidate_id、source_type、文本和上下文 | 标准输入对象 |
| PREPROCESS | 清洗格式、保留原文、按段落编号 | `preprocessed.json` |
| DIMENSION_EVAL | 隔离上下文调用各维度 subagent | `dimension-evals.json` |
| EVIDENCE_REVIEW | 审查证据、过度推断和评分冲突 | `evidence-review.json` |
| MAIN_SUMMARY | 汇总分数、扣分、评级和建议 | 汇总 JSON |
| REPORT | 写入内部 Markdown 报告和结构化 JSON | 最终输出文件 |

## 流程编排

### INIT

1. 如果用户提供 JSON，校验 `candidate_id`、`source_type`、`text`、`context`。
2. 如果用户只提供文本：
   - `candidate_id` 使用 `anonymous_YYYYMMDD_HHMMSS` 或用户给出的昵称。
   - `source_type` 默认 `小作文`。
   - `context` 缺省字段置空。
3. 创建输出目录 `docs/member-content-evals/{candidate_id}/`。
4. 不读取或修改 `docs/member-profiles/`，除非用户明确要求。

### PREPROCESS

调用 `preprocess/SKILL.md`：
- 保留候选人原文。
- 去掉无关包装格式，但不改写意思。
- 按自然段生成 `P1/P2/...` 编号。
- 输出 `preprocessed.json`。

### DIMENSION_EVAL

调用 `evaluate/SKILL.md`。

Main-agent 必须保证上下文隔离：
- 每个维度评估使用独立 subagent 或独立推理轮次。
- 每个 subagent 只接收：候选人段落、全局 context、当前维度 rubric、当前维度 prompt。
- 不把其他维度评分、最终评级规则或商业风险结果泄露给当前维度 subagent。
- 如果当前 harness 不支持 subagent，则按维度顺序处理，并在每个维度前明确重置判断，只保留该维度 rubric。

基础评分维度：
- 认知质量 `/20`
- 真实感悟 `/15`
- 社群价值观契合度 `/20`
- 贡献可能性 `/20`
- 务实落地能力 `/15`
- 表达与互动成熟度 `/10`

风险维度：
- 商业意图与推销风险：输出 `risk_deduction`，范围 `0-25`。

### EVIDENCE_REVIEW

调用 `review/SKILL.md`：
- 检查关键判断是否有段落证据。
- 检查是否把"可能"写成"确定"。
- 检查是否从文本外脑补作者动机。
- 检查高分与高风险是否冲突。
- 给出评分调整建议和人工复核建议。

### MAIN_SUMMARY

调用 `summarize/SKILL.md`：
- 基础分为六个加分维度之和，满分 100。
- `final_score = base_score - risk_deduction`。
- 根据证据审查结果调整置信度和参与建议。
- 输出 `S/A/B/C/D/M` 或组合标签，如 `A-M`、`B-M`。

## 汇总裁决原则

Main-agent 不重新逐字评分，只做校准和裁决：
- 有文本证据的评分优先。
- 证据不足的高分要降权或降低置信度。
- 风险项不因认知分高而自动抵消。
- 商业意图不透明时，参与建议保守。
- 对社群气质有破坏风险时，降低核心参与层级。
- 贡献潜力高但边界不清时，建议"观察参与"而非"核心共创"。

## 子 Skill 引用

| 子 Skill | 路径 | 职责 |
|----------|------|------|
| Preprocess Agent | `preprocess/SKILL.md` | 文本清洗、段落编号、原文保留 |
| Evaluate Agents | `evaluate/SKILL.md` | 维度 rubric、subagent 输入隔离、分项评分 |
| Review Agent | `review/SKILL.md` | 证据质量、一致性和过度推断审查 |
| Summarize Agent | `summarize/SKILL.md` | 最终分数、评级、角色建议和报告模板 |

## 质量检查清单

完成评估前检查：
- [ ] 报告没有对人格、智商或真实动机作绝对判断。
- [ ] 每个关键结论都有 `P#` 段落证据或明确写"无法判断"。
- [ ] 商业风险使用分级语言，不使用羞辱性或定罪式表达。
- [ ] JSON 中包含 `human_review_required` 和 `confidence`。
- [ ] Markdown 报告包含分项评分、正向信号、风险信号、推荐角色、追问问题。
- [ ] 没有修改 `docs/member-profiles/`。

