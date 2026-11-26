# Publishing WordPress Playground Blueprint

Multi-author blog and local news publication starter (**Rivertown Dispatch**) with editorial roles, structured categories, block-formatted articles, REST endpoints, and WordPress Abilities API support.

## What This Blueprint Provisions

- **Site Configuration:** Sets `blogname`, `blogdescription`, and date-based editorial permalinks (`/%year%/%monthnum%/%postname%/`).
- **Editorial Taxonomy:** Creates 4 categories: `Local News` (`local-news`), `Community` (`community`), `Culture` (`culture`), and `Opinion` (`opinion`).
- **Editorial Team Roles:** Creates 3 distinct core-role users alongside `admin`:
  - `maya_editor` (`editor`)
  - `david_author` (`author`)
  - `priya_contributor` (`contributor`)
- **Published Content:** Seeds 4 Gutenberg block-formatted articles distributed across authors and categories, plus `About` and `Editorial Policy` pages.
- **MU-Plugin (`/wordpress/wp-content/mu-plugins/wpai-publishing.php`):**
  - Registers `GET /wp-json/wpai/v1/editorial-summary`.
  - Registers WordPress 6.9+ Abilities API ability `wpai/editorial-summary` (cleanly guarded with `function_exists()`).

## Usage

```bash
npx -y @wp-playground/cli@3.1.66 run-blueprint --blueprint=blueprints/publishing/blueprint.json
```

## Verification Spec

See `verify.json` for automated verification checks covering categories, minimum users (`4`), minimum published posts (`4`), REST routes, and Abilities API registration.
