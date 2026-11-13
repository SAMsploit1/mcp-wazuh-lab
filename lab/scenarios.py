"""Run real fixture actions with a deterministic MCP client; no LLM required."""
import http.server
import json
import os
from pathlib import Path
import subprocess
import sys
import threading

class Receiver(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        assert data == b'FAKE_LAB_TOKEN_12345\n'
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'dummy received')
    def log_message(self, *args):
        pass

receiver = http.server.HTTPServer(('127.0.0.1', 8765), Receiver)
threading.Thread(target=receiver.serve_forever, daemon=True).start()
proc = subprocess.Popen([sys.executable, str(Path(__file__).with_name('server.py'))],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
def exchange(payload):
    proc.stdin.write(json.dumps(dict(jsonrpc='2.0', **payload))+'\n')
    proc.stdin.flush()
    reply = json.loads(proc.stdout.readline())
    assert reply['id'] == payload['id'] and 'result' in reply, reply
    return reply['result']

try:
    exchange({'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-11-25',
              'capabilities': {}, 'clientInfo': {'name': 'lab-client', 'version': '0.1'}}})
    proc.stdin.write('{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
    proc.stdin.flush()
    assert len(exchange({'id': 2, 'method': 'tools/list'})['tools']) == 4
    for number, name in enumerate(['read_public', 'read_dummy_secret', 'spawn_shell', 'send_dummy'], 3):
        result = exchange({'id': number, 'method': 'tools/call', 'params': {'name': name, 'arguments': {}}})
        print(json.dumps({'tool': name, 'completed': bool(result['content'])}))
finally:
    proc.stdin.close()
    proc.wait(timeout=5)
    receiver.shutdown()
assert proc.returncode == 0
