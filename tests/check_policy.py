"""Static XML/regex policy checks only; NOT a substitute for wazuh-logtest."""
from pathlib import Path
import re
import argparse
import json
import xml.etree.ElementTree as ET
from cases import regression_cases

root = Path(__file__).resolve().parents[1]
rules = ET.parse(root/'rules/mcp_rules.xml').getroot().findall('rule')
ids = [r.attrib['id'] for r in rules]
assert len(ids) == len(set(ids)) == 6
expected_mitre = {'110501': 'T1552.001', '110502': 'T1059.004', '110503': 'T1048', '110504': 'T1059.006', '110505': 'T1059.007'}
for rule in rules[1:]:
    assert rule.findtext('if_sid') == '110500'
    assert rule.findtext('mitre/id') == expected_mitre[rule.attrib['id']]
    assert all(field.attrib['name'] != 'sensitive' for field in rule.findall('field'))

def fields_match(rule, event):
    return all(field.attrib['name'] in event and re.search(field.text, event[field.attrib['name']]) for field in rule.findall('field'))

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--events', type=Path, help='Also check four freshly generated fixture events')
args = parser.parse_args()
cases = regression_cases()
if args.events:
    events = [json.loads(line) for line in args.events.read_text().splitlines()]
    expected = {'read_public': None, 'read_dummy_secret': '110501', 'spawn_shell': '110502', 'send_dummy': '110503'}
    assert [event['tool'] for event in events] == list(expected)
    assert all('sensitive' not in event for event in events)
    cases += [(event['tool'], event, expected[event['tool']]) for event in events]
for name, event, wanted in cases:
    matched = None
    if fields_match(rules[0], event):
        matches = [rule.attrib['id'] for rule in rules[1:] if fields_match(rule, event)]
        assert len(matches) <= 1, (name, matches)
        matched = matches[0] if matches else None
    assert matched == wanted, (name, wanted, matched)
print(f'{len(cases)} static policy checks passed; Wazuh engine validation still required.')
