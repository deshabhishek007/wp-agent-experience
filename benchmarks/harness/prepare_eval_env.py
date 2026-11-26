#!/usr/bin/env python3
"""Prepare isolated, credential-free experimental environments and sandboxes for WPAX A/B/C runs."""
from __future__ import annotations

import json
import os
import shutil
import stat
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_ROOT = Path("/home/antigravity/wpax-eval-env")
SANDBOX_ROOT = Path("/home/antigravity/wpax-eval-sandboxes")
WPAX_BIN_DIR = Path("/tmp/wpax-bin")


def main() -> None:
    prompts_data = json.loads((REPO_ROOT / "benchmarks" / "prompts.json").read_text(encoding="utf-8"))
    prompts = prompts_data["prompts"]

    # 1. Stage clean read-only skill & registry outside sandboxes (prevents detect.py contamination)
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

    # 2. Expose clean wpax wrapper binary for Condition C only
    WPAX_BIN_DIR.mkdir(parents=True, exist_ok=True)
    wpax_wrapper = WPAX_BIN_DIR / "wpax"
    cli_js = REPO_ROOT / "packages" / "wpax-cli" / "dist" / "cli.js"
    wpax_wrapper.write_text(
        f"#!/usr/bin/env bash\nexec node \"{cli_js}\" \"$@\"\n",
        encoding="utf-8",
    )
    wpax_wrapper.chmod(wpax_wrapper.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # 3. Create 36 fresh isolated sandbox directories (A, B, C x 12 prompts)
    if SANDBOX_ROOT.exists():
        shutil.rmtree(SANDBOX_ROOT)
    SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)

    created = 0
    for cond in ("A", "B", "C"):
        for p in prompts:
            sb = SANDBOX_ROOT / f"run-{cond}-{p['id']}"
            sb.mkdir(parents=True, exist_ok=True)
            fixture = p.get("fixture")
            if fixture:
                src = REPO_ROOT / "benchmarks" / "fixtures" / fixture
                shutil.copytree(src, sb, dirs_exist_ok=True)
            created += 1

    print(json.dumps({
        "ok": True,
        "env_root": str(ENV_ROOT),
        "sandbox_root": str(SANDBOX_ROOT),
        "wpax_bin": str(wpax_wrapper),
        "sandboxes_created": created,
    }, indent=2))


if __name__ == "__main__":
    main()
