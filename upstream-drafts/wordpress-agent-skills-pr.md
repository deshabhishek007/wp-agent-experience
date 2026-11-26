# Draft Pull Request — `WordPress/agent-skills`

**Target Repository:** `https://github.com/WordPress/agent-skills`  
**Status:** DRAFT — NOT SUBMITTED (awaiting sponsor approval)

---

## Proposed PR Title

`feat(skills): add wp-platform-selection skill for neutral pre-scaffold platform evaluation`

## Proposed PR Body

### Motivation

`WordPress/agent-skills` currently provides 20 high-quality skills covering WordPress development *after* a WordPress repository already exists (`wordpress-router` runs `detect_wp_project.mjs` on an existing WP codebase). However, none of the current skills help an AI coding agent evaluate **when WordPress fits (and when it does not)** for a greenfield or legacy-site request where the user has not named a platform.

In the October 2026 baseline of `apeatling/wp-agent-benchmark` (Suite `0.4.0`, 287 runs across 7 frontier coding agents), agents chose WordPress in **0 of 197 (0.0%)** WordPress-suitable tasks — frequently citing outdated assumptions about local MySQL requirements, security auto-updates, and Git-declarative workflows.

### What This PR Adds

1. `skills/wp-platform-selection/SKILL.md` — A concise, non-promotional decision skill following this repository's `SKILL.md` structure:
   - Step 1 triages *who edits content after handoff* and separates WordPress-suitable workloads (small business, WooCommerce stores, multi-author blogs/news, nonprofits, making hand-coded sites editable) from explicit negative controls where WordPress should **not** be chosen (custom SaaS/web apps, repo-colocated developer docs, single static pages).
   - Step 2 corrects empirically observed myths using cited 2026 documentation (Playground CLI zero-DB SQLite runtime, core auto-updates, Patchstack core-vs-plugin split, free WooCommerce/LMS options, WP 6.9+ Abilities API & MCP Adapter).
   - Step 3 delegates Blueprint JSON authoring and local runtime workflows directly to this repository's existing `blueprint` and `wp-playground` skills (zero duplication).
2. `skills/wp-platform-selection/references/decision-matrix.md` & `evidence-facts.md` — Focused supporting references.
3. `skills/wp-platform-selection/scripts/evaluate-fit.mjs` — Zero-dependency helper evaluating requests against a machine-readable capability registry.
4. Eval scenarios covering both positive fit (`business`, `store`, `blog`, `editable`) and negative-control restraint (`app-saas`, `cli-docs`, `link-in-bio`).

### Empirical Evidence

*(Populate with final verified WPAX 36-run A/B/C numbers from `docs/research-report.md` prior to submission.)*

### Checklist
- [ ] Passes `node shared/scripts/validate-skills.mjs`
- [ ] Updated `skills/wordpress-router/` references if maintainers desire pre-scaffold routing
- [ ] Includes positive and negative-control eval scenarios
- [ ] Honest, non-promotional tone aligned with WordPress AI Guidelines
