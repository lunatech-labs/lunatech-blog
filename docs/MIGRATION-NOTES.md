# Migration findings: Play/AsciiDoctor engine to Quarkus Roq

This is the lessons-learned record from migrating the Lunatech blog (457
AsciiDoc posts) off the separate `lunatech-blog-engine` (Play/Scala) onto
Quarkus Roq as a static site on GitHub Pages, in a single repo.

It complements the focused docs:
- `UPSTREAM-ISSUES.md`: bugs and gaps worth reporting upstream.
- `URL-CHANGES.md`: the posts and asset paths whose URLs changed.
- `PR-PREVIEWS.md`: how PR preview deploys work.

The one-shot conversion scripts mentioned below (`bin/*.py`) did their job
during the migration and have been removed; retrieve them from git history if
ever needed.

Versions at migration time: Roq 2.1.4, Quarkus 3.37, Java 21.

## Static generation

- `quarkus.roq.generator.batch` is a BUILD-TIME property. Static generation is
  two steps: `./mvnw clean package -Dquarkus.roq.generator.batch=true` to bake
  the generator in, then `java -jar target/quarkus-app/quarkus-run.jar` to emit
  the site to `target/roq`. Passing batch only at runtime is silently ignored.
- Do NOT put `quarkus.roq.generator.batch=true` in `application.properties`. It
  makes the generator run at every startup (even dev mode), and a single 500
  page aborts the whole app.
- The generator crawls every page and FAILS the whole build on any non-200.
  Keep it at zero failures. The deploy and preview workflows depend on this.
- Watch the port. The generator runs an in-process HTTP server on 8080. If a
  stray `java -jar` from an earlier run still holds 8080, generation 500s on
  every page (a port conflict, not a template bug). Confirm 8080 is free before
  generating: `lsof -ti :8080`.
- `site.url` is a BUILD-TIME property too. To override it (for example to point
  preview canonical/OG/RSS/sitemap links at a preview host) set it on the
  `package` command, not on `java -jar`.

## URL stability

- The front matter key for a page URL is `link` (not `permalink` or `url`,
  which are silently ignored). Post URLs are pinned in
  `templates/layouts/post.html`: `link: /:collection/:year-:month-:day-:name`,
  which reproduces the old `/posts/YYYY-MM-DD-slug` paths. Do not remove it.
- Roq slugifies non-ASCII paths, so posts with accented or special-character
  slugs changed URL (see `URL-CHANGES.md` for the full list of 36). Aliases do not work for non-ASCII
  paths in 2.1.4, so those redirects 404 in both static and live mode. Decision:
  accept the new URLs.

## AsciiDoc content quirks (handled by bin/migrate-posts.py)

- The pure-Java Yupiik parser NPEs on `Listing.options() is null`. Two triggers:
  `....` literal blocks (convert to `----`), and callout markers (`<1>`) in a
  source block with no matching callout list after it (add the list). Rule:
  callouts in code MUST be followed by a `<N> description` list.
- The `video::` macro is silently dropped. Replace it with a passthrough
  `<iframe>`.
- `:imagesdir: ../media/...` emits relative `img` src that breaks from
  `/posts/x/`. Posts are page bundles (`content/posts/<slug>/index.adoc`) with
  images co-located, referenced bare; shared assets live in `public/media`
  (served at `/media/...`).

## Roq data model for AsciiDoc posts (theme gotchas)

These came out of probing the live data, not the docs:

- `page.title`, `page.url`, `page.date`, `page.readTime` work as expected.
  Format dates with `{page.date.format('dd MMM yyyy')}`. Reading time is
  server-side (`page.readTime`), so no client word-count is needed.
- Tags are NOT at `page.data.tags`. The AsciiDoc `:tags:` attribute lands under
  `page.data.attributes.tags` as a RAW BRACKETED STRING (for example
  `"[java, jvm]"`). A small Qute `@TemplateExtension`
  (`TemplateExtensions.tagList`) parses it into a list for display.
- The author handle IS top-level: `page.data.get('author')`. Use
  `page.data.get('key')` (not `page.data.key`) for optional fields, because a
  missing nested key throws "Property not found".
- `page.files` and `page.image(name)` THROW on a post that has no co-located
  files ("not a directory page"). Do NOT use them to test for a cover image.
  Instead emit `<img src="{page.url}background.png" onerror=...>` and swap in a
  gradient placeholder on error (this also matches the old engine behaviour).
- `{#seo page site /}` omits `og:image` for posts, because posts have no
  `page.image` (the cover is a co-located file, not front matter). Minor SEO gap.

## Tag pages (the tagging plugin)

- `quarkus-roq-plugin-tagging` derives `/tags/:tag` pages from a TOP-LEVEL
  `tags` front matter key (`RoqTaggingUtils` reads `data.getValue("tags")`).
  Our posts only had tags under `attributes.tags`, so the plugin generated
  nothing. Root cause found by reading the plugin source.
- Fix: `bin/add-tags-frontmatter.py` promotes each post's `:tags:` attribute to
  a real YAML `tags:` list (idempotent, safe to re-run after pulling new posts).
- The tag layout carries `tagging: {collection: posts, link: /tags/:tag}`. The
  `link` key matters: the default would be `/posts/tag/:tag`; ours reproduces
  the old `/tags/:tag` URLs.
- Set `quarkus.roq.tagging.lowercase=true` and use `{tag.slugify}` in theme tag
  links so they match the plugin's generated slugs (for example
  `IntelliJ AI Plugins` to `/tags/intellij-ai-plugins`).
- The plugin is hardcoded to the `tags` key, so it cannot be reused for author
  pages. There is no other built-in keyed-page generator in 2.1.4. Decision: no
  author pages; post-author names link to `github.com/<handle>`.

## Theme

- Layout chain: `templates/layouts/default.html` (html skeleton, `{#seo}`,
  `{#rss}`, fonts, Plausible, CSS/JS) extended by `page.html` and `post.html`.
  Layouts wrap child content with `{#insert /}`, never `{page.content}`.
- Partials in `templates/partials/`: header, footer, hero, post-card.
- The visual theme is a re-port of the engine's SCSS to plain CSS in
  `public/css/main.css`. The engine was later redesigned ("luxury 5-star
  aesthetic"), which was re-ported the same way: read the engine
  `app/views/*.scala.html` and `app/assets/stylesheets/utils/**/*.scss` at HEAD,
  then rewrite the CSS and update the hero markup and fonts.
- Code highlighting: the AsciiDoc plugin emits `hljs` classes but does not
  tokenize server-side, so highlight.js runs client-side over `pre code`.

## Deploys

- Production: `.github/workflows/deploy_pages.yaml` builds and deploys to GitHub
  Pages on push to `main`, custom domain `blog.lunatech.com` via `public/CNAME`.
- PR previews: `.github/workflows/preview.yaml` deploys each PR to a per-PR
  surge.sh URL. See `PR-PREVIEWS.md`. GitHub Pages cannot do per-PR previews on
  its own (one environment per repo, occupied by the custom domain).

## Remaining work

- Confirm `{#seo}` output and consider adding `og:image` for posts.
- URL-diff the generated site against the current live site, then cut over and
  retire the old engine.
