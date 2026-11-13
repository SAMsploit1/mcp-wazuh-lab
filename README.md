# MCP evidence lab for Wazuh

Work in progress: deterministic MCP tool misuse, Wazuh rules, and explicit evidence limits.
No paid API, real credentials, or internet-facing service. Not a prompt injection exploit.

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

## What the first phase proves

The stdio fixture handles initialize, tools/list and tools/call. A deterministic
client runs four actual actions; the server emits structured JSON application
events. Real Wazuh logtest evaluates those events plus four negative controls.
The result files distinguish expected matches from observed matches.

The file sensitivity label is supplied by the fixture. A compromised server could
lie or suppress all these events. These rules demonstrate application-log
integration, not independent host detection. They do not infer malicious intent
from a shell alone, and the loopback transfer does not demonstrate internet exfiltration.

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
