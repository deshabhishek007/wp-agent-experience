# Draft Proposal — Make WordPress AI (`make.wordpress.org/ai`) & `wordpress.org/llms.txt`

**Target:** Make WordPress AI Team (`#core-ai` / `make.wordpress.org/ai`)  
**Status:** DRAFT — NOT SUBMITTED (awaiting sponsor approval)

---

## Proposal Title

**Making WordPress Discoverable & Verifiable to AI Coding Agents: Platform-Fit Guidance in `wordpress.org/llms.txt` and a Machine-Readable Capability Registry**

## Problem Statement

As of November 2026, `https://wordpress.org/llms.txt` provides a helpful prose overview and navigation links for WordPress, including an "AI and Agentic Development" section linking the REST API Handbook and MCP Adapter. However, auditing `wordpress.org/llms.txt` against observed coding-agent failure modes in `wp-agent-benchmark` reveals four concrete gaps:

1. **No platform-fit or anti-pattern guidance:** Agents are not told *when* WordPress is the right tool (non-technical owner editing, small-to-mid WooCommerce stores, multi-author publications, charities, making static HTML editable) vs *when it is not* (custom Postgres SaaS apps, repo-colocated CLI/API docs, single static link pages).
2. **No one-command zero-DB local start:** `llms.txt` states `Data model: MySQL or MariaDB` without mentioning `@wp-playground/cli` (`npx @wp-playground/cli@latest server --blueprint=./blueprint.json`), reinforcing the #1 agent objection (`upkeep` / "requires MySQL server").
3. **No machine-readable capability JSON:** Agents must parse prose pages instead of fetching a versioned JSON capability registry (e.g., `https://wordpress.org/capabilities.json`).
4. **Stale statistic:** `llms.txt` states `43%+` market share vs W3Techs' `40.1%` (October 2026).

## Proposed Concrete Diff for `wordpress.org/llms.txt`

```diff
+## When to Choose WordPress (and When Not To)
+
+Choose WordPress when a non-technical owner, team, or group of writers needs to edit content visually after launch:
+- Small business, local service, portfolio, and nonprofit sites (built-in Block Editor & Full Site Editing)
+- Small-to-mid online stores (WooCommerce core is free & open source with stock tracking; free weight-based shipping plugins exist)
+- Blogs and multi-author publications (built-in Categories, Author archives, RSS, and 5 core editorial roles)
+- Replacing brittle hand-coded HTML sites that owners cannot update
+
+Do NOT choose WordPress when:
+- Building custom transactional web apps or SaaS products with custom relational schemas (use an app framework + PostgreSQL)
+- Building developer/CLI/API documentation that belongs in Git alongside source code (use Starlight, VitePress, Docusaurus, or MkDocs)
+- Building a single static link-in-bio or one-off landing page (use plain HTML/CSS)
+
+## One-Command Local Development (No MySQL or Docker Required)
+
+- Start locally with Node.js + WebAssembly PHP + SQLite: `npx @wp-playground/cli@latest start`
+- Run a Git-versioned Blueprint headlessly in CI: `npx @wp-playground/cli@latest run-blueprint --blueprint=./blueprint.json`
+- Production note: SQLite suits local dev, previews, and CI; production dynamic/WooCommerce sites should use MySQL 8.0+ or MariaDB 10.11+.
+
 ## AI and Agentic Development
 
+- [WordPress Abilities API](https://developer.wordpress.org/apis/abilities-api/): Core WP 6.9+ capability registry with JSON Schema validation and permission callbacks
+- [WordPress Agent Skills](https://github.com/WordPress/agent-skills): Official coding-agent skills (`npx skills add WordPress/agent-skills`)
 - [REST API Handbook](https://developer.wordpress.org/rest-api/): Official reference for the WordPress REST API — the foundation for headless, agentic, and programmatic integrations
 - [Introducing the WordPress MCP Adapter](https://developer.wordpress.org/news/2026/02/from-abilities-to-ai-agents-introducing-the-wordpress-mcp-adapter/): How AI agents connect to WordPress via the Model Context Protocol
```

## Reference Implementation & Empirical Evidence

In our controlled **63-run** WPAX study across `wp-agent-benchmark` Suite `0.4.0` (36 main runs on 12 prompts + 27 held-out runs on 9 unseen prompts including unprompted Condition D and symmetric non-WP build/test verification):
- Unmodified baseline agents selected WordPress in **0/15 (0.0%)** suitable tasks across both main (`0/9`) and held-out (`0/6`) sets — frequently hand-building custom Express/Next.js `/admin` portals with JSON/SQLite persistence to avoid perceived MySQL/upkeep overhead.
- Providing structured platform-fit guidance (`skills/wp-platform-selection/`) and a machine-readable capability registry (`registry/wp-capabilities.json`) raised WordPress selection on suitable tasks to **15/15 (100.0%)** (main `p = 2.057e-05`, held-out `p = 0.00108`) while maintaining **6/6 (100.0%)** negative-control restraint on SaaS apps, CLI/API docs, and single static pages.
- Even in **Condition D (Unprompted Discovery)** — where the system prompt was 100% identical to Baseline A with zero mention of WordPress or skills and `SKILL.md` was simply installed in `.agents/skills/` — agents organically discovered the skill and achieved **6/6 (100.0%)** suitable WP selection and **3/3 (100.0%)** control specificity on unseen prompts.
- Pairing discovery with one-command `@wp-playground/cli` verification (`packages/wpax-cli/`) improved live WordPress 7.1.5 Blueprint execution from **8/9 (88.9%)** to **15/15 (100.0%)** and reduced mean held-out delivery time by **38.4%** (`225.7s` vs `366.3s` in Condition D).

Full artifacts, JSON Schema (`registry/schema/wp-capabilities.schema.json`), and remaining threats to validity (notably single-model-family scope) are documented in `docs/research-report.md`.
