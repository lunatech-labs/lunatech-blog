#!/usr/bin/env python3
"""Regenerate architecture.png for the SDV fleet-management post.

Hand-laid Pillow drawing (no auto-layout) reproducing the original
"SDV Fleet Management: the data path" diagram, corrected to match the
code in lunatech-labs/sdv-fleet-management:

  * the sidecar WRITES lat/lon into Kuksa over gRPC (Set), it does not Get
  * OTA state flows over DDI to HawkBit, NOT over an ota/{vin}/state MQTT
    topic; the backend polls HawkBit for progress

Run:  python3 architecture_diagram.py
"""
import math
from PIL import Image, ImageDraw, ImageFont

S = 2                       # supersample factor, downscaled at the end
W, H = 1600 * S, 1180 * S

BG     = (250, 250, 248)
MAROON = (107, 31, 46)      # Rust (Lunatech)
GREY   = (138, 127, 122)    # Eclipse SDV
CLIENT = (199, 192, 187)    # Client (Vue 3)
DARK   = (45, 42, 40)
LINE   = (70, 64, 60)
EDGE   = (120, 110, 104)    # edge label grey
RULE   = (200, 194, 188)

F = "/System/Library/Fonts/Supplemental/Georgia.ttf"
FB = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
def font(path, sz): return ImageFont.truetype(path, sz * S)
title_f = font(FB, 30)
box_t   = font(FB, 19)
box_s   = font(F, 15)
leg_f   = font(F, 16)
edge_f  = font(F, 15)
edge_s  = font(F, 13)
grp_f   = font(F, 19)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

def sc(*v): return tuple(x * S for x in v)

def ctext(cx, cy, text, fnt, fill, anchor="mm"):
    d.text(sc(cx, cy), text, font=fnt, fill=fill, anchor=anchor)

def box(x0, y0, x1, y1, fill, lines, outline=None, radius=14):
    d.rounded_rectangle(sc(x0, y0, x1, y1), radius=radius * S,
                        fill=fill, outline=outline or fill, width=2 * S)
    cx = (x0 + x1) / 2
    n = len(lines)
    th = (n - 1) * 26
    y = (y0 + y1) / 2 - th / 2
    txt = (255, 255, 255) if fill in (MAROON, GREY) else DARK
    for i, (s, big) in enumerate(lines):
        ctext(cx, y + i * 26, s, box_t if big else box_s, txt)

def arrow(p0, p1, color=LINE, width=2, head=11):
    d.line([sc(*p0), sc(*p1)], fill=color, width=width * S)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for s in (+1, -1):
        a = ang + math.pi - s * 0.42
        d.line([sc(*p1), sc(p1[0] + head * math.cos(a), p1[1] + head * math.sin(a))],
               fill=color, width=width * S)

def elabel(cx, cy, text, fnt=edge_f, fill=EDGE, box_bg=False):
    if box_bg:
        l, t, r, b = d.textbbox(sc(cx, cy), text, font=fnt, anchor="mm")
        pad = 5 * S
        d.rectangle([l - pad, t - pad, r + pad, b + pad], fill=BG)
    ctext(cx, cy, text, fnt, fill)

# ── Title + rule ──────────────────────────────────────────────────────────
ctext(62, 52, "SDV Fleet Management: the data path", title_f, DARK, anchor="lm")
d.line(sc(62, 100, 1540, 100), fill=RULE, width=3 * S)

# ── Legend ────────────────────────────────────────────────────────────────
for i, (col, lab) in enumerate([(MAROON, "Rust (Lunatech)"),
                                (GREY, "Eclipse SDV"),
                                (CLIENT, "Client (Vue 3)")]):
    y = 44 + i * 26
    d.rounded_rectangle(sc(1182, y - 9, 1202, y + 9), radius=3 * S, fill=col)
    ctext(1212, y, lab, leg_f, DARK, anchor="lm")

# ── 20 vehicles group ───────────────────────────────────────────────────────
d.rounded_rectangle(sc(62, 158, 628, 372), radius=18 * S, outline=GREY, width=2 * S)
ctext(84, 178, "20 vehicles", grp_f, DARK, anchor="lm")
box(88, 208, 312, 330, GREY,
    [("Kuksa Databroker", 1), ("VSS signals · gRPC", 0), (":55556 to :55575", 0)])
box(392, 208, 602, 330, MAROON,
    [("kuksa2mqtt", 1), ("sidecar · Rust", 0), ("1 Hz", 0)])
arrow((312, 269), (392, 269))
elabel(352, 246, "gRPC Set", edge_s, box_bg=True)
elabel(352, 292, "lat/lon", edge_s, box_bg=True)

# ── Top row brokers ─────────────────────────────────────────────────────────
box(660, 214, 968, 314, GREY, [("Eclipse Mosquitto", 1), ("MQTT broker · :1883", 0)])
box(1185, 214, 1493, 314, GREY, [("Eclipse HawkBit", 1), (":8083 · DDI poll loop", 0)])

# ── Middle row ──────────────────────────────────────────────────────────────
box(655, 492, 968, 596, MAROON,
    [("Rust backend", 1), ("axum · :3000", 0), ("in-memory fleet state", 0)])
box(1150, 488, 1493, 584, MAROON, [("OTA agents x20", 1), ("Rust", 0)])

# ── Browser ─────────────────────────────────────────────────────────────────
box(650, 822, 968, 936, CLIENT, [("Browser", 1), ("Vue 3", 0)])

# ── Edges: telemetry track ──────────────────────────────────────────────────
arrow((430, 372), (700, 314))
elabel(470, 392, "publish kuksa/+/telemetry/#", edge_f, box_bg=True)
arrow((812, 314), (812, 492))
elabel(760, 400, "subscribe")

# ── Edges: OTA track (corrected) ────────────────────────────────────────────
# backend asks HawkBit to start the rollout and polls it for progress (REST)
arrow((968, 528), (1185, 330))
elabel(1075, 408, "REST: rollout + poll", box_bg=True)
# HawkBit hands assigned actions down to the agents (DDI)
arrow((1300, 314), (1300, 488))
elabel(1372, 372, "DDI assigned actions", box_bg=True)
# agents report progress back up to HawkBit (DDI feedback) — no MQTT hop
arrow((1410, 488), (1410, 314), color=EDGE)
elabel(1430, 400, "DDI", edge_s, box_bg=True)
elabel(1430, 420, "feedback", edge_s, box_bg=True)
# agents set the new SoftwareVersion into each car's databroker (gRPC)
arrow((1150, 545), (430, 372), color=EDGE)
elabel(470, 470, "gRPC SetSoftwareVersion", box_bg=True)

# ── Edges: client track ─────────────────────────────────────────────────────
arrow((742, 596), (742, 822))
elabel(742, 660, "REST")
ctext(665, 700, "/fleet /campaigns /versions", edge_s, EDGE, anchor="lm")
arrow((878, 822), (878, 596))
elabel(878, 660, "WebSocket")
ctext(955, 730, "/ws/fleet /ws/campaigns", edge_s, EDGE, anchor="rm")

# ── Output ──────────────────────────────────────────────────────────────────
img = img.resize((1600, 1180), Image.LANCZOS)
img.save("architecture.png")
print("wrote architecture.png")
