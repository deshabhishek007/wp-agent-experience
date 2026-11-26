# WPAX Integration Overlay for `apeatling/wp-agent-benchmark`

This directory packages everything required to run WPAX **Condition B** (Discovery Skill + Capability Registry) and **Condition C** (Discovery Skill + Capability Registry + `wpax` CLI / `@wp-playground/cli` + Starter Blueprints) inside [`apeatling/wp-agent-benchmark`](https://github.com/apeatling/wp-agent-benchmark) Harbor Docker environments, and to export WPAX run logs into upstream `schema/choose-run.schema.json` (`1.0`) format.

## Files

- [`Dockerfile.wpax-overlay`](./Dockerfile.wpax-overlay): Layered Docker image overlay that adds Condition B or Condition C artifacts on top of any `wp-agent-benchmark` base environment (`dev-machine`, `claude-cloud`, or `codex-cloud`).
- [`setup-wpax-env.sh`](./setup-wpax-env.sh): Standalone shell installer invoked inside the Docker build or an interactive sandbox (`--condition B|C`).
- [`export_to_wpab.py`](./export_to_wpab.py): Deterministic converter that transforms WPAX `benchmarks/results/runs.jsonl` records into `apeatling/wp-agent-benchmark` `choose-run.schema.json` v1.0 JSONL records.

## Running Condition B or C in Harbor

1. Build the upstream `wp-agent-benchmark` base environment image (for example, `dev-machine`):

   ```bash
   docker build -t wpab-dev-machine:latest \
     -f /path/to/wp-agent-benchmark/benchmarks/environments/dev-machine/Dockerfile \
     /path/to/wp-agent-benchmark/benchmarks/environments/dev-machine
   ```

2. Build a WPAX overlay image from the root of this repository:

   ```bash
   # Condition B: Skill + Capability Registry only
   docker build -t wpab-wpax-cond-b:latest \
     --build-arg BASE_IMAGE=wpab-dev-machine:latest \
     --build-arg WPAX_CONDITION=B \
     -f benchmarks/wpab-integration/Dockerfile.wpax-overlay .

   # Condition C: Skill + Capability Registry + wpax CLI + Playground + Blueprints
   docker build -t wpab-wpax-cond-c:latest \
     --build-arg BASE_IMAGE=wpab-dev-machine:latest \
     --build-arg WPAX_CONDITION=C \
     -f benchmarks/wpab-integration/Dockerfile.wpax-overlay .
   ```

3. Reference `wpab-wpax-cond-b:latest` or `wpab-wpax-cond-c:latest` in a custom `wp-agent-benchmark` environment profile (`benchmarks/environments.toml`) while keeping all 28 (or 12) verbatim `requests.toml` prompts completely unmodified.

## Exporting WPAX Runs to `choose-run.schema.json` Format

```bash
python3 benchmarks/wpab-integration/export_to_wpab.py \
  --input benchmarks/results/runs.jsonl \
  --output benchmarks/results/wpab-choose-runs.jsonl \
  --batch 2026-11
```

Each exported line strictly obeys `schema/choose-run.schema.json` (`schema_version: "1.0"`, local run IDs formatted `CYYMM-LNNNN`, `additionalProperties: false`).

## Guardrails

- Never copy API keys, GitHub tokens, or `.env` files into overlay Docker images.
- Keep user prompts verbatim from `benchmarks/choose/requests.toml` across Conditions A, B, and C.
- Never alter negative-control prompts (`app`, `docs`, `page`) or coach agents toward WordPress on control tasks.
