---
name: zeal-onboarding-init
description: ZealSync onboarding 环境初始化。检查 lark-cli 安装和认证状态，引导用户完成配置。
---

# ZealSync Onboarding — Init

## 职责

- 检查 `lark-cli` 是否已安装且可用
- 验证 OAuth 认证状态
- 如未配置，引导用户完成安装和授权

## 检查流程

### 1. CLI 安装检查

运行 `which lark-cli`：

- 成功 → 进入步骤 2
- 失败 → 引导安装：
  ```bash
  # 推荐安装方式（根据官方文档）
  npm install -g @larksuite/cli
  # 或
  brew install larksuite/tap/lark-cli
  ```
  提示用户手动执行安装命令，安装完成后重新触发。

### 2. 认证状态检查

运行 `lark-cli doctor`：

- `ok: true` 且 `tokenStatus: valid` → 认证有效
- 失败或 token 过期 → 引导授权：
  ```bash
  lark-cli auth login
  ```
  提示用户执行 `lark-cli auth login`，按照浏览器弹出的 OAuth 流程完成授权。

### 3. 权限确认

运行 `lark-cli auth status`，检查 scope 是否包含：

- `docs:document:read`
- `docs:document:write`
- `wiki:node:create`
- `drive:file:upload`

如缺少关键权限，提示用户重新授权（使用 `--force` 或删除配置后重新 login）。

### 4. 飞书账号校验

从 `lark-cli auth status` 输出中读取 `userName`：

- 向用户确认："检测到你的飞书账号是 **{userName}**，这是你加入社群时使用的账号吗？"
- 用户确认 → 通过
- 用户否认 → 提示切换账号：`lark-cli auth login --force`

## 输出

成功时返回：
```json
{
  "larkReady": true,
  "userName": "...",
  "userOpenId": "..."
}
```

失败时返回错误信息，不更新状态。

## 错误处理

- 安装失败：记录具体错误，建议用户查看 `https://open.feishu.cn/document/no_class/mcp-archive/feishu-cli-installation-guide.md`
- 授权失败：提示检查网络、浏览器是否弹出、是否选择了正确的企业/组织
- 权限不足：列出缺失的权限范围，提示重新授权
