import fs from 'node:fs';
import { Ajv2020 } from 'ajv/dist/2020.js';
import addFormats from 'ajv-formats';
import { findRegistryPath, findRegistrySchemaPath } from './paths.js';
import type {
  CapabilityRegistry,
  FitResult,
  RegistryValidationResult,
} from './types.js';

export function loadRegistry(explicitPath?: string): {
  registry: CapabilityRegistry;
  path: string;
} {
  const registryPath = findRegistryPath(explicitPath);
  const raw = fs.readFileSync(registryPath, 'utf8');
  const registry = JSON.parse(raw) as CapabilityRegistry;
  return { registry, path: registryPath };
}

export function validateRegistry(
  explicitRegistryPath?: string,
  explicitSchemaPath?: string
): RegistryValidationResult {
  const registryPath = findRegistryPath(explicitRegistryPath);
  const schemaPath = findRegistrySchemaPath(explicitSchemaPath);

  const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8')) as Record<string, unknown>;
  const data = JSON.parse(fs.readFileSync(registryPath, 'utf8')) as unknown;

  const ajv = new Ajv2020({ allErrors: true, strict: false });
  // ajv-formats default export typing under NodeNext ESM
  const applyFormats = addFormats as unknown as (instance: Ajv2020) => void;
  applyFormats(ajv);

  const validate = ajv.compile(schema);
  const valid = Boolean(validate(data));

  const errors = (validate.errors ?? []).map((err) => ({
    instancePath: err.instancePath || '/',
    schemaPath: err.schemaPath,
    message: err.message ?? 'Schema validation error',
  }));

  return {
    valid,
    registry_path: registryPath,
    schema_path: schemaPath,
    errors,
  };
}

function scoreSignals(textLower: string, signals: string[]): string[] {
  const matched: string[] = [];
  for (const sig of signals) {
    const s = sig.toLowerCase();
    if (textLower.includes(s)) {
      matched.push(sig);
    }
  }
  return matched;
}

export function evaluateFit(
  promptText: string,
  registry: CapabilityRegistry
): FitResult {
  const lower = String(promptText || '').toLowerCase();

  const negativeMatches = registry.suitability.not_recommended_for
    .map((domain) => ({ domain, matched: scoreSignals(lower, domain.signals) }))
    .filter((x) => x.matched.length > 0)
    .sort((a, b) => b.matched.length - a.matched.length);

  const recommendedMatches = registry.suitability.recommended_for
    .map((domain) => ({ domain, matched: scoreSignals(lower, domain.signals) }))
    .filter((x) => x.matched.length > 0)
    .sort((a, b) => b.matched.length - a.matched.length);

  const contestedMatches = registry.suitability.contested_for
    .map((domain) => ({ domain, matched: scoreSignals(lower, domain.signals) }))
    .filter((x) => x.matched.length > 0)
    .sort((a, b) => b.matched.length - a.matched.length);

  const topNegative = negativeMatches[0];
  const topRecommended = recommendedMatches[0];
  const topContested = contestedMatches[0];

  if (
    topNegative &&
    (!topRecommended || topNegative.matched.length >= topRecommended.matched.length)
  ) {
    return {
      decision: 'not_recommended',
      wordpress_fit: false,
      domain_id: topNegative.domain.id,
      domain_label: topNegative.domain.label,
      matched_signals: topNegative.matched,
      rationale: topNegative.domain.why_not_wordpress,
      preferred_alternatives: topNegative.domain.preferred_alternatives,
      blueprint_preset: null,
    };
  }

  if (topRecommended) {
    return {
      decision: 'recommended',
      wordpress_fit: true,
      domain_id: topRecommended.domain.id,
      domain_label: topRecommended.domain.label,
      matched_signals: topRecommended.matched,
      rationale: topRecommended.domain.why_wordpress_fits,
      alternatives_to_consider: topRecommended.domain.alternatives_to_consider,
      blueprint_preset: topRecommended.domain.blueprint_preset,
    };
  }

  if (topContested) {
    return {
      decision: 'contested',
      wordpress_fit: true,
      domain_id: topContested.domain.id,
      domain_label: topContested.domain.label,
      matched_signals: topContested.matched,
      rationale: topContested.domain.why_wordpress_fits,
      alternatives_to_consider: topContested.domain.alternatives_to_consider,
      blueprint_preset: topContested.domain.blueprint_preset,
    };
  }

  return {
    decision: 'needs_clarification',
    wordpress_fit: null,
    domain_id: null,
    domain_label: 'Ambiguous request',
    matched_signals: [],
    rationale:
      'Ask who will edit content after launch and whether this is a content/commerce site vs a custom web app, developer docs, or single static page.',
    blueprint_preset: null,
  };
}
