# Handoff: porting the Lunatech visual theme to Roq

The migration to Quarkus Roq is functionally complete on branch
`migrate-to-quarkus-roq`. All 457 posts generate with zero failures, URLs are
stable, RSS/sitemap/pagination work, and a GitHub Pages workflow is in place. The
site currently renders with Roq's plain base theme. This doc is the starting point
for the remaining work: making it look like the Lunatech blog.

## Goal
Reproduce the look and behaviour of the old engine: header with logo and nav, hero
section, post cards on the index, a styled post page (author block, reading time,
tags, scroll progress), footer, fonts and colours. Plus SEO meta (Open Graph /
Twitter) and Plausible analytics.

## What to read in the old engine
Source: `~/Lunatech/Internal/lunatech-blog-engine`
- `app/views/*.scala.html`: `main`, `index`, `post`, `header`, `footer`, `head`,
  `notFound` (404). These are the templates to port to Qute.
- `app/assets/stylesheets/*.scss`: `_cover` (hero), `_card`, `_author`, `_tag`,
  `_post`, `_highlight`, `_progress`, plus buttons/social/logo. Port to plain CSS.
- `public/`: logos (`logo-lunatech-*.svg`), social icons, fonts, favicon,
  `js/highlight.pack.js`, `js/progress.js` (reading time + scroll bar). Copy the
  assets we keep into `public/`.
- `app/models/Post.scala`: how excerpt, reading time, tags, author were derived.

## Where things go in this Roq project (full quarkus-roq extension)
- Layouts: `templates/layouts/*.html` (Qute). A page selects one via `layout:` in
  front matter; layouts wrap child content with `{#insert /}` (NEVER `{page.content}`).
  `theme-layout: <name>` inherits the base theme's version.
- Partials: `templates/partials/*.html`.
- Static assets at the site root: `public/` (e.g. `public/css/...` -> `/css/...`).
  Do NOT use `static/` for root assets (it keeps a `/static/` prefix).
- Site title/description come from `content/index.html` front matter, not config.
- Built-in helpers: `{#seo page site /}` emits title + description + OG + Twitter
  tags; `{#rss site /}` adds the feed `<link>`. Use these instead of hand-rolling.

## Concrete TODO
1. DONE. Layout chain `default.html` -> `page.html` / `post.html` (post layout renders
   author block, date, reading time, tags, cover, body). Partials: header, footer, hero,
   post-card.
2. DONE. `content/index.html` restyled into hero + featured/last + card grid + pagination.
3. DONE. SCSS ported to `public/css/main.css` (plain CSS). Assets copied into `public/`.
4. DONE. Tag pages `/tags/:tag` via `quarkus-roq-plugin-tagging`. Root cause of the earlier
   failure: the plugin reads the TOP-LEVEL `tags` FM key, but our posts only had tags under
   the AsciiDoc `:tags:` attribute. Fix: `bin/add-tags-frontmatter.py` promotes `:tags:` to a
   real `tags:` YAML list on every post; `templates/layouts/tag.html` carries
   `tagging: {collection: posts, link: /tags/:tag}` (link key reproduces old URLs). Theme tag
   links use `{tag.slugify}` to match generated slugs. 0 dead tag links. Test: `ThemeTest`.
5. DECIDED (2026-06-29): no author pages. Post-author names link to `github.com/<handle>`.
   The old `/author/<github-handle>` URLs are intentionally not reproduced. (The tagging plugin
   is hardcoded to the `tags` key and cannot be reused for authors.)
6. DONE. Plausible snippet + `{#seo}` / `{#rss}` in `default.html`. (Minor gap: `{#seo}` omits
   og:image for posts, since posts have no `page.image`.)

## Hard-won gotchas (do not relearn these)
- `quarkus.roq.generator.batch` is a BUILD-TIME property. Static generation =
  `./mvnw clean package -Dquarkus.roq.generator.batch=true` THEN
  `java -jar target/quarkus-app/quarkus-run.jar` (emits `target/roq`). Setting batch
  only at runtime is silently ignored.
- The generator crawls every page and FAILS the whole build on any non-200. Keep it
  at zero failures.
- Front matter URL key is `link` (not `permalink`/`url`). Post URLs are pinned in
  `templates/layouts/post.html`: `link: /:collection/:year-:month-:day-:name`. Do not
  remove that line; it is what keeps every post URL stable.
- Roq slugifies non-ASCII paths; 9 posts changed URL (see docs/URL-CHANGES.md) and
  aliases do not work for non-ASCII paths in 2.1.4.
- The pure-Java AsciiDoc parser quirks are already handled by `bin/migrate-posts.py`
  (literal blocks, video macros). Re-run it after pulling new posts.

## Dev loop and verification
- Use the Quarkus Agent MCP: `quarkus_start` (dev mode, hot reload),
  `quarkus_restart`, `quarkus_logs`, `quarkus_callTool` for the running app.
- Full static check: the two-step generate command above, then confirm zero
  `request failed` lines and spot-check pages under `target/roq/`.
- Keep `docs/URL-CHANGES.md` and `docs/UPSTREAM-ISSUES.md` in mind.

## Suggested kickoff prompt for the new session
"Continue the Roq migration on branch migrate-to-quarkus-roq: port the Lunatech
visual theme. Read docs/THEME-HANDOFF.md and the old engine's views/SCSS in
~/Lunatech/Internal/lunatech-blog-engine, then build the Qute layouts and CSS."
