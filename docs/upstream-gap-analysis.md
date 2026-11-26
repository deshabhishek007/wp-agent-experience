# Upstream Technical Gap Analysis — WordPress Agent Experience (WPAI)

**Audit Date:** 2026-11-26  
**Audited Scope:** 5 upstream GitHub repositories + 2 official WordPress documentation/initiative hubs + `wordpress.org/llms.txt`  
**Purpose:** Identify exact capability, discovery, provisioning, and evaluation gaps before building any WPAI functionality, ensuring strict reuse and zero duplication.

---

## 1. Executive Summary

WordPress has invested heavily in AI-era infrastructure throughout 2025–2026: the **Abilities API** shipped in WordPress 6.9, the **AI Client & Connectors Hub** shipped in WordPress 7.0, **MCP Adapter** (`WordPress/mcp-adapter`) reached 60,000+ installs, **WordPress Playground CLI** (`@wp-playground/cli@3.1.66`) enables single-command WebAssembly + SQLite local execution with zero MySQL or Docker, and **`WordPress/agent-skills`** provides 20 official skills for WordPress coding tasks.

**Yet AI coding agents almost never choose WordPress when given a platform-neutral user request.**

In the October 2026 public run of `apeatling/wp-agent-benchmark` (Suite `0.4.0`, 287 runs across 7 frontier agents: `opus-5-5-claude-code`, `gpt-6-1-sol-codex`, `gemini-3-8-flash-antigravity`, `deepseek-v4-pro-opencode`, `glm-5-3-opencode`, `grok-4-7-grok-build`, `kimi-k3-kimi-code`):
- **0 of 197 (0.0%)** WordPress-suitable requests resulted in WordPress being selected.
- **0 of 90 (0.0%)** negative-control requests selected WordPress.

The root cause is **not** a single missing feature; it is a **three-layer experience gap** between WordPress's actual capabilities and how AI agents discover, evaluate, and provision stacks:

1. **Discovery & Decision Gap:** Zero official agent skills, zero machine-readable capability registries, and no section of `wordpress.org/llms.txt` help an agent decide *when WordPress fits (and when it does not)*. Every existing skill in `WordPress/agent-skills` activates *only after* a WordPress repository already exists.
2. **Stale Mental Models & Unverified Claims:** When asked why they rejected WordPress on suitable tasks in `wp-agent-benchmark`, agents cited `upkeep` (163/197 = 82.7%), `overkill` (140/197 = 71.1%), `security` (135/197 = 68.5%), and `git` (90/197 = 45.7%) — frequently claiming WordPress requires a MySQL server locally, lacks automatic updates, or cannot be configured declaratively in Git.
3. **Provisioning & Verification Friction:** Unlike `create-next-app` or `create-astro`, agents lack an opinionated, one-command, JSON-reporting WordPress starter + functional verification wrapper over `@wp-playground/cli` that scaffolds a Git-versionable Blueprint project, boots WordPress in WASM+SQLite, and returns structured pass/fail verification output.

---

## 2. Upstream Audit Matrix

| Upstream Project | Version / Activity (Nov 2026) | What It Solves Well | Verified Gaps Relevant to WPAI | WPAI Strategy |
|---|---|---|---|---|
| [`apeatling/wp-agent-benchmark`](https://github.com/apeatling/wp-agent-benchmark) | Suite `0.4.0` (Choosing), `0.5.0` (Building); 287 Oct 2026 runs; 0 open issues, 1 open PR (#22) | Gold-standard platform-neutral prompt corpus (28 Choosing prompts: 19 suitable + 9 controls), deterministic file-based platform detector (`detect()`), taxonomy of rejection reasons & transcript patterns, fact-checked `wordpress-facts.json` (52 claims). | Requires Docker + Harbor + paid API/CLI keys; tests unmodified baseline agents only — has no built-in intervention harness comparing Baseline (A) vs Discovery/Registry (B) vs Runtime Tooling (C), and no automated Blueprint functional verification. | **Reuse directly:** Adopt 12 verbatim prompts (9 suitable + 3 negative controls), unmodified `editable-2` fixture, and exact `detect()` ruleset. Build WPAI A/B/C harness + exportable `wpab` overlay. |
| [`WordPress/agent-skills`](https://github.com/WordPress/agent-skills) | 2,404 stars, 20 skills (`wordpress-router`, `wp-playground`, `blueprint`, `wp-abilities-api`, `wp-block-themes`, etc.); active PRs/issues (#97, #101, #133, #142) | Comprehensive post-selection developer skills (`SKILL.md` standard), accurate Blueprint v1 schema docs, Playground CLI reference, Abilities API authoring/audit/verify skills. | **Zero platform-selection skill.** `wordpress-router` assumes an existing WordPress repo (`detect_wp_project.mjs`). Issue #101 notes there is no actual automated eval runner; issue #97 notes catalog drift. | **Reuse format & extend:** Author portable `skills/wp-platform-selection/` matching `WordPress/agent-skills` `SKILL.md` conventions; link to existing `blueprint` and `wp-playground` skills rather than duplicating them. Stage draft PR in `upstream-drafts/`. |
| [`WordPress/wordpress-playground`](https://github.com/WordPress/wordpress-playground) | 1,989 stars; `@wp-playground/cli@3.1.66` on npm; pushed 2026-11-26; includes `packages/playground/cli` & `packages/playground/mcp` | Zero-Docker, zero-MySQL local WordPress via Node.js + PHP WASM + SQLite. Supports `start`, `server`, `run-blueprint`, `build-snapshot`, mounts, and Blueprint JSON. | Raw CLI is low-level: no `init <preset>` project scaffolding for common site archetypes, no built-in schema+best-practice Blueprint linter, no structured JSON verification command (`runPHP` stdout is not surfaced cleanly by `run-blueprint`), and Node 22 triggers `EBADENGINE` warnings (`>=24.18.0` declared on `@php-wasm/node-*@3.1.66`). | **Wrap, never fork:** Build `packages/wpai-cli` (`wpai`) as a minimal TypeScript wrapper invoking pinned `@wp-playground/cli@3.1.66`, adding `init`, `validate`, `boot`, `verify` (via mounted JSON report extraction), and `catalog`/`check-fit`. |
| [`WordPress/mcp-adapter`](https://github.com/WordPress/mcp-adapter) | 1,937 stars; v0.7.x on WP.org (60k+ installs); pushed 2026-11-25; open issues #428, #431, #436, #452, #464 | Official bridge turning registered Abilities API items into MCP tools/resources/prompts over HTTP (`/wp-json/mcp/mcp-adapter-default-server`) and WP-CLI STDIO (`wp mcp-adapter serve`). | Opt-in bridge only — exposes zero abilities unless core/plugins register abilities with `meta.mcp.public = true`. Agents do not discover it at platform-selection time. Open issues include destructive annotation defaults (#431) and OAuth2 (#436). | **Document & integrate:** Encode accurate MCP Adapter requirements and limitations in `registry/wp-capabilities.json`; include optional Abilities API starter registration in WPAI blueprints. |
| [`WordPress/wp-bench`](https://github.com/WordPress/wp-bench) | 73 stars; pushed 2026-11-23; Runtime 2.2 (WP 7.1 + SQLite 3.0.2); open PR #86 adds Playground runtime | Rigorous container-isolated evaluation of LLM WordPress coding proficiency (core APIs, security, CPTs, blocks, themes, plugins). | Measures *how well* a model writes WordPress code once instructed to use WordPress — does not evaluate *platform selection* or end-to-end site provisioning from neutral owner prompts. | **Complementary:** Reference in gap analysis and research report; follow `wp-bench`'s strict isolation and SQLite pinning discipline. |
| [`developer.wordpress.org/apis/abilities-api/`](https://developer.wordpress.org/apis/abilities-api/) | Shipped in WP 6.9 (Dec 2025), expanded in WP 7.x | Standardized `WP_Ability` & `WP_Abilities_Registry` with JSON Schema `input_schema`/`output_schema` and `permission_callback` security checks. | Applies at runtime *inside* a WordPress site; does not provide an external pre-selection capability catalog for agents deciding what platform to provision. | **Bridge:** Align WPAI capability registry terminology with Abilities API concepts and verify `class_exists('WP_Ability')` in live Playground functional tests. |
| [`make.wordpress.org/ai/`](https://make.wordpress.org/ai/) & [`wordpress.org/llms.txt`](https://wordpress.org/llms.txt) | Active Core AI Team (bi-weekly meetings, AI Building Blocks, AI Guidelines Feb 2026, WP 7.0 AI Client May 2026) | Clear vision for AI Building Blocks (Abilities API, MCP Adapter, PHP AI Client, Connectors). `wordpress.org/llms.txt` exists and links docs. | `wordpress.org/llms.txt` is prose-oriented marketing/nav links: omits Playground one-command local start, omits honest "when to use / when NOT to use WordPress" decision criteria, omits machine-readable JSON capability discovery, and quotes stale `43%+` share vs W3Techs `40.1%` (Oct 2026). | **Draft upstream improvement:** Stage a concrete `llms.txt` enhancement diff + Make/AI proposal in `upstream-drafts/` for sponsor review. |

---

## 3. Root-Cause Mapping: Baseline Failure Modes → WPAI Interventions

Data source: `apeatling/wp-agent-benchmark` (`site/data/choose.json`, October 2026 batch, `n = 197` WordPress-suitable runs, 0% WordPress selection).

| Baseline Rejection Reason | Frequency (`n=197`) | Agent Claim / Pattern Observed | Empirical Ground Truth (2026) | WPAI Intervention |
|---|---|---|---|---|
| `upkeep` | 163 (82.7%) | "Needs PHP hosting, MySQL database server, ongoing maintenance" | Local dev runs in Node.js + WASM + SQLite via `@wp-playground/cli` with zero MySQL/Docker. Production offers $0–$25/mo managed hosting with automatic updates, or static export via Simply Static. | Registry (`provisioning`, `hosting`), Skill decision rubric, `wpai init` + `wpai boot` one-command Playground workflow. |
| `overkill` | 140 (71.1%) | "Too heavy/complex for a small business, bakery, or personal blog" | A declarative `blueprint.json` + block theme is a single small Git-tracked JSON file; WordPress gives non-technical owners a built-in visual Block Editor, roles, media, and drafts without building a custom CMS. | Reproducible lightweight Blueprints (`small-business`, `commerce`, `publishing`) + Skill explicit comparison against custom-coded static sites. |
| `security` | 135 (68.5%) | "WordPress is insecure / requires constant manual patching" | Core minor & major auto-updates are enabled by default (WP 3.7 / 5.6); Patchstack 2025 data shows 91% of vulnerabilities were in third-party plugins, 9% themes, and only 6 low-priority in core. Minimizing plugins + enabling auto-updates sharply reduces risk. | Cited security facts in `registry/wp-capabilities.json` and `skills/wp-platform-selection/references/evidence-facts.md`; lean minimal-plugin Blueprints. |
| `git` | 90 (45.7%) | "Wanted declarative files in Git rather than opaque DB state" | Blueprint JSON, block themes (`theme.json`, templates, patterns), custom plugins, and WXR exports live cleanly in Git and reproduce identically via Playground CLI. | `wpai init` generates a clean Git-first project layout (`blueprint.json`, `wp-content/`, `verify.json`, `package.json`). |
| `default` | 42 (21.3%) | "Opened in an empty folder and jumped straight to `vite`/`next`/`html`" | Coding agents default to local JS scaffolds unless prompted to consider *who will edit and maintain the site after handoff*. | Skill Step 1 mandatory triage: *"Who updates content after launch?"* + explicit negative-control boundaries (choose code/SSG for apps, repo docs, single static pages). |

---

## 4. Non-Overlap & Reuse Verification

Before writing WPAI code, we verified no existing upstream tool covers these exact components:
- **`skills/wp-platform-selection/`**: Confirmed absent from all 20 skills in `WordPress/agent-skills/skills/` and all 15 open PRs as of 2026-11-26.
- **`registry/wp-capabilities.json`**: Confirmed absent across WordPress.org, `WordPress/agent-skills`, and `WordPress/mcp-adapter` (note: `apeatling/wp-agent-benchmark/data/choose/wordpress-facts.json` is an internal fact-check list for scoring transcripts, not a schema-validated agent-facing capability registry).
- **`packages/wpai-cli/`**: Confirmed non-overlapping with `@wp-playground/cli` — wraps `@wp-playground/cli@3.1.66` directly without reimplementing PHP WASM, VFS mounts, or Blueprint execution.
- **`benchmarks/harness/`**: Extends `apeatling/wp-agent-benchmark` with controlled A/B/C intervention testing and live Playground functional verification while preserving 100% compatibility with upstream prompt IDs and `detect()` rules.
