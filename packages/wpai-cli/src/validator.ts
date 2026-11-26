import fs from 'node:fs';
import path from 'node:path';
import type { ValidationIssue, ValidationResult } from './types.js';

/**
 * Exact allowed top-level Blueprint v1 keys from the official WordPress `blueprint` skill.
 */
export const ALLOWED_TOP_LEVEL_KEYS = new Set<string>([
  '$schema',
  'landingPage',
  'description',
  'meta',
  'preferredVersions',
  'features',
  'phpExtensionBundles',
  'extraLibraries',
  'constants',
  'plugins',
  'siteOptions',
  'login',
  'steps',
]);

export const ALLOWED_FEATURE_KEYS = new Set<string>(['networking', 'intl']);

export const ALLOWED_PREFERRED_VERSION_KEYS = new Set<string>(['php', 'wp']);

export const KNOWN_STEP_NAMES = new Set<string>([
  'activatePlugin',
  'activateTheme',
  'cp',
  'defineSiteUrl',
  'defineWpConfigConsts',
  'enableMultisite',
  'importThemeStarterContent',
  'importWordPressFiles',
  'importWxr',
  'installPlugin',
  'installTheme',
  'login',
  'mkdir',
  'mv',
  'resetData',
  'rm',
  'rmdir',
  'runPHP',
  'runPHPWithOptions',
  'runSql',
  'setSiteLanguage',
  'setSiteOptions',
  'unzip',
  'updateUserMeta',
  'wp-cli',
  'writeFile',
  'writeFiles',
]);

/**
 * Common WordPress runtime functions/globals that require wp-load.php when called inside runPHP.
 */
const WP_RUNTIME_PATTERN =
  /\b(wp_insert_post|wp_update_post|wp_delete_post|wp_create_user|wp_insert_user|wp_insert_term|wp_create_category|get_option|update_option|add_option|delete_option|get_bloginfo|get_posts|get_pages|get_page_by_path|get_term_by|get_users|register_post_type|register_taxonomy|rest_do_request|wp_register_ability|wp_get_abilities|wp_get_theme|get_mu_plugins|flush_rewrite_rules|WP_Query|WP_REST_Request|WP_Ability|WP_Abilities_Registry)\b|\$wpdb\b/;

const WP_LOAD_PATTERN = /wp-load\.php/;

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

export function validateBlueprintObject(
  data: unknown,
  filePath?: string
): ValidationResult {
  const errors: ValidationIssue[] = [];
  const warnings: ValidationIssue[] = [];

  if (!isPlainObject(data)) {
    errors.push({
      severity: 'error',
      code: 'ROOT_NOT_OBJECT',
      path: '$',
      message: 'Blueprint root must be a JSON object.',
    });
    return { valid: false, file: filePath, errors, warnings };
  }

  // 1. Check allowed top-level keys
  for (const key of Object.keys(data)) {
    if (!ALLOWED_TOP_LEVEL_KEYS.has(key)) {
      errors.push({
        severity: 'error',
        code: 'UNKNOWN_TOP_LEVEL_KEY',
        path: `$.${key}`,
        message: `Unknown top-level Blueprint v1 key "${key}". Allowed keys: ${Array.from(ALLOWED_TOP_LEVEL_KEYS).join(', ')}.`,
      });
    }
  }

  // 2. $schema (recommended warning if missing, error if non-string)
  if ('$schema' in data && typeof data.$schema !== 'string') {
    errors.push({
      severity: 'error',
      code: 'INVALID_SCHEMA_FIELD',
      path: '$.$schema',
      message: '"$schema" must be a string URL.',
    });
  } else if (!('$schema' in data)) {
    warnings.push({
      severity: 'warning',
      code: 'MISSING_SCHEMA_FIELD',
      path: '$.$schema',
      message:
        'Consider adding "$schema": "https://playground.wordpress.net/blueprint-schema.json" for editor validation.',
    });
  }

  // 3. landingPage
  if ('landingPage' in data) {
    if (typeof data.landingPage !== 'string' || !data.landingPage.startsWith('/')) {
      errors.push({
        severity: 'error',
        code: 'INVALID_LANDING_PAGE',
        path: '$.landingPage',
        message: '"landingPage" must be a string path starting with "/".',
      });
    }
  }

  // 4. description
  if ('description' in data && typeof data.description !== 'string') {
    errors.push({
      severity: 'error',
      code: 'INVALID_DESCRIPTION',
      path: '$.description',
      message: '"description" must be a string.',
    });
  }

  // 5. meta
  if ('meta' in data) {
    if (!isPlainObject(data.meta)) {
      errors.push({
        severity: 'error',
        code: 'INVALID_META',
        path: '$.meta',
        message: '"meta" must be an object.',
      });
    } else {
      const allowedMetaKeys = new Set(['title', 'description', 'author', 'categories']);
      for (const k of Object.keys(data.meta)) {
        if (!allowedMetaKeys.has(k)) {
          errors.push({
            severity: 'error',
            code: 'UNKNOWN_META_KEY',
            path: `$.meta.${k}`,
            message: `Unknown key "${k}" in meta. Allowed keys: title, description, author, categories.`,
          });
        }
      }
      if (typeof data.meta.title !== 'string' || data.meta.title.trim().length === 0) {
        errors.push({
          severity: 'error',
          code: 'MISSING_META_TITLE',
          path: '$.meta.title',
          message: '"meta.title" is required when "meta" is present.',
        });
      }
      if (typeof data.meta.author !== 'string' || data.meta.author.trim().length === 0) {
        errors.push({
          severity: 'error',
          code: 'MISSING_META_AUTHOR',
          path: '$.meta.author',
          message: '"meta.author" is required when "meta" is present.',
        });
      }
    }
  }

  // 6. preferredVersions
  if ('preferredVersions' in data) {
    if (!isPlainObject(data.preferredVersions)) {
      errors.push({
        severity: 'error',
        code: 'INVALID_PREFERRED_VERSIONS',
        path: '$.preferredVersions',
        message: '"preferredVersions" must be an object with optional "php" and "wp" keys.',
      });
    } else {
      for (const k of Object.keys(data.preferredVersions)) {
        if (!ALLOWED_PREFERRED_VERSION_KEYS.has(k)) {
          errors.push({
            severity: 'error',
            code: 'UNKNOWN_PREFERRED_VERSION_KEY',
            path: `$.preferredVersions.${k}`,
            message: `Unknown key "${k}" in preferredVersions. Only "php" and "wp" are allowed.`,
          });
        }
      }

      if ('php' in data.preferredVersions) {
        const php = data.preferredVersions.php;
        if (
          typeof php !== 'string' ||
          (php !== 'latest' && !/^\d+\.\d+$/.test(php))
        ) {
          errors.push({
            severity: 'error',
            code: 'INVALID_PHP_VERSION',
            path: '$.preferredVersions.php',
            message: `Invalid preferredVersions.php "${String(php)}". Must be "latest" or major.minor format (e.g. "8.3"), not a patch version like "8.3.6".`,
          });
        }
      }

      if ('wp' in data.preferredVersions) {
        const wp = data.preferredVersions.wp;
        if (typeof wp !== 'string' || wp.trim().length === 0) {
          errors.push({
            severity: 'error',
            code: 'INVALID_WP_VERSION',
            path: '$.preferredVersions.wp',
            message: '"preferredVersions.wp" must be a non-empty string (e.g. "latest", "6.9", "nightly").',
          });
        }
      }
    }
  }

  // 7. features (only networking and intl)
  if ('features' in data) {
    if (!isPlainObject(data.features)) {
      errors.push({
        severity: 'error',
        code: 'INVALID_FEATURES',
        path: '$.features',
        message: '"features" must be an object.',
      });
    } else {
      for (const [k, v] of Object.entries(data.features)) {
        if (!ALLOWED_FEATURE_KEYS.has(k)) {
          errors.push({
            severity: 'error',
            code: 'UNKNOWN_FEATURE_KEY',
            path: `$.features.${k}`,
            message: `Unknown feature "${k}". Blueprint v1 "features" only allows "networking" and "intl".`,
          });
        } else if (typeof v !== 'boolean') {
          errors.push({
            severity: 'error',
            code: 'INVALID_FEATURE_VALUE',
            path: `$.features.${k}`,
            message: `Feature "${k}" must be a boolean.`,
          });
        }
      }
    }
  }

  // 8. phpExtensionBundles / extraLibraries / plugins
  for (const arrayKey of ['phpExtensionBundles', 'extraLibraries'] as const) {
    if (arrayKey in data) {
      const val = data[arrayKey];
      if (!Array.isArray(val) || !val.every((item) => typeof item === 'string')) {
        errors.push({
          severity: 'error',
          code: 'INVALID_STRING_ARRAY',
          path: `$.${arrayKey}`,
          message: `"${arrayKey}" must be an array of strings.`,
        });
      }
    }
  }

  if ('plugins' in data) {
    if (!Array.isArray(data.plugins)) {
      errors.push({
        severity: 'error',
        code: 'INVALID_PLUGINS',
        path: '$.plugins',
        message: '"plugins" must be an array of plugin slugs, URLs, or resource objects.',
      });
    }
  }

  if ('constants' in data && !isPlainObject(data.constants)) {
    errors.push({
      severity: 'error',
      code: 'INVALID_CONSTANTS',
      path: '$.constants',
      message: '"constants" must be a JSON object.',
    });
  }

  if ('siteOptions' in data && !isPlainObject(data.siteOptions)) {
    errors.push({
      severity: 'error',
      code: 'INVALID_SITE_OPTIONS',
      path: '$.siteOptions',
      message: '"siteOptions" must be a JSON object.',
    });
  }

  if ('login' in data) {
    const login = data.login;
    if (typeof login !== 'boolean' && !isPlainObject(login)) {
      errors.push({
        severity: 'error',
        code: 'INVALID_LOGIN',
        path: '$.login',
        message: '"login" must be a boolean or an object with username/password.',
      });
    }
  }

  // 9. steps
  if ('steps' in data) {
    if (!Array.isArray(data.steps)) {
      errors.push({
        severity: 'error',
        code: 'INVALID_STEPS',
        path: '$.steps',
        message: '"steps" must be an array of step objects.',
      });
    } else {
      data.steps.forEach((rawStep, idx) => {
        const stepPath = `$.steps[${idx}]`;
        if (!isPlainObject(rawStep)) {
          errors.push({
            severity: 'error',
            code: 'STEP_NOT_OBJECT',
            path: stepPath,
            message: 'Each step must be a JSON object with a "step" string property.',
          });
          return;
        }

        const stepName = rawStep.step;
        if (typeof stepName !== 'string' || stepName.trim().length === 0) {
          errors.push({
            severity: 'error',
            code: 'MISSING_STEP_NAME',
            path: `${stepPath}.step`,
            message: 'Step object is missing a valid string "step" name.',
          });
          return;
        }

        // Reject common wrong step name "cli"
        if (stepName === 'cli') {
          errors.push({
            severity: 'error',
            code: 'INVALID_CLI_STEP_NAME',
            path: `${stepPath}.step`,
            message: 'Invalid step name "cli". Use "wp-cli" instead.',
          });
        } else if (!KNOWN_STEP_NAMES.has(stepName)) {
          warnings.push({
            severity: 'warning',
            code: 'UNKNOWN_STEP_NAME',
            path: `${stepPath}.step`,
            message: `Unrecognized Blueprint v1 step "${stepName}". Verify spelling against the Playground Blueprint schema.`,
          });
        }

        // Reject deprecated pluginZipFile / themeZipFile
        if ('pluginZipFile' in rawStep) {
          errors.push({
            severity: 'error',
            code: 'DEPRECATED_PLUGIN_ZIP_FILE',
            path: `${stepPath}.pluginZipFile`,
            message:
              '"pluginZipFile" is deprecated and rejected. Use "pluginData" instead.',
          });
        }

        if ('themeZipFile' in rawStep) {
          errors.push({
            severity: 'error',
            code: 'DEPRECATED_THEME_ZIP_FILE',
            path: `${stepPath}.themeZipFile`,
            message:
              '"themeZipFile" is deprecated and rejected. Use "themeData" instead.',
          });
        }

        // Step-specific checks
        if (stepName === 'installPlugin' && !('pluginData' in rawStep) && !('pluginZipFile' in rawStep)) {
          errors.push({
            severity: 'error',
            code: 'MISSING_PLUGIN_DATA',
            path: stepPath,
            message: 'installPlugin step requires "pluginData".',
          });
        }

        if (stepName === 'installTheme' && !('themeData' in rawStep) && !('themeZipFile' in rawStep)) {
          errors.push({
            severity: 'error',
            code: 'MISSING_THEME_DATA',
            path: stepPath,
            message: 'installTheme step requires "themeData".',
          });
        }

        if (stepName === 'writeFile') {
          if (typeof rawStep.path !== 'string' || rawStep.path.length === 0) {
            errors.push({
              severity: 'error',
              code: 'MISSING_WRITE_FILE_PATH',
              path: `${stepPath}.path`,
              message: 'writeFile step requires a non-empty string "path".',
            });
          }
          if (!('data' in rawStep)) {
            errors.push({
              severity: 'error',
              code: 'MISSING_WRITE_FILE_DATA',
              path: `${stepPath}.data`,
              message: 'writeFile step requires "data".',
            });
          }
        }

        if (stepName === 'setSiteOptions') {
          if (!isPlainObject(rawStep.options)) {
            errors.push({
              severity: 'error',
              code: 'INVALID_SET_SITE_OPTIONS',
              path: `${stepPath}.options`,
              message: 'setSiteOptions step requires an "options" object.',
            });
          }
        }

        if (stepName === 'wp-cli') {
          if (typeof rawStep.command !== 'string' || rawStep.command.trim().length === 0) {
            errors.push({
              severity: 'error',
              code: 'INVALID_WP_CLI_COMMAND',
              path: `${stepPath}.command`,
              message: 'wp-cli step requires a non-empty string "command".',
            });
          }
        }

        if (stepName === 'runPHP') {
          if (typeof rawStep.code !== 'string' || rawStep.code.trim().length === 0) {
            errors.push({
              severity: 'error',
              code: 'INVALID_RUN_PHP_CODE',
              path: `${stepPath}.code`,
              message: 'runPHP step requires a non-empty string "code".',
            });
          } else if (
            WP_RUNTIME_PATTERN.test(rawStep.code) &&
            !WP_LOAD_PATTERN.test(rawStep.code)
          ) {
            warnings.push({
              severity: 'warning',
              code: 'RUN_PHP_MISSING_WP_LOAD',
              path: `${stepPath}.code`,
              message:
                'runPHP step invokes WordPress functions/globals without loading "wp-load.php". Add `require_once \'/wordpress/wp-load.php\';` before calling WordPress APIs.',
            });
          }
        }

        if (stepName === 'runPHPWithOptions') {
          const opts = rawStep.options;
          if (!isPlainObject(opts) || typeof opts.code !== 'string') {
            errors.push({
              severity: 'error',
              code: 'INVALID_RUN_PHP_WITH_OPTIONS',
              path: `${stepPath}.options`,
              message: 'runPHPWithOptions step requires an "options" object with string "code".',
            });
          } else if (
            WP_RUNTIME_PATTERN.test(opts.code) &&
            !WP_LOAD_PATTERN.test(opts.code)
          ) {
            warnings.push({
              severity: 'warning',
              code: 'RUN_PHP_MISSING_WP_LOAD',
              path: `${stepPath}.options.code`,
              message:
                'runPHPWithOptions step invokes WordPress functions/globals without loading "wp-load.php".',
            });
          }
        }
      });
    }
  }

  return {
    valid: errors.length === 0,
    file: filePath,
    errors,
    warnings,
  };
}

export function validateBlueprintFile(filePath: string): ValidationResult {
  const absPath = path.resolve(filePath);
  if (!fs.existsSync(absPath)) {
    return {
      valid: false,
      file: absPath,
      errors: [
        {
          severity: 'error',
          code: 'FILE_NOT_FOUND',
          path: '$',
          message: `Blueprint file not found: ${absPath}`,
        },
      ],
      warnings: [],
    };
  }

  let rawText: string;
  try {
    rawText = fs.readFileSync(absPath, 'utf8');
  } catch (err) {
    return {
      valid: false,
      file: absPath,
      errors: [
        {
          severity: 'error',
          code: 'FILE_READ_ERROR',
          path: '$',
          message: `Unable to read blueprint file: ${err instanceof Error ? err.message : String(err)}`,
        },
      ],
      warnings: [],
    };
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(rawText);
  } catch (err) {
    return {
      valid: false,
      file: absPath,
      errors: [
        {
          severity: 'error',
          code: 'INVALID_JSON',
          path: '$',
          message: `Invalid JSON syntax: ${err instanceof Error ? err.message : String(err)}`,
        },
      ],
      warnings: [],
    };
  }

  return validateBlueprintObject(parsed, absPath);
}
