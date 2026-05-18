---
name: zeal-member-content-eval-preprocess
description: 当 zeal-member-content-eval 进入 PREPROCESS 阶段，需要清洗候选人文本、保留原文、按段落编号并生成后续评估输入时使用。
---

# Preprocess Agent

## 目标

把候选人原始内容整理成可引用、可复核的段落输入。预处理只做结构化，不做评价，不改写候选人观点。

## 输入

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

## 处理规则

1. 保留 `raw_text`，不要覆盖原文。
2. 去除明显无关的外层包装，例如 Markdown 代码围栏、邮件转发头、空白行堆叠。
3. 不删除候选人自己的标题、列表、链接、产品名或自我介绍，因为这些可能是评估证据。
4. 不改写候选人语气，不总结，不翻译。
5. 按自然段编号为 `P1/P2/...`。
6. 如果原文非常短，仍至少生成一个段落。
7. 如果文本包含 YAML frontmatter 或元信息，只在 `metadata_notes` 标记，不把它当作候选人正文评分证据。

## 输出 JSON

```json
{
  "candidate_id": "anonymous_001",
  "source_type": "小作文",
  "context": {
    "activity_name": "",
    "topic": "",
    "known_background": ""
  },
  "raw_text": "候选人原文",
  "paragraphs": [
    {
      "id": "P1",
      "text": "第一段原文"
    }
  ],
  "metadata_notes": [],
  "preprocess_warnings": []
}
```

## 输出路径

默认写入：

```text
docs/member-content-evals/{candidate_id}/preprocessed.json
```

如果用户只要求对话内评估，也要在最终回答中使用 `P#` 引用段落。

## 质量检查

- 段落顺序必须与原文一致。
- `paragraphs[].text` 不能是 Agent 的改写版本。
- 不要在本阶段输出任何分数、风险等级或参与建议。

