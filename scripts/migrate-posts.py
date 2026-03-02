#!/usr/bin/env python3
"""
Migrate Lunatech blog posts from AsciiDoc-attribute metadata to YAML frontmatter
for Quarkus Roq 2.0.4.
"""

import os
import re
import sys
import unicodedata
from pathlib import Path

POSTS_DIR = Path("posts")
MEDIA_DIR = Path("media")
OUTPUT_DIR = Path("content/posts")
AUTHORS_OUTPUT = Path("data/authors.yml")


def slugify(text):
    """Convert text to a URL-safe slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text


def safe_filename(filename):
    """Make filename URL-safe, preserving the date prefix."""
    name = filename.replace(".adoc", "")
    # Extract date prefix (YYYY-MM-DD)
    match = re.match(r"(\d{4}-\d{2}-\d{2})-(.*)", name)
    if match:
        date_prefix = match.group(1)
        slug_part = match.group(2)
        # Slugify the non-date part
        safe_slug = slugify(slug_part)
        return f"{date_prefix}-{safe_slug}.adoc"
    return filename


def yaml_quote(value):
    """Quote a YAML string value if it contains special characters."""
    if not value:
        return '""'
    # Quote if contains colons, brackets, quotes, or starts with special chars
    needs_quoting = any(c in value for c in ':{}&*?|>!%@`#,[]') or \
                    value.startswith(('-', ' ')) or \
                    value.endswith(' ') or \
                    value in ('true', 'false', 'null', 'yes', 'no')
    if needs_quoting:
        # Use double quotes and escape internal double quotes
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    return value


def parse_tags(tags_str):
    """Parse tags from AsciiDoc format like [tag1, tag2, tag3]."""
    if not tags_str:
        return []
    # Remove brackets
    tags_str = tags_str.strip()
    if tags_str.startswith("[") and tags_str.endswith("]"):
        tags_str = tags_str[1:-1]
    # Split by comma and trim
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    return tags


def parse_date(date_str):
    """Parse date from various formats like 'v1.0, 2025-01-01' or '2025-01-01'."""
    if not date_str:
        return None
    # Try to find YYYY-MM-DD pattern
    match = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", date_str)
    if match:
        parts = match.group(1).split("-")
        # Normalize to YYYY-MM-DD with zero-padding
        year = parts[0]
        month = parts[1].zfill(2)
        day = parts[2].zfill(2)
        return f"{year}-{month}-{day}"
    return None


def remove_ifdef_blocks(lines):
    """Remove ifdef::backend-html5[] ... endif::[] blocks."""
    result = []
    in_ifdef = False
    for line in lines:
        if line.strip().startswith("ifdef::backend-html5[]"):
            in_ifdef = True
            continue
        if in_ifdef and line.strip().startswith("endif::[]"):
            in_ifdef = False
            continue
        if in_ifdef:
            continue
        result.append(line)
    return result


def find_media_dir(filename):
    """Find the matching media directory for a post filename."""
    name = filename.replace(".adoc", "")
    media_path = MEDIA_DIR / name
    if media_path.is_dir():
        return name
    # Try with normalized date (no zero-padding)
    match = re.match(r"(\d{4})-0?(\d+)-0?(\d+)-(.*)", name)
    if match:
        alt_name = f"{match.group(1)}-{match.group(2)}-{match.group(3)}-{match.group(4)}"
        alt_path = MEDIA_DIR / alt_name
        if alt_path.is_dir():
            return alt_name
    return None


def has_background_image(media_dir_name):
    """Check if the media directory has a background.png."""
    if not media_dir_name:
        return False
    bg_path = MEDIA_DIR / media_dir_name / "background.png"
    return bg_path.exists()


def migrate_post(filepath):
    """Migrate a single post file, returning (output_path, author)."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Strip BOM and leading whitespace/newlines
    content = content.lstrip("\ufeff\n\r ")

    lines = content.split("\n")

    if not lines or not lines[0].startswith("= "):
        print(f"  WARNING: {filepath} does not start with '= ', skipping")
        return None, None

    # Extract title from first line
    title = lines[0][2:].strip()

    # Determine format
    # Format B: line 2 starts with :author:
    # Format A: line 2 is author name, line 3 is version/date
    author = None
    date = None
    attrs = {}
    content_start_line = 1  # After the title line

    is_format_b = len(lines) > 1 and lines[1].strip().startswith(":author:")

    if is_format_b:
        # Format B: attributes start on line 2
        content_start_line = 1
        i = 1
        while i < len(lines):
            line = lines[i].strip()
            if not line.startswith(":"):
                break
            # Parse attribute
            match = re.match(r"^:(\w[\w-]*):\s*(.*)", line)
            if match:
                key = match.group(1)
                value = match.group(2).strip()
                attrs[key] = value
            i += 1
            content_start_line = i

        author = attrs.get("author", "unknown")
        date_str = attrs.get("revdate", "")
        date = parse_date(date_str)
    else:
        # Format A: line 2 is author, line 3 is version/date
        if len(lines) > 1:
            author_line = lines[1].strip()
            if author_line and not author_line.startswith(":"):
                author = author_line
                content_start_line = 2
            else:
                author = "unknown"
                content_start_line = 1

        if len(lines) > 2 and content_start_line == 2:
            date_line = lines[2].strip()
            if date_line and not date_line.startswith(":"):
                date = parse_date(date_line)
                content_start_line = 3

        # Parse remaining attributes
        i = content_start_line
        while i < len(lines):
            line = lines[i].strip()
            if not line.startswith(":"):
                break
            match = re.match(r"^:(\w[\w-]*):\s*(.*)", line)
            if match:
                key = match.group(1)
                value = match.group(2).strip()
                attrs[key] = value
            i += 1
            content_start_line = i

    # Extract known attributes
    lang = attrs.get("lang", "en")
    tags_str = attrs.get("tags", "")
    tags = parse_tags(tags_str)
    imagesdir = attrs.get("imagesdir", "")
    toc = attrs.get("toc", "")
    toc_title = attrs.get("toc-title", "")
    toclevels = attrs.get("toclevels", "")

    # If no date from header, try from filename
    if not date:
        match = re.match(r"(\d{4}-\d{1,2}-\d{1,2})", filepath.name)
        if match:
            date = parse_date(match.group(1))

    if not date:
        print(f"  WARNING: No date found for {filepath}")
        date = "1970-01-01"

    # Determine media directory and background image
    media_dir_name = find_media_dir(filepath.stem)
    has_bg = has_background_image(media_dir_name)

    # Determine the output filename (safe slug)
    original_name = filepath.name
    safe_name = safe_filename(original_name)
    needs_alias = safe_name != original_name

    # Build original URL path for alias
    original_slug = original_name.replace(".adoc", "")
    safe_slug = safe_name.replace(".adoc", "")

    # Build YAML frontmatter
    fm_lines = ["---"]
    fm_lines.append("layout: post")
    fm_lines.append(f"title: {yaml_quote(title)}")
    fm_lines.append(f"date: {date}")
    fm_lines.append(f"author: {yaml_quote(author)}")
    fm_lines.append(f"lang: {lang}")

    if tags:
        fm_lines.append("tags:")
        for tag in tags:
            fm_lines.append(f"  - {yaml_quote(tag)}")

    if has_bg and media_dir_name:
        fm_lines.append(f"img: images/media/{media_dir_name}/background.png")

    if needs_alias:
        fm_lines.append("aliases:")
        fm_lines.append(f"  - /posts/{original_slug}")

    fm_lines.append("---")

    # Build the new content
    new_lines = fm_lines
    # Re-add the title
    new_lines.append(f"= {title}")
    new_lines.append("")

    # Add imagesdir with updated path if original post had one
    if media_dir_name:
        new_lines.append(f":imagesdir: /images/media/{media_dir_name}")
        new_lines.append("")

    # Add toc attributes if present
    if toc:
        new_lines.append(f":toc: {toc}")
        if toc_title:
            new_lines.append(f":toc-title: {toc_title}")
        if toclevels:
            new_lines.append(f":toclevels: {toclevels}")
        new_lines.append("")

    # Get remaining content lines (skip blank lines between attrs and content)
    remaining = lines[content_start_line:]

    # Remove ifdef blocks
    remaining = remove_ifdef_blocks(remaining)

    # Skip leading blank lines in content
    while remaining and not remaining[0].strip():
        remaining = remaining[1:]

    new_lines.extend(remaining)

    # Write output
    output_path = OUTPUT_DIR / safe_name
    output_content = "\n".join(new_lines)

    # Ensure trailing newline
    if not output_content.endswith("\n"):
        output_content += "\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_content)

    return output_path, author


def collect_authors(posts_dir):
    """Collect all unique authors from posts."""
    authors = set()
    for filepath in sorted(posts_dir.glob("*.adoc")):
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) < 2:
            continue

        # Check for Format B
        if lines[1].strip().startswith(":author:"):
            match = re.match(r"^:author:\s*(.*)", lines[1].strip())
            if match:
                authors.add(match.group(1).strip())
        else:
            # Format A: author on line 2
            author = lines[1].strip()
            if author and not author.startswith(":"):
                authors.add(author)

    return sorted(authors)


def generate_authors_yml(authors):
    """Generate authors.yml data file."""
    lines = []
    for author in authors:
        # Use the author handle as the key
        key = author.lower().replace(" ", "-")
        lines.append(f"{key}:")
        lines.append(f'  name: "{author}"')
        lines.append(f"  nickname: {yaml_quote(author)}")
        lines.append(f"  avatar: https://github.com/{author}.png")
        lines.append(f"  profile: https://github.com/{author}")
        lines.append("")

    os.makedirs(AUTHORS_OUTPUT.parent, exist_ok=True)
    with open(AUTHORS_OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Generated {AUTHORS_OUTPUT} with {len(authors)} authors")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    post_files = sorted(POSTS_DIR.glob("*.adoc"))
    print(f"Found {len(post_files)} posts to migrate")

    authors = set()
    success = 0
    errors = 0

    for filepath in post_files:
        try:
            output_path, author = migrate_post(filepath)
            if output_path:
                success += 1
                if author:
                    authors.add(author)
            else:
                errors += 1
        except Exception as e:
            print(f"  ERROR: {filepath}: {e}")
            errors += 1

    print(f"\nMigration complete: {success} succeeded, {errors} failed")
    print(f"Found {len(authors)} unique authors")

    # Generate authors.yml
    generate_authors_yml(sorted(authors))

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
