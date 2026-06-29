#!/usr/bin/env python3
"""
Idempotent migration transform for Lunatech blog posts (Asciidoctor engine -> Quarkus Roq).

Re-runnable at any time: running it again after contributors add new posts only changes
files that still contain a legacy construct. Already-migrated files are left untouched.

Transforms applied to every *.adoc under the target directory (default: content/posts):

  1. Literal blocks `....`  ->  listing blocks `----`
     The pure-Java AsciiDoc engine Roq uses (Yupiik) throws a NullPointerException on
     `....` literal blocks. `----` renders identically. Only converts lines that are
     exactly four dots (optionally trailing whitespace).

  2. `video::<id>[...]`  ->  responsive passthrough <iframe>
     The Java AsciiDoc plugin does not support the `video::` macro (it is silently
     dropped). Numeric id or a `vimeo` option -> Vimeo embed; otherwise YouTube.
     Honours width=, height= and start= options when present.

  3. `../media/...`  ->  `/media/...`
     Media moves to `static/media/` (served at `/media/...`). Relative `../media`
     references (in `:imagesdir:` and inline `image::` macros) would resolve wrong from
     a `/posts/<slug>/` page, so they are rewritten to absolute site paths.

Usage:
    python3 bin/migrate-posts.py [POSTS_DIR]      # default POSTS_DIR=content/posts
    python3 bin/migrate-posts.py --check [DIR]    # report files that WOULD change, exit 1 if any

This script does not touch the dotty post edge case or anything beyond the rules above.
"""
import re
import sys
from pathlib import Path

VIDEO_RE = re.compile(r'^video::([^\[\]\s]+)\[([^\]]*)\]\s*$')
LITERAL_RE = re.compile(r'^\.\.\.\.[ \t]*$')


def build_iframe(vid: str, opts: str) -> str:
    attrs = [a.strip() for a in opts.split(',') if a.strip()]
    kv = {}
    flags = []
    for a in attrs:
        if '=' in a:
            k, v = a.split('=', 1)
            kv[k.strip()] = v.strip()
        else:
            flags.append(a.lower())
    width = kv.get('width', '560')
    height = kv.get('height', '315')
    is_vimeo = 'vimeo' in flags or vid.isdigit()
    if is_vimeo:
        src = f'https://player.vimeo.com/video/{vid}'
    else:
        src = f'https://www.youtube.com/embed/{vid}'
        if 'start' in kv:
            src += f'?start={kv["start"]}'
    # Passthrough block so the engine emits the HTML verbatim.
    return (
        '++++\n'
        f'<iframe width="{width}" height="{height}" src="{src}" '
        'frameborder="0" allow="accelerometer; autoplay; clipboard-write; '
        'encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>\n'
        '++++'
    )


def transform(text: str) -> str:
    out = []
    for line in text.split('\n'):
        m = VIDEO_RE.match(line)
        if m:
            out.append(build_iframe(m.group(1), m.group(2)))
            continue
        if LITERAL_RE.match(line):
            out.append('----')
            continue
        # absolute-ise media paths (covers :imagesdir: and inline image:: macros)
        line = line.replace('../media/', '/media/').replace('../media', '/media')
        out.append(line)
    return '\n'.join(out)


def main() -> int:
    args = [a for a in sys.argv[1:] if a != '--check']
    check = '--check' in sys.argv[1:]
    posts_dir = Path(args[0]) if args else Path('content/posts')
    if not posts_dir.is_dir():
        print(f'error: posts directory not found: {posts_dir}', file=sys.stderr)
        return 2

    changed = []
    for f in sorted(posts_dir.glob('*.adoc')):
        original = f.read_text(encoding='utf-8')
        migrated = transform(original)
        if migrated != original:
            changed.append(f)
            if not check:
                f.write_text(migrated, encoding='utf-8')

    verb = 'would change' if check else 'changed'
    print(f'{len(changed)} file(s) {verb}:')
    for f in changed:
        print(f'  {f}')
    if check and changed:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
