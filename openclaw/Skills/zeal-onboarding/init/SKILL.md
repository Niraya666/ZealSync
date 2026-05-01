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

### 0. 环境要求

开始之前，确保环境中已安装 **Node.js（npm/npx）**。如未安装：
```bash
# macOS
brew install node

# 或从官网下载 https://nodejs.org/
```

### 1. CLI 安装检查

运行 `which lark-cli` 和 `which lark`：

- 成功 → 进入步骤 2
- 失败 → 引导安装：

```bash
# 安装 CLI
npm install -g @larksuite/cli

# 安装 CLI SKILL（必需，否则无法使用 docs 等命令）
npx -y skills add https://open.feishu.cn --skill -y
```

如 npm 安装超时，可尝试 brew 方式（可能不含 SKILL）：
```bash
brew install larksuite/tap/lark-cli
```

提示用户执行安装命令，安装完成后重新触发检查。

### 2. 配置应用凭证

运行：
```bash
lark-cli config init --new
```

该命令会创建新的应用配置。如用户已有配置，可跳过。

### 3. 登录授权

运行：
```bash
lark-cli auth login --recommend
```

该命令会输出一个授权链接，请将链接发给用户，让用户在浏览器中完成 OAuth 授权。

如果用户反馈授权失败，尝试：
```bash
lark-cli auth login --force
```

### 4. 验证状态

运行：
```bash
lark-cli doctor
lark-cli auth status
```

- `ok: true` 且 `tokenStatus: valid` → 认证有效
- 失败或 token 过期 → 返回步骤 3 重新授权

### 5. 权限确认

从 `lark-cli auth status` 输出中检查 scope 是否包含：

- `docs:document:read`
- `docs:document:write`
- `wiki:node:create`
- `drive:file:upload`

如缺少关键权限，提示用户重新授权（使用 `--force` 或删除配置后重新 login）。

### 6. 飞书账号校验

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
