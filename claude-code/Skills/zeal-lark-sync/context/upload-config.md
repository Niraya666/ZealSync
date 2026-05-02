# 飞书同步配置

## 说明

本文件记录 zeal-lark-sync Skill 运行所需的配置信息。

**重要**：Skill 的 INIT 阶段会自动尝试获取缺失的 token。Agent 会运行
`lark-cli` 命令创建云盘文件夹和 Base，并提取 token 写入本文件。
**仅在自动获取失败时才需要手动填写**。

## 配置项

| 配置项 | 说明 | 状态 |
|--------|------|------|
| `folder_token` | 云盘文件夹 token | 自动获取 |
| `base_token` | 多维表格 Base token | 自动获取 |
| `members_table_id` | 成员总表 ID | 自动获取或手动创建 |
| `sessions_table_id` | 活动记录表 ID | 自动获取或手动创建 |
| `drive_base_url` | 云盘文件 URL 前缀 | 固定值 |

## 自动获取命令参考

```bash
# 1. 创建云盘文件夹
lark-cli drive folder create --name "成员档案备份" --parent-position my_library
# 从 JSON 输出提取 folder_token

# 2. 创建多维表格 Base
lark-cli base +base-create --name "社群成员档案"
# 从 JSON 输出提取 base_token

# 3. 列出已有表
lark-cli base +table-list --base-token <BASE_TOKEN>
# 提取 members_table_id 和 sessions_table_id
```

## 当前配置

```yaml
folder_token: "YOUR_FOLDER_TOKEN"
base_token: "YOUR_BASE_TOKEN"
members_table_id: "tblXXXXXXXX"
sessions_table_id: "tblYYYYYYYY"
drive_base_url: "https://ecn7o2uqwaxt.feishu.cn/file"
```
