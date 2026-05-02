#!/usr/bin/env python3
"""批量导入成员档案到飞书多维表格。标准库 only。

核心机制：
1. 解析 index.json 和 .md 文件
2. 将 batch create payload 写入临时文件（避免换行截断）
3. 通过 $(cat file) 方式调用 lark-cli
4. 自动分批 + sleep 限流保护
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time

frontmatter_re = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)


def read_md_body(md_dir, name):
    """读取 .md 文件正文（去掉 frontmatter）。"""
    path = os.path.join(md_dir, f"{name}.md")
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    m = frontmatter_re.match(content)
    if m:
        return content[m.end():].strip()
    return content.strip()


def batch_create(base_token, table_id, fields, rows, batch_idx):
    """执行一批 batch create，返回 (ok, info)。

    关键：将 JSON 写入临时文件，通过 $(cat file) 中转给 lark-cli，
    避免 subprocess 传参时换行符被截断。
    """
    payload = {"fields": fields, "rows": rows}
    tmp_path = f"/tmp/zeal-lark-sync-batch-{batch_idx}.json"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)

    cmd = (
        f'lark-cli base +record-batch-create '
        f'--base-token {base_token} '
        f'--table-id {table_id} '
        f'--json "$(cat {tmp_path})"'
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # lark-cli 输出可能包含前缀，尝试从所有行中找 JSON
    lines = result.stdout.strip().splitlines()
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if data.get("ok"):
                return True, len(data.get("data", {}).get("data", []))
            return False, data.get("error", {}).get("message", line)
        except json.JSONDecodeError:
            continue
    return False, result.stdout or result.stderr


def import_members(base_token, table_id, index_path, md_dir, file_map, drive_base_url):
    """导入成员数据。"""
    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    member_fields = [
        "昵称", "行业", "岗位", "标签", "参与期数",
        "首次参与", "最近参与", "角色历史", "置信度",
        "档案文档", "原始文件", "档案内容"
    ]

    rows = []
    for m in data.get("members", []):
        name = m.get("canonical_name", "")
        file_token = file_map.get(name, "")
        file_url = f"{drive_base_url}/{file_token}" if file_token else ""
        body = read_md_body(md_dir, name)
        tags_str = "、".join(m.get("tags", []))
        roles = ";".join(f"{k}:{v}" for k, v in m.get("session_roles", {}).items())
        rows.append([
            name,
            m.get("industry", ""),
            m.get("role", ""),
            tags_str,
            m.get("session_count", 0),
            m.get("first_session", ""),
            m.get("last_session", ""),
            roles,
            m.get("alignment_confidence", ""),
            "",  # 档案文档 — 可选，由外部回填
            file_url,
            body,
        ])

    batch_size = 5
    total_ok = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        ok, info = batch_create(base_token, table_id, member_fields, batch, i // batch_size)
        if ok:
            total_ok += info
            print(f"批次 {i // batch_size + 1}: 成功 {info} 条")
        else:
            print(f"批次 {i // batch_size + 1}: 失败 — {info}")
            break
        time.sleep(5)

    print(f"\n总计导入: {total_ok}/{len(rows)}")
    return 0 if total_ok == len(rows) else 1


def import_sessions(base_token, table_id, index_path):
    """导入活动记录数据。"""
    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    session_fields = [
        "期数", "日期", "主题", "参与人数",
        "领航员", "主持人", "状态"
    ]

    rows = []
    for s in data.get("sessions", []):
        rows.append([
            s.get("phase", ""),
            s.get("date", ""),
            s.get("topic", ""),
            s.get("participants_count", 0),
            s.get("navigator", ""),
            s.get("host", ""),
            "已处理",
        ])

    if not rows:
        print("没有活动记录需要导入")
        return 0

    # 活动记录通常不超过 20 条，无需分批
    ok, info = batch_create(base_token, table_id, session_fields, rows, 0)
    if ok:
        print(f"活动记录导入成功: {info} 条")
        return 0
    else:
        print(f"活动记录导入失败: {info}")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Import member profiles to Lark Base")
    parser.add_argument("--base-token", required=True)
    parser.add_argument("--members-table", help="Members table ID")
    parser.add_argument("--sessions-table", help="Sessions table ID")
    parser.add_argument("--index", required=True, help="Path to index.json")
    parser.add_argument("--md-dir", default="docs/member-profiles", help="Directory of .md files")
    parser.add_argument("--file-map", default="", help='JSON string of {"name": "file_token"}')
    parser.add_argument("--drive-base-url", default="https://ecn7o2uqwaxt.feishu.cn/file", help="Drive file URL prefix")
    parser.add_argument("--import-sessions", action="store_true", help="Import sessions instead of members")
    args = parser.parse_args()

    file_map = {}
    if args.file_map:
        try:
            file_map = json.loads(args.file_map)
        except json.JSONDecodeError:
            print(f"无效的 file-map JSON: {args.file_map}", file=sys.stderr)
            return 1

    if args.import_sessions:
        if not args.sessions_table:
            print("--sessions-table 必填", file=sys.stderr)
            return 1
        return import_sessions(args.base_token, args.sessions_table, args.index)
    else:
        if not args.members_table:
            print("--members-table 必填", file=sys.stderr)
            return 1
        return import_members(
            args.base_token, args.members_table,
            args.index, args.md_dir, file_map, args.drive_base_url
        )


if __name__ == "__main__":
    sys.exit(main())
