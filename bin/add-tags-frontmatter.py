#!/usr/bin/env python3
"""Promote each post's AsciiDoc `:tags:` attribute to a top-level YAML
front matter `tags:` list.

The Roq tagging plugin derives `/tags/:tag` pages from the top-level `tags`
front matter key. Our migrated AsciiDoc posts only carry tags in the
`:tags: [..]` attribute (which Roq exposes nested under `attributes.tags`
as a raw string), so the plugin sees nothing. This script reads that
attribute and prepends a YAML front matter block so the plugin can generate
tag pages.

Idempotent: posts that already start with a `---` front matter fence are
skipped. Safe to re-run after pulling new posts.
"""
import re
import sys
from pathlib import Path

POSTS = Path(__file__).resolve().parent.parent / "content" / "posts"
TAGS_RE = re.compile(r"^:tags:\s*\[(.*)\]\s*$")


def parse_tags(line_body: str) -> list[str]:
    return [t.strip() for t in line_body.split(",") if t.strip()]


def yaml_block(tags: list[str]) -> str:
    """Block-style YAML list with double-quoted scalars (safe for spaces,
    '#', ':', and other YAML metacharacters that appear in tags)."""
    lines = ["tags:"]
    for t in tags:
        escaped = t.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'- "{escaped}"')
    return "\n".join(lines) + "\n"


def main() -> int:
    changed = skipped = no_tags = 0
    for adoc in sorted(POSTS.glob("*/index.adoc")):
        text = adoc.read_text(encoding="utf-8")
        if text.startswith("---\n"):
            skipped += 1
            continue
        tags = None
        for line in text.splitlines():
            m = TAGS_RE.match(line)
            if m:
                tags = parse_tags(m.group(1))
                break
        if not tags:
            no_tags += 1
            continue
        # block-style YAML with safe quoting for any special characters
        fm = yaml_block(tags)
        adoc.write_text(f"---\n{fm}---\n{text}", encoding="utf-8")
        changed += 1
    print(f"changed={changed} skipped(already had FM)={skipped} no_tags={no_tags}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
