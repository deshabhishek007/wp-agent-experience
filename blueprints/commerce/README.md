# Commerce WordPress Playground Blueprint

Reproducible online store starter (**Northline Bike Parts**) packaged in two variants so AI coding agents get both fast offline-deterministic verification and full upstream WooCommerce compatibility.

## Variants

### 1. `blueprint.json` (Fast Deterministic Store — Default)

- Zero external plugin download flakiness; boots cleanly in WordPress Playground with SQLite.
- Installs `/wordpress/wp-content/mu-plugins/wpax-store.php`:
  - Registers `wpax_product` custom post type (`show_in_rest: true`, route `/wp/v2/wpax_product`).
  - Exposes structured product meta fields: `wpax_sku`, `wpax_price`, `wpax_stock_qty`, and `wpax_weight_kg`.
  - Registers `GET/POST /wp-json/wpax/v1/shipping-quote?weight_kg=<kg>` for tiered weight-based shipping quotes.
  - Registers WordPress 6.9+ Abilities API ability `wpax/list-products` (guarded with `function_exists()`).
- Publishes `Shop` (front page), `Catalog`, `Cart`, `Shipping`, and `Contact` pages, and seeds 4 stocked products with weights.

### 2. `blueprint.woocommerce.json` (Full Upstream WooCommerce)

- Installs and activates `woocommerce` and `weight-based-shipping-for-woocommerce` directly from WordPress.org, configures `kg` weight units and `USD` currency, and seeds 4 `WC_Product_Simple` products with SKU, managed stock quantities, and weights.

## Usage

```bash
# Fast deterministic starter
npx -y @wp-playground/cli@3.1.66 run-blueprint --blueprint=blueprints/commerce/blueprint.json

# Full WooCommerce + Weight Based Shipping variant (requires wordpress.org network access)
npx -y @wp-playground/cli@3.1.66 run-blueprint --blueprint=blueprints/commerce/blueprint.woocommerce.json
```

## Verification Spec

See `verify.json` for automated checks covering pages, custom post type registration, minimum product count (`4`), REST routes (`/wp/v2/wpax_product`, `/wpax/v1/shipping-quote`), and Abilities API registration.
