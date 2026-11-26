import fs from 'node:fs';
import path from 'node:path';
import { findBlueprintPresetDir } from './paths.js';
import type { Blueprint, PresetName, VerifySpec } from './types.js';
import { PRESET_NAMES } from './types.js';

export interface PresetTemplate {
  preset: PresetName;
  defaultName: string;
  blueprint: Blueprint;
  verify: VerifySpec;
  readme: string;
}

export interface InitOptions {
  preset: PresetName;
  dir: string;
  name?: string;
  wp?: string;
  php?: string;
}

export interface InitResult {
  preset: PresetName;
  dir: string;
  source: 'repo-blueprints' | 'built-in';
  name: string;
  files_written: string[];
}

export function isValidPreset(value: string): value is PresetName {
  return (PRESET_NAMES as readonly string[]).includes(value);
}

function buildSmallBusinessTemplate(): PresetTemplate {
  const defaultName = 'Local Business Starter';
  const muPluginCode = `<?php
/**
 * Plugin Name: WPAX Business Essentials
 * Description: Lightweight business hours, inquiry REST endpoint, and WordPress 6.9+ Abilities API site-info registration.
 */
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

add_action( 'rest_api_init', function () {
    register_rest_route( 'wpax/v1', '/site-info', array(
        'methods'             => 'GET',
        'permission_callback' => '__return_true',
        'callback'            => function () {
            return rest_ensure_response( array(
                'site_name' => get_bloginfo( 'name' ),
                'tagline'   => get_bloginfo( 'description' ),
                'hours'     => get_option( 'wpax_business_hours', 'Mon-Fri 08:00-18:00, Sat 09:00-15:00' ),
                'phone'     => get_option( 'wpax_business_phone', '(555) 010-2026' ),
            ) );
        },
    ) );
} );

add_action( 'wp_abilities_api_categories_init', function () {
    if ( function_exists( 'wp_register_ability_category' ) ) {
        wp_register_ability_category( 'wpax', array(
            'label'       => 'WPAX Site',
            'description' => 'WordPress Agent Experience site metadata abilities.',
        ) );
    }
} );

add_action( 'wp_abilities_api_init', function () {
    if ( function_exists( 'wp_register_ability' ) ) {
        wp_register_ability( 'wpax/get-business-info', array(
            'label'               => 'Get Business Info',
            'description'         => 'Returns business name, hours, and contact phone number.',
            'category'            => 'wpax',
            'execute_callback'    => function () {
                return array(
                    'site_name' => get_bloginfo( 'name' ),
                    'hours'     => get_option( 'wpax_business_hours', 'Mon-Fri 08:00-18:00, Sat 09:00-15:00' ),
                    'phone'     => get_option( 'wpax_business_phone', '(555) 010-2026' ),
                );
            },
            'permission_callback' => '__return_true',
            'meta'                => array(
                'annotations' => array( 'readonly' => true ),
            ),
        ) );
    }
} );
`;

  const seedPhp = `<?php
require_once '/wordpress/wp-load.php';

$pages = array(
    'home' => array(
        'title'   => 'Home',
        'content' => '<!-- wp:heading {"level":1} --><h1>Welcome to Our Local Business</h1><!-- /wp:heading --><!-- wp:paragraph --><p>Edit this page visually in the WordPress Block Editor anytime—no code or Git required.</p><!-- /wp:paragraph -->',
    ),
    'services' => array(
        'title'   => 'Services',
        'content' => '<!-- wp:heading --><h2>Our Services &amp; Schedule</h2><!-- /wp:heading --><!-- wp:list --><ul><li>Core Service A — Daily</li><li>Core Service B — By Appointment</li></ul><!-- /wp:list -->',
    ),
    'about' => array(
        'title'   => 'About',
        'content' => '<!-- wp:heading --><h2>About Us</h2><!-- /wp:heading --><!-- wp:paragraph --><p>Locally owned and operated. Update our story, team photos, and announcements directly from WP Admin.</p><!-- /wp:paragraph -->',
    ),
    'contact' => array(
        'title'   => 'Contact',
        'content' => '<!-- wp:heading --><h2>Hours &amp; Contact</h2><!-- /wp:heading --><!-- wp:paragraph --><p>Hours: Mon-Fri 08:00-18:00, Sat 09:00-15:00. Reach us anytime by email or phone.</p><!-- /wp:paragraph -->',
    ),
);

$home_id = 0;
foreach ( $pages as $slug => $spec ) {
    $existing = get_page_by_path( $slug );
    if ( $existing ) {
        $id = $existing->ID;
    } else {
        $id = wp_insert_post( array(
            'post_type'    => 'page',
            'post_status'  => 'publish',
            'post_name'    => $slug,
            'post_title'   => $spec['title'],
            'post_content' => $spec['content'],
        ) );
    }
    if ( $slug === 'home' && $id ) {
        $home_id = $id;
    }
}

if ( $home_id ) {
    update_option( 'show_on_front', 'page' );
    update_option( 'page_on_front', $home_id );
}
update_option( 'permalink_structure', '/%postname%/' );
flush_rewrite_rules();
`;

  const blueprint: Blueprint = {
    $schema: 'https://playground.wordpress.net/blueprint-schema.json',
    landingPage: '/',
    meta: {
      title: defaultName,
      author: 'wpax',
      description: 'Owner-editable small business WordPress starter with Block Editor pages, REST endpoint, and Abilities API.',
      categories: ['small-business', 'wpax'],
    },
    preferredVersions: {
      php: '8.3',
      wp: 'latest',
    },
    login: true,
    steps: [
      {
        step: 'setSiteOptions',
        options: {
          blogname: defaultName,
          blogdescription: 'Owner-editable local business site powered by WordPress',
          wpax_business_hours: 'Mon-Fri 08:00-18:00, Sat 09:00-15:00',
          wpax_business_phone: '(555) 010-2026',
        },
      },
      {
        step: 'mkdir',
        path: '/wordpress/wp-content/mu-plugins',
      },
      {
        step: 'writeFile',
        path: '/wordpress/wp-content/mu-plugins/wpax-business-essentials.php',
        data: muPluginCode,
      },
      {
        step: 'runPHP',
        code: seedPhp,
      },
    ],
  };

  const verify: VerifySpec = {
    expected_blogname: defaultName,
    required_pages: ['home', 'services', 'about', 'contact'],
    required_options: {
      show_on_front: 'page',
    },
    required_rest_routes: ['/wp/v2/pages', '/wpax/v1/site-info'],
    require_abilities_api: true,
  };

  const readme = `# ${defaultName}

WordPress starter scaffolded by \`wpax init small-business\`.

## Local Preview (Zero MySQL / Zero Docker)

\`\`\`bash
npm run start
\`\`\`

## Automated Functional Verification

\`\`\`bash
wpax verify .
\`\`\`

## Owner Editing

Log in to \`/wp-admin/\` to edit Home, Services, About, and Contact pages visually in the WordPress Block Editor.
`;

  return { preset: 'small-business', defaultName, blueprint, verify, readme };
}

function buildCommerceTemplate(): PresetTemplate {
  const defaultName = 'WPAX Online Store';
  const muPluginCode = `<?php
/**
 * Plugin Name: WPAX Commerce Starter
 * Description: Lightweight product catalog CPT with SKU, price, stock quantity, weight-based shipping rules, and REST/Abilities integration.
 */
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

add_action( 'init', function () {
    register_post_type( 'wpax_product', array(
        'labels' => array(
            'name'          => 'Products',
            'singular_name' => 'Product',
        ),
        'public'       => true,
        'show_in_rest' => true,
        'supports'     => array( 'title', 'editor', 'custom-fields', 'thumbnail' ),
        'has_archive'  => true,
        'rewrite'      => array( 'slug' => 'products' ),
    ) );

    foreach ( array( 'sku', 'price_usd', 'stock_qty', 'weight_kg' ) as $meta_key ) {
        register_post_meta( 'wpax_product', $meta_key, array(
            'show_in_rest' => true,
            'single'       => true,
            'type'         => 'string',
        ) );
    }
} );

add_action( 'rest_api_init', function () {
    register_rest_route( 'wpax/v1', '/shipping-rates', array(
        'methods'             => 'GET',
        'permission_callback' => '__return_true',
        'callback'            => function () {
            return rest_ensure_response( array(
                'model' => 'weight-based',
                'tiers' => array(
                    array( 'max_kg' => 1.0, 'rate_usd' => 5.00 ),
                    array( 'max_kg' => 5.0, 'rate_usd' => 12.00 ),
                    array( 'max_kg' => 20.0, 'rate_usd' => 25.00 ),
                ),
            ) );
        },
    ) );
} );

add_action( 'wp_abilities_api_categories_init', function () {
    if ( function_exists( 'wp_register_ability_category' ) ) {
        wp_register_ability_category( 'wpax', array(
            'label'       => 'WPAX Store',
            'description' => 'Store catalog and shipping abilities.',
        ) );
    }
} );

add_action( 'wp_abilities_api_init', function () {
    if ( function_exists( 'wp_register_ability' ) ) {
        wp_register_ability( 'wpax/list-products', array(
            'label'               => 'List Catalog Products',
            'description'         => 'Lists published products with SKU, price, stock quantity, and weight.',
            'category'            => 'wpax',
            'execute_callback'    => function () {
                $items = get_posts( array(
                    'post_type'      => 'wpax_product',
                    'post_status'    => 'publish',
                    'posts_per_page' => 50,
                ) );
                return array_map( function ( $p ) {
                    return array(
                        'id'        => $p->ID,
                        'title'     => $p->post_title,
                        'sku'       => get_post_meta( $p->ID, 'sku', true ),
                        'price_usd' => get_post_meta( $p->ID, 'price_usd', true ),
                        'stock_qty' => get_post_meta( $p->ID, 'stock_qty', true ),
                        'weight_kg' => get_post_meta( $p->ID, 'weight_kg', true ),
                    );
                }, $items );
            },
            'permission_callback' => '__return_true',
            'meta'                => array(
                'annotations' => array( 'readonly' => true ),
            ),
        ) );
    }
} );
`;

  const seedPhp = `<?php
require_once '/wordpress/wp-load.php';

$pages = array(
    'shop' => array(
        'title'   => 'Shop',
        'content' => '<!-- wp:heading {"level":1} --><h1>Storefront</h1><!-- /wp:heading --><!-- wp:paragraph --><p>Browse our catalog below. Manage inventory, pricing, and WooCommerce extensions from WP Admin.</p><!-- /wp:paragraph -->',
    ),
    'cart' => array(
        'title'   => 'Cart & Checkout',
        'content' => '<!-- wp:heading --><h2>Cart &amp; Checkout</h2><!-- /wp:heading --><!-- wp:paragraph --><p>Ready for WooCommerce Cart/Checkout blocks and weight-based shipping rules.</p><!-- /wp:paragraph -->',
    ),
    'shipping-and-returns' => array(
        'title'   => 'Shipping & Returns',
        'content' => '<!-- wp:heading --><h2>Weight-Based Shipping</h2><!-- /wp:heading --><!-- wp:list --><ul><li>Up to 1 kg: $5.00</li><li>1–5 kg: $12.00</li><li>5–20 kg: $25.00</li></ul><!-- /wp:list -->',
    ),
    'contact' => array(
        'title'   => 'Contact',
        'content' => '<!-- wp:heading --><h2>Store Support</h2><!-- /wp:heading --><!-- wp:paragraph --><p>Questions about orders or wholesale stock? Contact our team anytime.</p><!-- /wp:paragraph -->',
    ),
);

$shop_id = 0;
foreach ( $pages as $slug => $spec ) {
    $existing = get_page_by_path( $slug );
    $id = $existing ? $existing->ID : wp_insert_post( array(
        'post_type'    => 'page',
        'post_status'  => 'publish',
        'post_name'    => $slug,
        'post_title'   => $spec['title'],
        'post_content' => $spec['content'],
    ) );
    if ( $slug === 'shop' && $id ) {
        $shop_id = $id;
    }
}

$products = array(
    array( 'title' => 'Starter Item Alpha', 'sku' => 'SKU-001', 'price' => '24.00', 'stock' => '45', 'weight' => '0.4' ),
    array( 'title' => 'Starter Item Beta',  'sku' => 'SKU-002', 'price' => '48.00', 'stock' => '18', 'weight' => '1.2' ),
    array( 'title' => 'Starter Item Gamma', 'sku' => 'SKU-003', 'price' => '75.00', 'stock' => '10', 'weight' => '2.5' ),
);

foreach ( $products as $item ) {
    $pid = wp_insert_post( array(
        'post_type'    => 'wpax_product',
        'post_status'  => 'publish',
        'post_title'   => $item['title'],
        'post_content' => '<!-- wp:paragraph --><p>Editable product description with SKU, stock tracking, and shipping weight.</p><!-- /wp:paragraph -->',
    ) );
    if ( $pid && ! is_wp_error( $pid ) ) {
        update_post_meta( $pid, 'sku', $item['sku'] );
        update_post_meta( $pid, 'price_usd', $item['price'] );
        update_post_meta( $pid, 'stock_qty', $item['stock'] );
        update_post_meta( $pid, 'weight_kg', $item['weight'] );
    }
}

if ( $shop_id ) {
    update_option( 'show_on_front', 'page' );
    update_option( 'page_on_front', $shop_id );
}
update_option( 'permalink_structure', '/%postname%/' );
flush_rewrite_rules();
`;

  const blueprint: Blueprint = {
    $schema: 'https://playground.wordpress.net/blueprint-schema.json',
    landingPage: '/',
    meta: {
      title: defaultName,
      author: 'wpax',
      description: 'Online store WordPress starter with catalog CPT, stock & weight metadata, shipping rules, and WooCommerce upgrade path.',
      categories: ['commerce', 'wpax'],
    },
    preferredVersions: {
      php: '8.3',
      wp: 'latest',
    },
    login: true,
    steps: [
      {
        step: 'setSiteOptions',
        options: {
          blogname: defaultName,
          blogdescription: 'Open-source online store powered by WordPress',
        },
      },
      {
        step: 'mkdir',
        path: '/wordpress/wp-content/mu-plugins',
      },
      {
        step: 'writeFile',
        path: '/wordpress/wp-content/mu-plugins/wpax-commerce-starter.php',
        data: muPluginCode,
      },
      {
        step: 'runPHP',
        code: seedPhp,
      },
    ],
  };

  const verify: VerifySpec = {
    expected_blogname: defaultName,
    required_pages: ['shop', 'cart', 'shipping-and-returns', 'contact'],
    required_post_types: ['wpax_product'],
    required_rest_routes: ['/wp/v2/wpax_product', '/wpax/v1/shipping-rates'],
    require_abilities_api: true,
  };

  const readme = `# ${defaultName}

WordPress commerce starter scaffolded by \`wpax init commerce\`.

## Local Preview (Zero MySQL / Zero Docker)

\`\`\`bash
npm run start
\`\`\`

## Automated Functional Verification

\`\`\`bash
wpax verify .
\`\`\`

## WooCommerce Upgrade Path

Add \`woocommerce\` and \`weight-based-shipping-for-woocommerce\` to \`blueprint.json\` or install them from WP Admin for full checkout and payment gateways.
`;

  return { preset: 'commerce', defaultName, blueprint, verify, readme };
}

function buildPublishingTemplate(): PresetTemplate {
  const defaultName = 'WPAX Community News';
  const seedPhp = `<?php
require_once '/wordpress/wp-load.php';

$categories = array(
    'local-news' => 'Local News',
    'guides'     => 'Guides',
    'opinion'    => 'Opinion',
);

$cat_ids = array();
foreach ( $categories as $slug => $label ) {
    $term = term_exists( $slug, 'category' );
    if ( ! $term ) {
        $term = wp_insert_term( $label, 'category', array( 'slug' => $slug ) );
    }
    if ( ! is_wp_error( $term ) ) {
        $cat_ids[ $slug ] = is_array( $term ) ? (int) $term['term_id'] : (int) $term;
    }
}

$authors = array(
    array( 'login' => 'maya_editor', 'email' => 'maya@example.org', 'name' => 'Maya Lin', 'role' => 'editor' ),
    array( 'login' => 'sam_reporter', 'email' => 'sam@example.org', 'name' => 'Sam Patel', 'role' => 'author' ),
    array( 'login' => 'alex_contrib', 'email' => 'alex@example.org', 'name' => 'Alex Rivera', 'role' => 'contributor' ),
);

$author_ids = array();
foreach ( $authors as $u ) {
    $existing = get_user_by( 'login', $u['login'] );
    if ( $existing ) {
        $uid = $existing->ID;
    } else {
        $uid = wp_insert_user( array(
            'user_login'   => $u['login'],
            'user_pass'    => wp_generate_password( 20, true ),
            'user_email'   => $u['email'],
            'display_name' => $u['name'],
            'role'         => $u['role'],
        ) );
    }
    if ( ! is_wp_error( $uid ) ) {
        $author_ids[ $u['login'] ] = (int) $uid;
    }
}

$pages = array(
    'about' => array(
        'title'   => 'About',
        'content' => '<!-- wp:heading --><h2>About Our Publication</h2><!-- /wp:heading --><!-- wp:paragraph --><p>Independent reporting and stories published using WordPress core editorial workflows.</p><!-- /wp:paragraph -->',
    ),
    'editorial-team' => array(
        'title'   => 'Editorial Team',
        'content' => '<!-- wp:heading --><h2>Meet Our Writers</h2><!-- /wp:heading --><!-- wp:paragraph --><p>Every contributor has their own login, role permissions, and automatic author archive page.</p><!-- /wp:paragraph -->',
    ),
);

foreach ( $pages as $slug => $spec ) {
    if ( ! get_page_by_path( $slug ) ) {
        wp_insert_post( array(
            'post_type'    => 'page',
            'post_status'  => 'publish',
            'post_name'    => $slug,
            'post_title'   => $spec['title'],
            'post_content' => $spec['content'],
        ) );
    }
}

$articles = array(
    array(
        'title'  => 'Town Council Approves New Community Trail',
        'cat'    => 'local-news',
        'author' => $author_ids['maya_editor'] ?? 1,
        'body'   => '<!-- wp:paragraph --><p>Local residents gathered Tuesday evening to celebrate approval of the three-mile walking and cycling loop.</p><!-- /wp:paragraph -->',
    ),
    array(
        'title'  => 'Weekend Farmers Market Guide',
        'cat'    => 'guides',
        'author' => $author_ids['sam_reporter'] ?? 1,
        'body'   => '<!-- wp:paragraph --><p>Seasonal produce schedules, parking tips, and bakeries opening early every Saturday morning.</p><!-- /wp:paragraph -->',
    ),
    array(
        'title'  => 'Why Independent Local Reporting Matters',
        'cat'    => 'opinion',
        'author' => $author_ids['maya_editor'] ?? 1,
        'body'   => '<!-- wp:paragraph --><p>Owning our domain, RSS feed, and editorial archive ensures our community stories remain accessible forever.</p><!-- /wp:paragraph -->',
    ),
);

foreach ( $articles as $art ) {
    wp_insert_post( array(
        'post_type'     => 'post',
        'post_status'   => 'publish',
        'post_title'    => $art['title'],
        'post_content'  => $art['body'],
        'post_author'   => $art['author'],
        'post_category' => isset( $cat_ids[ $art['cat'] ] ) ? array( $cat_ids[ $art['cat'] ] ) : array(),
    ) );
}

update_option( 'permalink_structure', '/%postname%/' );
flush_rewrite_rules();
`;

  const blueprint: Blueprint = {
    $schema: 'https://playground.wordpress.net/blueprint-schema.json',
    landingPage: '/',
    meta: {
      title: defaultName,
      author: 'wpax',
      description: 'Multi-author blog and local news publication starter using WordPress core Posts, Categories, and Editorial Roles.',
      categories: ['publishing', 'wpax'],
    },
    preferredVersions: {
      php: '8.3',
      wp: 'latest',
    },
    login: true,
    steps: [
      {
        step: 'setSiteOptions',
        options: {
          blogname: defaultName,
          blogdescription: 'Multi-author community blog and newsroom powered by WordPress',
        },
      },
      {
        step: 'runPHP',
        code: seedPhp,
      },
    ],
  };

  const verify: VerifySpec = {
    expected_blogname: defaultName,
    required_pages: ['about', 'editorial-team'],
    required_posts_min: 3,
    required_categories: ['local-news', 'guides', 'opinion'],
    required_users_min: 3,
    required_rest_routes: ['/wp/v2/posts', '/wp/v2/categories', '/wp/v2/users'],
    require_abilities_api: true,
  };

  const readme = `# ${defaultName}

Multi-author WordPress publishing starter scaffolded by \`wpax init publishing\`.

## Local Preview (Zero MySQL / Zero Docker)

\`\`\`bash
npm run start
\`\`\`

## Automated Functional Verification

\`\`\`bash
wpax verify .
\`\`\`

## Editorial Roles Included

- **Administrator** (default Playground admin)
- **Editor** (\`maya_editor\`)
- **Author** (\`sam_reporter\`)
- **Contributor** (\`alex_contrib\`)
`;

  return { preset: 'publishing', defaultName, blueprint, verify, readme };
}

export function getBuiltInPreset(preset: PresetName): PresetTemplate {
  switch (preset) {
    case 'small-business':
      return buildSmallBusinessTemplate();
    case 'commerce':
      return buildCommerceTemplate();
    case 'publishing':
      return buildPublishingTemplate();
  }
}

function copyDirRecursive(srcDir: string, destDir: string, written: string[]): void {
  fs.mkdirSync(destDir, { recursive: true });
  for (const entry of fs.readdirSync(srcDir, { withFileTypes: true })) {
    const srcPath = path.join(srcDir, entry.name);
    const destPath = path.join(destDir, entry.name);
    if (entry.isDirectory()) {
      copyDirRecursive(srcPath, destPath, written);
    } else if (entry.isFile()) {
      fs.copyFileSync(srcPath, destPath);
      written.push(destPath);
    }
  }
}

function applyBlueprintCustomizations(
  blueprint: Blueprint,
  options: { name?: string; wp?: string; php?: string }
): void {
  if (options.wp || options.php) {
    blueprint.preferredVersions = {
      ...(blueprint.preferredVersions ?? {}),
      ...(options.php ? { php: options.php } : {}),
      ...(options.wp ? { wp: options.wp } : {}),
    };
  }

  if (options.name) {
    if (blueprint.meta && typeof blueprint.meta === 'object') {
      blueprint.meta.title = options.name;
    }

    let updatedStep = false;
    if (Array.isArray(blueprint.steps)) {
      for (const step of blueprint.steps) {
        if (
          step &&
          step.step === 'setSiteOptions' &&
          step.options &&
          typeof step.options === 'object' &&
          !Array.isArray(step.options)
        ) {
          (step.options as Record<string, unknown>).blogname = options.name;
          updatedStep = true;
          break;
        }
      }
    }

    if (blueprint.siteOptions && typeof blueprint.siteOptions === 'object') {
      blueprint.siteOptions.blogname = options.name;
      updatedStep = true;
    }

    if (!updatedStep) {
      blueprint.steps = [
        { step: 'setSiteOptions', options: { blogname: options.name } },
        ...(blueprint.steps ?? []),
      ];
    }
  }
}

function slugifyPackageName(input: string): string {
  const slug = input
    .toLowerCase()
    .replace(/[^a-z0-9-]+/g, '-')
    .replace(/^-+|-+$/g, '');
  return slug || 'wpax-site';
}

export function initProject(options: InitOptions): InitResult {
  const targetDir = path.resolve(options.dir);
  fs.mkdirSync(targetDir, { recursive: true });

  const builtIn = getBuiltInPreset(options.preset);
  const repoPresetDir = findBlueprintPresetDir(options.preset);
  const written: string[] = [];

  let source: 'repo-blueprints' | 'built-in';
  let blueprint: Blueprint;
  let verifySpec: VerifySpec;
  let siteName = options.name ?? builtIn.defaultName;

  if (repoPresetDir) {
    source = 'repo-blueprints';
    copyDirRecursive(repoPresetDir, targetDir, written);

    const bpPath = path.join(targetDir, 'blueprint.json');
    blueprint = JSON.parse(fs.readFileSync(bpPath, 'utf8')) as Blueprint;
    applyBlueprintCustomizations(blueprint, {
      name: options.name,
      wp: options.wp,
      php: options.php,
    });
    fs.writeFileSync(bpPath, `${JSON.stringify(blueprint, null, 2)}\n`, 'utf8');

    const verifyPath = path.join(targetDir, 'verify.json');
    if (fs.existsSync(verifyPath)) {
      verifySpec = JSON.parse(fs.readFileSync(verifyPath, 'utf8')) as VerifySpec;
      if (options.name) {
        verifySpec.expected_blogname = options.name;
      } else if (verifySpec.expected_blogname) {
        siteName = verifySpec.expected_blogname;
      }
      fs.writeFileSync(verifyPath, `${JSON.stringify(verifySpec, null, 2)}\n`, 'utf8');
    } else {
      verifySpec = {
        ...builtIn.verify,
        ...(options.name ? { expected_blogname: options.name } : {}),
      };
      fs.writeFileSync(verifyPath, `${JSON.stringify(verifySpec, null, 2)}\n`, 'utf8');
      written.push(verifyPath);
    }
  } else {
    source = 'built-in';
    blueprint = structuredClone(builtIn.blueprint);
    verifySpec = structuredClone(builtIn.verify);
    applyBlueprintCustomizations(blueprint, {
      name: options.name,
      wp: options.wp,
      php: options.php,
    });
    if (options.name) {
      verifySpec.expected_blogname = options.name;
    }

    const bpPath = path.join(targetDir, 'blueprint.json');
    fs.writeFileSync(bpPath, `${JSON.stringify(blueprint, null, 2)}\n`, 'utf8');
    written.push(bpPath);

    const verifyPath = path.join(targetDir, 'verify.json');
    fs.writeFileSync(verifyPath, `${JSON.stringify(verifySpec, null, 2)}\n`, 'utf8');
    written.push(verifyPath);
  }

  // Write package.json with @wp-playground/cli scripts
  const pkgPath = path.join(targetDir, 'package.json');
  const pkgJson = {
    name: slugifyPackageName(siteName),
    version: '0.1.0',
    private: true,
    description: `${siteName} — WordPress Playground project scaffolded by wpax (${options.preset}).`,
    scripts: {
      start: 'npx -y @wp-playground/cli@3.1.66 server --blueprint=./blueprint.json --blueprint-may-read-adjacent-files --port=9400',
      'run-blueprint': 'npx -y @wp-playground/cli@3.1.66 run-blueprint --blueprint=./blueprint.json --blueprint-may-read-adjacent-files',
      verify: 'wpax verify .',
    },
  };
  fs.writeFileSync(pkgPath, `${JSON.stringify(pkgJson, null, 2)}\n`, 'utf8');
  if (!written.includes(pkgPath)) written.push(pkgPath);

  // Write README.md if not already provided by repo preset
  const readmePath = path.join(targetDir, 'README.md');
  if (!fs.existsSync(readmePath)) {
    const readmeText = options.name
      ? builtIn.readme.replace(builtIn.defaultName, options.name)
      : builtIn.readme;
    fs.writeFileSync(readmePath, readmeText, 'utf8');
    written.push(readmePath);
  }

  return {
    preset: options.preset,
    dir: targetDir,
    source,
    name: siteName,
    files_written: written.map((f) => path.relative(targetDir, f) || path.basename(f)),
  };
}
