# Recorded reviewer-revision run: 16 November 2026

**70/70 passed** through real Wazuh 4.14.10 on a disposable GitHub Codespace
(2 CPUs, 8 GiB RAM, Linux x86_64). The source was uploaded directly without
pushing the changes first. `sh scripts/run.sh` executed four real fixture tool
actions and evaluated those events plus 66 constructed regressions.

| Expected rule | Positive cases | Level | ATT&CK |
| --- | ---: | ---: | --- |
| 110501 — credential-related read | 13 | 8 | T1552.001 |
| 110502 — Unix shell | 19 | 8 | T1059.004 |
| 110503 — source-path transfer | 7 | 10 | T1048 |
| 110504 — inline Python | 3 | 8 | T1059.006 |
| 110505 — inline Node.js | 6 | 8 | T1059.007 |
| No custom alert | 22 | 0 or no rule | None |

All 70 records decoded as JSON. A second inspection of every raw output verified
expected levels and ATT&CK IDs for all 48 positives, no alert-generation message
for all 22 controls, and no ERROR/CRITICAL/WARNING messages. One control matched
no rule; 21 matched only the level-zero grouping rule.

- `events.jsonl`: the four newly executed application events (no sensitivity labels).
- `logtest-*.txt`: unmodified stdout/stderr from Wazuh for all 70 cases.
- `rule-results.json`: expected and observed rule IDs from the test runner.
- `validation-summary.json`: aggregate checks from local evidence inspection.
- `tested-source.sha256`: hashes of the rules, fixture, runner and Compose setup;
  verified against the local source before commit.
- `environment.txt`: remote architecture and Docker/Compose/Python versions.
- `resources.txt`: one post-test manager snapshot (86.07 MiB, 0.07% CPU).
  This is not a peak measurement and excludes Codespace/Docker overhead.

The script removed its containers. Evidence was downloaded before deleting only
the test Codespace. No dashboard or indexer was deployed, and no ports were
published. Fixture traffic stayed on loopback with fixed dummy data.

These results validate application-event decoding, Wazuh rule loading/matching,
and ATT&CK metadata. They do not validate real-client log collection, independent
host telemetry, agent ingestion, dashboard alerts, malicious intent or external
exfiltration. Keep the 13 November run as historical evidence of the original
sensitivity-label policy.
