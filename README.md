# MCP evidence lab for Wazuh

Work in progress: deterministic MCP tool misuse, Wazuh rules, and explicit evidence limits.
No paid API, real credentials, or internet-facing service. Not a prompt injection exploit.

[Read the walkthrough](https://samsploit1.github.io/posts/mcp-wazuh-evidence.html) ·
[Inspect the revised 70-case run](results/2026-11-16/) ·
[Original eight-case run](results/2026-11-13/)

## Run

Requires Docker Compose, Python 3, and enough disk for the images. On Apple Silicon,
the Wazuh image currently requests amd64 emulation; check availability and performance.

```sh
sh scripts/run.sh
```

The script tears down its own Compose services on exit. If interrupted forcefully,
run `docker compose down` in this directory. Images remain cached for reuse.
No existing Docker containers or images are deleted. Generated evidence is gitignored.

## Resource design

Manager: 1.5 CPU, 2 GiB RAM. Fixture: 0.5 CPU, 256 MiB RAM. These are container
limits, excluding Docker's Linux VM overhead. Keep the VM at 4 GiB and 2 CPUs
for the initial Mac test; measure responsiveness before increasing either limit.
Bounded container logs; no published ports; no restart policy; no indexer/dashboard.
Both containers have networking disabled (loopback remains available).

The manager image runs the database and analysis daemons and the actual `wazuh-logtest`
binary. This phase validates decoding and rule matching, not manager ingestion,
agent collection, alert delivery, or a running SOC deployment.

## Original recorded run (13 November 2026)

The stdio fixture handles initialize, tools/list and tools/call. A deterministic
client runs four actual actions; the server emits structured JSON application
events. Real Wazuh logtest evaluates those events plus four negative controls.
The result files distinguish expected matches from observed matches.

The original run used a fixture-supplied sensitivity label. The revised rules
classify reported paths in Wazuh instead; a compromised server could still lie
about a path or suppress all these events. These rules demonstrate application-log
integration, not independent host detection. They do not infer malicious intent
from a shell alone, and the loopback transfer does not demonstrate internet exfiltration.

## Reviewer revisions (16 November 2026)

- [Real-deployment telemetry and collection guide](TELEMETRY.md): SDK wrappers,
  gateways/proxies, desktop/IDE logs, normalization, and agent collection setup.
- Path policy in Wazuh for `.ssh/`, `.env`/`.env.*`, `.aws/credentials`, `.kube/config`.
  File reads use `path`; transfers use `source_path`; `sensitive` is ignored.
  The fixture now creates a dummy `.env` under its temporary lab directory.
- Shell paths expanded; separate Python `-c` and Node `-e`/`--eval` rules added.
- ATT&CK tags added to rules 110501–110505. Loopback transfer remains local only.

Run `python3 tests/check_policy.py` for 66 static XML/regex policy checks.
`sh scripts/run.sh` runs four fresh fixture events plus those 66 regression cases
through real Wazuh (70 cases total). The revised engine run passed **70/70** on
Wazuh 4.14.10 in a disposable two-core GitHub Codespace on 16 November 2026:
48 expected detections and 22 negative controls. All events decoded as JSON;
positive levels and ATT&CK tags were also verified from raw engine output.
See [raw evidence and source hashes](results/2026-11-16/). The containers and
test Codespace were deleted after retrieving the evidence. Static checks use
Python regex and supplement the actual Wazuh run.
The saved eight-case run and its screenshots predate these changes and remain
unchanged as historical evidence, not validation of the revised rules.

## Next evidence layer

Collect independent Linux process and file-access telemetry, relate it to the
server PID and identity, and compare it with these application events. Standard
containers cannot be assumed to support auditd: audit is kernel-wide and may
need a dedicated Linux VM. Do not add privileged mode or host mounts to bypass
that limitation. Record blind spots, collection cost, and false positives before
making publication claims.

## Sources

- [MCP stdio transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)
- [Wazuh rule testing](https://documentation.wazuh.com/current/user-manual/ruleset/testing.html)
- [Official Wazuh Docker deployment](https://github.com/wazuh/wazuh-docker/tree/v4.14.10/single-node)

Publication angle: **An MCP tool accessed a secret—what can Wazuh actually prove?**
Publish measured evidence and limitations before extending to independent telemetry.
