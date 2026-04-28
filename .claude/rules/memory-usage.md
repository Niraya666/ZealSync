# Memory 使用规范

## 记录时机

以下场景必须写入 memory：

- 发现坑点并解决后（技术陷阱、配置误区、工具限制）
- 确定某项技术决策不可行或需要调整方向时
- 完成某个 Phase 后的关键经验总结

## 记录格式

使用标准 memory 格式（参考 `.claude/` memory 系统）：

```markdown
---
name: <简短标识>
description: <一句话描述>
type: <project | feedback | user | reference>
---

- **问题**: 具体描述
- **解决**: 解决方案
- **适用场景**: 何时会再次遇到
```

## 记忆维护

- 定期 review memory 文件，删除过时或已失效的记录
- 同一问题的新发现优先更新现有 memory，避免重复
- project 类型的 memory 在 Phase 切换时必须重新评估时效性
