# Upstream issues to file against Quarkus Roq

Found while migrating this blog to Roq 2.1.4 (Quarkus 3.37). Repo:
https://github.com/quarkiverse/quarkus-roq

## Bugs

### 1. Java AsciiDoc parser NPE on literal blocks (`....`)
`quarkus-roq-plugin-asciidoc` (Yupiik parser) throws on any literal block:
`java.lang.NullPointerException: io.yupiik.asciidoc.model.Listing.options() is null`
(at `AsciidocConverter.apply`). The page returns 500.
- Repro: a post containing a `....` ... `....` literal block.
- Impact: 24 of our 457 posts. Workaround: convert `....` to `----`.
- Likely upstream in the yupiik asciidoc-java library; worth filing in Roq so they
  can forward / pin a fixed version.

### 2. Java AsciiDoc parser NPE on callouts without a callout list
A source block with callout markers (`<1>`, `<2>`) but no following callout list
hits the same `Listing.options()` NPE.
- Repro: a `[source]` block with a trailing `<1>` and no `<1> ...` colist after it.
- Workaround: add a proper callout list (valid AsciiDoc regardless).

### 3. `video::` macro silently dropped
The Java AsciiDoc plugin renders nothing for `video::ID[youtube]` and emits no
warning. Either support it or warn on unsupported macros.
- Impact: 7 posts. Workaround: passthrough `<iframe>`.

### 4. Aliases plugin does not work for non-ASCII alias paths
`quarkus-roq-plugin-aliases`: an alias whose path contains non-ASCII characters
(apostrophe, accents, ellipsis) returns 404 in both static generation and live
serving (the registered route does not match the generator's percent-encoded
request). A `:` in an alias path breaks Vert.x route registration at startup
(`path param does not follow the variable naming rules`).
- Repro: `aliases: ["/posts/atlassian’s-confluence"]`.
- ASCII aliases work fine (static meta-refresh page is generated).

### 5. Generator fails on the aliases plugin's own redirect routes
With the aliases plugin active, the generator crawls the alias paths expecting
200, but the plugin registers Vert.x 302 redirect routes for them, so the crawl
sees a 302 and `andFailFast()` aborts the whole generation. The generator should
tolerate (or follow) redirects for paths owned by the aliases plugin.

## Enhancements

### 6. Publish a `quarkus-roq-bom` to align plugin versions
There is no consumer BOM. You must pin `quarkus-roq` and every
`quarkus-roq-plugin-*` version individually (we share one `${roq.version}`
property as a workaround). A `io.quarkiverse.roq:quarkus-roq-bom` importable into
`dependencyManagement` would let consumers add plugins without versions and avoid
mismatches. (Today only internal `*-parent` reactor POMs exist, not a BOM.)

### 7. Warn on unrecognized front matter keys
`permalink` and `url` are silently ignored (the key is `link`). A build-time
warning for unknown front matter keys would have saved real time.

## Docs / DX

### 8. Document permalink placeholders and the `link` key
The placeholder set (`:name`, `:slug`, `:year`, `:month`, `:day`, `:collection`,
`:path`, `:raw-path`, ...) and the `link` front matter key are not clearly
documented. We reverse-engineered them from `TemplateLink` and
`RoqFrontMatterKeys` in the jars.

### 9. Make the build-time `generator.batch` situation obvious
`quarkus.roq.generator.batch` is build-time fixed. Setting it at runtime only logs
a WARN and the app silently starts as a server that never generates. A clearer
signal (or docs note) would help, since "nothing generated" looks like a hang.

### 10. Document `static/` vs `public/` path mapping
`static/` keeps a `/static/` prefix in output; `public/` serves at root. This is
easy to get wrong (every image 404s) and deserves a prominent note.
