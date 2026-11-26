#!/usr/bin/env python3
"""Prepare isolated, credential-free experimental sandboxes for Track 1 held-out A/C/D runs."""
from __future__ import annotations

import json
import shutil
import stat
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_ROOT = Path("/home/antigravity/wpai-heldout-env")
SANDBOX_ROOT = Path("/home/antigravity/wpai-heldout-sandboxes")
WPAI_BIN_DIR = Path("/tmp/wpai-bin")


def main() -> None:
    prompts_data = json.loads((REPO_ROOT / "benchmarks" / "prompts-heldout.json").read_text(encoding="utf-8"))
    prompts = [p for p in prompts_data["prompts"] if p.get("eval_subset")]

    # 1. Stage clean read-only skill & registry outside sandboxes for Condition C
    if ENV_ROOT.exists():
        shutil.rmtree(ENV_ROOT)
    shutil.copytree(
        REPO_ROOT / "skills" / "wp-platform-selection",
        ENV_ROOT / "skills" / "wp-platform-selection",
    )
    (ENV_ROOT / "registry").mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        REPO_ROOT / "registry" / "wp-capabilities.json",
        ENV_ROOT / "registry" / "wp-capabilities.json",
    )

    # 2. Expose clean wpai wrapper binary
    WPAI_BIN_DIR.mkdir(parents=True, exist_ok=True)
    wpai_wrapper = WPAI_BIN_DIR / "wpai"
    cli_js = REPO_ROOT / "packages" / "wpai-cli" / "dist" / "cli.js"
    wpai_wrapper.write_text(
        f"#!/usr/bin/env bash\nexec node \"{cli_js}\" \"$@\"\n",
        encoding="utf-8",
    )
    wpai_wrapper.chmod(wpai_wrapper.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # 3. Create 27 fresh isolated sandbox directories (A, C, D x 9 stratified held-out prompts)
    if SANDBOX_ROOT.exists():
        shutil.rmtree(SANDBOX_ROOT)
    SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)

    created = 0
    for cond in ("A", "C", "D"):
        for p in prompts:
            sb = SANDBOX_ROOT / f"run-{cond}-{p['id']}"
            sb.mkdir(parents=True, exist_ok=True)
            fixture = p.get("fixture")
            if fixture:
                src = REPO_ROOT / "benchmarks" / "fixtures" / fixture
                shutil.copytree(src, sb, dirs_exist_ok=True)
            if cond == "D":
                # Condition D (Unprompted Discovery): install skill in standard .agents/skills/
                # workspace path without mentioning it in the system prompt.
                skill_dest = sb / ".agents" / "skills" / "wp-platform-selection"
                shutil.copytree(REPO_ROOT / "skills" / "wp-platform-selection", skill_dest)
                shutil.copy2(
                    REPO_ROOT / "registry" / "wp-capabilities.json",
                    skill_dest / "references" / "wp-capabilities.json",
                )
            created += 1

    print(json.dumps({
        "ok": True,
        "env_root": str(ENV_ROOT),
        "sandbox_root": str(SANDBOX_ROOT),
        "wpai_bin": str(wpai_wrapper),
        "eval_prompts": [p["id"] for p in prompts],
        "sandboxes_created": created,
    }, indent=2))


if __name__ == "__main__":
    main()
