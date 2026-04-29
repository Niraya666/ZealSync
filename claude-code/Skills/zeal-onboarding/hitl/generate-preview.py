#!/usr/bin/env python3
"""
ZealSync HITL 预览生成器
自动从 server log 读取实际端口，替换模板占位符，生成 HTML 预览文件。

用法:
    python3 generate-preview.py \
        --server-log /tmp/zeal-server-LZY.log \
        --user-md ./USER-profile/LZY/USER.md \
        --template ./hitl-template.html \
        --output ./USER-profile/LZY/hitl-preview.html
"""

import argparse
import re
from datetime import datetime


def parse_frontmatter(md_content):
    """解析 YAML frontmatter，返回 (frontmatter_dict, body)"""
    fm_match = re.match(r'^---\n(.*?)\n---\n+(.*)', md_content, re.DOTALL)
    if not fm_match:
        return {}, md_content
    
    fm_text = fm_match.group(1)
    body = fm_match.group(2)
    
    fm = {}
    for line in fm_text.split('\n'):
        if ':' in line and not line.startswith('#'):
            key, val = line.split(':', 1)
            fm[key.strip()] = val.strip()
    return fm, body


def parse_tags(tags_str):
    """解析 tags 字符串，返回 list"""
    if not tags_str:
        return []
    # 处理 [tag1, tag2] 或 "tag1", 'tag2' 格式
    cleaned = tags_str.strip().strip('[]')
    if not cleaned:
        return []
    tags = []
    for t in cleaned.split(','):
        t = t.strip().strip('"').strip("'")
        if t:
            tags.append(t)
    return tags


def read_server_port(log_path):
    """从 server log 文件读取实际端口"""
    try:
        with open(log_path, 'r') as f:
            log = f.read()
        match = re.search(r'SERVER_PORT:(\d+)', log)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def render_sections(body_md):
    """将 Markdown body 渲染为 HTML sections"""
    sections = []
    section_pattern = r'^# (.+?)\n(.*?)(?=\n# |\Z)'
    
    for match in re.finditer(section_pattern, body_md, re.DOTALL | re.MULTILINE):
        title = match.group(1).strip()
        content = match.group(2).strip()
        
        if title in ['Metadata & External Context']:
            content_html = f'<pre>{content}</pre>'
        else:
            content_html = content
            # Bold
            content_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content_html)
            # Lists
            content_html = re.sub(r'^- (.+)$', r'<li>\1</li>', content_html, flags=re.MULTILINE)
            content_html = re.sub(r'(<li>.+</li>\n?)+', r'<ul>\g<0></ul>', content_html, flags=re.DOTALL)
            # Links
            content_html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', content_html)
            # Paragraphs
            content_html = re.sub(r'\n\n+', '</p><p>', content_html)
            content_html = '<p>' + content_html + '</p>'
            content_html = content_html.replace('<p></p>', '')
        
        sections.append(f'<div class="section"><h2>{title}</h2><div>{content_html}</div></div>')
    
    return '\n'.join(sections)


def main():
    parser = argparse.ArgumentParser(description='ZealSync HITL Preview Generator')
    parser.add_argument('--server-log', required=True, help='Path to server log file')
    parser.add_argument('--user-md', required=True, help='Path to USER.md')
    parser.add_argument('--template', required=True, help='Path to hitl-template.html')
    parser.add_argument('--output', required=True, help='Output HTML path')
    args = parser.parse_args()
    
    # Read inputs
    with open(args.user_md, 'r') as f:
        md_content = f.read()
    
    with open(args.template, 'r') as f:
        template = f.read()
    
    # Parse frontmatter
    fm, body = parse_frontmatter(md_content)
    
    nickname = fm.get('name', 'User')
    description = fm.get('description', '')
    tags = parse_tags(fm.get('tags', ''))
    
    # Generate HTML components
    tags_html = ''.join(f'<span class="tag">{t}</span>' for t in tags)
    sections_html = render_sections(body)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Read actual server port
    actual_port = read_server_port(args.server_log)
    if not actual_port:
        print(f"WARNING: Could not read port from {args.server_log}, using fallback 8765")
        actual_port = '8765'
    else:
        print(f"Server port detected: {actual_port}")
    
    # Replace placeholders
    html = template
    html = html.replace('{{NICKNAME}}', nickname)
    html = html.replace('{{DESCRIPTION}}', description)
    html = html.replace('{{TIMESTAMP}}', timestamp)
    html = html.replace('{{TAGS_HTML}}', tags_html)
    html = html.replace('{{SECTIONS_HTML}}', sections_html)
    html = html.replace('{{RAW_MARKDOWN}}', md_content)
    html = html.replace('{{SERVER_PORT}}', actual_port)
    
    # Write output
    with open(args.output, 'w') as f:
        f.write(html)
    
    print(f"Preview generated: {args.output}")


if __name__ == '__main__':
    main()
