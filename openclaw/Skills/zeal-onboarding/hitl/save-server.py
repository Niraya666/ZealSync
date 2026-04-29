#!/usr/bin/env python3
"""
ZealSync HITL 本地保存服务
接收 POST 请求，将内容写入指定文件路径
零第三方依赖，仅使用 Python 标准库
"""

import http.server
import socketserver
import json
import sys
import os

# 文件路径从命令行参数传入
FILE_PATH = sys.argv[1] if len(sys.argv) > 1 else './USER.md'
# PORT=0 表示自动选择可用端口
PORT = 0


class SaveHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # 静默日志，避免干扰 skill 输出
        pass

    def do_POST(self):
        if self.path == '/save':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))

                content = data.get('content', '')

                # 确保目录存在
                dir_path = os.path.dirname(FILE_PATH)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)

                # 写入文件
                with open(FILE_PATH, 'w', encoding='utf-8') as f:
                    f.write(content)

                self._send_json(200, {'ok': True, 'path': FILE_PATH})
            except Exception as e:
                self._send_json(500, {'ok': False, 'error': str(e)})
            return

        self._send_json(404, {'ok': False, 'error': 'not found'})

    def do_OPTIONS(self):
        # CORS 预检
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))


def main():
    with socketserver.TCPServer(("", PORT), SaveHandler) as httpd:
        actual_port = httpd.server_address[1]
        # 输出端口信息，供 skill 解析
        print(f"SERVER_PORT:{actual_port}", flush=True)
        httpd.serve_forever()


if __name__ == '__main__':
    main()
