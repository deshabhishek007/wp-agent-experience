# Draft Issue / Pull Request — `apeatling/wp-agent-benchmark`

**Target Repository:** `https://github.com/apeatling/wp-agent-benchmark`  
**Status:** DRAFT — NOT SUBMITTED (awaiting sponsor approval)

---

## Proposed Title

`feat(choose): add reproducible WPAX intervention overlays (Discovery Skill + Capability Registry + Playground CLI)`

## Proposed Body

### Context

`wp-agent-benchmark` established a clear empirical baseline in October 2026 (`Suite 0.4.0`): across 7 frontier coding agents and 197 WordPress-suitable requests, agents selected WordPress **0 times (0.0%)**, citing `upkeep` (82.7%), `overkill` (71.1%), `security` (68.5%), and `git` (45.7%).

A natural next scientific question is **interventional**: if WordPress ships better agent-facing discovery (a balanced platform-selection skill + machine-readable capability registry) and a one-command Playground wrapper CLI (`wpax`), how much does WordPress selection improve on suitable tasks — and crucially, does negative-control specificity (`app`, `docs`, `page`) stay clean?

### Proposed Contribution

We built a lightweight, non-invasive integration overlay (`benchmarks/wpab-integration/` in `wp-agent-experience`) designed to slot into `wp-agent-benchmark` without altering baseline tasks:

1. **Docker Environment Overlay (`Dockerfile.wpax-overlay`):** Extends `dev-machine` with:
   - **Condition B:** Installed `wp-platform-selection` skill + `registry/wp-capabilities.json`
   - **Condition C:** Condition B + `wpax` CLI wrapping pinned `@wp-playground/cli@3.1.66`
2. **Schema-Compatible Record Exporter (`export_to_wpab.py`):** Converts WPAX controlled run logs into `schema/choose-run.schema.json`-compatible records tagged with explicit condition metadata.
3. **Live Functional Verification Hook:** Extends file-only `detect()` checks with optional `wpax verify` execution in WordPress Playground WASM to confirm that generated WordPress blueprints actually boot cleanly and fulfill prompt requirements.

### Controlled 36-Run Results (`Suite 0.4.0` Prompts)

Evaluating 12 verbatim `Suite 0.4.0` tasks (9 WordPress-suitable + 3 negative controls: `app-3`, `docs-1`, `page-2`) across Conditions A, B, and C (`benchmarks/results/runs.jsonl`, exported to `choose-run.schema.json` format in `benchmarks/results/wpab-choose-export.jsonl`):

| Condition | Suitable WP Selection (95% Wilson CI) | Negative-Control Specificity | Live Playground Verified (WP Outputs) | Fisher's One-Sided `p` vs A |
|---|---|---|---|---|
| **A (Baseline)** | 0/9 (0.0%) [0.0%, 29.9%] | 3/3 (100.0%) | n/a (0 WP outputs) | — |
| **B (Skill + Registry)** | 9/9 (100.0%) [70.1%, 100.0%] | 3/3 (100.0%) | 8/9 (88.9%) | `2.057e-05` |
| **C (Skill + Registry + `wpax`)** | 9/9 (100.0%) [70.1%, 100.0%] | 3/3 (100.0%) | 9/9 (100.0%) | `2.057e-05` |

Crucially, live Playground verification distinguished Condition B from Condition C: in `B-business-3`, an agent authored a 16-step Blueprint without a runtime tool and hit a step #16 PHP fatal error (`exit code 255`) upon independent verification, whereas all 9 Condition C runs self-verified via `wpax verify` before completion. We would welcome feedback on running these overlays across the full multi-vendor Harbor matrix (`claude`, `codex`, `gemini`, `opencode`, `cursor`).
