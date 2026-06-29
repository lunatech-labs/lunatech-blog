#!/usr/bin/env python3
"""
One-time conversion of flat posts into Roq page bundles, co-locating each post's
OWN media only. Shared assets stay in public/media with their /media/... URLs.

Before: content/posts/<slug>.adoc            +  public/media/<slug>/...  (own)
                                              +  public/media/<other>/... (shared)
After:  content/posts/<slug>/index.adoc       (own images -> bare refs)
        content/posts/<slug>/<own images>
        public/media/<other>/...              (shared: untouched, /media/... refs kept)

Rules:
- Move public/media/<slug>/* (the post's own dir, incl. by-convention background.png)
  into the bundle; rewrite its references (and `:imagesdir:`) to bare filenames.
- References to ANY OTHER /media/<dir>/ (shared images, downloads, retrospectives,
  en/fr variants) are left untouched and keep living in public/media.

--apply performs changes; default is a dry-run report.
"""
import os
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

ROOT = Path('.')
POSTS = ROOT / 'content' / 'posts'
MEDIA = ROOT / 'public' / 'media'

IMAGESDIR_RE = re.compile(r'^:imagesdir:\s*(\S+)\s*$')
# image::T[ , image:T[ , link:T[  — target has no whitespace
REF_RE = re.compile(r'\b(image:{1,2}|link:)([^\[\]\s]+)(\[)')
LISTING_RE = re.compile(r'^(----|\.\.\.\.)\s*$')

apply = '--apply' in sys.argv[1:]
report = {'posts': 0, 'bundled_media': 0, 'no_own_media': 0,
          'files_moved': 0, 'refs_rewritten': 0, 'sanitised': 0}


def sanitize(name: str) -> str:
    return re.sub(r'[^A-Za-z0-9._-]', '_', urllib.parse.unquote(name))


def convert(adoc: Path):
    report['posts'] += 1
    slug = adoc.stem
    bundle = POSTS / slug
    own = MEDIA / slug
    own_prefixes = (f'/media/{slug}/', f'media/{slug}/')
    lines = adoc.read_text(encoding='utf-8').split('\n')

    imagesdir = next((m.group(1) for ln in lines
                      if (m := IMAGESDIR_RE.match(ln))), None)
    imagesdir_is_own = imagesdir in (f'/media/{slug}', f'/media/{slug}/')

    has_own = own.is_dir() and any(own.iterdir())
    report['bundled_media' if has_own else 'no_own_media'] += 1

    if not apply:
        # still exercise rewrite to count, but don't write
        pass

    # rewrite content
    out, in_listing = [], False
    for ln in lines:
        if IMAGESDIR_RE.match(ln):
            if imagesdir_is_own:
                continue          # drop: own images become bare refs
            out.append(ln)        # keep: points at a shared dir
            continue
        if LISTING_RE.match(ln):
            in_listing = not in_listing
            out.append(ln)
            continue
        if in_listing:
            out.append(ln)
            continue

        def repl(m):
            kind, target, br = m.group(1), m.group(2), m.group(3)
            if target.startswith(('http://', 'https://', 'data:')):
                return m.group(0)
            # absolute reference into our own media dir -> bare filename
            for p in own_prefixes:
                if target.startswith(p):
                    report['refs_rewritten'] += 1
                    return kind + sanitize(os.path.basename(target)) + br
            # bare reference resolved via an own imagesdir -> sanitise, keep bare
            if imagesdir_is_own and '/' not in target:
                if sanitize(target) != target:
                    report['sanitised'] += 1
                report['refs_rewritten'] += 1
                return kind + sanitize(target) + br
            # shared / external / other-dir reference -> leave untouched
            return m.group(0)

        out.append(REF_RE.sub(repl, ln))

    if not apply:
        return

    bundle.mkdir(exist_ok=True)
    if has_own:
        for f in sorted(own.iterdir()):
            if f.is_file():
                dest = bundle / sanitize(f.name)
                shutil.move(str(f), str(dest))
                report['files_moved'] += 1
        # remove now-empty own dir
        try:
            own.rmdir()
        except OSError:
            pass
    (bundle / 'index.adoc').write_text('\n'.join(out), encoding='utf-8')
    adoc.unlink()


def main():
    for a in sorted(POSTS.glob('*.adoc')):
        convert(a)
    print(('APPLIED' if apply else 'DRY-RUN') + ' summary:')
    for k in report:
        print(f'  {k}: {report[k]}')
    if MEDIA.is_dir():
        remaining = [d.name for d in sorted(MEDIA.iterdir()) if d.is_dir()]
        print(f'  dirs remaining in public/media (shared/downloads): {len(remaining)}')


if __name__ == '__main__':
    main()
