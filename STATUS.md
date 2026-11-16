# First lab run — 13 November 2026

Completed on an M4 MacBook Air with 16 GB RAM. No cloud resources or paid APIs.

- Four actual MCP tool actions completed in a network-isolated container.
- Wazuh 4.14.10 logtest: eight of eight cases passed.
- Three positive detections: dummy secret read, shell spawn, dummy-data transfer.
- Five controls produced no custom alert (the level-zero grouping rule may match).
- Post-test Wazuh container snapshot: 81.38 MiB RAM, 0.15% CPU. Not a peak measurement;
  excludes Docker Desktop and Linux VM overhead. Hard limit: 2 GiB and 1.5 CPU.
- Fixture limited to 256 MiB and 0.5 CPU; no published ports, no host credentials.
- Approximately 2 GiB of additional host disk use observed during image download;
  roughly 27 GiB available afterward. Images remain cached.
- Lab containers were removed after the test. Docker's stop command reported it was
  not running, but its engine still responded afterward, so full Docker shutdown
  could not be confirmed. Quit Docker Desktop manually to release VM resources.
  Starting Docker had automatically resumed existing Shuffle services.

## Findings that matter for publication

1. A JSON key called `action` collides with a Wazuh static field when used with a
   dynamic `<field>` rule. The fixture uses `mcp_action` instead.
2. Logtest requires the analysis daemon. The lightweight image startup restores
   packaged configuration and starts database plus analysis daemons without the
   full indexer/dashboard stack. The test runner waits for the logtest socket.
3. These are application events from an instrumented fixture, not independent
   kernel observations. Matching them proves parsing and rule behavior only.
4. A shell start does not establish malicious intent. The file sensitivity label
   is asserted by the fixture, and a compromised server can omit or forge it.

## Next milestone

Add independent Linux process/file-access telemetry and compare coverage with
application events. Determine whether a bounded dedicated VM is required for
audit collection. Do not claim auditd support inside ordinary Docker containers.
Then measure runtime peaks and collect end-to-end Wazuh ingestion evidence before
writing the publication as a validated detection guide.

GitHub connection is only needed when ready to create or push the public repository.
No repository was created or code published during this run.


## Reviewer revision — 16 November 2026

Implemented Farouk Musa's four requests: practical telemetry/collection guidance
in TELEMETRY.md, Wazuh-side credential-path classification (no sensitivity label),
expanded shell paths plus inline Python/Node rules, and ATT&CK tags. New rule IDs
110504–110505 extend the MCP pack's 110500–110505 range.

Static XML and 66 policy regressions pass. The updated full runner passed
70/70 cases on real Wazuh 4.14.10 in a two-core, 8 GiB GitHub Codespace:
four fresh fixture events plus 66 constructed regressions. Raw output confirms
48 positive matches with expected levels/ATT&CK tags and 22 negative controls.
All 70 events decoded as JSON. Tested source hashes were verified locally.
Evidence is saved in results/2026-11-16/. The runner removed its containers;
the Codespace was deleted after the evidence download.
The 13 November run above describes the original rules only; its sensitivity-label
finding is historical and is addressed by this revision. Independent host telemetry
and end-to-end ingestion remain unvalidated. Publication source was revised in the
separate SAMsploit1.github.io Codex worktree; no deployment is implied here.
