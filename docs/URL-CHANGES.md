# URL changes in the Quarkus Roq migration

During the migration from the Asciidoctor/Play engine to Quarkus Roq, these
posts changed URL. Their filenames contain non-ASCII characters (apostrophes,
accents, ellipsis, en-dash, colon) which Roq slugifies into the URL. Roq 2.1.4
cannot generate working redirects for non-ASCII alias paths, so by decision the
old URLs are **not** redirected; they simply change. Every other post (~448)
keeps a byte-identical URL.

Affected posts: 9

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
