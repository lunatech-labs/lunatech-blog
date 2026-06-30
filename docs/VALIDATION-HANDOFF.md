# Validation handoff

This is a handoff for a fresh session to validate the recent round of fixes on
the `migrate-to-quarkus-roq` branch (PR #284). It lists what changed, how it was
verified, and a checklist to re-validate independently.

## What changed in this round

All changes sit on top of the earlier migration work. Commits, newest first:

- `Build with JDK 25` - compiler release 25 in `pom.xml`; `setup-java` version 25
  in both `.github/workflows/deploy_pages.yaml` and `preview.yaml`.
- `Co-locate OpenSearch XML examples as .xml.txt` - see "Constraints" below.
- `Use front matter tags; drop redundant AsciiDoc metadata attributes` - the
  theme reads tags from front matter (`page.data.get('tags')`), tag links
  lowercase via `{tag.toLowerCase.slugify}` to match the lowercase tag pages,
  display keeps original casing. `:title:` and `:tags:` attributes stripped from
  all 458 posts. `TemplateExtensions.java` (the `:tags:` string parser) deleted.
- `Co-locate post media into bundles; drop public/media` - every post asset moved
  from `public/media` into its page bundle; references rewritten to bare
  filenames; `public/media` removed.
- `Fix invalid multiple level-0 AsciiDoc headings` - three posts had more than one
  `= ` title; rogue ones demoted to `==`.

Earlier in the migration (already on the branch): missing-image fixes, author
avatar guard, and the documented URL changes. See `PARITY-AUDIT.md` and
`URL-CHANGES.md`.

## How it was verified

- Full static generation: `./mvnw clean package -Dquarkus.roq.generator.batch=true -DskipTests`
  then `java -jar target/quarkus-app/quarkus-run.jar`. Result: exit 0, 0
  "Roq request failed" lines, output in `target/roq`.
- `ThemeTest` passes (3/3) via `./mvnw test`.
- Tag links: 382 tag pages generated, 382 distinct tags linked, 0 dead tag links.
- Media: every co-located image, PDF, jar, `.sc`, `.tex`, `.py`, `.txt` and the
  two `.xml.txt` downloads are served from their bundle; no `/media` directory in
  the output; the only remaining `/media` reference in source is an external
  `alfresco.com` URL.

## Constraints and decisions (do not "fix" these)

- Roq renders any bundle file ending in `.xml` as a Qute template (it needs this
  for `feed.xml` and `sitemap.xml`). So `.xml` download files cannot be bundle
  attachments. The two OpenSearch examples are therefore named `.xml.txt` and
  served verbatim. Other non-image downloads (PDF, jar, `.sc`, `.tex`, `.py`,
  `.txt`) co-locate without issue.
- `quarkus.roq.tagging.lowercase=true` must stay. Tested: removing it generates
  mixed-case tag page URLs (`/tags/ALGOL`) while the theme links are lowercase,
  producing 43 dead tag links. It pairs with the template `toLowerCase`.
- URL changes: 36 posts change URL because Roq slugifies (lowercase, collapse
  repeated hyphens, strip punctuation, drop non-ASCII). These cannot be pinned or
  redirected in Roq 2.1.4 (explicit `link:` is re-slugified; the aliases plugin
  crashes on `:`, truncates `---`, lowercases, and emits a malformed refresh).
  All 36 are recorded in `URL-CHANGES.md` by decision.
- The migration retrospective post (`2026-06-29-migrating-our-blog-to-quarkus-roq`)
  is `draft: true` and is intentionally not generated; it contains literal
  `/media/...` placeholder text that is not a real reference.

## Validation checklist for the new session

1. Free port 8080 (`lsof -ti :8080`), then generate:
   `./mvnw clean package -Dquarkus.roq.generator.batch=true -DskipTests && java -jar target/quarkus-app/quarkus-run.jar`.
   Expect exit 0 and zero "Roq request failed".
2. `./mvnw test` - expect `ThemeTest` 3/3.
3. Confirm `public/media` does not exist and no bundle references `/media/...`
   except the external alfresco URL:
   `grep -rhoE '/media/[^ ")\]]+' content/posts/*/index.adoc | sort -u`.
4. Confirm 0 dead tag links (script in "How it was verified").
5. Spot-check restored images on the Surge preview
   (`https://lunatech-blog-pr-284.surge.sh`): `/posts/2010-03-03-plan-cruncher`,
   `/posts/2007-06-15-benelux-jboss-user-group-8-june-2007-first-photos`,
   `/posts/2008-02-18-marketing-books-developers`.
6. Spot-check a co-located download renders and is reachable:
   `/posts/2007-12-14-seam-action-javapolis-presentation/` (PDF) and the two
   `.xml.txt` files under the OpenSearch post.
7. Confirm no post has more than one `= ` heading:
   `for f in content/posts/*/index.adoc; do n=$(grep -cE '^= ' "$f"); [ "$n" -gt 1 ] && echo "$n $f"; done`.
8. Confirm the build runs on JDK 25 (`java -version`, `maven.compiler.release` in
   `pom.xml`, `java-version: '25'` in both workflows).
