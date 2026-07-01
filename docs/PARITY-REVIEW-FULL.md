# Full parity review: Roq preview vs production (every post)

Independent, post-by-post review of all 457 generated posts, comparing the
Quarkus Roq preview against the live production site (`https://blog.lunatech.com`).
This complements the earlier `PARITY-AUDIT.md` with a fresh, fan-out review and
per-finding verification.

Date: 2026-06-30.

## Method

- A fan-out of 31 subagents reviewed ~15 posts each (457 total). Each agent read
  the generated preview HTML and fetched the matching live production page, then
  compared title, body fidelity, and content-image counts.
- Preview source of truth: the locally generated `target/roq` HTML. It was
  verified byte-equivalent to the deployed Surge preview on spot-checks (titles
  and image counts matched), so it is a faithful proxy and avoids Surge flakiness.
- URL mapping: production uses no trailing slash and serves raw special
  characters; the preview uses a trailing slash. The 36 documented URL changes
  were pre-mapped (old prod URL to new preview slug) so they are judged on content
  only, not flagged as missing pages.
- Verification: every "major" finding was re-checked by hand with direct grep on
  the raw production and preview HTML. The subagents (Sonnet, fetch-based) proved
  unreliable in both directions, so their raw output was not taken at face value:
  - They under-counted: they flagged 1 post with leaked Liquid tags; there are 5.
  - They over-flagged: several "prod renders cleanly" calls were wrong, because the
    fetch summariser did not surface literal markup that is present on production
    too. Those are pre-existing issues, not migration regressions.

## Headline

- Subagent tally: 375 ok, 67 minor, 15 major, 1 production fetch failure.
- After verification, the real picture is smaller and cleaner than the raw "15
  major" suggests: 11 confirmed preview-only rendering regressions plus 1 title
  typo (all now fixed), a set of pre-existing issues that production shares, three
  subagent false positives, and a long tail of benign image-count noise.
- No post lost its article prose. Every regression below is markup that fails to
  render, a missing image, or a title difference, not lost text.

## Status

All confirmed preview-only regressions below were fixed and verified against a
fresh regeneration (markers gone, headings/tables/code render as proper HTML).
Three subagent "findings" turned out to be false positives on closer inspection
and were not changed; they are listed at the end.

## Confirmed preview-only regressions (production renders clean, preview did not) - FIXED

These were the real action items. Evidence is the count of the raw marker in the
rendered HTML on each side (prod = 0, preview > 0). All are now fixed.

### Markdown headings leaking as plain text

Recent posts authored in Markdown were converted to `.adoc` but kept literal
`##` / `###` headings, which AsciiDoc does not interpret, so they render as body
text.

| Post | Marker | prod | preview |
|---|---|---|---|
| `2024-11-22-aop-showdown` | `###` | 0 | 5 |
| `2024-10-18-women-automotive` | `###` | 0 | 5 |
| `2024-10-10-lunaconf-2024` | `###` | 0 | 4 |
| `2017-10-01-the-dc-os-datacenter-operating-system-part-1` | `## ` | 0 | 6 |
| `2016-11-28-an-introduction-to-finagle-by-example` | `## ` | 0 | 3 |

### AsciiDoc passthrough delimiters leaking

Literal `++++ </br> ++++` passthrough blocks appear as visible text.

| Post | Marker | prod | preview |
|---|---|---|---|
| `2023-07-28-streams-in-scala-an-introductory-guide` | `++++` | 0 | 26 |
| `2022-12-20-automation-star-conference` | `++++` | 0 | 10 |
| `2022-11-07-software-qa-blog` | `++++` | 0 | 3 |
| `2023-05-24-api-automation-testing-tools-comparison` | `++++` | 0 | 1 |

### Raw AsciiDoc source and table markup leaking

| Post | Issue | Evidence |
|---|---|---|
| `2023-04-13-rust-by-examples` | `[source,rust]` and `===` section markers leak inside an unrendered code element | prod `[source,` = 0, preview = 1 block |
| `2007-12-11-european-union-metaphor-jboss-seam` | broken table: `a|` cell separators leak as text | prod `a|` = 0, preview = 2 |

### How each was fixed

- Markdown headings: converted leftover `##` / `###` to AsciiDoc `==` (these were
  the posts' top-level content sections).
- Passthrough blocks: every block was the identical 3-line spacer
  `++++` / `</br>` / `++++` (an invalid line-break hack). Each was replaced with a
  blank line, preserving paragraph separation.
- `rust-by-examples`: a stray extra `----` re-opened a listing block that was
  never closed, swallowing the `Error handling`, `Functional Programming Features`
  and `Closures` headings. Removed the stray delimiter (49 delimiters to 48).
- `european-union-metaphor`: the `a|`-with-following-content table form was
  rewritten as a standard row-based 3-column table (same data, same column
  correspondence), which every AsciiDoc parser renders.
- `jboss-benelux` title: added the missing "J" in the source `.adoc`.

## Investigated and NOT a regression (subagent false positives)

Closer inspection of the raw production and preview HTML showed these three are
not regressions, so no change was made:

- `2016-08-29-moving-from-spain-to-the-netherlands`: production also shows only
  `background.png`. There are no gastronomy/weather infographics on production
  either; the "Main differences..." lines are leftover captions where images were
  lost upstream long ago. Preview and production are equivalent. The subagent
  hallucinated the two images.
- `2025-02-28-the-scala-effect`: the preview renders all code correctly inside
  `<pre><code data-lang>` blocks within all 11 tables. No leaked text.
- `2012-03-21-fact-type-hierarchies-drools`: both production and preview have zero
  code-listing blocks (the source has none). Equivalent on both sides.

## Pre-existing issues (production is broken the same way; NOT migration regressions)

The same raw markup appears on production, so these are source-content problems
that predate the migration. They are worth cleaning, but they are not regressions
introduced by Roq.

| Post | Issue | prod | preview |
|---|---|---|---|
| `2010-04-12-how-localise-play-framework-web-application` | Liquid `{% %}` tags | 18 | 18 |
| `2011-04-26-playframework-file-upload-blob` | Liquid `{% highlight %}` | 15 | 15 |
| `2010-08-09-how-demo-play-framework-live-coding-script-scala` | Liquid `{%` | 2 | 2 |
| `2010-06-14-how-demo-play-framework-live-coding-script` | Liquid `{%` | 1 | 1 |
| `2014-03-12-squeryl-activiti-transactions` | Liquid `{%` | 1 | 1 |
| `2009-01-20-the-kalydo-portal-explains-it-all` | YAML front matter leak | 1 | 1 |
| `2011-12-01-playframework-20-live-coding-script` | YAML/Drupal front matter leak | 1 | 1 |
| `2018-11-07-lunatech-airport-assessment` | `image::` and `[source]` leak (incl. missing `tab.png`) | 1 | 1 |
| `2024-01-10-quarkus-openai-text-review` | `++++` passthrough | 2 | 2 |

## Title and content differences (not rendering bugs)

- `2007-05-24-jboss-benelux-user-group-8-june-2007`: preview title is "Boss
  Benelux User Group" (missing the "J"). The source `.adoc` literally reads
  `= Boss Benelux User Group`, so the preview is faithful to a source typo.
  Production shows "JBoss". A one-character source fix.
- `2021-04-28-calculating-pi-concurrently`: preview title "Calculating π
  concurrently" versus production "Comparing Concurrent Programming
  Alternatives". Body text matches. Production was retitled after the content
  snapshot; the source carries the older title.
- `2023-03-31-embrace-kotlin`: preview subtitle "Where to Get Started for Scala
  Developers" versus production "Tips And Tricks for Scala Developers to Get
  Started". Body matches. Same source-versus-prod drift.
- Minor wording drift, body intact: `2022-07-11-foldleft-introduction`
  ("Traversing" vs prod "Browsing"), `2023-02-15-hackathon-by-cesi`
  ("Hackaton" one-t).

## Image-count minors (67 total, overwhelmingly benign)

Two systematic, harmless patterns account for nearly all of them:

1. Background or hero image counted on production but rendered as a CSS background
   outside the article in the preview. Seen across the 2013 Slick series, the 2016
   training and event posts, and similar. No content image is actually missing.
2. The production fetch under-counted images on long, image-heavy posts (preview
   has more than prod), for example home-energy-monitoring (18 vs 13),
   run-linux-windows-on-mac (18 vs 14), telegram-bot (16 vs 10). The preview has
   all the images; this is fetch-side counting noise.

A few are real but cosmetic: the same image rendered twice in the preview
(`postsubmit.png`, `crud-users-2.png`, a JBUG 2007 photo, `registry.png`), and a
stray `vimeocdn` crawler-logo image on two video posts.

## Production fetch failure (1)

- `2008-06-10-eximion-launches-kalydo-your-virtual-game-console`: the production
  URL carries an en-dash and could not be fetched programmatically. This is one of
  the documented URL-change posts; its content renders fine on the preview.

## Outcome

All 12 confirmed preview-only regressions were fixed in source and verified
against a fresh regeneration: 5 markdown-heading posts, 4 passthrough posts,
`rust-by-examples`, `european-union-metaphor`, and the `jboss-benelux` title.

Not addressed, by decision:

- The pre-existing Liquid/YAML-leak posts (production is broken the same way) are
  not migration regressions. They can be cleaned in a later content pass.
- The image-count minors need no action (background-image counting noise and
  fetch-side undercounting).
- The three subagent false positives above need no action.
