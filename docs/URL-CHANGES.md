# URL changes in the Quarkus Roq migration

When the old Asciidoctor/Play engine served a post, it used the source filename
as the URL slug almost verbatim. Quarkus Roq instead slugifies every slug it
generates: it lowercases, collapses any run of non-alphanumeric characters into a
single hyphen, strips characters it cannot represent, and drops non-ASCII
characters. So any post whose filename relied on uppercase letters, repeated
hyphens, punctuation, or accented characters gets a different URL on the new site.

These URLs cannot be pinned back to their old form. The slug is regenerated from
the page name and an explicit `link:` front matter value is slugified the same
way, so it cannot reproduce the old characters. Redirects are not viable either:
the Roq 2.1.4 aliases plugin crashes the build on a `:` in an alias path (Vert.x
reads it as a route parameter), truncates an alias at the first `---`, lowercases
the alias, and emits a malformed `meta refresh`. GitHub Pages, the production
host, has no server-side redirect support of its own.

Decision: accept the new URLs and record them here. Every other post (about 420)
keeps a byte-identical URL.

Total changed: 36.

## The /media/ asset namespace

The old site served every post asset from `/media/<slug>/<file>`. Post assets
now live in the post bundle and are served from `/posts/<slug>/<file>`, so the
mapping is mechanical: replace `/media/` with `/posts/` (and apply the slug
rename table below for the 36 renamed posts).

External deep links to old `/media/` image URLs (hotlinks, cached RSS entries,
image search results) break after cutover; GitHub Pages cannot redirect them.
Decision: accept this for images.

Downloadable documents are the exception: the PDF, zip, jar, and xlsx files in
post bundles are also copied verbatim into `public/media/<slug>/`, so their
old URLs (for example the Play Framework cheat sheet at
`/media/2010-06-08-play-framework-cheat-sheet/play-cheat-sheet.pdf`) keep
working. The bundle copy stays canonical; the `public/media/` copy is a frozen
legacy-URL shim for historical posts. Two posts are excluded (the 2007
OpenSearch Confluence jar and the 2008 FPI Nice PDF): their old slugs contain
non-ASCII characters that Roq slugifies even for `public/` files, so the old
URL cannot be reproduced; those files remain available at their new bundle
URLs only.

## Non-ASCII characters (9)

Apostrophes, accents, an ellipsis, an en-dash and a colon. Roq drops or
transliterates them.

| Old URL | New URL |
|---|---|
| `/posts/2006-04-03-i-wish-i-could-write-joel…` | `/posts/2006-04-03-i-wish-i-could-write-joel` |
| `/posts/2007-07-06-opensearch-plug-atlassian’s-confluence` | `/posts/2007-07-06-opensearch-plug-atlassian-s-confluence` |
| `/posts/2008-05-19-nouvelles-technologies-de-développement-fpi-2008-nice` | `/posts/2008-05-19-nouvelles-technologies-de-d-veloppement-fpi-2008-nice` |
| `/posts/2008-07-22-programmer’s-private-office` | `/posts/2008-07-22-programmer-s-private-office` |
| `/posts/2008-12-05-mini-conférence-java-ee-le-14-janvier-2009-à-sophia-antipolis` | `/posts/2008-12-05-mini-conf-rence-java-ee-le-14-janvier-2009-sophia-antipolis` |
| `/posts/2009-07-14-15-juillet-2009-sophia-antipolis-soirée-agile` | `/posts/2009-07-14-15-juillet-2009-sophia-antipolis-soir-e-agile` |
| `/posts/2011-06-30-reviewing-play’s-dependency-management` | `/posts/2011-06-30-reviewing-play-s-dependency-management` |
| `/posts/2021-10-08-devoxx-france-2021-edition-spéciale-9-3` | `/posts/2021-10-08-devoxx-france-2021-edition-sp-ciale-9-3` |
| `/posts/2025-05-20-part-4:-angular-19-deep-dive-–-smarter-forms-with-signals-and-control-flow` | `/posts/2025-05-20-part-4-angular-19-deep-dive-smarter-forms-with-signals-and-control-flow` |

## Repeated hyphens (10)

The old filenames used `--` or `---` (often where the title had " - "). Roq
collapses any run of hyphens to one.

| Old URL | New URL |
|---|---|
| `/posts/2016-01-04-functional-rotterdam---5th-edition` | `/posts/2016-01-04-functional-rotterdam-5th-edition` |
| `/posts/2016-01-18-fast-track-to-scala---training` | `/posts/2016-01-18-fast-track-to-scala-training` |
| `/posts/2016-05-16-on-the-road-again---scala-days-berlin-2016` | `/posts/2016-05-16-on-the-road-again-scala-days-berlin-2016` |
| `/posts/2016-06-20-functional-rotterdam---10-` | `/posts/2016-06-20-functional-rotterdam-10` |
| `/posts/2016-08-15-play-framework---how-to-handle-a-big-json-file` | `/posts/2016-08-15-play-framework-how-to-handle-a-big-json-file` |
| `/posts/2016-09-05-shapeless---computing-deltas` | `/posts/2016-09-05-shapeless-computing-deltas` |
| `/posts/2016-09-05-shapeless---introduction-resources` | `/posts/2016-09-05-shapeless-introduction-resources` |
| `/posts/2016-10-03-play-framework---beginner-tutorial---make-a-post-request` | `/posts/2016-10-03-play-framework-beginner-tutorial-make-a-post-request` |
| `/posts/2016-12-19-functional-rotterdam--15` | `/posts/2016-12-19-functional-rotterdam-15` |
| `/posts/2018-02-05-apache-spark-for-scala-training---2nd-session-at-lunatech` | `/posts/2018-02-05-apache-spark-for-scala-training-2nd-session-at-lunatech` |
| `/posts/2023-07-28-streams-in-scala--an-introductory-guide` | `/posts/2023-07-28-streams-in-scala-an-introductory-guide` |
| `/posts/2025-10-12-getting-started-with-angular-19--your-first-signals-powered-app` | `/posts/2025-10-12-getting-started-with-angular-19-your-first-signals-powered-app` |

## Uppercase letters (5)

Roq lowercases the slug.

| Old URL | New URL |
|---|---|
| `/posts/2013-05-23-Third-Clojure-Meetup-at-Lunatech` | `/posts/2013-05-23-third-clojure-meetup-at-lunatech` |
| `/posts/2018-01-12-lightbend-spark-for-scala-Professional` | `/posts/2018-01-12-lightbend-spark-for-scala-professional` |
| `/posts/2020-02-19-using-dotty-union-types-with-akka-typed-part-II` | `/posts/2020-02-19-using-dotty-union-types-with-akka-typed-part-ii` |
| `/posts/2021-10-26-rendre-son-CSS-modulaire-avec-bem-et-sass` | `/posts/2021-10-26-rendre-son-css-modulaire-avec-bem-et-sass` |
| `/posts/2025-05-26-demystify-LLMs` | `/posts/2025-05-26-demystify-llms` |

## Punctuation stripped (8)

A bang, parentheses, a dot, colons, plus signs and ampersands are removed and the
gaps collapsed.

| Old URL | New URL |
|---|---|
| `/posts/2007-08-23-starting-a-game-company---eximion-story-pt.1` | `/posts/2007-08-23-starting-a-game-company-eximion-story-pt-1` |
| `/posts/2016-01-04-our-first-award!` | `/posts/2016-01-04-our-first-award` |
| `/posts/2016-12-20-dealing-with-heavy-boxes-(monads)` | `/posts/2016-12-20-dealing-with-heavy-boxes-monads` |
| `/posts/2017-10-01-the-dc-os-(Datacenter-Operating-System)-part-1` | `/posts/2017-10-01-the-dc-os-datacenter-operating-system-part-1` |
| `/posts/2025-04-04-full-stack-authentication-boilerplate:-angular-+-nestjs-+-postgresql` | `/posts/2025-04-04-full-stack-authentication-boilerplate-angular-nestjs-postgresql` |
| `/posts/2025-04-04-part-1-introduction-&-stack-breakdown-for-the-angular-+-nestjs-auth-boilerplate` | `/posts/2025-04-04-part-1-introduction-stack-breakdown-for-the-angular-nestjs-auth-boilerplate` |
| `/posts/2025-04-17-genai:-optimizing-local-large-language-models-performance` | `/posts/2025-04-17-genai-optimizing-local-large-language-models-performance` |
| `/posts/2025-04-22-part-2:-backend-setup-with-nestjs` | `/posts/2025-04-22-part-2-backend-setup-with-nestjs` |
| `/posts/2025-05-06-part-3:-frontend-setup-with-angular` | `/posts/2025-05-06-part-3-frontend-setup-with-angular` |

## Data fix (1)

The source bundle for this post carried a literal percent-encoded en-dash
(`%e2%80%93`) in its directory name, which produced the unreadable slug
`...kalydo-e2-80-93-your...`. The directory was renamed to drop the stray
character, giving a clean slug.

| Old URL | New URL |
|---|---|
| `/posts/2008-06-10-eximion-launches-kalydo-–-your-virtual-game-console` | `/posts/2008-06-10-eximion-launches-kalydo-your-virtual-game-console` |
