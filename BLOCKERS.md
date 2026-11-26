# BLOCKERS.md — Active & Resolved Blockers

## Active Blockers

| ID | Severity | Description | Impact | Workaround / Mitigation | Escalation Needed? |
|---|---|---|---|---|---|
| BLK-001 | Low | Native cloud scheduling (`/schedule`, `/automation`, `crontab`) not available in remote devbox | Cannot schedule automatic background wakes if conversation pauses | Persisted full resume protocol in `AGENTS.md` + frequent git commits; sponsor can trigger `/goal` or send a message from mobile browser | No |
| BLK-002 | Medium | No third-party LLM API keys (`OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) configured in VM | Cannot run live cross-vendor models (Claude/GPT/Grok) directly from this VM | Execute controlled experiments using Google-managed Antigravity subagents + provide ready-to-run `wp-agent-benchmark` integration overlay for multi-model Harbor runs; document single-model-family scope transparently in `docs/research-report.md` | No |

## Resolved Blockers

| ID | Description | Resolution | Resolved At (UTC) |
|---|---|---|---|
| BLK-000 | `@php-wasm/node-*@3.1.66` emits `EBADENGINE` warning requesting `node >= 24.18.0` while VM runs `v22.23.5` | Verified end-to-end with `run-blueprint` + `--mount`: WordPress 7.1.5 + PHP 8.3.36 + Abilities API (`WP_Ability`) booted and returned clean JSON in ~20s on Node v22.23.5. Warning is non-blocking. | 2026-11-26T07:49:01Z |
| BLK-003 | Subagent rate limit (`resource_exhausted`) hit after Run 33/36 (`09:31:25Z`) | After rate-limit recovery, clean sandboxes for the final 3 Condition C negative controls (`C-docs-1`, `C-page-2`, `C-app-3`) ran cleanly to completion on `inherit`. | 2026-11-26T11:04:23Z |
