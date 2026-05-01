# Align Agent — 身份对齐

## 触发条件
当 Extract Agent 完成数据提取后，调用本 Agent 进行身份对齐。

## 输入
`docs/member-profiles/session-{n}-raw.json`

**上下文**：运行前读取 `context/community-rules.md` 了解角色定义，读取 `context/name-corrections.md` 了解已知的昵称-实名映射和 ASR 修正。

## 核心任务

将三重命名空间对齐到统一的 **小作文昵称**（canonical_name）：
1. `essays[].nickname` — 小作文中的微信群昵称
2. `attendees[].name` — 纪要中的实名/化名
3. `speakers[].speaker_id` — 智能章节中的说话人编号

## 对齐 Loop

### Round 1: Identity Extractor

为每个候选身份生成 enriched identity card：

**小作文身份卡片**：
```json
{
  "type": "essay",
  "nickname": "{昵称}",
  "industry": "{行业}",
  "role": "{岗位}",
  "self_descriptions": ["自我描述1", "自我描述2"],
  "topic_tags": ["标签1", "标签2"],
  "mentioned_others": ["提及的人名"],
  "quotes": ["核心观点"]
}
```

**纪要身份卡片**：
```json
{
  "type": "attendee",
  "name": "{实名}",
  "background": "背景描述",
  "role_hint": "host|navigator|participant",
  "self_intro_summary": "自我介绍摘要"
}
```

**说话人身份卡片**：
```json
{
  "type": "speaker",
  "speaker_id": "说话人{N}",
  "self_mentions": ["自我称呼"],
  "mentioned_by_others": ["被他人称呼"],
  "topic_tags": ["标签1"],
  "name_hints": ["名字线索"]
}
```

**提取规则**：
- 从 `content` 中提取所有第一人称表述（"我是..."、"我叫..."、"我在..."）
- 从 `chapters[].content` 中提取说话人的自我称呼和被他人称呼
- 从 `background` 中提取行业、岗位关键词
- 生成话题标签：参考 `context/topic-tags.md` 中的话题词库

### Round 2: Matcher

基于 identity cards 建立映射，评分维度：

| 线索类型 | 权重 | 说明 |
|----------|------|------|
| 名字直接匹配 | 最高 | 昵称与实名中的字完全匹配 |
| 行业关键词重叠 | 高 | 行业/岗位关键词在多个来源中同时出现 |
| 自我描述匹配 | 高 | "我是做XX的" ↔ attendee背景"XX" |
| 话题标签匹配 | 中 | 小作文话题与 speaker 发言话题一致 |
| 被他人提及 | 中 | 小作文A提到B的名字，speaker章节中被称呼为B |

**输出**：`candidate_mappings`
```json
{
  "mappings": [
    {
      "canonical_name": "{小作文昵称}",
      "aliases": ["{纪要实名}"],
      "speaker_ids": ["说话人{N}"],
      "essay_nickname": "{原始小作文标识}",
      "confidence": "high|medium|low",
      "role_in_session": "host|navigator|participant",
      "reasoning": "对齐理由简述"
    }
  ]
}
```

### Round 3: Verifier

验证完整性：
- [ ] 所有 speaker 都有映射？
- [ ] 所有 essay nickname 都有映射？
- [ ] 无 "一个 speaker → 多个 canonical_name" 冲突？
- [ ] 无 "一个 canonical_name → 多个 speaker" 冲突？
- [ ] 主持人已识别？
- [ ] 领航员已识别？

验证一致性：
- 检查角色标注是否合理（一人不能同时是主持人和领航员）

### Round 4: Judge（条件触发）

对 NEEDS_REVIEW / CONFLICT 案例重新推理：
- 读取更多上下文（如相邻章节的发言）
- 对比多期数据（如该成员是否在其他期出现过）
- 查阅 `context/name-corrections.md` 了解已知的 ASR 错误和映射
- 如仍无法确定，标记为 UNCERTAIN 并说明原因

## 对齐原则

1. **canonical_name 采用小作文昵称**
   - `@昵称-行业-岗位` → canonical_name: "昵称"
   - `@昵称（备注）` → canonical_name: "昵称"
   - `@&` 等特殊符号 → 原样保留为 canonical_name

2. **纪要实名作为 aliases**
   - 将纪要中的实名加入 `aliases` 列表

3. **角色识别**
   - 主持人：参考 `context/community-rules.md` 中的主持人定义
   - 领航员：纪要中明确标注 "领航员XXX"
   - 参与者：默认角色

4. **ASR 修正**
   - 对齐时查阅 `context/name-corrections.md` 中的 ASR 错误修正表
   - 如遇到已知的识别错误（如行业描述错误），优先采用正确表述

## 输出

写入 `docs/member-profiles/session-{n}-aligned.json`

```json
{
  "session_id": "第X期",
  "date": "YYYY-MM-DD",
  "canonical_names": [
    {
      "name": "{canonical_name}",
      "aliases": ["{实名}"],
      "speaker_ids": ["说话人{N}"],
      "essay_nickname": "{原始标识}",
      "confidence": "high|medium|low",
      "role_in_session": "host|navigator|participant"
    }
  ],
  "uncertain": [
    {
      "speaker_id": "说话人{N}",
      "possible_names": ["候选1", "候选2"],
      "reason": "无法确定的原因"
    }
  ]
}
```
