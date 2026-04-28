# Git 工作流规范

## 分支策略

- **main**: 稳定分支，仅接受经过 Review 的合并
- **develop**: 日常开发分支（默认工作分支）
- **feature/***: 功能分支，从 develop 切出
- **Phase-0/***: Phase-0 专属分支，当前默认在此类分支开发

## 提交规范

- 所有代码修改必须提交后再 push
- Commit message 使用英文，格式：`<type>: <subject>`
  - `feat`: 新功能
  - `fix`: 修复
  - `docs`: 文档
  - `refactor`: 重构
  - `chore`: 杂项
- 每次 commit 保持单一职责，禁止批量无关修改

## 推送要求

- 代码修改或新增功能后，必须执行 `git push`
- Push 前确保本地分支与远程同步，必要时先 pull
- 禁止 force push 到任何共享分支
