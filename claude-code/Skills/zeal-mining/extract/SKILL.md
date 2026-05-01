# Extract Agent — 数据提取

## 触发条件
当主 Skill 需要处理某一期活动时，调用本 Agent。

## 输入
1. 好物分享汇总文档中对应期数的小作文段落
2. 会议纪要全文

**上下文**：运行前读取 `context/community-rules.md` 了解社群特定的格式规范和数据源路径。

## 任务

### 1. 提取小作文数据

从小作文段落中，逐人提取：

```json
{
  "essays": [
    {
      "nickname": "{昵称}",
      "industry": "{行业}",
      "role": "{岗位}",
      "raw_header": "@{昵称}-{行业}-{岗位}",
      "content": "完整小作文正文",
      "favorites": ["好物1", "好物2"],
      "mentions": ["提及的人名1", "提及的人名2"]
    }
  ]
}
```

**提取规则**：
- `@昵称-行业-岗位：` → 拆分为 nickname + industry + role
- `@昵称：`（无行业岗位）→ industry 和 role 为空字符串
- `@昵称（备注）：` → nickname 为昵称部分，备注信息放入 `notes`
- 好物分享：从 `- 好物分享：` 后提取，支持多行列表
- 提及他人：匹配正文中 `@` 开头的人名、直呼全名、或 "感谢XX"、"提到XX" 等表达

### 2. 提取会议纪要数据

从纪要全文中提取：

```json
{
  "attendees": [
    {
      "name": "{实名}",
      "background": "背景描述",
      "role_hint": "host|navigator|participant",
      "self_intro_text": "完整的自我介绍段落"
    }
  ],
  "speakers": [
    {
      "speaker_id": "说话人{N}",
      "chapters": [
        {
          "timestamp": "00:01",
          "title": "章节标题",
          "content": "完整的章节转录内容"
        }
      ]
    }
  ],
  "decisions": ["决策描述1"],
  "quotes": [
    {
      "text": "金句内容",
      "speaker_id": "说话人X",
      "context": "解读或上下文"
    }
  ]
}
```

**提取规则**：
- **参会人员介绍**：在 "参会人员自我介绍" 或 "个人介绍与产品推荐" 板块下，逐人提取 name + background
- **角色识别**（参考 context/community-rules.md）：
  - 主持人：从纪要开头查找 "主持人"、"[主持人姓名] 开场" 等表述，或议程中明确标注
  - 领航员：查找 "领航员" + 人名
  - 参与者：其余人员
- **说话人章节**：从 "智能章节" 板块下，按 `### 00:01  章节标题` 格式提取，每个说话人可能出现在多个章节
- **关键决策**：从 "关键决策" 板块提取
- **金句**：从 "金句时刻" 板块提取

### 3. 提取会话元数据

```json
{
  "session_id": "第X期",
  "date": "YYYY-MM-DD",
  "theme": "会议主题"
}
```

## 输出

将提取结果写入文件：`docs/member-profiles/session-{n}-raw.json`

**输出格式要求**：
- 必须使用合法的 JSON 格式
- 所有字符串使用 UTF-8 编码
- `content` 字段保留原始文本（含换行符转义）
- `chapters[].content` 保留完整章节文本

## 错误处理
- 如果小作文段落或纪要文件不存在，报告错误并终止
- 如果提取结果为空（如无参会人员），报告警告但继续
