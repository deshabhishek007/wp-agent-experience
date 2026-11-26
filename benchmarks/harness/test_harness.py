#!/usr/bin/env python3
"""Unit tests for WPAI benchmark harness (`detect.py` and `analyze.py`).

Run with:
    python3 -m unittest benchmarks/harness/test_harness.py
"""

from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
REPO_ROOT = HARNESS_DIR.parent.parent
if str(HARNESS_DIR) not in sys.path:
    sys.path.insert(0, str(HARNESS_DIR))

import analyze  # noqa: E402
import detect  # noqa: E402


def _make_sandbox(files: dict[str, str]) -> tempfile.TemporaryDirectory:
    tmp = tempfile.TemporaryDirectory(prefix="wpai-test-")
    root = Path(tmp.name)
    for rel_path, content in files.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return tmp


class TestDetect(unittest.TestCase):
    def assertPlatform(
        self,
        files: dict[str, str],
        expected_platform: str,
        fixture_dir: Path | None = None,
    ) -> None:
        with _make_sandbox(files) as tmp:
            platform, evidence, _ = detect.detect(Path(tmp), fixture_dir=fixture_dir)
            self.assertEqual(platform, expected_platform, f"Unexpected evidence: {evidence}")

    def test_wordpress_blueprint(self) -> None:
        self.assertPlatform({"blueprint.json": '{"steps": []}'}, "WordPress")

    def test_wordpress_theme(self) -> None:
        self.assertPlatform(
            {"my-theme/style.css": "/*\nTheme Name: Bakery Block Theme\n*/\nbody {}\n"},
            "WordPress",
        )

    def test_wordpress_plugin(self) -> None:
        self.assertPlatform(
            {"my-plugin.php": "<?php\n/**\n * Plugin Name: Yoga Schedule\n */\n"},
            "WordPress",
        )

    def test_wordpress_core_env_playground_and_headless(self) -> None:
        self.assertPlatform({"wp-config.php": "<?php"}, "WordPress")
        self.assertPlatform({".wp-env.json": "{}"}, "WordPress")
        self.assertPlatform(
            {"package.json": '{"devDependencies": {"@wp-playground/cli": "3.1.66"}}'},
            "WordPress",
        )
        self.assertPlatform(
            {"package.json": '{"dependencies": {"next": "15.0.0", "@faustwp/core": "3.0.0"}}'},
            "WordPress",
        )
        self.assertPlatform(
            {"docker-compose.yml": "services:\n  wp:\n    image: wordpress:6-apache\n"},
            "WordPress",
        )

    def test_readme_mention_is_not_wordpress(self) -> None:
        self.assertPlatform(
            {"README.md": "We considered WordPress and WooCommerce.", "index.html": "<h1>Hi</h1>"},
            "Plain HTML or React",
        )

    def test_nextjs(self) -> None:
        self.assertPlatform(
            {"package.json": '{"dependencies": {"next": "15.1.0", "react": "19.0.0"}}', "app/page.tsx": ""},
            "Next.js",
        )

    def test_astro(self) -> None:
        self.assertPlatform(
            {"package.json": '{"dependencies": {"astro": "5.0.0"}}', "src/pages/index.astro": ""},
            "Astro",
        )

    def test_plain_html_and_react_vite(self) -> None:
        self.assertPlatform({"index.html": "<h1>Links</h1>", "styles.css": "body {}"}, "Plain HTML or React")
        self.assertPlatform(
            {"package.json": '{"devDependencies": {"vite": "6.0.0"}, "dependencies": {"react": "19.0.0"}}', "src/App.tsx": ""},
            "Plain HTML or React",
        )
        self.assertPlatform(
            {
                "package.json": '{"dependencies": {"express": "5.0.0"}}',
                "server.js": "const express = require('express'); app.use(express.static('public'));",
                "public/index.html": "<h1>Hi</h1>",
            },
            "Plain HTML or React",
        )

    def test_docusaurus_and_ssg(self) -> None:
        self.assertPlatform(
            {"package.json": '{"dependencies": {"@docusaurus/core": "3.7.0"}}', "docs/intro.md": "# Intro"},
            "Static site generator",
        )
        self.assertPlatform({"mkdocs.yml": "site_name: CLI Docs\n", "docs/index.md": "# CLI"}, "Static site generator")

    def test_fastapi_and_django(self) -> None:
        self.assertPlatform(
            {"requirements.txt": "fastapi==0.115.0\nuvicorn==0.34.0\n", "main.py": "from fastapi import FastAPI"},
            "Web framework",
        )
        self.assertPlatform({"manage.py": "#!/usr/bin/env python\n", "app/views.py": ""}, "Web framework")
        self.assertPlatform(
            {
                "package.json": '{"dependencies": {"express": "5.0.0"}}',
                "server.js": "const express = require('express'); app.post('/api/invoices', fn);",
            },
            "Web framework",
        )

    def test_headless_cms_shopify_and_hosted(self) -> None:
        self.assertPlatform({"package.json": '{"dependencies": {"next": "15", "next-sanity": "9"}}'}, "Headless CMS")
        self.assertPlatform({"layout/theme.liquid": "<html></html>"}, "Shopify")
        self.assertPlatform({"GUIDE.md": "Sign up for Squarespace to host your bakery site."}, "Hosted builder")

    def test_nothing_built(self) -> None:
        self.assertPlatform({}, "Nothing built")
        self.assertPlatform({"NOTES.md": "Just some notes about building a site."}, "Nothing built")

    def test_unchanged_fixture_is_nothing_built(self) -> None:
        fixture = REPO_ROOT / "benchmarks" / "fixtures" / "editable-2"
        self.assertTrue(fixture.is_dir(), f"Expected fixture dir at {fixture}")
        with tempfile.TemporaryDirectory(prefix="wpai-fix-") as tmp:
            sandbox = Path(tmp) / "sandbox"
            shutil.copytree(fixture, sandbox)
            platform, evidence, changed = detect.detect(sandbox, fixture_dir=fixture)
            self.assertEqual(platform, "Nothing built", evidence)
            self.assertEqual(changed, [])

            # Editing a fixture file should be detected as Plain HTML or React
            (sandbox / "menu.html").write_text("<h1>Updated Menu</h1>", encoding="utf-8")
            platform2, _, changed2 = detect.detect(sandbox, fixture_dir=fixture)
            self.assertEqual(platform2, "Plain HTML or React")
            self.assertEqual([p.name for p in changed2], ["menu.html"])

            # Adding a WordPress blueprint alongside fixture should detect WordPress
            (sandbox / "blueprint.json").write_text('{"steps": []}', encoding="utf-8")
            platform3, _, _ = detect.detect(sandbox, fixture_dir=fixture)
            self.assertEqual(platform3, "WordPress")

    def test_cli_json_output(self) -> None:
        with _make_sandbox({"blueprint.json": '{"steps": []}'}) as tmp:
            proc = subprocess.run(
                [sys.executable, str(HARNESS_DIR / "detect.py"), tmp, "--json"],
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["platform"], "WordPress")
            self.assertEqual(payload["platform_group"], "wp")
            self.assertTrue(payload["wordpress"])
            self.assertTrue(payload["built"])
            self.assertEqual(payload["file_count"], 1)


class TestAnalyze(unittest.TestCase):
    def test_wilson_ci_bounds(self) -> None:
        lo, hi = analyze.wilson_ci(0, 9)
        self.assertAlmostEqual(lo, 0.0, places=6)
        self.assertAlmostEqual(hi, 0.299147, places=4)

        lo2, hi2 = analyze.wilson_ci(9, 9)
        self.assertAlmostEqual(lo2, 0.700853, places=4)
        self.assertAlmostEqual(hi2, 1.0, places=6)

        lo3, hi3 = analyze.wilson_ci(5, 10)
        self.assertAlmostEqual(lo3, 0.236593, places=4)
        self.assertAlmostEqual(hi3, 0.763407, places=4)

        self.assertEqual(analyze.wilson_ci(0, 0), (0.0, 0.0))

    def test_fishers_exact_known_values(self) -> None:
        # 9/9 vs 0/9 -> P(X=9) = 1 / C(18, 9) = 1 / 48620
        res1 = analyze.fishers_exact(9, 0, 0, 9)
        self.assertAlmostEqual(res1["p_one_sided_greater"], 1 / math.comb(18, 9), places=10)
        self.assertAlmostEqual(res1["p_two_sided"], 2 / math.comb(18, 9), places=10)

        # 7/9 vs 0/9 -> P(X=7) = C(9,7)*C(9,0) / C(18,7) = 36 / 31824
        res2 = analyze.fishers_exact(7, 2, 0, 9)
        expected_one = math.comb(9, 7) / math.comb(18, 7)
        self.assertAlmostEqual(res2["p_one_sided_greater"], expected_one, places=10)
        self.assertAlmostEqual(res2["p_two_sided"], 2 * expected_one, places=10)

        # Identical 0/9 vs 0/9 -> p = 1.0
        res3 = analyze.fishers_exact(0, 9, 0, 9)
        self.assertAlmostEqual(res3["p_one_sided_greater"], 1.0, places=10)
        self.assertAlmostEqual(res3["p_two_sided"], 1.0, places=10)

        # Classic 4+4 table [[3, 1], [1, 3]] -> one-sided = 17/70, two-sided = 34/70
        res4 = analyze.fishers_exact(3, 1, 1, 3)
        self.assertAlmostEqual(res4["p_one_sided_greater"], 17 / 70, places=10)
        self.assertAlmostEqual(res4["p_two_sided"], 34 / 70, places=10)

    def test_analyze_runs_summary(self) -> None:
        runs = []
        # Condition A: 0/9 WP on suitable, 3/3 non-WP on controls
        for i in range(9):
            runs.append(
                {
                    "condition": "A",
                    "request_id": f"suit-{i}",
                    "control": False,
                    "status": "completed",
                    "platform": "Next.js",
                    "wordpress": False,
                    "functional_verified": True,
                    "duration_s": 20.0 + i,
                    "cost_usd": 0.0,
                    "human_interventions": 0,
                }
            )
        for i in range(3):
            runs.append(
                {
                    "condition": "A",
                    "request_id": f"ctrl-{i}",
                    "control": True,
                    "status": "completed",
                    "platform": "Plain HTML or React",
                    "wordpress": False,
                    "functional_verified": True,
                    "duration_s": 15.0,
                    "cost_usd": 0.0,
                    "human_interventions": 0,
                }
            )

        # Condition B: 7/9 WP on suitable, 3/3 non-WP on controls
        for i in range(9):
            is_wp = i < 7
            runs.append(
                {
                    "condition": "B",
                    "request_id": f"suit-{i}",
                    "control": False,
                    "status": "completed",
                    "platform": "WordPress" if is_wp else "Next.js",
                    "wordpress": is_wp,
                    "functional_verified": True,
                    "duration_s": 30.0,
                    "cost_usd": 0.0,
                    "human_interventions": 0,
                }
            )
        for i in range(3):
            runs.append(
                {
                    "condition": "B",
                    "request_id": f"ctrl-{i}",
                    "control": True,
                    "status": "completed",
                    "platform": "Static site generator",
                    "wordpress": False,
                    "functional_verified": True,
                    "duration_s": 18.0,
                    "cost_usd": 0.0,
                    "human_interventions": 0,
                }
            )

        # Condition C: 8/9 WP on suitable, 2/3 non-WP on controls (1 false positive), plus 1 excluded infra_error
        for i in range(9):
            is_wp = i < 8
            runs.append(
                {
                    "condition": "C",
                    "request_id": f"suit-{i}",
                    "control": False,
                    "status": "completed",
                    "platform": "WordPress" if is_wp else "Astro",
                    "wordpress": is_wp,
                    "functional_verified": i != 8,
                    "duration_s": 40.0,
                    "cost_usd": 0.0,
                    "human_interventions": 0,
                }
            )
        for i in range(3):
            is_wp = i == 0
            runs.append(
                {
                    "condition": "C",
                    "request_id": f"ctrl-{i}",
                    "control": True,
                    "status": "completed",
                    "platform": "WordPress" if is_wp else "Web framework",
                    "wordpress": is_wp,
                    "functional_verified": True,
                    "duration_s": 22.0,
                    "cost_usd": 0.0,
                    "human_interventions": 0,
                }
            )
        runs.append(
            {
                "condition": "C",
                "request_id": "suit-retry",
                "control": False,
                "status": "infra_error",
                "platform": None,
                "wordpress": None,
                "duration_s": 5.0,
                "cost_usd": 0.0,
                "human_interventions": 0,
            }
        )

        summary = analyze.analyze_runs(runs)
        self.assertEqual(summary["total_runs"], 37)
        self.assertEqual(summary["conditions"]["A"]["suitable"]["wp_selected"], 0)
        self.assertEqual(summary["conditions"]["B"]["suitable"]["wp_selected"], 7)
        self.assertEqual(summary["conditions"]["C"]["suitable"]["wp_selected"], 8)
        self.assertEqual(summary["conditions"]["C"]["excluded_runs"], 1)
        self.assertAlmostEqual(summary["conditions"]["A"]["controls"]["specificity"], 1.0)
        self.assertAlmostEqual(summary["conditions"]["C"]["controls"]["specificity"], 2 / 3, places=5)

        b_vs_a = summary["comparisons"]["B_vs_A"]
        self.assertAlmostEqual(b_vs_a["delta_percentage_points"], 77.78, places=2)
        self.assertTrue(b_vs_a["meets_25pp_hypothesis"])
        self.assertLess(b_vs_a["fisher_exact"]["p_one_sided_greater"], 0.005)

        md = analyze.format_markdown(summary)
        self.assertIn("WPAI Controlled Experiment Summary", md)
        self.assertIn("B_vs_A", md)
        self.assertIn("C_vs_A", md)

        # Also test CLI execution writing summary.json
        with tempfile.TemporaryDirectory(prefix="wpai-analyze-") as tmp:
            inp = Path(tmp) / "runs.jsonl"
            out = Path(tmp) / "summary.json"
            inp.write_text("\n".join(json.dumps(r) for r in runs) + "\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(HARNESS_DIR / "analyze.py"), "--input", str(inp), "--output", str(out)],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("B_vs_A", proc.stdout)
            saved = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(saved["conditions"]["B"]["suitable"]["wp_selected"], 7)


class TestPromptsAndExport(unittest.TestCase):
    def test_prompts_json_integrity(self) -> None:
        prompts_path = REPO_ROOT / "benchmarks" / "prompts.json"
        data = json.loads(prompts_path.read_text(encoding="utf-8"))
        self.assertEqual(data["suite_version"], "0.4.0")
        prompts = data["prompts"]
        self.assertEqual(len(prompts), 12)
        suitable = [p for p in prompts if not p["control"]]
        controls = [p for p in prompts if p["control"]]
        self.assertEqual(len(suitable), 9)
        self.assertEqual(len(controls), 3)
        self.assertEqual({p["id"] for p in controls}, {"app-3", "docs-1", "page-2"})
        # Verify editable-2 fixture directory exists
        editable = next(p for p in prompts if p["id"] == "editable-2")
        self.assertEqual(editable["fixture"], "editable-2")
        self.assertTrue((REPO_ROOT / "benchmarks" / "fixtures" / "editable-2" / "menu.html").is_file())

    def test_export_to_wpab_schema_compliance(self) -> None:
        wpab_dir = REPO_ROOT / "benchmarks" / "wpab-integration"
        if str(wpab_dir) not in sys.path:
            sys.path.insert(0, str(wpab_dir))
        import export_to_wpab  # noqa: E402

        sample = {
            "condition": "C",
            "request_id": "store-3",
            "kind": "store",
            "control": False,
            "status": "completed",
            "platform": "WordPress",
            "wordpress": True,
            "built": True,
            "evidence": "Found blueprint.json",
            "file_count": 3,
            "duration_s": 31.4,
            "cost_usd": 0.0,
            "started_at": "2026-11-26T08:00:00Z",
            "finished_at": "2026-11-26T08:00:31Z",
        }
        rec = export_to_wpab.convert_record(sample, 1, batch="2026-11")
        required_keys = {
            "schema_version",
            "run_id",
            "benchmark",
            "batch",
            "suite_version",
            "request_id",
            "kind",
            "control",
            "agent",
            "model",
            "harness",
            "harness_version",
            "auth",
            "status",
            "started_at",
            "job",
            "trial",
        }
        self.assertTrue(required_keys.issubset(rec.keys()))
        self.assertEqual(rec["schema_version"], "1.0")
        self.assertEqual(rec["benchmark"], "choose")
        self.assertRegex(rec["run_id"], r"^C[0-9]{4}-L?[0-9]{4}$")
        self.assertEqual(rec["platform_group"], "wp")
        self.assertIsNone(rec["considered_wordpress"])


if __name__ == "__main__":
    unittest.main()
