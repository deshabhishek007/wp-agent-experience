# WPAX — WordPress Agent Experience

Making WordPress easier for AI coding agents to independently **discover, evaluate, select, provision, and operate** when appropriate — backed by controlled, reproducible experiments.

> **Status:** Active autonomous mission (`2026-11-26` → `2026-11-29`). See [`STATUS.md`](./STATUS.md), [`TASKS.md`](./TASKS.md), and [`EXPERIMENTS.md`](./EXPERIMENTS.md) for live progress.

## Why WPAX Exists

In the October 2026 run of [`apeatling/wp-agent-benchmark`](https://github.com/apeatling/wp-agent-benchmark) (`Suite 0.4.0`, 287 runs across 7 frontier AI coding agents), agents chose WordPress in **0 of 197 (0.0%)** WordPress-suitable requests (bakeries, yoga studios, online candle/bike-parts stores, multi-author local news sites, charities, and uneditable legacy cafe sites).

Our [`docs/upstream-gap-analysis.md`](./docs/upstream-gap-analysis.md) traces this to three concrete gaps:
1. **No pre-selection discovery skill:** `WordPress/agent-skills` has 20 skills, all assuming a WordPress codebase already exists.
2. **Stale mental models:** Agents repeatedly reject WordPress citing local MySQL setup (`upkeep` 82.7%), complexity (`overkill` 71.1%), manual security patching (`security` 68.5%), and Git workflows (`git` 45.7%).
3. **Provisioning & verification friction:** Agents lack a one-command starter + JSON functional verification CLI over official `@wp-playground/cli`.

## Components

| Deliverable | Path | Purpose |
|---|---|---|
| **Upstream Gap Analysis** | [`docs/upstream-gap-analysis.md`](./docs/upstream-gap-analysis.md) | Audit of 7 upstream WordPress AI & benchmark repos/docs |
| **Platform-Selection Skill** | [`skills/wp-platform-selection/`](./skills/wp-platform-selection/) | Portable `SKILL.md` with honest decision matrix & negative controls |
| **Capability Registry** | [`registry/wp-capabilities.json`](./registry/wp-capabilities.json) | JSON-Schema-validated, source-cited WordPress capability & suitability catalog |
| **WPAX TypeScript CLI** | [`packages/wpax-cli/`](./packages/wpax-cli/) | Minimal wrapper around pinned `@wp-playground/cli@3.1.66` (`init`, `validate`, `boot`, `verify`, `catalog`, `check-fit`) |
| **Reproducible Blueprints** | [`blueprints/`](./blueprints/) | Tested `small-business`, `commerce`, and `publishing` WordPress Playground Blueprints |
| **Benchmark & Experiments** | [`benchmarks/`](./benchmarks/) | 12 verbatim `wp-agent-benchmark` prompts (9 suitable + 3 negative controls) × 3 conditions (A/B/C = 36 runs) |
| **Research Report** | [`docs/research-report.md`](./docs/research-report.md) | Empirical results, Fisher's exact tests, artifact inspections, and honest limitations |
| **Upstream Drafts** | [`upstream-drafts/`](./upstream-drafts/) | Staged PRs & proposals (unsubmitted pending sponsor approval) |

## Quick Start

```bash
# 1. Install dependencies & build CLI
npm ci && npm run build

# 2. Validate capability registry & all blueprints
npm run validate

# 3. Run unit tests & benchmark harness tests
npm test
python3 -m unittest discover -s benchmarks/harness -p 'test_*.py' -v

# 4. Scaffold and functionally verify a WordPress site in WASM + SQLite (zero Docker/MySQL)
npx wpax init small-business --dir /tmp/my-bakery --name "Sunrise Bakery"
npx wpax verify /tmp/my-bakery --json
```

## Reproducibility & Agent Handoff

- **Reproducibility & Handoff:** Any replacement coding agent can resume from repository state via [`AGENTS.md`](./AGENTS.md).
