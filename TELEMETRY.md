# Bringing MCP activity into Wazuh

`integration=mcp_lab` is this repository's normalized event schema, not a log
format emitted automatically by MCP servers or clients. The options below are
deployment guidance; this lab has not validated collection from real deployments.

## Choose a collection point

- **Server SDK middleware / tool wrapper:** wrap the registered tool handlers in
  your MCP SDK. Record the request ID, server/tool identity, start/completion,
  outcome, and the operations the handler actually performs. A `tools/call`
  argument is a requested path, not proof that a file was read. Instrument the
  file-read, subprocess, and send functions to report completed operations. For
  stdio servers, write newline-delimited JSON to a separate protected file or
  stderr; stdout carries JSON-RPC and must not contain these application logs.
- **Logging proxy or gateway:** place it on the actual request path for a remote
  MCP server, or use a stdio wrapper for a local subprocess. Capture
  `tools/call` request IDs, tool names, approved metadata and responses. Account
  for authentication, transport and TLS termination in your deployment. A gateway
  sees protocol requests and results, not arbitrary child processes or filesystem
  access inside the server. Use server/host telemetry to establish those actions.
- **Desktop and IDE client logs:** inspect the client's documented MCP/debug-log
  settings and configured log directory. Paths, formats and detail vary by client
  and version. Verify with a harmless call whether request ID, tool name, arguments,
  outcome and server identity are present; many logs contain only transport errors.
  Normalize what is actually recorded. Do not turn a requested operation into a
  completed `file_read` or `network_send` event without supporting evidence.

Protect logs against alteration, restrict readers, rotate them, and redact tool
results, file contents, credentials and authorization headers. Log metadata only.
Correlate sources using timestamp, request ID, server instance, PID and user where
available. These fields are recommended for deployment; the minimal lab fixture
does not yet populate them all. Application logging can still be suppressed or
forged by a compromised server; independent host telemetry remains a separate task.

## Normalize completed operations

Use the existing `mcp_lab` integration marker only for a trusted collector configured
to produce this schema. It is a routing value, not an authentication control.

```json
{"integration":"mcp_lab","mcp_action":"file_read","path":"/home/example/.ssh/id_ed25519","tool":"read_file","request_id":"example-42"}
{"integration":"mcp_lab","mcp_action":"process_start","executable":"/usr/bin/python3","argument1":"-c","tool":"run","request_id":"example-43"}
{"integration":"mcp_lab","mcp_action":"network_send","source_path":"/srv/app/.env","destination":"127.0.0.1","tool":"send","request_id":"example-44"}
```

These are illustrative metadata, not recorded deployment evidence. Report
`executable` as a resolved absolute path and `argument1` as argv[1], not a parsed
shell-command string. Report canonical absolute file paths (resolve `..` and
symlinks at the operation boundary). The policy also recognizes literal `~/.ssh/`
paths for adapters that preserve that spelling. If the source of sent bytes is
unknown, omit `source_path`; do not guess provenance from a preceding request.
Rule 110503 needs an actual source path and will miss untracked or transformed data.

## Collect the normalized file

For example, on the host running a Wazuh agent, configure a dedicated JSON-lines
file and restart the agent after validating the configuration:

```xml
<localfile>
  <log_format>json</log_format>
  <location>/var/log/mcp/activity.jsonl</location>
</localfile>
```

Install `rules/mcp_rules.xml` under `/var/ossec/etc/rules/` on the manager, check
that IDs 110500–110505 are free, test representative events with
`/var/ossec/bin/wazuh-logtest`, then reload/restart the manager through your normal
change process. Confirm the agent can read the file, generate a benign test event,
and verify its arrival and expected alert in the running system. This collection
path and end-to-end delivery are **not validated by the current lab**.

## Wazuh owns the path policy

Rules 110501 and 110503 use PCRE2 on `path` and `source_path`, respectively:

```text
(?:^|/)(?:\.ssh/|\.env(?:\.[^/]*)?$|\.aws/credentials$|\.kube/config$)
```

This matches `.ssh/` contents, `.env` and `.env.*`, `.aws/credentials`, and
`.kube/config`. It deliberately includes `.env.example`; tune documented public
examples and authorized automation for your environment. It does not classify file
contents, detect every credential store, or prove credential theft. A centrally
maintained Wazuh CDB list is another option for an explicit site-specific path
inventory; this pack implements the regex policy only. Neither rule uses
`sensitive`, so a supplied `sensitive=no` cannot override a matching path.

Rule 110502 matches sh/bash/dash/zsh/ksh/ash under `/bin`, `/usr/bin`, and
`/usr/local/bin`. Rules 110504 and 110505 match Python `-c` and Node `-e`/`--eval`
when that flag is argv[1]. They intentionally leave ordinary script invocations
outside this inline-code policy. Other interpreter paths, flags before `-c`,
combined flags, wrappers such as `env`, and other runtimes require additional
normalization and tested rules. Shell or inline-code execution alone does not
establish malicious intent.

## ATT&CK context

| Rule | Mapping | Meaning and limit |
| --- | --- | --- |
| 110501 | T1552.001 — Credentials in Files | Credential-related path access; contents and malicious intent unproven. |
| 110502 | T1059.004 — Unix Shell | Shell execution; legitimate tool use can match. |
| 110503 | T1048 — Exfiltration Over Alternative Protocol | Transfer behavior analogy; the fixture sends only dummy bytes over loopback. No external exfiltration or C2 channel is demonstrated. |
| 110504 | T1059.006 — Python | Inline Python code. |
| 110505 | T1059.007 — JavaScript/JScript | Inline Node.js code. |

T1041 is not used because the lab does not establish a command-and-control channel.
ATT&CK tags support triage and dashboards; they do not turn a local test into proof
of an adversary technique.
