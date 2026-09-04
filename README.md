# lunatech-blog

Lunatech's engineering blog at [blog.lunatech.com](https://blog.lunatech.com/).

The site is a static site generated with [Quarkus Roq](https://iamroq.com/).
Posts are written in [AsciiDoc](https://asciidoc.org/), rendered with Qute
templates from `templates/`, and published to GitHub Pages.

## Repository layout

- `content/posts/<yyyy-MM-dd-title>/index.adoc`: one directory (bundle) per post
- `content/posts/<yyyy-MM-dd-title>/*.png`: images and other assets used by that post
- `content/index.html`, `content/feed.xml`, `content/sitemap.xml`: site pages
- `templates/`: Qute layouts and partials (theme)
- `public/`: files copied verbatim to the site root (CSS, JS, fonts, favicon)
- `src/main/resources/application.properties`: site configuration
- `scripts/`: single-file Java maintenance utilities, run directly with `java`
- `src/test/java/`: theme smoke tests plus the post naming and availability checks

## Writing a post

1. Fork or branch this repository.
2. Create a bundle directory: `content/posts/yyyy-MM-dd-your-title/`. Use only
   lowercase letters, digits and single hyphens in the name; see
   [Post directory names](#post-directory-names).
3. Write your post in `index.adoc` in that directory, starting with front matter:

   ```
   ---
   title: "Your post title"
   author: "your-github-username"
   tags:
   - "java"
   - "quarkus"
   ---

   Your AsciiDoc content here.
   ```

   The author is your GitHub username; your GitHub avatar is shown on the post
   card. Refer to images with plain relative paths, for example
   `image::diagram.png[Diagram]`, and put the files in the same directory.
4. Add a `background.png` in the bundle; it is used as the card and hero image.
5. Open a pull request. CI builds the site and comments a preview URL
   (Surge.sh) on the PR, rebuilt on every push.

Posts dated in the future are excluded from the build until their date passes;
the site rebuilds daily so they publish automatically on (or shortly after)
their date.

## Compress your images

Every post carries at least one image, so please keep them small. PNGs larger
than 1 MB fail the PR check. Compress with `pngcrush`:

```commandline
brew install pngcrush
pngcrush -rem allb -brute -reduce in.png out.png
```

## Previewing locally

Run the site in dev mode with live reload (requires Java 25):

```commandline
./mvnw quarkus:dev
```

Then open http://localhost:8080. To generate the full static site into
`target/roq`:

```commandline
./mvnw package quarkus:run -DskipTests -Dquarkus.roq.generator.batch=true
```

## Post directory names

A post's URL is its directory name, so the two must match. Roq slugifies the
name when it builds the URL: it lowercases, and replaces accents, curly quotes
and punctuation with `-`, then collapses runs of `-` and trims the edges. A
directory named outside that alphabet is therefore served at a URL that does
not match it, which silently breaks anything working out a post URL from disk.

So a post directory must already be its own slug:

```
yyyy-MM-dd- followed by lowercase letters, digits and single hyphens
```

No uppercase, no accents, no punctuation, no doubled hyphens, no trailing
hyphen. Write accents and punctuation in the `title:` front matter instead,
which is display text and unaffected. For example, a post titled
"Mini-conférence Java EE" belongs in `2008-12-05-mini-conference-java-ee/`.

`PostFolderNameTest` enforces this on every `./mvnw test`, so CI rejects a
directory that breaks the rule. It only reads the filesystem, so it does not
build the site and adds no measurable time to the build. When it fails it names
each offending directory and the slug it should have:

```commandline
./mvnw test -Dtest=PostFolderNameTest
```

To fix offenders, use `scripts/RenamePosts.java`. It reports what it would do
and changes nothing without `--apply`:

```commandline
java scripts/RenamePosts.java content/            # print the renames, exit 1 if any are pending
java scripts/RenamePosts.java content/ --apply    # perform them with git mv
```

It refuses to act if a derived slug would collide with an existing directory,
and routes a rename that only changes capitalisation through a temporary name,
because macOS and Windows treat `Foo` and `foo` as the same path.

Renaming a directory whose post is already published **changes a live URL**.
Keep the old one working by adding the previous path to the front matter, which
generates a redirect page at the old URL:

```
aliases: [posts/2008-12-05-mini-conf-rence-java-ee]
```

## Checking that posts are reachable

`PostAvailabilityTest` starts the site and requests every post bundle in
`content/posts/`, failing on any that does not answer HTTP 200. It runs with
the rest of the suite, so CI will not deploy a post that stopped rendering:

```commandline
./mvnw test -Dtest=PostAvailabilityTest
```

It takes the post list from disk rather than from the sitemap on purpose. A
post that fails to render never reaches the sitemap, so checking the sitemap
alone would not notice it had gone; reading the directory means a post cannot
disappear silently. When posts fail it lists all of them at once, rather than
stopping at the first.

It derives each URL from the directory name, which is correct only while the
naming rule above holds. The two tests are a pair: break the naming rule and
`PostFolderNameTest` fails, not this one.

## Deployment

Merging to `main` deploys straight to production: the
[Deploy to GitHub Pages](https://github.com/lunatech-labs/lunatech-blog/actions/workflows/deploy_pages.yaml)
workflow builds the site and publishes it to GitHub Pages. There is no
separate acceptance environment; review your post on the PR preview before
merging.
