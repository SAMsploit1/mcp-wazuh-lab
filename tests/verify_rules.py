"""Validate generated events and negative controls against real wazuh-logtest."""
import json
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[1]
events = [json.loads(line) for line in (root/'evidence/events.jsonl').read_text().splitlines()]
expected = {'read_public': None, 'read_dummy_secret': '110501', 'spawn_shell': '110502', 'send_dummy': '110503'}
assert [e['tool'] for e in events] == list(expected), 'Expected exactly four fresh scenario events'
cases = [(e['tool'], e, expected[e['tool']]) for e in events]
cases += [
    ('unrelated source', dict(integration='other', mcp_action='file_read', sensitive='yes'), None),
    ('ordinary process', dict(integration='mcp_lab', mcp_action='process_start', executable='/usr/bin/python3'), None),
    ('ordinary send', dict(integration='mcp_lab', mcp_action='network_send', sensitive='no'), None),
    ('missing sensitivity', dict(integration='mcp_lab', mcp_action='file_read'), None),
]
report = []
for name, event, wanted in cases:
    result = subprocess.run(['docker', 'compose', 'exec', '-T', 'manager',
                             '/var/ossec/bin/wazuh-logtest'], cwd=root,
                            input=json.dumps(event)+'\n', text=True, capture_output=True, timeout=30)
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert 'Phase 2' in output, output
    assert not re.search(r'ERROR|CRITICAL', output), output
    found = re.findall(r"id: '([0-9]+)'", output)
    matched = found[-1] if found else None
    passed = matched == wanted if wanted else matched not in {'110501', '110502', '110503'}
    report.append(dict(case=name, expected=wanted, actual=matched, passed=passed))
    (root/'evidence'/('logtest-'+name.replace(' ', '-')+'.txt')).write_text(output)
(root/'evidence/rule-results.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
assert all(row['passed'] for row in report), 'Rule regression detected'
