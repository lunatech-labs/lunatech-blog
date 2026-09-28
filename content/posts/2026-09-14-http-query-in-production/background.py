"""Regenerates background.png, the card and hero image for this post.

    python3 background.py

Type as the image: QUERY set in Playfair Display, the theme's --font-display, so
the card is the same face as the post title and every heading under it. A solid
block sits in the counter of the Q, which is the body the verb carries. The
counter is located geometrically rather than guessed at: render a Q into a mask,
flood the outside, and whatever background the flood cannot reach is the counter.

Only exact-background pixels count in that mask. Thresholding it instead picks up
the antialiased rim on the *outside* of the glyph, and the block then swells into
a padlock across the Q's stem.

Playfair Display is SIL OFL and is fetched from Google Fonts on first run into a
cache under the system temp directory, never into this bundle. The legacy css
endpoint serves TTF, which Pillow can read; css2 serves woff2, which it cannot.
"""
import pathlib
import tempfile
import urllib.request

from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).parent

# Cached outside the bundle on purpose: Roq publishes every file in a post
# directory, so a font dropped in here would ship as a site asset.
FONTS = pathlib.Path(tempfile.gettempdir()) / "lunatech-blog-fonts"

FACES = {
    "PlayfairDisplay.ttf":
        "https://fonts.gstatic.com/s/playfairdisplay/v40/"
        "nuFvD-vYSZviVYUb_rj3ij__anPXJzDwcbmjWBN2PKeiunDXbtY.ttf",
    "PlayfairDisplayItalic.ttf":
        "https://fonts.gstatic.com/s/playfairdisplay/v40/"
        "nuFRD-vYSZviVYUb_rj3ij__anPXDTnCjmHKM4nYO7KN_qiTXtHA_A.ttf",
}

S = 3                                   # supersampling, so the hairline serifs survive
W, H = 1200 * S, 630 * S

NOIR = (11, 11, 12)                     # the theme's --noir
CREAM = (239, 230, 210)                 # --cream
GOLD = (201, 169, 97)                   # --gold
GOLD_DEEP = (169, 136, 71)              # --gold-deep
GRAY = (122, 116, 106)

SUBTITLE = "safe  ·  idempotent  ·  carries a body"


def face(name):
    FONTS.mkdir(exist_ok=True)
    path = FONTS / name
    if not path.exists():
        urllib.request.urlretrieve(FACES[name], path)
    return str(path)


img = Image.new("RGB", (W, H), NOIR)
d = ImageDraw.Draw(img)

# --- fit QUERY to the measure ---------------------------------------------

TARGET = int(W * 0.62)
size = 40
while d.textlength("QUERY", font=ImageFont.truetype(face("PlayfairDisplay.ttf"), size)) < TARGET:
    size += 4

font = ImageFont.truetype(face("PlayfairDisplay.ttf"), size)
sub = ImageFont.truetype(face("PlayfairDisplayItalic.ttf"), int(size * 0.105))

word_w = d.textlength("QUERY", font=font)
wl, wt, wr, wb = font.getbbox("QUERY")
sub_w = d.textlength(SUBTITLE, font=sub)
sl, st, sr, sb = sub.getbbox(SUBTITLE)

GAP_RULE = 44 * S
GAP_SUB = 34 * S

stack = (wb - wt) + GAP_RULE + GAP_SUB + (sb - st)
top = (H - stack) / 2

x = (W - word_w) / 2
y = top - wt
d.text((x, y), "QUERY", font=font, fill=CREAM)

# --- the body, in the counter of the Q ------------------------------------

ql, qt, qr, qb = font.getbbox("Q")
pad = 120                                # enough that the glyph never touches the edge
mask = Image.new("L", (int(qr - ql) + pad * 2, int(qb - qt) + pad * 2), 0)
ImageDraw.Draw(mask).text((pad - ql, pad - qt), "Q", font=font, fill=255)
ImageDraw.floodfill(mask, (0, 0), 128)

px = mask.load()
xs, ys = [], []
for yy in range(mask.height):
    for xx in range(mask.width):
        if px[xx, yy] == 0:              # only what the flood could not reach
            xs.append(xx)
            ys.append(yy)

# Bounding-box centre, not the centroid: the counter is an oval and the tail
# drags a centroid off the middle of the bowl.
cx = x + ql + (min(xs) + max(xs)) / 2 - pad
cy = y + qt + (min(ys) + max(ys)) / 2 - pad
counter_w = max(xs) - min(xs)
counter_h = max(ys) - min(ys)

cy += counter_h * 0.05                   # the oval is widest a little below its middle
block = min(counter_w, counter_h) * 0.62
d.rounded_rectangle(
    [cx - block / 2, cy - block / 2, cx + block / 2, cy + block / 2],
    radius=block * 0.16, fill=GOLD)

# --- footing --------------------------------------------------------------

rule_y = y + wb + GAP_RULE
half = sub_w / 2 + 46 * S
d.line([W / 2 - half, rule_y, W / 2 + half, rule_y], fill=GOLD_DEEP, width=1 * S)
d.text(((W - sub_w) / 2, rule_y + GAP_SUB - st), SUBTITLE, font=sub, fill=GRAY)

d.rectangle([0, 0, 6 * S, H], fill=GOLD)

img.resize((1200, 630), Image.LANCZOS).save(HERE / "background.png", optimize=True)
print("wrote", HERE / "background.png")
