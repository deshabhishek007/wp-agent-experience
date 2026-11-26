# WPAI — WordPress Agent Experience Mission Charter

- **Mission Start (UTC):** 2026-11-26T07:42:25Z
- **Mission Deadline (UTC, +72h):** 2026-11-29T07:42:25Z
- **Repository:** https://github.com/patilswapnilv/wp-agent-experience
- **Sponsor:** Swapnil V. Patil (`patilswapnilv`)
- **Execution Mode:** Google-managed remote execution exclusively (no local MacBook dependency)

## Objective

Make WordPress easier for AI agents to independently discover, evaluate, select, provision, and operate when appropriate — and demonstrate measurable improvements through controlled, reproducible experiments.

## Hypothesis

Providing AI coding agents with:
1. A neutral, evidence-backed **platform-selection agent skill** (`skills/wp-platform-selection/`),
2. A **machine-readable WordPress capability registry** (`registry/wp-capabilities.json`), and
3. A **minimal TypeScript CLI wrapping official WordPress Playground** (`packages/wpai-cli/`) with reproducible blueprints and functional verification

will produce a measurable improvement (target hypothesis: **+25 percentage points**) in appropriate WordPress selection on WordPress-suitable tasks while maintaining low/zero false-positive WordPress selection on negative controls (web apps/SaaS, developer docs, single static link pages).

This is an empirical hypothesis to be tested honestly — never fabricated or gamed.


## Deliverables & Priorities

### P0 (Must Deliver — Never Compromise)
1. **D1:** Upstream technical gap analysis (`docs/upstream-gap-analysis.md`)
2. **D2:** Portable platform-selection agent skill (`skills/wp-platform-selection/`)
3. **D3:** Machine-readable WordPress capability registry + JSON Schema (`registry/`)
4. **D4:** Minimal TypeScript CLI wrapping official `@wp-playground/cli` (`packages/wpai-cli/`)
5. **D5 (core):** First verified blueprint (`blueprints/small-business/`)
6. **D6 (core):** Automated functional verification tests
7. **D7/D8 (core):** Integration with `apeatling/wp-agent-benchmark` and controlled A/B/C experiment harness with real evidence

### P1 (High Value)
8. **D5 (full):** Commerce (`blueprints/commerce/`) and Publishing (`blueprints/publishing/`) blueprints
9. **D8 (full):** Full 36 controlled experiments (12 prompts × 3 conditions A/B/C, including 3 negative controls)
10. **D9:** Reproducible documentation and GitHub Actions CI
11. **D10:** Research report with actual evidence, statistical analysis, artifact inspection, and limitations (`docs/research-report.md`)
12. **D12:** Draft upstream contributions (`upstream-drafts/`) — staged locally only, requiring sponsor approval before external submission

### P2 (Polish)
13. **D11:** Tested release candidate (`v0.1.0-rc.1`) with verified package build, clean exports, and publication materials

## Autonomy Boundaries

- **Autonomous:** Research, architecture, implementation, testing, debugging, refactoring, local branches, commits, draft PRs inside `patilswapnilv/wp-agent-experience`.
- **Requires Sponsor Approval:** External publication, upstream PR/issue submission, production deployment, access to unrelated repos, visibility/license changes.
