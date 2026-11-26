# WPAI — WordPress Agent Experience

Making WordPress easier for AI coding agents to independently **discover, evaluate, select, provision, and operate** when appropriate — backed by controlled, reproducible experiments.

> **Release Status:** `v0.1.0-rc.1` verified (`36/36` controlled experiments complete, all 12 deliverables shipped). See [`docs/research-report.md`](./docs/research-report.md), [`EXPERIMENTS.md`](./EXPERIMENTS.md), and [`RELEASE.md`](./RELEASE.md).

## Headline Empirical Results (`n = 36` Controlled Trials)

Evaluated on 12 verbatim platform-neutral prompts from [`apeatling/wp-agent-benchmark`](https://github.com/apeatling/wp-agent-benchmark) `Suite 0.4.0` (9 WordPress-suitable tasks + 3 negative controls: `app-3`, `docs-1`, `page-2`):

| Condition | Suitable Tasks: Chose WP (95% Wilson CI) | Negative Controls: Avoided WP | Live WP Playground Verified (WP Outputs) | Fisher's One-Sided `p` vs A |
|---|---|---|---|---|
| **A — Baseline (Unmodified)** | **0/9 (0.0%)** [0.0%, 29.9%] | **3/3 (100.0%)** | n/a (0 WP outputs) | — |
| **B — Discovery Skill + Registry** | **9/9 (100.0%)** [70.1%, 100.0%] | **3/3 (100.0%)** | **8/9 (88.9%)** | `2.057 × 10⁻⁵` |
| **C — Skill + Registry + `wpai` CLI** | **9/9 (100.0%)** [70.1%, 100.0%] | **3/3 (100.0%)** | **9/9 (100.0%)** | `2.057 × 10⁻⁵` |

- **Why Condition C outperformed Condition B on runtime reliability:** Without a runtime verification loop, `WPAI-B-business-3` shipped a 16-step Blueprint that failed at step #16 with PHP exit code `255` in WordPress Playground. Every Condition C agent ran `wpai verify` against live WordPress 7.1.5 before finishing (`9/9` verified).
- **Honest scope & limitations:** Results reflect in-distribution prompts within a single model family where agents in B/C were instructed to consult the installed skill; multi-vendor held-out evaluation via [`benchmarks/wpab-integration/`](./benchmarks/wpab-integration/) is recommended next (see [`docs/research-report.md`](./docs/research-report.md) §7).

## Why WPAI Exists

In the October 2026 run of [`apeatling/wp-agent-benchmark`](https://github.com/apeatling/wp-agent-benchmark) (`Suite 0.4.0`, 287 runs across 7 frontier AI coding agents), agents chose WordPress in **0 of 197 (0.0%)** WordPress-suitable requests.

Our [`docs/upstream-gap-analysis.md`](./docs/upstream-gap-analysis.md) traces this to three concrete gaps:
1. **No pre-selection discovery skill:** `WordPress/agent-skills` has 20 skills, all assuming a WordPress codebase already exists.
2. **Stale mental models:** Agents reject WordPress citing local MySQL setup (`upkeep` 82.7%), complexity (`overkill` 71.1%), manual security patching (`security` 68.5%), and Git workflows (`git` 45.7%).
3. **Provisioning & verification friction:** Agents lack a one-command starter + JSON functional verification CLI over official `@wp-playground/cli`.

## Deliverables & Repository Map

| # | Deliverable | Path | Purpose |
|---|---|---|---|
| 1 | **Upstream Gap Analysis** | [`docs/upstream-gap-analysis.md`](./docs/upstream-gap-analysis.md) | Audit of 7 upstream WordPress AI & benchmark repos/docs + `llms.txt` |
| 2 | **Platform-Selection Skill** | [`skills/wp-platform-selection/`](./skills/wp-platform-selection/) | Portable `SKILL.md` with honest decision matrix & negative controls |
| 3 | **Capability Registry** | [`registry/wp-capabilities.json`](./registry/wp-capabilities.json) | JSON-Schema-validated, source-cited WordPress capability & suitability catalog |
| 4 | **WPAI TypeScript CLI** | [`packages/wpai-cli/`](./packages/wpai-cli/) | Minimal wrapper around pinned `@wp-playground/cli@3.1.66` (`init`, `validate`, `boot`, `verify`, `catalog`, `check-fit`) |
| 5 | **Reproducible Blueprints** | [`blueprints/`](./blueprints/) | Tested `small-business`, `commerce`, and `publishing` WordPress Playground Blueprints |
| 6 | **Verification Tests** | [`packages/wpai-cli/test/`](./packages/wpai-cli/test/) | `19` Node unit tests + `4` live WordPress Playground integration tests + `19` Python tests |
| 7 | **Benchmark Integration** | [`benchmarks/`](./benchmarks/) | 12 verbatim `wpab` prompts, ported `detect.py`, Docker overlay & `choose-run` exporter |
| 8 | **36 Controlled Experiments** | [`benchmarks/results/`](./benchmarks/results/) | `runs.jsonl` (36 trials), `summary.json`, `artifact-manifest.json`, `wpab-choose-export.jsonl` |
| 9 | **Docs & CI** | [`docs/architecture.md`](./docs/architecture.md), [`.github/workflows/ci.yml`](./.github/workflows/ci.yml) | Architecture specification & automated CI workflow |
| 10 | **Research Report** | [`docs/research-report.md`](./docs/research-report.md) | Empirical results, Fisher's exact tests, artifact inspections, and honest limitations |
| 11 | **Release Candidate** | [`RELEASE.md`](./RELEASE.md) | `v0.1.0-rc.1` verification checklist and test execution evidence |
| 12 | **Upstream Drafts** | [`upstream-drafts/`](./upstream-drafts/) | Staged PRs, `llms.txt` diff, & publication draft (unsubmitted pending sponsor approval) |

## Quick Start

```bash
# 1. Install dependencies & build CLI
npm ci && npm run build

# 2. Validate capability registry & all blueprints
npm run validate

# 3. Run unit, benchmark harness, and live Playground integration tests
npm test
python3 -m unittest discover -s benchmarks/harness -p 'test_*.py' -v
npm run test:integration

# 4. Recompute 36-run statistical summary from recorded trials
python3 benchmarks/harness/analyze.py

# 5. Scaffold and functionally verify a WordPress site in WASM + SQLite (zero Docker/MySQL)
npx wpai init small-business --dir /tmp/my-bakery --name "Sunrise Bakery"
npx wpai verify /tmp/my-bakery --json
```

## Reproducibility & Agent Handoff

- Any coding agent can audit or resume from repository state via [`AGENTS.md`](./AGENTS.md).
