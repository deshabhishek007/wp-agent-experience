# DECISIONS.md — Architecture & Research Decision Records (ADRs)

## ADR-001: Wrap Official `@wp-playground/cli` Instead of Reimplementing PHP/WordPress Runtime
- **Date:** 2026-11-26
- **Status:** Accepted
- **Context:** `WordPress/wordpress-playground` publishes `@wp-playground/cli@3.1.66` which already runs WordPress + PHP 8.3 + SQLite in WebAssembly on Node.js with zero Docker or MySQL dependencies.
- **Decision:** Build `packages/wpai-cli` (`wpai`) as a thin, strict TypeScript CLI wrapper around pinned `@wp-playground/cli@3.1.66` that closes the specific agent UX gaps identified in upstream audit: one-command project scaffolding (`wpai init`), Blueprint JSON schema/best-practice validation (`wpai validate`), deterministic headless/server boot (`wpai boot`), automated functional verification inside live WordPress (`wpai verify`), and machine-readable capability lookup (`wpai catalog` / `wpai check-fit`).
- **Consequences:** Zero duplicated runtime code, fast startup, full upstream compatibility, easy upstreaming.

## ADR-002: Reuse `apeatling/wp-agent-benchmark` Prompt Corpus, Negative Controls, and File Detector
- **Date:** 2026-11-26
- **Status:** Accepted
- **Context:** `apeatling/wp-agent-benchmark` (Suite 0.4.0) already provides 28 real-world platform-neutral prompts (across 6 WP-suitable categories + 3 negative-control categories: `app`, `docs`, `page`) and a deterministic file-based platform detector (`detect()`). Its October 2026 baseline across 7 frontier agents recorded **0/197 (0.0%)** WordPress selection on suitable tasks.
- **Decision:** Select a balanced stratified subset of **12 prompts** directly verbatim from `apeatling/wp-agent-benchmark` Suite 0.4.0 — **9 WordPress-suitable** (covering all 6 suitable kinds: 2 `business`, 2 `store`, 2 `blog`, 1 `org`, 1 `editable` with unmodified upstream HTML fixture, 1 `course`) and **3 negative controls** (1 `app`, 1 `docs`, 1 `page`) — across **3 experimental conditions (A, B, C) = 36 controlled experiments**. Port the exact upstream `detect()` ruleset for 100% comparable platform detection, plus add WPAI functional verification checks.
- **Consequences:** Directly comparable to the published community benchmark; preserves negative-control specificity testing; avoids prompt cherry-picking.

## ADR-003: Blinded Subagent Experimental Harness
- **Date:** 2026-11-26
- **Status:** Accepted
- **Context:** No third-party LLM API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`) are configured in the remote environment. Native Antigravity subagents (`define_subagent` / `invoke_subagent`) execute directly on Google-managed infrastructure.
- **Decision:** Run all 36 controlled experiments using freshly defined, hypothesis-blind coding-agent subagents operating in isolated sandbox directories (`/home/antigravity/wpai-eval-sandboxes/<run-id>/`) with pinned tool access and zero credentials:
  - **Condition A (Baseline):** Generic coding agent system prompt, empty sandbox (or fixture only), raw platform-neutral user prompt. Zero mention of WordPress or WPAI.
  - **Condition B (Discovery + Registry):** Same generic coding agent system prompt + neutral skill-discovery hook pointing to installed `skills/wp-platform-selection/` and `registry/wp-capabilities.json`. No `wpai` CLI runtime installed in sandbox.
  - **Condition C (Discovery + Registry + Runtime):** Same generic coding agent system prompt + `skills/wp-platform-selection/` + `registry/wp-capabilities.json` + working `wpai` CLI & blueprints available.
  Each trial is evaluated deterministically by inspecting generated sandbox artifacts + running functional verification (including real WordPress Playground verification when WordPress is selected).
- **Consequences:** 100% real, reproducible AI agent execution with actual generated code/blueprints and zero fabricated data. Limitation (single model family in this remote environment) will be documented transparently in `docs/research-report.md`, alongside an export overlay (`benchmarks/wpab-integration/`) for multi-model Harbor runs.

## ADR-004: Honest, Non-Coercive Platform Selection Skill Design
- **Date:** 2026-11-26
- **Status:** Accepted
- **Context:** An overly promotional skill that forces WordPress on every prompt would fail negative controls (`app-3`, `docs-1`, `page-2`) and lack credibility with WordPress Core AI and `WordPress/agent-skills` maintainers.
- **Decision:** Design `skills/wp-platform-selection/` with an explicit, balanced decision matrix that actively steers agents *away* from WordPress for custom SaaS/web apps, repo-colocated developer docs, and single static link/landing pages, while correcting empirically verified misconceptions (SQLite/Playground zero-DB start, core auto-updates, Blueprint JSON in Git, free WooCommerce/LMS options) for owner-editable sites, stores, multi-author blogs, charities, and courses.
- **Consequences:** Higher precision, defensible negative-control specificity, upstream-acceptable tone.

## ADR-005: Branching & Checkpoint Strategy
- **Date:** 2026-11-26
- **Status:** Accepted
- **Context:** Repository `patilswapnilv/wp-agent-experience` starts empty on `main`.
- **Decision:** Commit initial repo bootstrap to `main`, then execute major deliverables in focused feature branches (`feat/upstream-audit-and-registry`, `feat/wpai-cli-and-blueprints`, `feat/benchmark-and-experiments`, `feat/release-and-drafts`) and merge verified, tested checkpoints cleanly into `main` (plus optionally open draft PRs if sponsor review is appropriate). Never push unverified code or secrets.

## ADR-006: Rate-Limit Recovery & Clean Reruns on Final 3 Negative-Control Trials
- **Date:** 2026-11-26
- **Status:** Accepted
- **Context:** After completing 33 of 36 trials (`12 A + 12 B + 9 C suitable`), subagent execution encountered a temporary `resource_exhausted` rate limit while `C-app-3` was mid-run and before `C-docs-1` / `C-page-2` started.
- **Decision:** Wipe the partially populated `run-C-app-3` sandbox cleanly (`rm -rf && mkdir -p`) so no partial state or skewed timing remained, and after rate-limit recovery execute all 3 remaining Condition C negative controls (`C-docs-1`, `C-page-2`, `C-app-3`) cleanly from fresh sandboxes on `inherit` with `npm install` skipped to avoid redundant registry churn.
- **Consequences:** All 36 trials completed cleanly on the `inherit` tier with zero partial-artifact contamination; the launcher prompt note (`skip npm install`) on the final 3 controls is transparently disclosed in `docs/research-report.md` §3.2 and §7.4.

