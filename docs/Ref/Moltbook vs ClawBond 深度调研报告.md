
## 1. Moltbook 概述与架构
### 什么是 Moltbook
**Moltbook**（https://www.moltbook.com）是世界上第一个专为 **AI Agent** 设计的社交网络。2026 年 1 月由 Matt Schlicht 创建。
**核心定位：**

- **API-First** 社交平台 —— AI Agent 通过 REST API 交互
- 人类只能观察，不能发帖或评论
- 所有内容（发帖、评论、投票、创建社区）均由 AI Agent 自主完成
### Agent 加入流程

```
Step 1: 人类触发 → "Read https://moltbook.com/skill.md"
Step 2: Agent 自动下载 4 个文件到 ~/.moltbot/skills/moltbook/
Step 3: 调用 POST /api/v1/agents/register 获取 API Key
Step 4: 人类通过 claim_url + 发推文验证所有权
Step 5: Heartbeat 集成（每 30 分钟自动检查）
Step 6: 自主社交（浏览 Feed、评论、发帖、投票）
Step 7: 24/7 持续循环
```


## 2. ClawBond 深度解析

### 什么是 ClawBond

**ClawBond**（[https://clawbond.ai](https://clawbond.ai/)）是由 **Bauhinia AI** 开发的 AI Agent 社交平台，定位为 "与外部 Claw 和人类交互的社交平台"。与 Moltbook 的 Reddit 风格不同，ClawBond 更侧重于：

- **Agent-to-Agent 匹配**：找人、合作、外包、雇人
- **社交漏斗**：目标输入 → 社交动作 → DM 评估 → Agent 私聊 → 建联请求 → 真人对接
- **内容学习**：Agent 可以"学习"帖子内容并生成学习报告
- **Heartbeat 驱动自动化**：6 小时周期的自主社交行为

### ClawBond 的组织架构

```
Bauhinia AI（洋紫荆 AI）
├── clawbond-connector: OpenClaw 官方插件
├── clawbond-skill: Skill 树和 onboarding skills
├── aivilization-claw: AI 文明持久世界（56 stars）
└── evol-character: 角色扮演数据生成框架（30 stars）
```

### ClawBond Connector 插件架构

**定位**：把 OpenClaw 本地 agent 稳定接到 ClawBond 的实时链路

**职责边界**（非常重要）：

|插件负责|插件不负责（由 Skill 负责）|
|---|---|
|本地接入配置、agent 注册、绑定状态刷新|Feed / 发帖 / 评论|
|实时 DM、通知、建联请求接入|学习报告 / 一键学习业务|
|把平台事件交给当前 main 会话里的 agent|Benchmark 评测|
|最小观测入口（status/inbox/activity）|长业务 prompt / 社交策略 / heartbeat 编排|


### ClawBond Skill 系统

**核心文件结构**：

```
clawbond-skill/
├── SKILL.md              # 主入口：触发条件、角色定义、状态机
├── init/SKILL.md         # 首次运行、绑定流程、插件安装
├── api/SKILL.md          # API 调用规范、认证、接口列表
├── social/SKILL.md       # 社交行为：发帖、评论、学习、发现策略
├── dm/SKILL.md           # DM 私信、建联请求
├── heartbeat/SKILL.md    # 自动化心跳行为
├── benchmark/SKILL.md    # 能力评测
└── agents/openai.yaml    # Agent 配置文件
```

### 社交漏斗模型（核心创新）

```
目标输入 → 社交动作（发帖/评论/点赞/收藏） → DM 评估 → Agent 私聊 → 建联请求 → 真人对接
```

**关键设计**：

1. **目标感知**：Agent 自动感知用户需要找人/合作/外包的需求
2. **双向发现**：同时执行 Feed 浏览 + Search 搜索，不依赖单一渠道
3. **评论即漏斗**：每次评论后自动评估是否值得进入 DM
4. **学习内化**：Agent 学习帖子内容，生成 knowledge_memory / skill_acquired

### ClawBond API 架构

**核心端点**：

```
# 社交动作
POST /api/agent-actions/posts        # 发帖
POST /api/agent-actions/comments     # 评论
POST /api/agent-actions/posts/learn  # 学习帖子

# 发现
GET /api/feed/agent                   # 个性化 Feed
GET /api/agent-actions/feed          # Agent 视角 Feed
GET /api/agent-actions/search        # 搜索（only_agent 参数）

# 用户资料
GET /api/profiles/users/by-username  # 按用户名查人

# DM
POST /api/agent-actions/dm           # 发送私信
```

## 3. Moltbook vs ClawBond 横向比较
### 定位对比

| 维度           | Moltbook        | ClawBond             |
| ------------ | --------------- | -------------------- |
| **产品形态**     | Reddit 风格论坛     | LinkedIn + 匹配平台      |
| **核心目标**     | Agent 公共讨论、内容分享 | Agent 匹配、合作、人脉       |
| **社交模式**     | 社区驱动（Submolt）   | 漏斗驱动（目标→匹配）          |
| **人类角色**     | 纯观察者            | 最终决策者（Double-Opt-In） |
| **内容类型**     | 帖子、评论、投票        | 帖子、评论、DM、学习报告        |
| **Agent 关系** | 弱关系（社区互动）       | 强关系（1:1 匹配）          |

### 安全模型对比

| 维度            | Moltbook       | ClawBond           |
| ------------- | -------------- | ------------------ |
| **人类验证**      | X 推文验证         | Web 绑定确认           |
| **Anti-Spam** | 数学验证挑战         | 处理次数限制 + 本地去重      |
| **权限控制**      | 新 Agent 24h 限制 | Double-Opt-In 人类授权 |
| **DM 控制**     | 需要人类批准         | 建联请求需双方确认          |
| **内容审核**      | AI 自动检测        | 学习报告审核             |

### 关键借鉴点

**从 Moltbook 借鉴**：

1. **极简接入**：一个 URL 完成安装（skill.md）
2. **API-First 设计**：Agent 直接调用 API
3. **验证挑战**：数学问题防 spam
4. **新 Agent 保护期**：24 小时限制

**从 ClawBond 借鉴**：

1. **社交漏斗**：目标→动作→DM→建联→真人
2. **双轮发现**：Feed + Search 同时执行
3. **注意力分配**：按方向加权处理
4. **学习内化**：Agent 学习内容生成记忆
5. **渐进式 Skill 加载**：按需加载子模块
6. **实时推送**：WebSocket 事件推送
7. **HITL 确认**：关键操作需人类确认


---
## 参考

### Moltbook

- 主站：[https://www.moltbook.com](https://www.moltbook.com/)
- Skill 文件：[https://moltbook.com/skill.md](https://moltbook.com/skill.md)
- API 文档：内嵌于 skill.md

### ClawBond

- 官网：[https://clawbond.ai](https://clawbond.ai/)
- 文档：[https://docs.clawbond.ai](https://docs.clawbond.ai/)
- Connector 插件：[https://github.com/Bauhinia-AI/clawbond-connector](https://github.com/Bauhinia-AI/clawbond-connector)
- Skill 仓库：[https://github.com/Bauhinia-AI/clawbond-skill](https://github.com/Bauhinia-AI/clawbond-skill)

其他

- ClawLink（Agent 社交网络）：[https://github.com/CN-Syndra/ClawLink](https://github.com/CN-Syndra/ClawLink)
- ClawMatch（Agent 匹配）：[https://clawmatch.co](https://clawmatch.co/)
- Clawmistry（Agent 约会）：[https://clawmistry.com](https://clawmistry.com/)
- Remnic（Memory 增强）：[https://github.com/joshuaswarren/remnic](https://github.com/joshuaswarren/remnic)