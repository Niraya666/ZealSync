# Profile Agent — 画像生成

## 触发条件
当 Align Agent 完成身份对齐后，调用本 Agent 生成/更新个人档案。

## 输入
1. `docs/member-profiles/session-{n}-aligned.json` — 对齐结果
2. `docs/member-profiles/session-{n}-raw.json` — 原始提取数据（用于补充发言内容、好物等）

**上下文**：运行前读取 `context/topic-tags.md` 了解话题分类词库。

## 任务

为每个 `canonical_name` 生成或更新个人档案 Markdown。

### 档案结构

```markdown
---
canonical_name: {小作文昵称}
aliases:
  - {纪要实名1}
  - {纪要实名2}
industry: {行业}
role: {岗位}
first_seen: {首次出现日期}
sessions_count: {参与期数}
roles:
  - {session: "第X期", role: "主持人/领航员/参与者"}
confidence: {high|medium|low}
---

## Identity

### 背景信息
{从会议纪要 attendees 中提取的背景描述，合并多期信息}

### 技能标签
{从发言内容和小作文中提取的技能关键词}

### 兴趣领域
{从好物分享和话题标签中提取的兴趣方向}

## Activity History

| 期数 | 日期 | 角色 | 好物分享 |
|------|------|------|----------|
| 第X期 | YYYY-MM-DD | 角色 | 好物名称 |

## Core Views

> "引用原文中的核心观点，保留原文表述"
> —— 第X期，关于{主题}的看法

{每条观点需标注：}
{ - 来源期数}
{ - 来源类型：小作文 / 会议纪要发言 / 关键决策}
{ - 主题标签（参考 context/topic-tags.md）}

## Reviews & Interactions

### 主动提及他人
- 第X期小作文中提到 {canonical_name}：{具体内容摘要}
- 第X期发言中提及 {canonical_name}：{具体内容摘要}

### 被他人提及
- 第X期 {canonical_name} 的小作文中提及：{具体内容摘要}
- 第X期 {canonical_name} 的发言中提及：{具体内容摘要}

## Favorites

- {好物名称}（{类型}，第X期）
  {推荐理由摘要}

## Network

{可选，V2阶段补充}
{ - 互动频率较高的人}
{ - 共同参与的主题}
```

### 信息来源映射

| 档案 Section | 数据来源 | 提取规则 |
|-------------|----------|----------|
| Identity / 背景信息 | `attendees[].background` | 合并多期描述，去重 |
| Identity / 技能标签 | `speakers[].chapters` + `essays[].content` | 提取 "我做..."、"我擅长..." 等表述 |
| Activity History | `session_id` + `date` + `aligned.role` + `essays[].favorites` | 逐期汇总 |
| Core Views | `speakers[].chapters` + `essays[].content` | 提取有观点性的表述，标注主题 |
| Reviews / 主动提及 | `essays[].mentions` | 记录谁在什么期提到了谁 |
| Reviews / 被他人提及 | 其他成员的 mentions | 交叉引用 |
| Favorites | `essays[].favorites` | 分类并保留推荐理由 |

### 好物分类

将好物按类型分类：
- **书籍**：《书名》
- **App/工具**：App名称
- **影视**：电影名 / B站视频 / 电视剧
- **地点**：地名（公园、城市、景点）
- **生活方式**：习惯、方法、理念
- **其他**：无法归类的

### 跨期聚合规则

当更新已有档案时：
- **Activity History**：追加新行
- **Core Views**：追加新观点，同一主题下的观点按时间排列
- **Favorites**：去重追加，保留所有期数的推荐
- **Identity**：补充新信息（如某期提到的新背景），不覆盖已有信息
- **sessions_count**：+1
- **roles**：追加新角色记录

## 输出

将档案写入 `docs/member-profiles/{canonical-name}.md`

如果档案已存在，使用 Edit 工具追加新内容，不覆盖已有信息。

同时更新 `docs/member-profiles/index.json` 的 `members_summary` 部分。
