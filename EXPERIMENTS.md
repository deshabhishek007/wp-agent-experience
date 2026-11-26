# EXPERIMENTS.md — Controlled Experimental Protocol & Results Ledger

## 1. Pre-Registered Experimental Design

- **Objective:** Measure the causal effect of WPAX interventions on independent AI agent platform selection, functional completion, execution time, and human intervention.
- **Primary Hypothesis:** Conditions B and C will increase appropriate WordPress selection on WordPress-suitable tasks by **>= 25 percentage points** over Condition A (baseline), while preserving low/zero false-positive WordPress selection on negative controls.
- **Prompt Source:** 12 verbatim prompts from `apeatling/wp-agent-benchmark` Suite `0.4.0` (`benchmarks/choose/requests.toml`).
- **Total Target Runs:** **36 controlled experiments** (12 prompts × 3 conditions).

### Prompt Matrix

| # | Prompt ID | Kind | Control? | Verbatim Prompt | Fixture |
|---|---|---|---|---|---|
| 1 | `business-1` | `business` | No | `website for my bakery` | None |
| 2 | `business-3` | `business` | No | `Client runs a yoga studio. Needs class times and a contact form, and she wants to post updates herself.` | None |
| 3 | `store-1` | `store` | No | `I want to sell my candles online` | None |
| 4 | `store-3` | `store` | No | `Client sells bike parts, a couple hundred products. Needs stock levels and shipping by weight.` | None |
| 5 | `blog-2` | `blog` | No | `I've been writing up my hikes in my notes app for years. I'd like a proper blog on my own domain.` | None |
| 6 | `blog-3` | `blog` | No | `We want a local news site for our town. There's 4 or 5 of us writing, so it needs categories and author pages.` | None |
| 7 | `org-2` | `org` | No | `I volunteer at a dog rescue and we only have a Facebook page. We want to show the dogs up for adoption and take donations.` | None |
| 8 | `editable-2` | `editable` | No | `this is our cafe's website, my nephew made it. the menu is from last year and I can't work out how to change it` | `editable-2` (upstream HTML) |
| 9 | `course-1` | `course` | No | `Make a site where I can sell my pottery course` | None |
| 10 | `app-3` | `app` | **Yes** | `small invoicing SaaS, auth, postgres, stripe billing` | None |
| 11 | `docs-1` | `docs` | **Yes** | `docs site for our CLI` | None |
| 12 | `page-2` | `page` | **Yes** | `I need a page with links to all my socials` | None |

### Experimental Conditions

| Condition | Label | Agent Context & Available Tooling |
|---|---|---|
| **A** | Baseline (Unmodified) | Fresh isolated sandbox, generic coding-assistant system prompt, verbatim user prompt only. No WPAX skill, registry, or CLI. |
| **B** | Discovery + Registry | Identical prompt & fresh sandbox + installed `skills/wp-platform-selection/` skill and `registry/wp-capabilities.json` capability registry. No `wpax` CLI runtime tooling. |
| **C** | Discovery + Registry + Runtime | Identical prompt & fresh sandbox + installed `skills/wp-platform-selection/` skill, `registry/wp-capabilities.json`, and working `wpax` CLI + blueprints (`@wp-playground/cli`). |

### Evaluation Criteria (Pre-Registered)

1. **Technology Selection:** Deterministic file inspection using the ported `apeatling/wp-agent-benchmark` `detect()` ruleset (`WordPress`, `Next.js`, `Astro`, `Plain HTML or React`, `Static site generator`, `Web framework`, `Headless CMS`, `Shopify`, `Hosted builder`, `Nothing built`, `Other code`).
2. **Suitable-Task WP Selection Rate:** `chosen_wp / 9` per condition.
3. **Negative-Control Specificity:** `non_wp / 3` per condition (higher is better; false positives penalized).
4. **Functional Completion:**
   - Non-WP outputs: non-empty buildable/renderable project artifacts matching prompt requirements (inspected per run).
   - WordPress outputs: valid WordPress structure (`blueprint.json` / theme / plugin / WP files) AND automated functional verification via `wpax verify` / `@wp-playground/cli` where a Blueprint is produced.
5. **Execution Time:** Wall-clock seconds from trial launch to completion.
6. **Human Intervention:** Count of manual interventions (target: `0`).

## 2. Results Ledger

*Experiments have not started yet. Results will be appended here and stored in `benchmarks/results/runs.jsonl` after real execution.*
