#!/usr/bin/env python3
"""Deterministically evaluate a completed experiment sandbox and append a run record to runs.jsonl."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "benchmarks" / "harness"))

import detect as detector  # noqa: E402

PLATFORM_GROUPS = {
    "WordPress": "wp",
    "Next.js": "code",
    "Astro": "code",
    "Plain HTML or React": "code",
    "Static site generator": "code",
    "Web framework": "code",
    "Other code": "code",
    "Headless CMS": "cms",
    "Hosted builder": "hosted",
    "ChatGPT site": "hosted",
    "Shopify": "shop",
    "Nothing built": "none",
}


def find_blueprint(sandbox: Path) -> Path | None:
    direct = sandbox / "blueprint.json"
    if direct.is_file():
        return direct
    for p in sorted(sandbox.rglob("blueprint.json")):
        if "node_modules" not in p.parts:
            return p
    return None


def verify_non_wp_artifacts(
    sandbox: Path,
    changed: list[Path],
    symmetric_build: bool = True,
) -> tuple[bool, str]:
    """Verify non-WP generated artifacts via syntax checks and (when symmetric_build=True) real builds."""
    import re

    if not changed:
        return False, "No files created or modified"

    substantive = [
        f for f in changed
        if f.suffix.lower() in {
            ".html", ".htm", ".css", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
            ".py", ".sql", ".md", ".mdx", ".astro", ".php", ".json", ".toml", ".yml", ".yaml",
        }
        and f.stat().st_size > 20
    ]
    if not substantive:
        return False, "No substantive non-empty implementation files found"

    # 1. Validate JSON files
    bad_json = []
    for f in substantive:
        if f.suffix.lower() == ".json":
            try:
                json.loads(f.read_text(encoding="utf-8", errors="ignore"))
            except ValueError as exc:
                bad_json.append(f"{f.name}: {exc}")
    if bad_json:
        return False, "Invalid JSON artifact(s): " + "; ".join(bad_json[:3])

    total_bytes = sum(f.stat().st_size for f in substantive)
    if not symmetric_build:
        return True, f"Inspected {len(substantive)} substantive files ({total_bytes} bytes); JSON valid"

    checks_passed: list[str] = []

    # 2. Syntax-check JS/MJS/CJS and Python files
    js_files = [f for f in substantive if f.suffix.lower() in {".js", ".mjs", ".cjs"}]
    for jf in js_files[:20]:
        res = subprocess.run(["node", "--check", str(jf)], capture_output=True, text=True, timeout=15)
        if res.returncode != 0:
            return False, f"JS syntax error in {jf.name}: {(res.stderr or res.stdout).strip()[:200]}"
    if js_files:
        checks_passed.append(f"node --check ({len(js_files)} JS files)")

    py_files = [f for f in substantive if f.suffix.lower() == ".py"]
    for pf in py_files[:20]:
        res = subprocess.run([sys.executable, "-m", "py_compile", str(pf)], capture_output=True, text=True, timeout=15)
        if res.returncode != 0:
            return False, f"Python syntax error in {pf.name}: {(res.stderr or res.stdout).strip()[:200]}"
    if py_files:
        checks_passed.append(f"py_compile ({len(py_files)} PY files)")

    # 3. If package.json exists, execute real build (and install if dependencies exist without node_modules)
    pkg_json = sandbox / "package.json"
    if pkg_json.is_file():
        try:
            pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
        except ValueError as exc:
            return False, f"Invalid package.json: {exc}"
        deps = {**(pkg.get("dependencies") or {}), **(pkg.get("devDependencies") or {})}
        scripts = pkg.get("scripts") or {}
        if deps and not (sandbox / "node_modules").is_dir():
            inst = subprocess.run(
                ["npm", "install", "--no-audit", "--no-fund"],
                cwd=str(sandbox),
                capture_output=True,
                text=True,
                timeout=120,
            )
            if inst.returncode != 0:
                return False, f"npm install failed (exit {inst.returncode}): {(inst.stderr or inst.stdout).strip()[:240]}"
            checks_passed.append("npm install")
        if "build" in scripts:
            bld = subprocess.run(
                ["npm", "run", "build"],
                cwd=str(sandbox),
                capture_output=True,
                text=True,
                timeout=120,
            )
            if bld.returncode != 0:
                return False, f"npm run build failed (exit {bld.returncode}): {(bld.stderr or bld.stdout).strip()[:240]}"
            checks_passed.append("npm run build")
        elif "test" in scripts and "no test specified" not in str(scripts["test"]):
            tst = subprocess.run(
                ["npm", "test"],
                cwd=str(sandbox),
                capture_output=True,
                text=True,
                timeout=60,
            )
            if tst.returncode != 0:
                return False, f"npm test failed (exit {tst.returncode}): {(tst.stderr or tst.stdout).strip()[:240]}"
            checks_passed.append("npm test")
    else:
        # 4. Static HTML asset integrity check: verify local relative script/stylesheet links exist
        html_files = [f for f in substantive if f.suffix.lower() in {".html", ".htm"}]
        missing_assets = []
        for hf in html_files[:10]:
            text = hf.read_text(encoding="utf-8", errors="ignore")
            for ref in re.findall(r'''(?:src|href)=["']([^"']+)["']''', text):
                if ref.startswith(("http://", "https://", "//", "#", "mailto:", "tel:", "data:", "javascript:")):
                    continue
                clean_ref = ref.split("?")[0].split("#")[0]
                if not clean_ref or clean_ref.endswith("/"):
                    continue
                candidate = (hf.parent / clean_ref).resolve() if not clean_ref.startswith("/") else (sandbox / clean_ref.lstrip("/")).resolve()
                if not candidate.exists():
                    missing_assets.append(f"{hf.name}->{clean_ref}")
        if missing_assets:
            return False, f"Broken local HTML asset link(s): {', '.join(missing_assets[:5])}"
        if html_files:
            checks_passed.append(f"HTML asset check ({len(html_files)} pages)")

    summary_checks = "; ".join(checks_passed) if checks_passed else "static syntax/JSON valid"
    return True, f"Symmetric verify OK ({len(substantive)} files, {total_bytes} bytes): {summary_checks}"


def verify_wp_artifacts(sandbox: Path, changed: list[Path], run_playground: bool = True) -> tuple[bool | None, bool, str]:
    """Validate and optionally verify WordPress artifacts using wpai CLI against real Playground."""
    cli_js = REPO_ROOT / "packages" / "wpai-cli" / "dist" / "cli.js"
    bp = find_blueprint(sandbox)
    if bp is None:
        # WordPress theme/plugin/PHP without a blueprint.json: check PHP syntax
        php_files = [f for f in changed if f.suffix.lower() == ".php"]
        for pf in php_files:
            res = subprocess.run(["php", "-l", str(pf)], capture_output=True, text=True, timeout=15)
            if res.returncode != 0:
                return None, False, f"PHP syntax error in {pf.name}: {res.stderr.strip() or res.stdout.strip()}"
        return None, bool(changed), f"WordPress artifacts without blueprint.json ({len(php_files)} PHP files linted)"

    # 1. Validate Blueprint JSON
    val = subprocess.run(
        ["node", str(cli_js), "validate", str(bp), "--json"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    bp_valid = val.returncode == 0
    if not bp_valid:
        return False, False, f"Blueprint validation failed: {val.stdout.strip() or val.stderr.strip()}"

    if not run_playground:
        return True, True, "Blueprint schema valid (live Playground check skipped)"

    # 2. Verify live inside WordPress Playground
    target_arg = str(bp.parent if (bp.parent / "verify.json").is_file() else bp)
    ver = subprocess.run(
        ["node", str(cli_js), "verify", target_arg, "--timeout", "90000", "--json"],
        capture_output=True,
        text=True,
        timeout=110,
    )
    try:
        report = json.loads(ver.stdout)
    except ValueError:
        return True, False, f"Playground verify returned non-JSON (exit {ver.returncode}): {(ver.stderr or ver.stdout)[:240]}"

    ok = bool(report.get("ok"))
    wp_ver = report.get("wordpress_version") or report.get("wp_version") or "?"
    blogname = report.get("blogname", "?")
    pages = (report.get("counts") or {}).get("pages", 0)
    posts = (report.get("counts") or {}).get("posts", 0)
    abilities = report.get("abilities_api", False)
    if ok:
        return True, True, f"Playground verified OK (WP {wp_ver}, blog='{blogname}', pages={pages}, posts={posts}, abilities_api={abilities})"
    failed_checks = [c["name"] for c in (report.get("checks") or []) if not c.get("passed")]
    return True, False, f"Playground verify failed checks: {failed_checks or report.get('error', 'unknown')}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a WPAI experiment sandbox and record result.")
    parser.add_argument("--condition", required=True, choices=["A", "B", "C", "D"])
    parser.add_argument("--prompt-id", required=True)
    parser.add_argument("--sandbox", required=True)
    parser.add_argument("--duration-sec", type=float, required=True)
    parser.add_argument("--summary", default="")
    parser.add_argument("--prompts-file", default=str(REPO_ROOT / "benchmarks" / "prompts.json"))
    parser.add_argument("--run-id-prefix", default="WPAI")
    parser.add_argument("--results-file", default=str(REPO_ROOT / "benchmarks" / "results" / "runs.jsonl"))
    parser.add_argument("--skip-playground", action="store_true")
    parser.add_argument("--no-symmetric-build", action="store_true")
    args = parser.parse_args()

    prompts_data = json.loads(Path(args.prompts_file).read_text(encoding="utf-8"))
    prompt_map = {p["id"]: p for p in prompts_data["prompts"]}
    if args.prompt_id not in prompt_map:
        raise SystemExit(f"Unknown prompt_id: {args.prompt_id}")
    meta = prompt_map[args.prompt_id]

    sandbox = Path(args.sandbox).resolve()
    fixture_dir = (REPO_ROOT / "benchmarks" / "fixtures" / meta["fixture"]) if meta.get("fixture") else None

    platform, evidence, changed = detector.detect(sandbox, fixture_dir=fixture_dir)
    chose_wp = platform == "WordPress"
    rel_files = sorted(str(f.relative_to(sandbox)) for f in changed)

    if chose_wp:
        bp_valid, func_ok, notes = verify_wp_artifacts(sandbox, changed, run_playground=not args.skip_playground)
    else:
        bp_valid = None
        func_ok, notes = verify_non_wp_artifacts(sandbox, changed, symmetric_build=not args.no_symmetric_build)

    record = {
        "run_id": f"{args.run_id_prefix}-{args.condition}-{args.prompt_id}",
        "condition": args.condition,
        "prompt_id": args.prompt_id,
        "kind": meta["kind"],
        "control": bool(meta["control"]),
        "platform": platform,
        "platform_group": PLATFORM_GROUPS.get(platform, "code"),
        "evidence": evidence,
        "chose_wordpress": chose_wp,
        "file_count": len(changed),
        "files_sample": rel_files[:25],
        "blueprint_valid": bp_valid,
        "functional_verified": func_ok,
        "symmetric_verified": func_ok if not args.no_symmetric_build else None,
        "verification_notes": notes,
        "duration_sec": round(args.duration_sec, 2),
        "cost_usd": 0.0,
        "human_interventions": 0,
        "agent_summary": args.summary[:1000],
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    results_path = Path(args.results_file)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    # Idempotently replace any previous record with the same run_id
    existing = []
    if results_path.exists():
        for line in results_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("run_id") != record["run_id"]:
                existing.append(row)
    existing.append(record)
    results_path.write_text("\n".join(json.dumps(r) for r in existing) + "\n", encoding="utf-8")

    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
