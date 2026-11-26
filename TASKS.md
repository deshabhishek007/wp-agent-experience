# TASKS.md — WPAX Execution Board

**Priority Rule:** Never compromise P0 for P1 or P2.

## P0 — Core Mission (Must Deliver)

- [x] **T0.1** Verify remote environment, GitHub auth, network, and orchestration capabilities (`ENVIRONMENT.md`)
- [x] **T0.2** Initialize persistent repository state (`MISSION.md`, `AGENTS.md`, `ENVIRONMENT.md`, `TASKS.md`, `STATUS.md`, `DECISIONS.md`, `BLOCKERS.md`, `EXPERIMENTS.md`, `RELEASE.md`)
- [ ] **T0.3** Complete WordPress Playground CLI smoke test (`@wp-playground/cli`) and verify WordPress + PHP 8.3 + SQLite + Abilities API runtime *(in progress)*
- [ ] **T0.4** Complete Deliverable 1: Upstream technical gap analysis covering all 7 upstream repos/docs (`docs/upstream-gap-analysis.md`)
- [ ] **T0.5** Complete Deliverable 3: Machine-readable WordPress capability registry + JSON Schema + validator (`registry/`)
- [ ] **T0.6** Complete Deliverable 2: Portable platform-selection agent skill (`skills/wp-platform-selection/`)
- [ ] **T0.7** Complete Deliverable 4: Minimal TypeScript CLI wrapping official `@wp-playground/cli` (`packages/wpax-cli/`) with `init`, `validate`, `boot`, `verify`, `catalog`, `check-fit`
- [ ] **T0.8** Complete Deliverable 5 (core): First verified reproducible blueprint (`blueprints/small-business/`)
- [ ] **T0.9** Complete Deliverable 6 (core): Automated unit + functional WordPress Playground verification tests
- [ ] **T0.10** Complete Deliverable 7: Benchmark integration with `apeatling/wp-agent-benchmark` (12 verbatim prompts, ported deterministic detector, functional verifier, `wpab` overlay)
- [ ] **T0.11** Execute pilot + P0 controlled experiment batch (Conditions A, B, C) and verify artifact inspection pipeline

## P1 — Full Experimental Evidence, Blueprints & Upstream Drafts

- [ ] **T1.1** Complete Deliverable 5 (full): Commerce (`blueprints/commerce/`) and Publishing (`blueprints/publishing/`) blueprints + functional Playground verification
- [ ] **T1.2** Complete Deliverable 8: Full 36 controlled experiments (12 prompts × 3 conditions A/B/C, including 3 negative controls) with real saved artifacts and statistical analysis
- [ ] **T1.3** Complete Deliverable 9: Reproducible documentation (`README.md`, `docs/architecture.md`) and GitHub Actions CI (`.github/workflows/ci.yml`)
- [ ] **T1.4** Complete Deliverable 10: Empirical research report (`docs/research-report.md`) with actual evidence, statistical tests, artifact inspection, threats to validity, and limitations
- [ ] **T1.5** Complete Deliverable 12: Draft upstream contributions (`upstream-drafts/` for `WordPress/agent-skills`, `apeatling/wp-agent-benchmark`, `make.wordpress.org/ai`, `wordpress.org/llms.txt`) — staged locally, unsubmitted

## P2 — Release Candidate & Polish

- [ ] **T2.1** Complete Deliverable 11: Verified release candidate (`v0.1.0-rc.1`), full test suite pass, clean build & packaging audit (`RELEASE.md`)
- [ ] **T2.2** Final sponsor summary report with repository links, evidence table, and approval requests for any external/upstream actions
