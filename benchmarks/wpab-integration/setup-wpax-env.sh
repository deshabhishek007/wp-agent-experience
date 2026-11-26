#!/usr/bin/env bash
# Installs WPAX Condition B (Skill + Registry) or Condition C (Skill + Registry + Playground CLI + Blueprints)
# into standard AI coding-agent skill discovery directories inside a Harbor container or local sandbox.
#
# Usage:
#   ./setup-wpax-env.sh --condition B|C [--wpax-home /opt/wpax] [--target-home "$HOME"]

set -euo pipefail

CONDITION="C"
WPAX_HOME="${WPAX_HOME:-/opt/wpax}"
TARGET_HOME="${HOME:-/root}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --condition)
      CONDITION="${2^^}"
      shift 2
      ;;
    --wpax-home)
      WPAX_HOME="$2"
      shift 2
      ;;
    --target-home)
      TARGET_HOME="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 --condition B|C [--wpax-home /opt/wpax] [--target-home \$HOME]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 2
      ;;
  esac
done

if [[ "${CONDITION}" != "B" && "${CONDITION}" != "C" ]]; then
  echo "Error: --condition must be B or C (got '${CONDITION}')." >&2
  exit 2
fi

SKILL_SRC="${WPAX_HOME}/skills/wp-platform-selection"
REGISTRY_SRC="${WPAX_HOME}/registry/wp-capabilities.json"

if [[ ! -d "${SKILL_SRC}" ]]; then
  echo "Error: skill directory not found at ${SKILL_SRC}" >&2
  exit 1
fi
if [[ ! -f "${REGISTRY_SRC}" ]]; then
  echo "Error: capability registry not found at ${REGISTRY_SRC}" >&2
  exit 1
fi

# Install skill into standard agent discovery paths across Claude Code, Codex, Cursor, and generic agents.
SKILL_TARGETS=(
  "${TARGET_HOME}/.claude/skills/wp-platform-selection"
  "${TARGET_HOME}/.codex/skills/wp-platform-selection"
  "${TARGET_HOME}/.cursor/skills/wp-platform-selection"
  "${TARGET_HOME}/.agents/skills/wp-platform-selection"
)

for dest in "${SKILL_TARGETS[@]}"; do
  mkdir -p "$(dirname "${dest}")"
  rm -rf "${dest}"
  cp -R "${SKILL_SRC}" "${dest}"
done

# Make capability registry discoverable at a predictable path.
mkdir -p "${TARGET_HOME}/.wpax"
cp "${REGISTRY_SRC}" "${TARGET_HOME}/.wpax/wp-capabilities.json"

if [[ "${CONDITION}" == "B" ]]; then
  # Condition B deliberately excludes Playground runtime & blueprints to isolate Discovery + Registry.
  rm -rf "${WPAX_HOME}/blueprints" "${TARGET_HOME}/.wpax/blueprints" || true
  echo "[wpax] Configured Condition B (Discovery Skill + Capability Registry) for ${TARGET_HOME}."
  exit 0
fi

# Condition C: Also install starter blueprints and pre-warm @wp-playground/cli@3.1.66 if Node/npm is present.
if [[ -d "${WPAX_HOME}/blueprints" ]]; then
  rm -rf "${TARGET_HOME}/.wpax/blueprints"
  cp -R "${WPAX_HOME}/blueprints" "${TARGET_HOME}/.wpax/blueprints"
fi

if command -v npm >/dev/null 2>&1; then
  npm install -g @wp-playground/cli@3.1.66 --no-audit --no-fund
fi

echo "[wpax] Configured Condition C (Discovery Skill + Registry + Playground CLI + Blueprints) for ${TARGET_HOME}."
