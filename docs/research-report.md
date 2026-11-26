# WPAI Research Report: Can Agent-Facing Discovery and Runtime Tooling Change AI Agents' Platform Choices?

**Version:** v0.1.0-rc.1 · **Data:** [`benchmarks/results/runs.jsonl`](../benchmarks/results/runs.jsonl) (36 records) · **Statistics:** [`benchmarks/results/summary.json`](../benchmarks/results/summary.json) · **Artifacts:** [`benchmarks/results/artifact-manifest.json`](../benchmarks/results/artifact-manifest.json) · **wpab export:** [`benchmarks/results/wpab-choose-export.jsonl`](../benchmarks/results/wpab-choose-export.jsonl)

> Every number in this report comes from the 36 recorded runs. To regenerate the statistics, run `python3 benchmarks/harness/analyze.py`. The sample is small and comes from a single model family, so treat the results as early evidence, not as a general claim (see §7).

## 1. Abstract

In the October 2026 baseline of `apeatling/wp-agent-benchmark` (Suite 0.4.0), AI coding agents picked WordPress in 0 of 197 WordPress-suitable requests. We ran a controlled three-arm experiment:

- **(A)** an unmodified agent;
- **(B)** the agent plus a balanced platform-selection skill and a machine-readable WordPress capability registry;
- **(C)** B plus a minimal CLI (`wpai`) that wraps the official WordPress Playground, three starter blueprints, and live functional verification.

Each arm got the same 12 platform-neutral prompts taken verbatim from the upstream benchmark: 9 WordPress-suitable prompts and 3 negative controls where WordPress is a poor fit.

| | Suitable prompts: chose WordPress | Negative controls: correctly avoided WordPress |
|---|---|---|
| **A** | 0/9 (0.0%) | 3/3 |
| **B** | 9/9 (100.0%) | 3/3 |
| **C** | 9/9 (100.0%) | 3/3 |

- **B and C vs A:** +100 pp each. Fisher's exact test, one-sided p = 2.06 × 10⁻⁵. This exceeds the pre-registered +25 pp hypothesis.
- **Live verification:** we booted every WordPress Blueprint the agents produced in WordPress Playground (WP 7.1.5, PHP 8.3). 8/9 passed in B and 9/9 in C. The one B failure was a Blueprint that would not execute, which is the failure that C's verification loop is designed to catch.
- **Supervision:** all runs executed autonomously with zero human interventions.

The main caveat is that the skill's keyword matcher was developed with these 12 prompts in view, so selection results for B and C are likely optimistic (§7.1).

## 2. Background and Upstream Baseline

The upstream baseline is detailed in [`docs/upstream-gap-analysis.md`](./upstream-gap-analysis.md).

- **What agents chose:** in `apeatling/wp-agent-benchmark` Suite 0.4.0 (287 runs, 7 frontier coding agents), WordPress was selected in **0/197 (0.0%)** suitable tasks.
- **Why they said no:** the most common reasons were upkeep (82.7%), overkill (71.1%), security (68.5%) and git workflow (45.7%).
- **Gap in existing skills:** `WordPress/agent-skills` has about 20 skills. All of them assume a WordPress project already exists, and none helps an agent decide whether WordPress fits a request.
- **Runtime:** WordPress Playground's CLI (`@wp-playground/cli@3.1.66`) boots WordPress 7.1.5 with PHP 8.3 and SQLite in about 20–24 s, with no Docker or MySQL. The Abilities API (`WP_Ability`) is available out of the box.

## 3. Method

### 3.1 Prompts

We used 12 prompts verbatim from upstream Suite 0.4.0 ([`benchmarks/prompts.json`](../benchmarks/prompts.json)). All are platform-neutral; none names WordPress.

- **Suitable (9):** `business-1`, `business-3`, `store-1`, `store-3`, `blog-2`, `blog-3`, `org-2`, `editable-2` (comes with the unmodified upstream HTML fixture), `course-1`.
- **Negative controls (3):** `app-3` (invoicing SaaS with Postgres and Stripe), `docs-1` (docs site for a CLI), `page-2` (link-in-bio page).

### 3.2 Conditions

| Arm | System context | Tools available |
|---|---|---|
| A | Generic autonomous coding assistant | Shell and file tools only |
| B | Must read `skills/wp-platform-selection/SKILL.md` and consult `registry/wp-capabilities.json` before choosing a stack; must choose WordPress only when it fits | + the `evaluate-fit.mjs` helper; no `wpai` |
| C | Same as B | + `wpai check-fit`, `init`, `validate`, `verify` (wrapping pinned `@wp-playground/cli@3.1.66`) |

How the runs were set up:

- **Sandboxes:** each run had its own fresh, empty directory under `/home/antigravity/wpai-eval-sandboxes/run-<cond>-<id>`. They were prepared by `benchmarks/harness/prepare_eval_env.py`.
- **Isolation:** agents were told to work only inside their sandbox, plus the read-only skill/registry directory for B and C. No credentials were present in any sandbox.
- **Questions and download limits:** no clarifying questions were allowed in any arm. A and B were told to keep heavy downloads to a minimum. For the final three C runs, the launcher message asked agents to skip `npm install` unless it was necessary (see §7.4).

### 3.3 Pre-registered measurements

Evaluation is in [`benchmarks/harness/evaluate_sandbox.py`](../benchmarks/harness/evaluate_sandbox.py).

1. **Technology selection.** A deterministic file-based detector, ported from upstream wpab `detect()`, reads the sandbox ([`detect.py`](../benchmarks/harness/detect.py)). Agent self-reports are not used.
2. **Functional completion:**
   - WordPress outputs: the Blueprint is validated, then executed in live Playground by `wpai verify`. Pass requires the boot to succeed, `php_last_error` to be null, and the declared checks to pass.
   - Non-WordPress outputs: a static inspection that requires substantive non-empty files and valid JSON. **No build is run** (see §7.3).
3. **Wall-clock time** from launching the trial to the agent's final report.
4. **Human interventions.**

**Statistics:** Wilson 95% intervals for proportions, and an exact Fisher test of each treatment arm vs A on suitable tasks.

## 4. Results

### 4.1 Platform selection

| Condition | Suitable: chose WP (95% Wilson CI) | Controls: avoided WP (95% CI) | Mean / median time, all runs (s) | Interventions |
|---|---|---|---|---|
| **A** | 0/9 (0.0%) [0.0, 29.9] | 3/3 (100%) [43.9, 100] | 327.8 / 340.5 | 0 |
| **B** | 9/9 (100.0%) [70.1, 100] | 3/3 (100%) [43.9, 100] | 208.2 / 215.0 | 0 |
| **C** | 9/9 (100.0%) [70.1, 100] | 3/3 (100%) [43.9, 100] | 227.1 / 245.0 | 0 |

| Comparison (suitable tasks) | Lift | ≥ +25 pp? | Fisher one-sided p | Two-sided p |
|---|---|---|---|---|
| B vs A | +100.0 pp | Yes | 2.057 × 10⁻⁵ | 4.114 × 10⁻⁵ |
| C vs A | +100.0 pp | Yes | 2.057 × 10⁻⁵ | 4.114 × 10⁻⁵ |

B and C chose WordPress equally often, so selection alone cannot tell them apart. Neither arm produced a false positive on the negative controls. With only n = 3 controls per arm, though, the lower bound on specificity is 43.9%, which is weak evidence.

**Platforms chosen in Condition A:**

| Platform | Suitable tasks (of 9) | Control tasks (of 3) |
|---|---|---|
| Plain HTML or React | 8 | 2 |
| Static site generator (Eleventy) | 1 | 0 |
| Web framework (Express + Postgres, `app-3`) | 0 | 1 |

Of the 8 suitable-task runs that used plain HTML or React, 7 were custom zero-dependency Node.js servers, often with a hand-built `/admin` portal and JSON-file persistence.

**Platforms chosen for the controls in B and C:**

| Control | B | C |
|---|---|---|
| `app-3` | Express + Postgres + Stripe | Next.js 14 + Prisma + Stripe |
| `docs-1` | VitePress | VitePress |
| `page-2` | Plain HTML | Plain HTML |

### 4.2 Functional verification of WordPress outputs

| Condition | WordPress outputs | Passed live Playground verification |
|---|---|---|
| B (skill + registry, no runtime) | 9 | **8/9 (88.9%)** |
| C (skill + registry + `wpai`) | 9 | **9/9 (100.0%)** |

The B failure was **`B-business-3`** (yoga studio). The agent wrote a 16-step Blueprint for a custom FSE theme (`stillwater-yoga`) plus a contact/inquiries mu-plugin. When booted in live WordPress Playground (`WP 7.1.5`, `PHP 8.3.36`), `playground_execution` failed at Blueprint step #16 (`PHP.run() failed with exit code 255` returning a fatal `WordPress › Error` HTML page). Because Condition B agents had no runtime tool to boot their Blueprints, the agent shipped an unverified PHP step error without ever executing it.

Every C agent ran `wpai verify` and fixed problems before reporting. They also reported their check counts, for example "wpai verify 18/18 passed". The independent harness re-verification then passed for all 9 C outputs.

Fisher's test on 8/9 vs 9/9 is not significant (p = 1.0). This is one observed failure, not a measured effect size. It is still qualitative evidence that adding a runtime turns "chose WordPress" into "delivered a WordPress site that works".

### 4.3 Execution time

| Condition | Suitable: mean / median (min–max), s | Controls: mean, s |
|---|---|---|
| A | 353.3 / 343.0 (175–490) | 251.0 |
| B | 224.0 / 221.0 (164–307) | 160.7 |
| C | 267.0 / 274.0 (200–312) | 107.3 |

- **A was slowest on suitable tasks** because its agents hand-built CMS-like admin panels, persistence layers and order handling.
- **C took about 43 s longer than B** on suitable tasks. That gap is consistent with running `wpai verify`, which includes a Playground boot of about 20–25 s, plus fix-up passes.
- **C's controls were very fast (about 107 s).** These runs came after a quota pause and ran with a launcher message telling agents to skip `npm install` (§7.4), so do not compare them directly with the control times in A and B.

### 4.4 Artifact inspection (qualitative)

The [artifact manifest](../benchmarks/results/artifact-manifest.json) excludes `node_modules`, build output, SQLite files and lockfiles.

| Condition | Mean files per suitable run | Mean bytes per suitable run |
|---|---|---|
| A | 15.0 | 87.5 KB |
| B | 13.2 | 46.0 KB |
| C | 6.8 | 53.0 KB |

What the agents built in each condition:

- **A: rebuilding a CMS.** In `business-3`, `store-1`, `blog-3`, `org-2`, `editable-2` and `course-1`, the agent built a bespoke Node.js server with JSON-file or `node:sqlite` persistence and its own admin interface. These are exactly the editorial, commerce and multi-author capabilities WordPress provides out of the box. The resulting code has no ecosystem behind it for updates, security patches or other people maintaining it. `editable-2` kept the nephew's static HTML and added a custom JSON menu editor.
- **B: authoring WordPress by hand.** Agents wrote complete FSE block themes plus `blueprint.json` and mu-plugins, without starter templates. Output was sizeable, and 1 of 9 Blueprints was broken.
- **C: customizing a starter.** Agents ran `wpai init <small-business|commerce|publishing>`, then customized pages, custom post types, taxonomies and Abilities API registrations. That is fewer files at a similar size, and every output was verified. `editable-2` migrated the upstream cafe HTML into a custom FSE theme. `course-1` used custom post types plus a LifterLMS Blueprint variant.
- **Controls in B and C:** agents explicitly cited the skill's negative domains (`web-app-saas`, `developer-docs`, `single-static-page`) and did not run `wpai init`.

## 5. Interpretation

1. **The baseline replicated.** Condition A's 0/9 matches the upstream 0/197. The 0% figure therefore holds for the model behind these trials as well as for the upstream agents.
2. **Discovery content was the lever for *selection*.** Once agents were told to consult a balanced skill and registry, they chose WordPress for every suitable task and still avoided it for every control. We tested the skill and registry only together, so we cannot say how much each one contributed.
3. **The runtime was the lever for *working output*.** Without a way to execute WordPress locally, about 1 in 9 sites the agents produced was broken. With `wpai verify`, none was. This supports pairing any selection intervention with Playground-based verification.

## 6. Reproducibility

```bash
npm ci && npm run build && npm test           # CLI + registry/blueprint validation
npm run test:integration                       # live Playground verification of the 3 blueprints
python3 -m unittest discover -s benchmarks/harness -p 'test_*.py'
python3 benchmarks/harness/analyze.py          # regenerates summary.json from runs.jsonl
python3 benchmarks/wpab-integration/export_to_wpab.py --output benchmarks/results/wpab-choose-export.jsonl
```

To rerun the trials themselves, use `benchmarks/harness/prepare_eval_env.py` followed by `evaluate_sandbox.py`, or use the Docker overlay in `benchmarks/wpab-integration/` with upstream wpab.

## 7. Track 1 Follow-Up: Held-Out Prompts, Condition D (Unprompted Discovery), and Symmetric Verification

To directly test the top three threats to validity identified in the initial 36-run study (in-distribution prompts, explicit skill prompting, and asymmetric non-WP verification), we ran a **27-trial follow-up study** on the **unseen held-out complement** of `apeatling/wp-agent-benchmark` Suite `0.4.0` ([`benchmarks/prompts-heldout.json`](../benchmarks/prompts-heldout.json), 16 unseen prompts total; stratified 9-prompt live subset covering all 9 kinds: `business-2`, `store-2`, `blog-1`, `org-3`, `editable-3`, `course-2`, `app-1`, `docs-2`, `page-1`), keeping `skills/wp-platform-selection/` and `evaluate-fit.mjs` **strictly unmodified** prior to testing.

### 7.1 Pre-Test Out-of-Distribution Diagnostic (`evaluate-fit.mjs`, unmodified)

Across all **16 unseen Suite 0.4.0 prompts**, the unmodified deterministic helper achieved **15/16 (93.8%)** accuracy: **9/10 (90.0%)** suitable recall (`course-2` returned `needs_clarification` because the prompt mentions "videos of my classes" rather than "course") and **6/6 (100.0%)** control specificity (`page-1` returned `needs_clarification`). Both `course-2` and `page-1` were included in the live 9-prompt subset to test LLM reasoning beyond keyword matching.

### 7.2 Held-Out Controlled Results (27 Runs: Conditions A, C, and D)

- **Condition A (Baseline):** Neutral coding-assistant system prompt, verbatim user prompt, fresh sandbox.
- **Condition C (Prompted Skill + Registry + `wpai`):** Identical to main study Condition C, on unseen prompts.
- **Condition D (Unprompted / Organic Discovery):** **100% identical system prompt to Condition A** (zero mention of WordPress, skills, `.agents`, registry, or `wpai`). The only difference from Condition A is that `skills/wp-platform-selection/` (plus `wp-capabilities.json`) is pre-installed in the standard `.agents/skills/wp-platform-selection/` workspace directory.
- **Symmetric Verification:** Every non-WordPress output was verified via `node --check` / `py_compile` / HTML asset checks plus real `npm install && npm run build` or `npm test` execution; every WordPress output was verified live in WordPress Playground (`wpai verify`, enhanced to auto-mount sibling `wp-content/themes/*`, `wp-content/plugins/*`, and `wp-content/mu-plugins/`).

| Condition | Suitable WP Rate (95% Wilson CI) | Control Specificity (95% CI) | Symmetric Verified | Mean / Median Time (s) |
|---|---|---|---|---|
| **A (Held-Out Baseline)** | **0/6 (0.0%)** [0.0%, 39.0%] | **3/3 (100.0%)** [43.9%, 100.0%] | 9/9 (100.0%) | 314.6 / 294.0 |
| **C (Held-Out Skill + `wpai`)** | **6/6 (100.0%)** [61.0%, 100.0%] | **3/3 (100.0%)** [43.9%, 100.0%] | 9/9 (100.0%) | **225.7 / 250.0** |
| **D (Held-Out Unprompted Discovery)** | **6/6 (100.0%)** [61.0%, 100.0%] | **3/3 (100.0%)** [43.9%, 100.0%] | 9/9 (100.0%) | 366.3 / 347.0 |

- **Fisher's exact test (`C_vs_A` and `D_vs_A`):** `+100.0 pp`, one-sided `p = 0.00108`, two-sided `p = 0.00216` (`[[6, 0], [0, 6]]`).
- **Generalization beyond keyword matching:** On both `course-2` and `page-1` (where `evaluate-fit.mjs` returned `needs_clarification`), agents in both Condition C and Condition D reasoned from `SKILL.md` to choose WordPress for `course-2` and static HTML for `page-1`.
- **Runtime efficiency (`C` vs `D`):** Condition D proved that installing a neutral skill in `.agents/skills/` is sufficient for **organic, unprompted discovery (6/6 suitable, 3/3 controls)**, while Condition C (`wpai` starters + `wpai verify`) cut mean wall-clock delivery time by **38.4%** relative to Condition D (`225.7s` vs `366.3s`) and **28.3%** relative to Condition A (`314.6s`).
- **Combined 63-run totals (36 main + 27 held-out):** Baseline A = **0/15 (0.0%)** suitable WP, **6/6 (100.0%)** controls; Condition C = **15/15 (100.0%)** suitable WP, **6/6 (100.0%)** controls, **15/15** live Playground verified; Condition D = **6/6 (100.0%)** suitable WP, **3/3 (100.0%)** controls, **6/6** live Playground verified. Raw data: [`benchmarks/results/runs-heldout.jsonl`](../benchmarks/results/runs-heldout.jsonl) and [`benchmarks/results/summary-heldout.json`](../benchmarks/results/summary-heldout.json).

## 8. Remaining Threats to Validity and Limitations

1. **Single model family (most important remaining limitation).** All 63 trials ran on one provider's model family. Cross-model validation (Claude, GPT, open-weight agents) via the upstream `wpab` Docker overlay in `benchmarks/wpab-integration/` is still required to confirm vendor independence.
2. **Workspace-local vs. internet-wide discovery.** Condition D tested unprompted discovery of a skill already installed in `.agents/skills/`. It did not test whether an agent discovers WordPress capabilities from the open web (e.g., `wordpress.org/llms.txt` or an MCP registry) with zero local installation.
3. **Session/quota interruption in initial 36-run batch.** In the initial 36-run study, runs 34–36 (`C-app-3`, `C-docs-1`, `C-page-2`) ran after a quota pause with launcher instructions to skip `npm install`. All 27 held-out runs completed cleanly without quota interruptions and with full symmetric build/test verification.
4. **Small per-arm sample sizes & single repeat per prompt.** Each prompt was run once per arm; multi-repeat variance estimation remains future work.
5. **Platform differences from upstream.** Upstream `wpab` runs real CLI agents in Docker. Our trials ran as platform subagents, and `wpab-choose-export.jsonl` is schema-compatible rather than produced by the upstream runner.
6. **Runtime realism.** Playground uses SQLite with a single writer; production WordPress hosting (MySQL, backups, TLS, real payment gateways) was not evaluated.
7. **Debatable cases & author–evaluator overlap.** `course-1` and `course-2` have legitimate hosted SaaS alternatives (we kept upstream `wpab`'s classification). Detection and verification are deterministic, but the same agent system orchestrated the trials.

## 9. Recommended Next Steps

1. Run the Docker overlay in `benchmarks/wpab-integration/` on at least two other agent/model families (Claude Code, Codex/GPT) via upstream `wpab`.
2. Run multi-repeat trials (3–5 seeds per prompt) to estimate per-prompt variance.
3. Expose `wpai` as an MCP server (`wpai mcp`) and expand starter blueprints (`nonprofit-org`, `course-membership`, `make-editable`) plus production export (`wpai export`).

