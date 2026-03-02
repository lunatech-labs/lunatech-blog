# Lunatech Blog

The Lunatech engineering blog, powered by [Quarkus Roq](https://iamroq.com/) — a static site generator built on Quarkus.

Blog posts are written in [AsciiDoc](https://asciidoc.org/) format with YAML frontmatter.

**Live site:** [blog.lunatech.com](https://blog.lunatech.com)

## Writing a new blog post

1. Create a new `.adoc` file in `content/posts/` with the naming format `YYYY-MM-DD-title-slug.adoc`
2. Add YAML frontmatter at the top of the file:

```asciidoc
---
layout: post
title: "Your Post Title"
date: 2025-01-15
author: yourgithubhandle
lang: en
tags:
  - tag1
  - tag2
img: images/media/2025-01-15-title-slug/background.png
---
= Your Post Title

:imagesdir: /images/media/2025-01-15-title-slug

Your content here...
```

3. Add your images in `public/images/media/YYYY-MM-DD-title-slug/`:
   - `background.png` — featured image for the post card (required)
   - Any other images referenced in the post

## Preview locally

```bash
./mvnw quarkus:dev
```

The blog will be available at [http://localhost:8080](http://localhost:8080) with live reload.

## Build for production

```bash
./mvnw package -DskipTests -Droq
```

The static site output is generated in `target/roq/`.

## Deployment

Merging to `main` automatically deploys the blog to GitHub Pages via the GitHub Actions workflow.

## Project structure

```
content/
  index.html              Homepage
  404.html                Error page
  posts/                  Blog posts (AsciiDoc with YAML frontmatter)
  authors/                Author pages
data/
  authors.yml             Author metadata
  menu.yml                Navigation menu
public/
  css/style.css           Stylesheet
  images/                 Logos, avatars
  images/media/           Post images (background.png, etc.)
templates/
  layouts/                Page layouts (Qute templates)
  partials/               Reusable components
pom.xml                   Maven project with Roq dependencies
```

## Compressing images

Images should be compressed before committing. Install `pngcrush`:

```bash
brew install pngcrush
pngcrush -rem allb -brute -reduce input.png output.png
```
