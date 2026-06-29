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
1. Layout chain: `default.html` (html/head/body, includes head partial, `{#seo}`,
   Plausible, CSS/JS) -> `page.html` and `post.html` extend it. Override the local
   `post` layout (we already pin the post URL there: see below) so it renders the
   author block, date, reading time, tags, and the article body.
2. Index: `content/index.html` already paginates (24/page) and lists posts. Restyle
   into the hero + cards layout.
3. CSS: port the SCSS to `public/css/main.css` (or keep SCSS via the web-bundler).
4. Tag pages (`/tags/:tag`): OPEN ISSUE. `quarkus-roq-plugin-tagging` with a layout
   carrying `tagging: posts` + `link: /tags/:tag` did NOT generate pages in 2.1.4.
   Investigate (content-anchor page? derived-collection publish config?) or build
   tag pages manually by grouping `site.collections.posts` by tag.
5. Author pages (`/author/:name`): create `data/authors.yml` (handle -> name,
   avatar, bio, links) and generate a page per author, e.g. a `from-data` collection
   or grouping posts by author. Old URL was `/author/<github-handle>`.
6. Analytics + meta: Plausible snippet in the head; confirm `{#seo}` output.

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
