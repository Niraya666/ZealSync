# zeal-mining

## 触发条件

当用户需要以下操作时触发本 Skill：
- "挖掘社群历史纪要中的成员信息"
- "从会议纪要中提取成员画像"
- "对齐小作文和会议纪要中的人名"
- "生成成员档案"
- "汇总活动参与记录"
- "分析社群成员数据"

## 概述

本 Skill 将分散在 ZealSync 社群历史活动记录中的成员信息挖掘出来，对齐到统一的命名空间，生成可累积的个人档案和活动汇总表。

**数据来源**：
- 好物分享汇总（`.docs/内容回顾/张江-星辰大海Coffee_Chat内容回顾.md`）：成员小作文 + 好物推荐
- AI 会议纪要（`.docs/内容回顾/会议纪要/第X期_*.md`）：参会人员介绍 + 智能章节发言记录

**核心挑战**：
- 小作文中的 `@昵称-行业-岗位` 与纪要中的实名/说话人编号不对齐
- 同一人在不同期可能使用不同行业描述
- 纪要中说话人只有编号，需通过内容推断身份

**设计原则**：
- 全部 Agent 驱动，无脚本
- canonical_name 采用小作文中的微信群昵称
- 纪要实名作为 `aliases`
- 支持一次性初始化（全量）和增量更新（每期后自动追加）

## 状态机

```
[INIT] → [EXTRACT] → [ALIGN] → [PROFILE] → [MERGE] → [DONE]
           ↑___________________________|
           (增量更新时，从 MERGE 回到 EXTRACT 处理下一期)
```

### 状态说明

| 状态 | 说明 | 输入 | 输出 |
|------|------|------|------|
| INIT | 确定处理范围（全量/增量） | 用户指令 | 待处理的期数列表 |
| EXTRACT | 提取结构化数据 | 原始 Markdown | `session-{n}-raw.json` |
| ALIGN | 身份对齐 | `session-{n}-raw.json` | `session-{n}-aligned.json` |
| PROFILE | 生成档案 | 对齐结果 + 原始数据 | `{canonical-name}.md` |
| MERGE | 合并到索引 | 档案 + 现有索引 | 更新后的 `index.json` |
| DONE | 完成 | - | 最终报告 |

## 流程编排

### 初始化模式（全量处理）

```
1. 识别所有待处理期数（从 .docs/内容回顾/会议纪要/ 目录下扫描）
2. FOR each 期数 IN [第一期, ..., 第十期]:
   a. 调用 Extract Agent → 生成 session-{n}-raw.json
   b. 调用 Align Agent → 生成 session-{n}-aligned.json
   c. 调用 Profile Agent → 生成/更新各成员档案
   d. 调用 Merge Agent → 更新 index.json
3. 生成最终报告（总成员数、对齐置信度、不确定案例列表）
```

### 增量模式（单期追加）

```
1. 确定新期数（从用户输入或最新纪要文件推断）
2. 调用 Extract Agent → 生成 session-{n}-raw.json
3. 调用 Align Agent → 生成 session-{n}-aligned.json
4. FOR each canonical_name IN aligned结果:
   a. 检查档案是否存在
   b. 存在 → Merge Agent 追加更新
   c. 不存在 → Profile Agent 生成新档案
5. Merge Agent 更新 index.json
6. 生成增量报告（新增成员、更新成员、不确定案例）
```

## 子 Skill 调用

### Extract Agent

```
调用条件：进入 EXTRACT 状态
输入：
  - .docs/内容回顾/张江-星辰大海Coffee_Chat内容回顾.md（对应期数的小作文段落）
  - .docs/内容回顾/会议纪要/第{n}期_*.md（纪要全文）
输出：
  - docs/member-profiles/session-{n}-raw.json
说明：参见 extract/SKILL.md
```

### Align Agent

```
调用条件：EXTRACT 完成后进入 ALIGN 状态
输入：
  - docs/member-profiles/session-{n}-raw.json
输出：
  - docs/member-profiles/session-{n}-aligned.json
说明：参见 align/SKILL.md。采用多 Agent Loop（Extractor→Matcher→Verifier→Judge）
```

### Profile Agent

```
调用条件：ALIGN 完成后进入 PROFILE 状态
输入：
  - docs/member-profiles/session-{n}-aligned.json
  - docs/member-profiles/session-{n}-raw.json
输出：
  - docs/member-profiles/{canonical-name}.md
说明：参见 profile/SKILL.md。复用 ZealSync USER.md 范式
```

### Merge Agent

```
调用条件：PROFILE 完成后进入 MERGE 状态
输入：
  - 新生成的/更新的档案文件
  - 现有 docs/member-profiles/index.json
输出：
  - 更新后的 docs/member-profiles/index.json
  - 更新后的档案文件
说明：参见 merge/SKILL.md
```

## 输出规范

### 个人档案路径

```
docs/member-profiles/
├── index.json                    # 活动汇总表和成员统计
├── Shawn.md                      # 成员个人档案
├── 三金.md
├── TX.md
├── Eva.md
└── ...
```

### 中间产物路径

```
docs/member-profiles/
├── session-第十期-raw.json       # Extract 输出
├── session-第十期-aligned.json   # Align 输出
├── session-第九期-raw.json
├── session-第九期-aligned.json
└── ...
```

### 档案命名规则

- 文件名使用 canonical_name（小作文昵称）
- 英文名保留原样：`Shawn.md`, `TX.md`, `Eva.md`
- 中文名保留原样：`三金.md`, `薛晓杰.md`
- 特殊符号处理：`&.md`（如 `&`）

## 增量更新触发

每期新活动结束后，可通过以下方式触发增量更新：
1. 用户明确指令："更新第X期数据"
2. 检测到新的纪要文件：`.docs/内容回顾/会议纪要/第{n}期_*.md`
3. 检测到新的小作文：`.docs/内容回顾/张江-星辰大海Coffee_Chat内容回顾.md` 有新期段落

## 质量检查清单

每完成一期处理，检查：
- [ ] 所有小作文中的昵称都有对应的 canonical_name
- [ ] 所有说话人都有映射（或明确标记为 UNCERTAIN）
- [ ] 主持人（Eva）已正确识别
- [ ] 领航员已正确识别
- [ ] 档案中包含 Identity + Activity History
- [ ] 好物分享已提取并分类
- [ ] index.json 已更新

## 注意事项

1. **Eva 特殊处理**：Eva 在所有期中都是主持人，aliases 包含 "伊娃"
2. **多期成员**：如三金参与多期，档案中保留所有期的 Activity History
3. **角色变化**：某人可能从参与者变为领航员，保留历史角色记录
4. **不确定案例**：低置信度映射标记为 UNCERTAIN，不生成档案或生成低置信度档案
5. **文件编码**：所有输出使用 UTF-8，中文内容保留原样
