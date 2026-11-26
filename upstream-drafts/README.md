# Upstream Contribution & Publication Drafts

> [!IMPORTANT]
> **Governance Policy:** Every document in this directory is a **local draft only**.
> Per WPAX autonomy rules (`MISSION.md`), **no upstream pull requests, GitHub issues, Make WordPress posts, or public blog articles have been submitted**.
> Explicit sponsor approval is required before publishing or submitting any artifact externally.

## Staged Draft Inventory

1. [`wordpress-agent-skills-pr.md`](./wordpress-agent-skills-pr.md) — Draft PR adding `wp-platform-selection` skill + eval scenarios to `WordPress/agent-skills` (updated with 63-run main + held-out + Condition D evidence).
2. [`wp-agent-benchmark-pr.md`](./wp-agent-benchmark-pr.md) — Draft PR/Issue proposing WPAX intervention overlays (Conditions B, C, and unprompted Condition D) for `apeatling/wp-agent-benchmark`.
3. [`wordpress-llms-txt-proposal.md`](./wordpress-llms-txt-proposal.md) — Draft `make.wordpress.org/ai` proposal + concrete diff to improve `wordpress.org/llms.txt` for agent platform discovery.
4. [`publication-post-draft.md`](./publication-post-draft.md) — Technical research post summarizing verified 63-run empirical results (36 main + 27 held-out), Condition D organic discovery, symmetric verification, and honest limitations.

## Sponsor Approval Checklist (Before External Submission)

- [ ] Confirm repository visibility (`patilswapnilv/wp-agent-experience`: private → public) and open-source license (`GPL-2.0-or-later` or `MIT`) so upstream PRs can link to reproducible artifacts.
- [ ] Approve PR #1: Fork `WordPress/agent-skills` and open PR with `skills/wp-platform-selection/`.
- [ ] Approve PR #2: Fork `apeatling/wp-agent-benchmark` and open PR/Issue with `benchmarks/wpab-integration/` overlay.
- [ ] Approve Post #3 & #4: Publish `make.wordpress.org/ai` proposal and technical write-up.
