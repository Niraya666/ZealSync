#!/usr/bin/env python3
"""批量上传 .md 文件到飞书云盘，上传前将 YAML frontmatter 转换为 Markdown 表格。标准库 only。"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time

frontmatter_re = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)


def parse_frontmatter(yaml_text):
    """简单解析 YAML key-value，返回 [(key, value), ...]。"""
    items = []
    for line in yaml_text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        # 去掉引号
        if len(value) >= 2:
            if (value[0] == '"' and value[-1] == '"') or \
               (value[0] == "'" and value[-1] == "'"):
                value = value[1:-1]
        # 列表 [a, b, c] → a、b、c
        if value.startswith('[') and value.endswith(']'):
            inner = value[1:-1]
            parts = [p.strip().strip('"').strip("'") for p in inner.split(',')]
            value = '、'.join(parts)
        items.append((key, value))
    return items


def frontmatter_to_table(content):
    """将 YAML frontmatter 转换为 Markdown 表格，返回转换后的全文。"""
    m = frontmatter_re.match(content)
    if not m:
        return content

    items = parse_frontmatter(m.group(1))
    if not items:
        return content[m.end():].strip()

    rows = [f"| {k} | {v} |" for k, v in items]
    table = "| 属性 | 内容 |\n|------|------|\n" + "\n".join(rows)
    body = content[m.end():].strip()
    return table + "\n\n" + body


def upload_file(file_path, folder_token):
    """上传单个文件到云盘，返回 (ok, file_token_or_error)。"""
    result = subprocess.run(
        ["lark-cli", "drive", "+upload",
         "--folder-token", folder_token,
         "--file-path", file_path],
        capture_output=True, text=True
    )
    # lark-cli 输出可能包含前缀文本，尝试从最后一行解析 JSON
    lines = result.stdout.strip().splitlines()
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if data.get("ok"):
                return True, data.get("data", {}).get("file_token", "")
            return False, data.get("error", {}).get("message", line)
        except json.JSONDecodeError:
            continue
    return False, result.stdout or result.stderr


def main():
    parser = argparse.ArgumentParser(description="Upload member profile .md files to Lark drive")
    parser.add_argument("--md-dir", required=True, help="Directory containing .md files")
    parser.add_argument("--folder-token", required=True, help="Target folder token")
    parser.add_argument("--delay", type=float, default=1.2, help="Delay between uploads (seconds)")
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary converted files")
    args = parser.parse_args()

    md_files = sorted([
        f for f in os.listdir(args.md_dir)
        if f.endswith(".md") and f != "index.md"
    ])

    ok_count = 0
    fail_count = 0

    for filename in md_files:
        name = filename[:-3]  # strip .md
        orig_path = os.path.join(args.md_dir, filename)

        # 读取原始文件并转换 frontmatter
        with open(orig_path, "r", encoding="utf-8") as f:
            content = f.read()
        converted = frontmatter_to_table(content)

        # 写入临时文件
        tmp_fd, tmp_path = tempfile.mkstemp(prefix=f"zeal-lark-{name}-", suffix=".md")
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            f.write(converted)

        ok, info = upload_file(tmp_path, args.folder_token)
        if ok:
            print(f"OK:{name}:{info}")
            ok_count += 1
        else:
            # retry once
            time.sleep(2)
            ok, info = upload_file(tmp_path, args.folder_token)
            if ok:
                print(f"OK:{name}:{info}")
                ok_count += 1
            else:
                print(f"FAIL:{name}:{info}")
                fail_count += 1

        # 清理临时文件（除非 --keep-temp）
        if not args.keep_temp:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

        time.sleep(args.delay)

    print(f"\nSUMMARY:ok={ok_count}:fail={fail_count}:total={len(md_files)}", file=sys.stderr)
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
