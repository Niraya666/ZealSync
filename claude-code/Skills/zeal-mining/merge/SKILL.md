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
- 按以下规则追加/更新：

### 2. 追加规则

```
现有档案 ← 新期数据
```

**frontmatter 更新**：
```yaml
sessions_count: {原值 + 1}
roles:
  - {追加新角色记录}
```

**Activity History**：
- 在表格末尾追加新行
- 保持时间倒序或正序一致

**Core Views**：
- 在 "## Core Views" section 末尾追加新观点
- 标注期数和主题

**Reviews & Interactions**：
- "主动提及他人"：追加新期提及记录
- "被他人提及"：追加新期被提及记录

**Favorites**：
- 检查是否已存在（去重）
- 如果不存在，追加到列表
- 保留期数标注

### 3. 索引更新

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
- `sessions`：追加新活动记录
- `members_summary.total_unique`：如果新增成员，+1
- `members_summary.navigator_history`：如果新期有领航员，追加记录

### 4. 特殊处理

**Eva 的合并**：
- Eva 在所有期中都是主持人
- 合并时确保 `roles` 中包含所有期的主持记录
- `aliases` 中包含 "伊娃"

**角色变更**：
- 某人从 "参与者" 变为 "领航员" 时，保留历史角色记录
- 格式：`{session: "第X期", role: "参与者"}` → `{session: "第Y期", role: "领航员"}`

**别名合并**：
- 如果新期发现某 canonical_name 的新 alias，追加到 `aliases` 列表
- 例如：第一期 "三金" 无 alias，后续期发现纪要中叫 "三金" 但背景不同，不新增 alias

## 输出

- 更新后的 `docs/member-profiles/{canonical-name}.md`
- 更新后的 `docs/member-profiles/index.json`

## 错误处理
- 如果 `index.json` 不存在，创建新的索引文件
- 如果档案文件格式不符合预期，报告警告并尝试修复
