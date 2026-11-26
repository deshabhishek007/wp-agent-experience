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

### Controlled Results (`Suite 0.4.0`: 36 Main + 27 Held-Out Runs = 63 Total)

Evaluating 12 verbatim `Suite 0.4.0` tasks (9 suitable + 3 controls) in the main study (`runs.jsonl`, exported to `choose-run.schema.json` format in `wpab-choose-export.jsonl`) and 9 completely **held-out** `Suite 0.4.0` tasks (6 suitable + 3 controls across all 9 kinds, including unprompted **Condition D** where `.agents/skills/wp-platform-selection/` is installed silently with zero system-prompt mention and symmetric non-WP `npm run build` / `npm test` verification):

| Study & Condition | Suitable WP Selection (95% Wilson CI) | Negative-Control Specificity | Verified (Live Playground / Symmetric) | Fisher One-Sided `p` vs A |
|---|---|---|---|---|
| **Main A (Baseline)** | 0/9 (0.0%) [0.0%, 29.9%] | 3/3 (100.0%) | 12/12 static (0 WP) | — |
| **Main B (Skill + Registry)** | 9/9 (100.0%) [70.1%, 100.0%] | 3/3 (100.0%) | 8/9 WP Playground | `2.057e-05` |
| **Main C (Skill + Registry + `wpax`)** | 9/9 (100.0%) [70.1%, 100.0%] | 3/3 (100.0%) | 9/9 WP Playground | `2.057e-05` |
| **Held-Out A (Baseline)** | 0/6 (0.0%) [0.0%, 39.0%] | 3/3 (100.0%) | 9/9 symmetric build/test | — |
| **Held-Out C (Skill + `wpax`)** | 6/6 (100.0%) [61.0%, 100.0%] | 3/3 (100.0%) | 9/9 (6/6 WP + 3/3 symmetric) | `0.00108` |
| **Held-Out D (Unprompted Discovery)** | 6/6 (100.0%) [61.0%, 100.0%] | 3/3 (100.0%) | 9/9 (6/6 WP + 3/3 symmetric) | `0.00108` |

Live Playground verification caught a fatal Blueprint bug in Condition B (`B-business-3`, exit code `255`), while `wpax` starters cut mean held-out delivery time by 38.4% vs unprompted Condition D (`225.7s` vs `366.3s`). We would welcome feedback on running these overlays across the full multi-vendor Harbor matrix (`claude`, `codex`, `gemini`, `opencode`, `cursor`).
