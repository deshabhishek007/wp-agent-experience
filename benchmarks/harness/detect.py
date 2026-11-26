#!/usr/bin/env python3
"""Deterministic platform detector ported from apeatling/wp-agent-benchmark.

Works out which platform an agent built with strictly from the files it created
or modified inside a sandbox directory. Looks for working evidence (dependencies,
config files, WordPress core/blueprint/theme/plugin files), never for platform
names mentioned only in prose (e.g. a README mentioning WordPress does not count
as a WordPress site).

Usage:
    python3 benchmarks/harness/detect.py <sandbox_dir> [--fixture <fixture_dir>] [--json]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable

SKIP_DIRS = {
    "node_modules",
    ".git",
    ".next",
    "vendor",
    ".astro",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".cache",
    ".svelte-kit",
    ".nuxt",
    ".agents",
    ".claude",
    ".cursor",
}

CODE_EXT = {
    ".html",
    ".htm",
    ".css",
    ".js",
    ".mjs",
    ".cjs",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".svelte",
    ".astro",
    ".php",
    ".py",
    ".rb",
    ".go",
    ".liquid",
    ".json",
    ".toml",
    ".yml",
    ".yaml",
}

# Dependency names matched exactly against package.json, composer.json, requirements, pyproject, and Gemfile.
WP_DEPS = {
    "johnpbloch/wordpress",
    "roots/wordpress",
    "roots/bedrock",
    "wordpress/wordpress",
    "@wp-playground/cli",
    "@wordpress/env",
    "@faustwp/core",
    "@faustwp/cli",
    "wpgraphql",
    "@wordpress/api-fetch",
    "wp-now",
}

CMS_DEPS = {
    "sanity",
    "@sanity/client",
    "next-sanity",
    "strapi",
    "@strapi/strapi",
    "payload",
    "decap-cms",
    "decap-cms-app",
    "netlify-cms",
    "netlify-cms-app",
    "tinacms",
    "@directus/sdk",
    "directus",
    "contentful",
    "@tryghost/content-api",
    "ghost",
}

SHOP_DEPS = {
    "@shopify/hydrogen",
    "@shopify/cli",
    "@shopify/theme",
    "shopify-buy",
    "@shopify/storefront-api-client",
}

SSG_DEPS = {
    "@11ty/eleventy",
    "gatsby",
    "@docusaurus/core",
    "vitepress",
    "mkdocs",
    "mkdocs-material",
    "jekyll",
    "hugo-bin",
}

FRAMEWORK_DEPS = {
    "express",
    "django",
    "flask",
    "rails",
    "laravel/framework",
    "@sveltejs/kit",
    "nuxt",
    "@remix-run/react",
    "@remix-run/node",
    "fastapi",
    "fastify",
    "koa",
    "hono",
    "@nestjs/core",
}

HOSTED = re.compile(
    r"\b(squarespace|wix|webflow|substack|carrd|framer|godaddy website builder|"
    r"weebly|ghost\(pro\)|beehiiv|kajabi|teachable|thinkific|podia|gumroad|etsy|big cartel)\b",
    re.I,
)
SHOPIFY = re.compile(r"\bshopify\b", re.I)

PLATFORM_GROUPS: dict[str, str] = {
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


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk(root: Path) -> Iterable[Path]:
    for dirpath, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(names):
            path = Path(dirpath) / name
            if path.is_file():
                yield path


def load_fixture_hashes(fixture_dir: Path | str | None) -> dict[str, str]:
    """Build relative-path -> sha256 map from a fixture directory or JSON manifest."""
    if fixture_dir is None:
        return {}
    p = Path(fixture_dir)
    if not p.exists():
        raise FileNotFoundError(f"Fixture path not found: {p}")
    if p.is_file():
        data = json.loads(p.read_text(encoding="utf-8"))
        return {str(k): str(v) for k, v in data.items()}
    hashes: dict[str, str] = {}
    for file_path in walk(p):
        rel = file_path.relative_to(p).as_posix()
        hashes[rel] = sha(file_path)
    return hashes


def deps(root: Path, files: list[Path]) -> set[str]:
    """Every dependency name the project declares across common manifest formats."""
    found: set[str] = set()
    for path in files:
        name = path.name
        try:
            if name in ("package.json", "composer.json"):
                data = json.loads(path.read_text(errors="ignore"))
                for key in ("dependencies", "devDependencies", "require", "require-dev", "peerDependencies"):
                    found |= set((data.get(key) or {}).keys())
                if name == "composer.json" and str(data.get("type", "")).startswith("wordpress-"):
                    found.add("wordpress/wordpress")
            elif name in ("requirements.txt", "Pipfile") or name.endswith("requirements.txt"):
                for line in path.read_text(errors="ignore").splitlines():
                    m = re.match(r"\s*([A-Za-z0-9_.\-]+)", line)
                    if m:
                        found.add(m.group(1).lower())
            elif name == "pyproject.toml":
                found |= {
                    m.lower()
                    for m in re.findall(r'"([A-Za-z0-9_.\-]+)\s*[<>=~!]', path.read_text(errors="ignore"))
                }
            elif name == "Gemfile":
                found |= set(re.findall(r"""gem\s+['"]([^'"]+)['"]""", path.read_text(errors="ignore")))
        except (OSError, ValueError):
            pass
    return found


def compose_images(files: list[Path]) -> list[str]:
    images: list[str] = []
    for path in files:
        if path.name in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml", "Dockerfile"):
            text = path.read_text(errors="ignore")
            images += re.findall(r"(?:image:|FROM)\s*([^\s]+)", text)
    return [i.lower() for i in images]


def static_server(changed: list[Path]) -> bool:
    """Express used only to serve static files: express.static or sendFile, with no write routes."""
    server = " ".join(
        f.read_text(errors="ignore")[:50000]
        for f in changed
        if f.suffix.lower() in (".js", ".mjs", ".cjs", ".ts")
        and "express" in f.read_text(errors="ignore")[:50000]
    )
    serves = re.search(r"express\.static|sendFile", server)
    takes_data = re.search(r"\.(post|put|patch|delete)\s*\(", server)
    return bool(serves) and not takes_data


def detect(root: Path | str, fixture_dir: Path | str | None = None) -> tuple[str, str, list[Path]]:
    """Detect the platform built in `root`, ignoring unchanged files from `fixture_dir`.

    Returns:
        (platform, evidence, changed_files)
    """
    root_path = Path(root)
    fixture = load_fixture_hashes(fixture_dir)
    files = list(walk(root_path))
    rel = {f: f.relative_to(root_path).as_posix() for f in files}
    changed = [f for f in files if fixture.get(rel[f]) != sha(f)]
    if not changed:
        return "Nothing built", "No new or changed files", []

    names = {rel[f] for f in files}
    lower = {n.lower() for n in names}
    d = deps(root_path, files)
    images = compose_images(files)

    # WordPress: core files, theme/plugin, WordPress dependency, wp-env, Playground blueprint, or WP Docker image.
    wp_files = sorted(
        n
        for n in lower
        if re.search(
            r"(^|/)(wp-config(-sample)?\.php|wp-includes/|wp-content/(themes|plugins)/|\.wp-env\.json$|blueprint\.json$)",
            n,
        )
    )
    theme = any(f.name == "style.css" and "Theme Name:" in f.read_text(errors="ignore")[:2000] for f in files)
    plugin = any(
        f.suffix == ".php" and re.search(r"^\s*\*?\s*Plugin Name:", f.read_text(errors="ignore")[:2000], re.M)
        for f in files
    )
    if wp_files or theme or plugin or d & WP_DEPS or any(i.startswith(("wordpress", "bitnami/wordpress")) for i in images):
        why = (
            wp_files[:3]
            or (["a WordPress theme"] if theme else [])
            or (["a WordPress plugin"] if plugin else [])
            or sorted(d & WP_DEPS)
            or ["a WordPress Docker image"]
        )
        return "WordPress", "Found " + ", ".join(why), changed

    if any("/.openai/hosting" in "/" + n for n in lower):
        return "ChatGPT site", "Published to ChatGPT hosting (.openai/hosting.json)", changed

    if d & SHOP_DEPS or any(n.endswith(("layout/theme.liquid", "shopify.theme.toml")) for n in lower):
        return "Shopify", "Shopify theme or Shopify dependency", changed

    if (
        d & CMS_DEPS
        or any(i.startswith(("ghost", "strapi", "directus")) for i in images)
        or any(re.search(r"(^|/)(admin/config\.yml|tina/config|sanity\.config|studio/sanity)", n) for n in lower)
    ):
        return "Headless CMS", "CMS: " + ", ".join(sorted(d & CMS_DEPS) or ["CMS config files"]), changed

    if "next" in d:
        return "Next.js", "next in dependencies", changed

    if "astro" in d:
        return "Astro", "astro in dependencies", changed

    ssg = (
        d & SSG_DEPS
        or (
            {"hugo"}
            if any(
                n in ("hugo.toml", "hugo.yaml", "config.toml")
                and "baseurl" in (root_path / n).read_text(errors="ignore").lower()
                for n in names
            )
            else set()
        )
        or ({"mkdocs"} if "mkdocs.yml" in lower else set())
        or ({"jekyll"} if "_config.yml" in lower and "gemfile" in lower else set())
    )
    if ssg:
        return "Static site generator", ", ".join(sorted(ssg)), changed

    if d & FRAMEWORK_DEPS == {"express"} and static_server(changed):
        return "Plain HTML or React", "HTML, CSS and JavaScript, served by a small Express static server", changed

    if d & FRAMEWORK_DEPS or "manage.py" in lower:
        return "Web framework", ", ".join(sorted(d & FRAMEWORK_DEPS) or ["Django"]), changed

    code = [f for f in changed if f.suffix.lower() in CODE_EXT and f.name not in ("package.json", "package-lock.json")]
    docs_text = " ".join(f.read_text(errors="ignore")[:20000] for f in changed if f.suffix.lower() in (".md", ".txt"))
    if not code:
        if SHOPIFY.search(docs_text):
            return "Shopify", "Instructions to use Shopify, no site code", changed
        hosted_match = HOSTED.search(docs_text)
        if hosted_match:
            return "Hosted builder", "Instructions to use " + hosted_match.group(1) + ", no site code", changed
        return "Nothing built", "Only notes or plans: " + ", ".join(rel[f] for f in changed[:5]), changed

    if any(f.suffix.lower() in (".html", ".htm", ".css", ".js", ".jsx", ".tsx", ".ts") for f in changed) or "vite" in d or "react" in d:
        return "Plain HTML or React", "HTML, CSS and JavaScript" + (" with Vite" if "vite" in d else ""), changed

    return "Other code", ", ".join(sorted({f.suffix for f in code})), changed


def detect_result(root: Path | str, fixture_dir: Path | str | None = None) -> dict:
    """Return a structured detection payload compatible with WPAX & wp-agent-benchmark."""
    root_path = Path(root)
    platform, evidence, changed = detect(root_path, fixture_dir=fixture_dir)
    return {
        "platform": platform,
        "platform_group": PLATFORM_GROUPS.get(platform, "code"),
        "wordpress": platform == "WordPress",
        "built": platform != "Nothing built",
        "evidence": evidence,
        "file_count": len(changed),
        "files": sorted(f.relative_to(root_path).as_posix() for f in changed)[:300],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Detect which platform an AI agent built with inside a sandbox directory."
    )
    parser.add_argument("sandbox_dir", type=Path, help="Path to the sandbox workspace directory.")
    parser.add_argument(
        "--fixture",
        type=Path,
        default=None,
        help="Optional path to a fixture directory (or fixture.json manifest) whose unchanged files should be ignored.",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit machine-readable JSON output.")
    args = parser.parse_args(argv)

    if not args.sandbox_dir.exists():
        print(f"Error: sandbox directory does not exist: {args.sandbox_dir}", file=sys.stderr)
        return 2

    result = detect_result(args.sandbox_dir, fixture_dir=args.fixture)
    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Platform:       {result['platform']} ({result['platform_group']})")
        print(f"WordPress:      {result['wordpress']}")
        print(f"Built:          {result['built']}")
        print(f"Changed files:  {result['file_count']}")
        print(f"Evidence:       {result['evidence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
