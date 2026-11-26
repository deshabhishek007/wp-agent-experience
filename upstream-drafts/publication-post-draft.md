# Publication Draft — Why AI Agents Never Pick WordPress (and What Happens When Discovery Meets Playground Verification)

**Status:** DRAFT — NOT PUBLISHED (awaiting sponsor approval)  
**Target Venues:** Technical blog post / Make WordPress AI discussion / Engineering research note

---

## Summary

In October 2026, [`apeatling/wp-agent-benchmark`](https://github.com/apeatling/wp-agent-benchmark) (`Suite 0.4.0`) tested 7 frontier AI coding agents across 287 website-building runs. On the 197 tasks specifically suited to a CMS — bakeries, yoga studios, small online shops, multi-author local news sites, charities, and legacy hand-coded HTML sites that owners couldn't update — AI agents chose WordPress **0 times (0.0%)**.

Even more striking than what agents rejected was **what they built instead**: in our baseline reproduction, when asked to build a yoga studio site, candle shop, local newsroom, or dog rescue site, unmodified agents spent 5–8 minutes hand-rolling custom Node.js HTTP servers, JSON-file databases, and bespoke `/admin` portals from scratch — reinventing a brittle single-project CMS to avoid what they assumed was WordPress's heavy MySQL setup, manual patching burden, and hostility to Git.

We ran **WordPress Agent Experience (WPAX)** to test a straightforward hypothesis: *if we give coding agents honest, structured platform-selection guidance, a machine-readable capability registry, and a one-command WordPress Playground verification CLI, do they choose WordPress when it fits — without forcing WordPress onto SaaS apps, CLI docs, or static link pages?*

---

## Three Gaps We Found in Upstream WordPress AI Tooling

Auditing `WordPress/agent-skills`, `WordPress/wordpress-playground`, `WordPress/mcp-adapter`, `WordPress/wp-bench`, the WordPress Abilities API, and `wordpress.org/llms.txt` revealed three specific gaps:

1. **Zero pre-scaffold platform-selection guidance:** All 20 skills in `WordPress/agent-skills` assume a WordPress repository *already exists*. Nothing helps an agent decide *whether* WordPress fits a user's greenfield request.
2. **Outdated mental models in `llms.txt` and model weights:** Agents cite `upkeep` (82.7%), `overkill` (71.1%), `security` (68.5%), and `git` (45.7%) — unaware that `@wp-playground/cli` boots WordPress 7.1.5 + PHP 8.3 + SQLite in ~20 seconds with zero MySQL/Docker, that Blueprints are declarative JSON in Git, and that WP 6.9+ ships a native `WP_Ability` capability registry.
3. **No closed-loop functional verification wrapper:** `run-blueprint` runs headlessly, but agents lacked a simple JSON-emitting `init -> validate -> verify` loop to confirm that their generated Blueprint, custom post types, REST routes, and Abilities actually boot cleanly without PHP errors.

---

## Controlled 36-Run Experiment (`Suite 0.4.0` Prompts)

We evaluated 12 verbatim platform-neutral prompts from `wp-agent-benchmark` (9 WordPress-suitable tasks + 3 negative controls: an invoicing SaaS with Postgres/Stripe, CLI documentation, and a social link-in-bio page) across three isolated arms (`n = 36` total runs):

- **Condition A (Baseline):** Unmodified coding agent in a clean sandbox.
- **Condition B (Discovery + Registry):** Agent equipped with `skills/wp-platform-selection/SKILL.md` and `registry/wp-capabilities.json` (no runtime CLI).
- **Condition C (Discovery + Registry + Runtime):** Condition B plus `@wpax/cli` wrapping pinned `@wp-playground/cli@3.1.66` (`wpax init`, `validate`, `verify`).

| Condition | Suitable Tasks: Chose WP (95% Wilson CI) | Negative Controls: Avoided WP | Live WP Playground Verified | Mean Time — Suitable Tasks |
|---|---|---|---|---|
| **A (Baseline)** | **0/9 (0.0%)** [0.0%, 29.9%] | **3/3 (100.0%)** | n/a (0 WP outputs) | 353.3 s |
| **B (Skill + Registry)** | **9/9 (100.0%)** [70.1%, 100.0%] | **3/3 (100.0%)** | **8/9 (88.9%)** | 224.0 s |
| **C (Skill + Registry + `wpax`)** | **9/9 (100.0%)** [70.1%, 100.0%] | **3/3 (100.0%)** | **9/9 (100.0%)** | 267.0 s |

### Key Takeaways

1. **Discovery changed selection (`p = 2.06 × 10⁻⁵`):** Both Condition B and Condition C lifted WordPress selection on suitable tasks from **0% to 100%** (Fisher's exact test one-sided `p = 2.057e-05`), while keeping **3/3 (100%)** restraint on negative controls (`app-3` → Express/Next.js + Postgres + Stripe; `docs-1` → VitePress; `page-2` → plain HTML/CSS).
2. **Runtime verification caught broken Blueprints:** In Condition B (`B-business-3`), the agent hand-authored a 16-step Blueprint without a runtime tool; when we booted it in live WordPress Playground (`WP 7.1.5`), step #16 failed with a fatal PHP exit code `255`. Every Condition C agent ran `wpax verify` against live WordPress Playground before finishing, resulting in **9/9 (100%)** verified working sites.
3. **Less bespoke boilerplate, faster than reinventing a CMS:** Condition C agents finished suitable tasks ~86 seconds faster on average than Condition A agents (267.0s vs 353.3s) because they customized verified Blueprints instead of writing custom admin portals from scratch.

---

## Follow-Up Validation: Held-Out Prompts & Unprompted Discovery (`n = 27`)

To verify that these gains were not an artifact of prompt overlap or explicit skill instructions, we ran a 27-trial follow-up on **9 completely unseen** `Suite 0.4.0` prompts (6 suitable + 3 controls across all 9 kinds) with **strictly unmodified** skills and **symmetric verification** (running real `npm run build` / `npm test` on non-WordPress outputs):

- **Condition A (Held-Out Baseline):** `0/6 (0.0%)` suitable WP, `3/3 (100.0%)` controls, `9/9` symmetric verified (`314.6s` mean).
- **Condition C (Held-Out Skill + `wpax`):** `6/6 (100.0%)` suitable WP (`p = 0.00108`), `3/3 (100.0%)` controls, `9/9` verified (`225.7s` mean — **38.4% faster than Condition D**).
- **Condition D (Unprompted Discovery — identical system prompt to Baseline A, skill installed silently in `.agents/skills/`):** `6/6 (100.0%)` suitable WP (`p = 0.00108`), `3/3 (100.0%)` controls, `9/9` verified (`366.3s` mean). Even on `course-2` and `page-1` where the static keyword helper returned `needs_clarification`, agents reasoned directly from `SKILL.md` to make the right call.

---

## Limitations & What Needs Testing Next

To keep these findings grounded:
- **Single model family & small `n`:** All 63 runs (36 main + 27 held-out) executed within a single model family. Running our `benchmarks/wpab-integration/` Docker overlay across all 7 multi-vendor agents in `wp-agent-benchmark` (Claude, GPT, Gemini, open-weight) is the essential next validation step.
- **Workspace-local vs. open-web discovery:** Condition D proves agents organically discover a skill installed in `.agents/skills/`, but does not yet measure discovery from `wordpress.org/llms.txt` or a remote MCP server with zero local setup.
- **Local SQLite vs production MySQL:** WordPress Playground's WebAssembly + SQLite runtime makes local agent provisioning and CI verification trivial, but production multi-user/WooCommerce deployments still require managed WordPress or MySQL/MariaDB hosting.

All code, JSON schemas, blueprints, raw `runs.jsonl` / `runs-heldout.jsonl` records, statistical scripts, and draft upstream contributions are reproducible from the WPAX repository.
