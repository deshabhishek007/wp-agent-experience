# RELEASE.md — Release Candidate Checklist & Verification Evidence

**Version:** `v0.1.0-rc.1`  
**Status:** Ready / Verified  
**Verified At (UTC):** `2026-11-26T12:56:31Z`

## Release Readiness Checklist (12/12 Deliverables)

- [x] **Deliverable 1:** [`docs/upstream-gap-analysis.md`](./docs/upstream-gap-analysis.md) — Complete technical audit of all 7 upstream repos/docs + `wordpress.org/llms.txt` with exact issue/commit/metric citations.
- [x] **Deliverable 2:** [`skills/wp-platform-selection/`](./skills/wp-platform-selection/) — Portable `SKILL.md`, `references/decision-matrix.md`, `references/evidence-facts.md`, and zero-dependency `scripts/evaluate-fit.mjs`.
- [x] **Deliverable 3:** [`registry/wp-capabilities.json`](./registry/wp-capabilities.json) + [`registry/schema/wp-capabilities.schema.json`](./registry/schema/wp-capabilities.schema.json) — Validated against JSON Schema Draft 2020-12.
- [x] **Deliverable 4:** [`packages/wpax-cli/`](./packages/wpax-cli/) — Minimal TypeScript CLI wrapping pinned `@wp-playground/cli@3.1.66` (`init`, `validate`, `boot`, `verify`, `catalog`, `check-fit`, `validate-registry`, all supporting `--json`).
- [x] **Deliverable 5:** [`blueprints/`](./blueprints/) — Reproducible `small-business`, `commerce` (deterministic + full WooCommerce variant), and `publishing` blueprints validated and booted in live WordPress Playground (`WP 7.1.5`, `PHP 8.3.36`).
- [x] **Deliverable 6:** Functional verification tests passing (`19/19` Node unit tests + `4/4` live WordPress Playground end-to-end integration tests + `19/19` Python harness unit tests).
- [x] **Deliverable 7:** [`benchmarks/`](./benchmarks/) — `apeatling/wp-agent-benchmark` integration (`12` verbatim `Suite 0.4.0` prompts, unmodified `editable-2` HTML fixture, ported `detect.py`, `wpab-integration/` Docker overlay, and schema-verified `wpab-choose-export.jsonl`).
- [x] **Deliverable 8:** [`benchmarks/results/runs.jsonl`](./benchmarks/results/runs.jsonl) — **36/36 controlled experiments completed** (`12` Condition A + `12` Condition B + `12` Condition C, including `3` negative controls per arm) with real execution timings, live Playground verification, [`summary.json`](./benchmarks/results/summary.json), and [`artifact-manifest.json`](./benchmarks/results/artifact-manifest.json).
- [x] **Deliverable 9:** [`README.md`](./README.md), [`docs/architecture.md`](./docs/architecture.md), and [`.github/workflows/ci.yml`](./.github/workflows/ci.yml) — Reproducible documentation & automated GitHub Actions CI pipeline.
- [x] **Deliverable 10:** [`docs/research-report.md`](./docs/research-report.md) — Empirical research report with Wilson 95% CIs, exact Fisher's exact tests (`p = 2.057e-05`), `B-business-3` runtime failure diagnosis, artifact inspections, and 10 honest threats to validity / limitations.
- [x] **Deliverable 11:** Release candidate `v0.1.0-rc.1` verified end-to-end via full test battery and annotated Git tag.
- [x] **Deliverable 12:** [`upstream-drafts/`](./upstream-drafts/) — 4 staged drafts (`wordpress-agent-skills-pr.md`, `wp-agent-benchmark-pr.md`, `wordpress-llms-txt-proposal.md`, `publication-post-draft.md`) — **unsubmitted pending explicit sponsor approval**.
- [x] **Credential Audit:** Zero secrets or tokens committed.

---

## Verification Battery Evidence (`v0.1.0-rc.1`)

| Verification Command | Scope | Result |
|---|---|---|
| `npm run build` | TypeScript compilation (`packages/wpax-cli`) | **Exit 0** |
| `npm run validate` | `registry/wp-capabilities.json` (AJV Draft 2020-12) + all 3 `blueprints/*/blueprint.json` | **Exit 0 (4/4 valid)** |
| `npm test` | CLI unit, Blueprint validator, preset scaffolding, `check-fit`, registry tests | **19/19 passed (0 failed)** |
| `npm run test:integration` | Live `@wp-playground/cli@3.1.66` (`WP 7.1.5`, `PHP 8.3.36`) verification across `wpax init` + all 3 repo blueprints (`84.3s`) | **4/4 passed (0 failed)** |
| `python3 -m unittest discover -s benchmarks/harness -p 'test_*.py' -v` | Ported `detect.py` parity, Wilson CI, Fisher's exact test, `runs.jsonl` & `choose-run` export | **19/19 passed (0 failed)** |
| `python3 benchmarks/harness/analyze.py` | Regenerates `benchmarks/results/summary.json` from `36/36` recorded trials | **Exit 0 (36 runs verified)** |
