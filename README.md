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
- `public/`: files copied verbatim to the site root (CSS, JS, shared images, legacy `/media/` downloads)
- `src/main/resources/application.properties`: site configuration
- `docs/URL-CHANGES.md`: URL differences from the previous blog engine

## Writing a post

1. Fork or branch this repository.
2. Create a bundle directory: `content/posts/yyyy-MM-dd-your-title/`.
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

## Deployment

Merging to `main` deploys straight to production: the
[Deploy to GitHub Pages](https://github.com/lunatech-labs/lunatech-blog/actions/workflows/deploy_pages.yaml)
workflow builds the site and publishes it to GitHub Pages. There is no
separate acceptance environment; review your post on the PR preview before
merging.
