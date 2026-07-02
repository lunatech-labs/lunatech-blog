#!/usr/bin/env python3
"""Move each post's AsciiDoc document header (title, author, revision) into
YAML front matter and drop it from the body.

The migrated posts keep an AsciiDoc header:

    ---
    tags: [...]
    ---
    = Title
    author
    v1.0, 2005-04-10

Asciidoctor renders that header inside the article body (a second <h1>
plus an author/revision byline), which duplicates the title and metadata
the Roq theme already renders from front matter. This script promotes the
title and author to front matter (the theme reads page.title and
page.data.author; the date comes from the filename) and removes the header
lines so the body no longer double-renders them.

Idempotent: a post whose body no longer starts with a `= ` title is left
untouched. Safe to re-run.
"""
import re
import sys
from pathlib import Path

POSTS = Path(__file__).resolve().parent.parent / "content" / "posts"
REVISION_RE = re.compile(r"^v\d|^\d{4}-\d{2}-\d{2}")
EMAIL_RE = re.compile(r"\s*<[^>]*>\s*$")


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def split_front_matter(text: str):
    """Return (fm_lines, body) where fm_lines are the lines inside the
    leading --- fence (without the fences), or (None, text) if absent."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    fm = text[4:end + 1]           # inclusive of trailing newline of last fm line
    body = text[end + len("\n---\n"):]
    return fm.splitlines(), body


def main() -> int:
    dry = "--dry-run" in sys.argv
    changed = skipped = 0
    samples = []
    for adoc in sorted(POSTS.glob("*/index.adoc")):
        text = adoc.read_text(encoding="utf-8")
        fm_lines, body = split_front_matter(text)
        if fm_lines is None:
            skipped += 1
            continue

        lines = body.splitlines()
        # index of first non-blank body line
        i = 0
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        if i >= len(lines) or not lines[i].startswith("= "):
            skipped += 1                       # already transformed / no title
            continue

        title = lines[i][2:].strip()
        remove = {i}
        author = None
        # author line: immediately after title, non-blank (AsciiDoc header grammar)
        j = i + 1
        if j < len(lines) and lines[j].strip() != "":
            author = EMAIL_RE.sub("", lines[j].strip()).strip()
            remove.add(j)
            # revision line: immediately after author, if it looks like one
            k = j + 1
            if k < len(lines) and REVISION_RE.match(lines[k].strip()):
                remove.add(k)

        new_body_lines = [l for idx, l in enumerate(lines) if idx not in remove]
        # drop leading blank lines left behind by the removed header
        while new_body_lines and new_body_lines[0].strip() == "":
            new_body_lines.pop(0)
        new_body = "\n".join(new_body_lines) + ("\n" if body.endswith("\n") else "")

        # build new front matter: prepend title/author unless already present
        have_title = any(re.match(r"\s*title\s*:", l) for l in fm_lines)
        have_author = any(re.match(r"\s*author\s*:", l) for l in fm_lines)
        prefix = []
        if not have_title:
            prefix.append(f"title: {yaml_quote(title)}")
        if author and not have_author:
            prefix.append(f"author: {yaml_quote(author)}")
        new_fm = "\n".join(prefix + fm_lines)

        new_text = f"---\n{new_fm}\n---\n{new_body}"
        if dry:
            if len(samples) < 4:
                samples.append((adoc.parent.name, title, author,
                                sorted(remove)))
        else:
            adoc.write_text(new_text, encoding="utf-8")
        changed += 1

    print(f"{'would change' if dry else 'changed'}={changed} skipped={skipped}")
    for name, title, author, rm in samples:
        print(f"  {name}: title={title!r} author={author!r} removed_body_lines={rm}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
