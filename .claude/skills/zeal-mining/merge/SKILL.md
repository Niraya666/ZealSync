# Merge Agent — 增量合并

## 触发条件
两种情况：
1. **初始化**：一次性处理全部 10 期历史数据时，每处理完一期后合并
2. **增量更新**：每期新活动结束后，将新期数据合并到现有档案

## 输入
1. 新期的 `session-{n}-aligned.json` 和 `session-{n}-raw.json`
2. 现有档案目录 `docs/member-profiles/*.md`
3. 现有索引 `docs/member-profiles/index.json`

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
- 不对行业描述的差异做主动合并（如"芯片"与"新电工程师"并存是正常现象，可能源于 ASR 识别差异或自述角度不同）

### 3. 不处理的情况

以下情况**保持原样，不做特殊合并逻辑**：
- `industry` / `role` frontmatter 字段：保留首次出现的值，后续期不更新
- `aliases`：首次建立档案时写入，后续期发现的新 alias 才追加
- 跨期行业描述差异：不尝试智能合并（如"芯片"vs"新电"），保留各期原始表述
- 观点冲突：同一成员在不同期对同一话题的不同看法，**全部保留**，标注期数，体现观点演进

### 4. 索引更新

更新 `docs/member-profiles/index.json`：

```json
{
  "sessions": [
    {
      "session_id": "第十期",
      "date": "2026-04-26",
      "theme": "社群发展方向与项目规划讨论",
      "host": ["Eva"],
      "navigators": [],
      "participants": ["Shawn", "三金", "TX"],
      "essays_count": 10,
      "alignment_confidence": 0.92
    }
  ],
  "members_summary": {
    "total_unique": 35,
    "hosts": ["Eva"],
    "navigator_history": {
      "三金": ["第一期"],
      "薛晓杰": ["第九期"]
    }
  }
}
```

**更新规则**：
- `sessions`：按时间顺序追加新活动记录
- `members_summary.total_unique`：仅当新增成员时 +1
- `members_summary.navigator_history`：如果新期有领航员，追加 `{nickname: [期数列表]}`

## 特殊处理

**Eva**：
- `canonical_name` 统一为 "Eva"
- `aliases` 包含 "伊娃"
- 所有期中 role 为 "主持人"
- 合并时确保 `roles` 中包含所有期的主持记录

**角色变化**：
- 某人从 "参与者" 变为 "领航员" 时，保留两条记录
- 格式：`{session: "第一期", role: "参与者"}` + `{session: "第五期", role: "领航员"}`

## 输出

- 更新后的 `docs/member-profiles/{canonical-name}.md`
- 更新后的 `docs/member-profiles/index.json`

## 错误处理
- 如果 `index.json` 不存在，创建新的索引文件
- 如果档案文件格式不符合预期，报告警告并尝试修复
