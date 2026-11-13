# Recorded run: 13 November 2026

Wazuh 4.14.10, amd64 image under emulation on an Apple M4 host. Python fixture
ran as arm64. `events.jsonl` contains the four actual application events;
`logtest-*.txt` contains the raw rule-engine output for each case;
`rule-results.json` records expected and observed matches.

All eight assertions passed: three positive matches and five negative controls.
Rule 110500 is a level-zero grouping rule, not one of the three custom alerts.

These are application-log and rule-engine results. They do not establish Linux
audit collection, manager ingestion, indexed alerts, prompt-injection exploitation,
or independent detection of a compromised server. The receiver used loopback
and the payload was a fixed dummy token.

After the tests, one `docker stats` snapshot showed the manager at 81.38 MiB
and 0.15% CPU. This was not a peak measurement and excludes Docker VM overhead.
The runner subsequently changed from whole-engine stats to Compose-only stats;
the fixture, rules, and matching assertions were unchanged.
