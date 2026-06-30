# Parity audit: Roq preview vs live blog

Compared the PR-284 Surge preview (`https://lunatech-blog-pr-284.surge.sh`)
against the current production site (`https://blog.lunatech.com`), post by post.

Method: pulled the 457 post URLs from the preview sitemap, fetched each post on
both sites, extracted the rendered `post__content` body and image list, and
diffed text similarity and image counts. Also diffed every local post directory
name (the old slug) against the slug Roq generated.

Date: 2026-06-29.

## Summary

- Body text is faithful everywhere. 448 of 448 directly comparable posts score
  0.95 or higher on body-text similarity; the changed-URL posts score 0.97 to
  0.99. No post lost article text.
- All 457 posts render (no 500s), the RSS feed, sitemap, pagination (pages 2-20)
  and 382 tag pages are all present and reachable.
- Two real regression classes need fixing: missing images and undocumented URL
  changes.

## Issue 1: missing images (38 posts, 72 images)

Inline `image:` macros silently drop when the macro is not well formed on a
single line. The Yupiik (pure-Java) AsciiDoc parser renders only the part it can
read and discards the rest. The image files are present in the bundles; only the
rendering is lost. Three triggers:

1. The `[alt text]` bracket wraps across a line break (most common). Example:
   `image:photo.png[Drinks outside with the first few` then `people]` on the next
   line.
2. Consecutive inline images glued with no separating space:
   `image:a.png[...]image:b.png[...]` (post `2010-03-03-plan-cruncher`, 8 images).
3. An image nested inside a link macro on wrapped lines:
   `http://jaxlondon.com/[image:jaxlondon-logo.png[JAX London]]`.

Worst hit: `2007-06-15-benelux-jboss-user-group-8-june-2007-first-photos` (11
images), `2010-03-03-plan-cruncher` (8), `2008-02-18-marketing-books-developers`
(4). The rest lose 1 to 3 each (mostly conference and retrospective posts).

Fix: normalize every image macro so its `[...]` is intact on one line and
consecutive images are space separated. Mechanical and safe; renders identically
to the old site.

Note: one apparent loss is spurious. `2010-04-12-how-localise-play-framework-web-application`
shows fewer images only because the live site still serves a dead
`/confluence/.../link_attachment_7.gif` icon; the preview correctly omits it.

## Issue 2: undocumented URL changes (26 posts)

`URL-CHANGES.md` documents 9 posts (non-ASCII slugs) that change URL by decision.
The audit found 26 more posts whose old URL is live today and now 404s on the new
site. Roq normalizes the slug in ways the old engine did not:

- Collapses repeated hyphens: `shapeless---computing-deltas` becomes
  `shapeless-computing-deltas`.
- Lowercases: `Third-Clojure-Meetup-at-Lunatech`, `demystify-LLMs`,
  `rendre-son-CSS-...`, `...akka-typed-part-II`.
- Strips special characters: `our-first-award!`, `dealing-with-heavy-boxes-(monads)`,
  `pt.1`, and the 2025 posts using `:` `+` `&` (for example
  `part-2:-backend-setup-with-nestjs`).

These split into two repair tiers:

- Clean ASCII (collapsed dashes and case only): can be pinned back to the exact
  old URL. About 16 posts.
- Special characters (`: + & ( ) ! .`): same limitation as the documented 9.
  Roq cannot reproduce these in a path, so they either get a redirect or are
  accepted and documented. About 10 posts.

Plus one data-quality bug: `2008-06-10-eximion-launches-kalydo-%e2%80%93-your-virtual-game-console`
carries a literal percent-encoded en-dash (`%e2%80%93`) in the directory name,
which produces the ugly slug `...kalydo-e2-80-93-your...`. This should be cleaned
regardless of the URL decision.

## Issue 3: minor differences (not regressions)

- Author avatar: when a post's `author` is a full name rather than a GitHub
  handle (for example "Michael Pentowski"), the theme builds
  `https://github.com/Michael Pentowski.png`, an invalid URL with a space. It
  falls back to the placeholder via `onerror`, so it looks fine, but it fires a
  404. Worth guarding: only build the GitHub avatar when the handle has no space.
- RSS feed size: the new feed lists all 457 posts; the old feed listed the 30
  most recent. By design, but a visible difference.
- The migration retrospective post (`2026-06-29-migrating-our-blog-to-quarkus-roq`)
  is `draft: true` and is intentionally not generated.
- `{#seo}` still omits `og:image` for posts (already a known gap).

## Fixes applied

- Images: normalized the broken `image:` macros across 50 posts (line-joined the
  `[alt]` brackets, space separated glued macros, rewrote image-in-link to the
  `image:file[alt,link=URL]` form). After a full static regeneration the 72
  dropped images all render and no post lost images or body text.
- Author avatar: `post.html` and `post-card.html` now only build the GitHub
  avatar and profile link when the author handle has no space; full-name authors
  show their name with the placeholder avatar and no broken request.
- URLs: pinning the changed URLs back to their old form proved impossible in Roq
  2.1.4. An explicit `link:` is slugified the same way the default slug is, and
  the aliases plugin cannot produce working redirects for these paths (it crashes
  the build on a `:`, truncates at `---`, lowercases, and emits a malformed
  `meta refresh`). All 36 changes are therefore recorded in `URL-CHANGES.md`,
  extending the original 9-post decision. The one data artifact (the kalydo
  `%e2%80%93` directory) was renamed to a clean slug.
- Verification: `./mvnw clean package -Dquarkus.roq.generator.batch=true` then
  `java -jar target/quarkus-app/quarkus-run.jar` generates with 0 failures;
  `ThemeTest` passes (3/3).
