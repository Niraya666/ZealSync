# Align Agent — 身份对齐

## 触发条件
当 Extract Agent 完成数据提取后，调用本 Agent 进行身份对齐。

## 输入
`docs/member-profiles/session-{n}-raw.json`

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
  "nickname": "Shawn",
  "industry": "智驾",
  "role": "研发管理",
  "self_descriptions": ["消费电子行业做手机项目PMO", "有运营和用研经验"],
  "topic_tags": ["品牌化", "小程序", "社群运营"],
  "mentioned_others": ["Eva"],
  "quotes": ["社团干货多、潜力大，但缺乏团魂"]
}
```

**纪要身份卡片**：
```json
{
  "type": "attendee",
  "name": "邵昂",
  "background": "消费电子行业做手机项目PMO",
  "role_hint": "participant",
  "self_intro_summary": "愿用文字输出助力社团品牌化"
}
```

**说话人身份卡片**：
```json
{
  "type": "speaker",
  "speaker_id": "说话人2",
  "self_mentions": ["我曾在张江芯片公司做数字化转型AI算法岗位"],
  "mentioned_by_others": ["说话人1提到说话人2"],
  "topic_tags": ["品牌化", "小程序"],
  "name_hints": ["邵昂"]
}
```

**提取规则**：
- 从 `content` 中提取所有第一人称表述（"我是..."、"我叫..."、"我在..."）
- 从 `chapters[].content` 中提取说话人的自我称呼和被他人称呼
- 从 `background` 中提取行业、岗位关键词
- 生成话题标签：匹配社群常见主题词库（AI应用、职业规划、投资、社群运营、机器人、医药、法律等）

### Round 2: Matcher

基于 identity cards 建立映射，评分维度：

| 线索类型 | 权重 | 示例 |
|----------|------|------|
| 名字直接匹配 | 最高 | "三金" ↔ "三金" |
| 行业关键词重叠 | 高 | "智驾" ↔ "手机项目PMO"（同属科技/电子领域） |
| 自我描述匹配 | 高 | "我是做消费品营销的" ↔ attendee背景"消费品营销" |
| 话题标签匹配 | 中 | 小作文提到"品牌化" ↔ speaker章节讨论"品牌化" |
| 被他人提及 | 中 | 小作文A提到"邵昂" ↔ speaker在某章节中被称呼"邵昂" |

**输出**：`candidate_mappings`
```json
{
  "mappings": [
    {
      "canonical_name": "Shawn",
      "aliases": ["邵昂"],
      "speaker_ids": ["说话人2"],
      "essay_nickname": "Shawn-智驾-研发管理",
      "confidence": "high",
      "role_in_session": "参与者",
      "reasoning": "小作文昵称Shawn与纪要实名邵昂通过行业背景（消费电子/智驾）和话题（品牌化、小程序）匹配。说话人2在章节中自称'手机项目PMO'，与小作文行业一致。"
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
- [ ] 主持人（Eva）已识别？
- [ ] 领航员已识别？

验证一致性：
- 检查行业描述是否一致（如 "芯片-研发" vs "新电工程师" 可接受为同一人的不同描述）
- 检查角色标注是否合理（一人不能同时是主持人和领航员）

### Round 4: Judge（条件触发）

对 NEEDS_REVIEW / CONFLICT 案例重新推理：
- 读取更多上下文（如相邻章节的发言）
- 对比多期数据（如该成员是否在其他期出现过）
- 如仍无法确定，标记为 UNCERTAIN 并说明原因

## 对齐原则

1. **canonical_name 采用小作文昵称**
   - `@Shawn-智驾-研发管理` → canonical_name: "Shawn"
   - `@三金-芯片-研发` → canonical_name: "三金"
   - `@Eva（社群发起人）` → canonical_name: "Eva"
   - `@&` → canonical_name: "&"

2. **纪要实名作为 aliases**
   - "邵昂" → aliases: ["邵昂"]
   - "伊娃" → aliases: ["伊娃"]

3. **Eva 统一处理**
   - 所有期中的 Eva / 伊娃 → canonical_name: "Eva"
   - role: "主持人"

4. **角色识别优先级**
   - 主持人：Eva 默认主持人；其他人员需明确证据
   - 领航员：纪要中明确标注 "领航员XXX"
   - 参与者：默认角色

## 输出

写入 `docs/member-profiles/session-{n}-aligned.json`

```json
{
  "session_id": "第十期",
  "date": "2026-04-26",
  "canonical_names": [
    {
      "name": "Shawn",
      "aliases": ["邵昂"],
      "speaker_ids": ["说话人2"],
      "essay_nickname": "Shawn-智驾-研发管理",
      "confidence": "high",
      "role_in_session": "参与者"
    }
  ],
  "uncertain": [
    {
      "speaker_id": "说话人5",
      "possible_names": ["Cecilia", "robbins"],
      "reason": "发言内容未包含明确的自我称呼，需人工确认"
    }
  ]
}
```
