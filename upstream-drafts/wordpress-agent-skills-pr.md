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

### Empirical Evidence (63 Controlled Runs: 36 Main + 27 Held-Out Including Unprompted Discovery)

1. **Main study (`n = 36`, 12 verbatim `Suite 0.4.0` prompts — 9 suitable + 3 controls):**
   - **Condition A (Baseline):** **0/9 (0.0%)** selected WordPress on suitable tasks; **3/3 (100.0%)** negative-control specificity.
   - **Condition B (Skill + Registry):** **9/9 (100.0%)** suitable (`+100.0 pp`, Fisher one-sided `p = 2.057e-05`), **3/3 (100.0%)** controls, **8/9 (88.9%)** live Playground verified.
   - **Condition C (Skill + Registry + `wpai verify`):** **9/9 (100.0%)** suitable, **3/3 (100.0%)** controls, **9/9 (100.0%)** live WordPress Playground (`WP 7.1.5`) verified.

2. **Held-out generalization & unprompted discovery (`n = 27`, 9 completely unseen `Suite 0.4.0` prompts across all 9 kinds — 6 suitable + 3 controls; skill kept strictly unmodified):**
   - **Pre-test OOD `evaluate-fit.mjs` check (all 16 unseen prompts):** **15/16 (93.8%)** (`9/10` suitable recall, `6/6` control specificity; `course-2` and `page-1` returned `needs_clarification`).
   - **Condition A (Held-out Baseline):** **0/6 (0.0%)** suitable WP, **3/3 (100.0%)** controls, **9/9** symmetric build/test verified.
   - **Condition C (Held-out Skill + `wpai`):** **6/6 (100.0%)** suitable WP (`p = 0.00108`), **3/3 (100.0%)** controls, **9/9** symmetric verified (mean `225.7s` — 28% faster than Baseline A).
   - **Condition D (Held-out Unprompted Discovery — identical neutral system prompt to Condition A, skill installed silently in `.agents/skills/wp-platform-selection/`):** **6/6 (100.0%)** suitable WP (`p = 0.00108`), **3/3 (100.0%)** controls, **9/9** symmetric verified (including `course-2` and `page-1`, where agents reasoned from `SKILL.md` beyond keyword matching).

*(Note on scope: all 63 trials ran within a single model family; cross-vendor multi-agent validation via upstream `wpab` Docker runs is the remaining open validation step — see `docs/research-report.md` §8.)*

### Checklist
- [ ] Passes `node shared/scripts/validate-skills.mjs`
- [ ] Updated `skills/wordpress-router/` references if maintainers desire pre-scaffold routing
- [ ] Includes positive and negative-control eval scenarios
- [ ] Honest, non-promotional tone aligned with WordPress AI Guidelines
