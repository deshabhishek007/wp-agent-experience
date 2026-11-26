# Small Business WordPress Playground Blueprint

Starter WordPress Blueprint for local small businesses, service providers, and community organizations (configured out of the box as **Hearthstone Bakery**).

## What This Blueprint Provisions

- **Site Configuration:** Sets `blogname`, `blogdescription`, pretty permalinks (`/%postname%/`), and disables page comments by default.
- **Gutenberg Block Pages:** Publishes `Home` (assigned as static front page via `show_on_front=page` and `page_on_front`), `Services`, `About`, `Contact`, and `Updates` (assigned as `page_for_posts`), plus an initial published announcement post.
- **MU-Plugin (`/wordpress/wp-content/mu-plugins/wpax-business.php`):**
  - Registers `GET /wp-json/wpax/v1/business-info` exposing opening hours, contact details, and services.
  - Registers WordPress 6.9+ Abilities API category `wpax` and ability `wpax/get-business-info` (cleanly guarded with `function_exists()`).

## Usage

Run headlessly to verify setup:

```bash
npx -y @wp-playground/cli@3.1.66 run-blueprint --blueprint=blueprints/small-business/blueprint.json
```

Start a local interactive preview server:

```bash
npx -y @wp-playground/cli@3.1.66 server --blueprint=blueprints/small-business/blueprint.json
```

## Verification Spec

See `verify.json` for automated checks (`expected_blogname`, `required_pages`, `required_rest_routes`, `require_abilities_api`, and `required_mu_plugins`).
