# Merge Agent — 增量合并

## 触发条件
两种情况：
1. **初始化**：一次性处理全部历史数据时，每处理完一期后合并
2. **增量更新**：每期新活动结束后，将新期数据合并到现有档案

## 输入
1. 新期的 `session-{n}-aligned.json` 和 `session-{n}-raw.json`
2. 现有档案目录 `docs/member-profiles/*.md`
3. 现有索引 `docs/member-profiles/index.json`

**上下文**：运行前读取 `docs/zeal-mining/docs/zeal-mining/context/community-rules.md` 了解社群特定的角色定义和特殊处理规则。

## 合并逻辑

### 1. 判断成员是否存在

检查 `docs/member-profiles/{canonical-name}.md` 是否存在：

**情况 A：新成员（档案不存在）**
- 调用 Profile Agent 生成完整档案
- 在 `index.json` 的 `members_summary.total_unique` +1

**情况 B：已有成员（档案存在）**
- 读取现有档案
- 按以下规则追加/更新

### 2. 追加规则

**frontmatter 更新**：
```yaml
sessions_count: {原值 + 1}
roles:
  - {session: "第Y期", role: "参与者"}   # 追加新角色记录，保留历史
```

**Activity History**：
- 在表格末尾**追加新行**
- 保持时间顺序一致（建议按时间正序：第一期在上，最新期在下）

**Core Views**：
- 在 `## Core Views` section **末尾追加**新观点
- 标注期数和主题

**Reviews & Interactions**：
- `主动提及他人`：**追加**新期提及记录
- `被他人提及`：**追加**新期被提及记录

**Favorites**：
- 检查是否已存在（按名称去重）
- 如果不存在，**追加**到列表，保留期数标注

**Identity / 背景信息**：
- **补充追加**，不删除已有内容
- 新期提到的背景信息追加到现有描述之后

### 3. 不处理的情况

以下情况**保持原样，不做特殊合并逻辑**：
- `industry` / `role` frontmatter 字段：保留首次出现的值，后续期不更新
- `aliases`：首次建立档案时写入，后续期发现的新 alias 才追加
- 跨期行业描述差异：不尝试智能合并，保留各期原始表述
  - 例外：如果 `docs/zeal-mining/context/name-corrections.md` 中有 ASR 修正记录，优先采用正确表述
- 观点冲突：同一成员在不同期对同一话题的不同看法，**全部保留**，标注期数，体现观点演进

### 4. 索引更新

更新 `docs/member-profiles/index.json`：

```json
{
  "sessions": [
    {
      "session_id": "第X期",
      "date": "YYYY-MM-DD",
      "theme": "会议主题",
      "host": ["主持人昵称"],
      "navigators": ["领航员昵称"],
      "participants": ["参与者昵称"],
      "essays_count": N,
      "alignment_confidence": 0.92
    }
  ],
  "members_summary": {
    "total_unique": N,
    "hosts": ["主持人昵称"],
    "navigator_history": {
      "昵称": ["第X期", "第Y期"]
    }
  }
}
```

**更新规则**：
- `sessions`：按时间顺序追加新活动记录
- `members_summary.total_unique`：仅当新增成员时 +1
- `members_summary.navigator_history`：如果新期有领航员，追加 `{nickname: [期数列表]}`

## 特殊处理

参考 `docs/zeal-mining/context/community-rules.md` 中的角色定义处理特殊情况：

- **主持人**：所有期中的主持人角色记录保留
- **角色变化**：某人从 "参与者" 变为 "领航员" 时，保留两条记录
- **别名合并**：如果新期发现某 canonical_name 的新 alias，追加到 `aliases` 列表

## 输出

- 更新后的 `docs/member-profiles/{canonical-name}.md`
- 更新后的 `docs/member-profiles/index.json`

## 错误处理
- 如果 `index.json` 不存在，创建新的索引文件
- 如果档案文件格式不符合预期，报告警告并尝试修复
