"""Minimal deterministic MCP stdio fixture. Instrumentation is NOT kernel telemetry."""
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request

ROOT = Path(os.environ.get('LAB_ROOT', '/tmp/mcp-evidence-lab'))
ROOT.mkdir(parents=True, exist_ok=True)
(ROOT / 'public.txt').write_text('public example document\n')
(ROOT / '.env').write_text('FAKE_LAB_TOKEN_12345\n')
EVENTS = Path(os.environ.get('LAB_EVENTS', str(ROOT / 'events.jsonl')))

def event(action, **fields):
    with EVENTS.open('a') as stream:
        stream.write(json.dumps(dict(integration='mcp_lab', mcp_action=action, **fields)) + '\n')

def call(name):
    if name in ('read_public', 'read_dummy_secret'):
        sensitive = name == 'read_dummy_secret'
        path = ROOT / ('.env' if sensitive else 'public.txt')
        result = path.read_text()
        event('file_read', tool=name, path=str(path.resolve()))
        return result
    if name == 'spawn_shell':
        result = subprocess.check_output(['/bin/sh', '-c', 'printf lab-child-process'], text=True)
        event('process_start', tool=name, executable='/bin/sh', argument1='-c')
        return result
    if name == 'send_dummy':
        data = (ROOT / '.env').read_bytes()
        # Fixed loopback destination; never accepts arbitrary URLs or file paths.
        request = urllib.request.Request('http://127.0.0.1:8765', data=data, method='POST')
        with urllib.request.urlopen(request, timeout=3) as response:
            result = response.read().decode()
        event('network_send', tool=name, destination='127.0.0.1', source_path=str((ROOT / '.env').resolve()), bytes=len(data))
        return result
    raise ValueError('Unknown tool')

TOOLS = ['read_public', 'read_dummy_secret', 'spawn_shell', 'send_dummy']
for line in sys.stdin:
    try:
        request = json.loads(line)
        method = request.get('method')
        if 'id' not in request:
            continue
        if method == 'initialize':
            result = dict(protocolVersion='2025-11-25', capabilities={'tools': {}},
                          serverInfo={'name': 'mcp-evidence-fixture', 'version': '0.1.0'})
        elif method == 'tools/list':
            result = {'tools': [dict(name=name, description='Isolated lab fixture: '+name,
                                    inputSchema={'type': 'object', 'properties': {}, 'additionalProperties': False})
                                for name in TOOLS]}
        elif method == 'tools/call':
            result = {'content': [{'type': 'text', 'text': call(request['params']['name'])}]}
        else:
            print(json.dumps({'jsonrpc': '2.0', 'id': request['id'],
                              'error': {'code': -32601, 'message': 'Method not found'}}), flush=True)
            continue
        print(json.dumps({'jsonrpc': '2.0', 'id': request['id'], 'result': result}), flush=True)
    except Exception as error:
        print(str(error), file=sys.stderr, flush=True)
        raise
