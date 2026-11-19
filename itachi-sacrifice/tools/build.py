#!/usr/bin/env python3
"""Writes index.html, compositions/*.html and cues.json for the Itachi explainer.

  python3 tools/build.py            # look pass (style.css only)
  python3 tools/build.py --blocking # blocking pass (adds assets/blocking.css)
  python3 tools/build.py --sound    # look pass + the sfx audio track

Every sound cue is recorded by the same call that writes its animation, so the cue
times are read from the timelines, never guessed.
"""
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
BLOCKING = "--blocking" in sys.argv
SOUND = "--sound" in sys.argv

CYAN = ("#35E0F2", "#A6F7FF", "#1BA9C4")
YELLOW = ("#FFD23F", "#FFF0A0", "#E8A912")
NAVY = "#0B1E4A"

FLAME = "M150 8 C168 66 206 96 222 150 C230 124 244 108 260 96 C270 166 278 222 272 284 C266 360 214 410 150 410 C86 410 34 360 28 284 C24 232 34 188 50 156 C58 180 66 194 80 204 C78 136 118 96 150 8 Z"
FLAME_HL = "M118 120 C95 180 70 220 72 290 C74 330 92 352 112 360 C100 320 104 270 124 220 C134 190 134 150 118 120 Z"
FLAME_SH = "M272 280 C272 358 218 410 150 410 C120 410 96 400 76 384 C150 400 230 360 250 250 C262 255 272 265 272 280 Z"
HEART = "M150 262 C60 200 10 150 10 92 C10 46 46 12 90 12 C118 12 140 28 150 50 C160 28 182 12 210 12 C254 12 290 46 290 92 C290 150 240 200 150 262 Z"
HEART_HL = "M60 50 C40 60 32 80 34 104 C46 86 62 72 86 64 C80 54 70 50 60 50 Z"
HEART_SH = "M290 92 C290 150 240 200 150 262 C140 255 130 248 122 242 C200 196 262 150 272 60 C284 70 290 82 290 92 Z"
STAR8 = "M150 0 L176 104 L256 44 L196 124 L300 150 L196 176 L256 256 L176 196 L150 300 L124 196 L44 256 L104 176 L0 150 L104 124 L44 44 L124 104 Z"

cues = []


def box(left, top, w, h, extra=""):
    return f'style="left:{left}px;top:{top}px;width:{w}px;height:{h}px;{extra}"'


# ---------------------------------------------------------------- shapes
def flame(id, left, top, w, pal, eyes=True, extras="", glow=True):
    h = round(w * 1.4)
    base, hl, sh = pal
    g = f'<svg id="{id}-g" class="glow" viewBox="0 0 300 420"><path d="{FLAME}" fill="{base}"/></svg>' if glow else ""
    e = ""
    if eyes:
        e = f'''<g id="{id}-eyes"><ellipse cx="118" cy="270" rx="16" ry="24" fill="{NAVY}"/><ellipse cx="182" cy="270" rx="16" ry="24" fill="{NAVY}"/>
      <circle id="{id}-gl" cx="123" cy="261" r="6" fill="#fff"/><circle cx="187" cy="261" r="6" fill="#fff"/></g>'''
    return f'''<div id="{id}" class="obj" {box(left, top, w, h)}>{g}
  <svg id="{id}-b" class="body" viewBox="0 0 300 420"><path d="{FLAME}" fill="{base}"/>
    <path class="hl" d="{FLAME_HL}" fill="{hl}"/><path class="sh" d="{FLAME_SH}" fill="{sh}"/>
    <path d="M150 300 C166 326 184 346 180 372 C176 394 164 402 150 402 C136 402 124 394 120 372 C116 346 134 326 150 300 Z" fill="{hl}" opacity="0.75"/>{extras}{e}</svg></div>'''


def pip(id, left, top, w):
    return f'''<div id="{id}" class="obj" {box(left, top, w, w)}>
  <svg id="{id}-b" class="body" viewBox="0 0 300 300">
    <ellipse cx="112" cy="276" rx="28" ry="14" fill="#7B4FE6"/><ellipse cx="188" cy="276" rx="28" ry="14" fill="#7B4FE6"/>
    <ellipse id="{id}-al" cx="34" cy="178" rx="18" ry="32" fill="#8A5EF0"/><ellipse id="{id}-ar" cx="266" cy="178" rx="18" ry="32" fill="#8A5EF0"/>
    <ellipse cx="150" cy="160" rx="122" ry="112" fill="#9B6BFF"/>
    <ellipse class="hl" cx="104" cy="96" rx="50" ry="30" fill="#BC9CFF" transform="rotate(-24 104 96)"/>
    <path class="sh" d="M272 160 C272 222 218 272 150 272 C118 272 90 262 70 246 C150 262 238 230 258 120 C267 132 272 146 272 160 Z" fill="#7B4FE6"/>
    <path d="M38 204 C100 236 200 236 262 204 L262 228 C200 262 100 262 38 228 Z" fill="#FFD23F"/>
    <path class="sh" d="M150 246 C200 246 236 236 262 228 L262 236 C226 252 190 258 150 258 Z" fill="#E8A912"/>
    <path d="M200 236 L230 234 L242 294 L208 292 Z" fill="#FF8A3D"/>
    <g id="{id}-eyes"><ellipse cx="112" cy="138" rx="26" ry="38" fill="#14123A"/><ellipse cx="188" cy="138" rx="26" ry="38" fill="#14123A"/>
      <circle cx="121" cy="122" r="9" fill="#fff"/><circle cx="197" cy="122" r="9" fill="#fff"/>
      <circle cx="104" cy="154" r="4" fill="#fff"/><circle cx="180" cy="154" r="4" fill="#fff"/></g>
  </svg></div>'''


def lantern(id, left, top, w=120, lit=True):
    h = round(w * 170 / 120)
    off = "0" if lit else "0.85"
    gop = "" if lit else ' style="opacity:0"'
    return f'''<div id="{id}" class="obj" {box(left, top, w, h)}>
  <svg id="{id}-g" class="glow"{gop} viewBox="0 0 120 170"><ellipse cx="60" cy="95" rx="50" ry="60" fill="#FFD23F"/></svg>
  <svg class="body" viewBox="0 0 120 170"><rect x="58" y="0" width="4" height="26" fill="#9B6BFF"/>
    <rect x="34" y="22" width="52" height="16" rx="6" fill="#5A3AB0"/>
    <rect x="14" y="34" width="92" height="112" rx="42" fill="#FF8A3D"/>
    <rect class="hl" x="26" y="48" width="22" height="56" rx="11" fill="#FFC08A"/>
    <path class="sh" d="M106 90 C106 124 90 146 60 146 C76 136 92 116 94 80 Z" fill="#D9631E"/>
    <rect id="{id}-off" x="14" y="34" width="92" height="112" rx="42" fill="#2A1E5A" opacity="{off}"/>
    <rect x="34" y="142" width="52" height="16" rx="6" fill="#5A3AB0"/></svg></div>'''


def house(id, left, top, w=140):
    h = round(w * 170 / 160)
    return f'''<div id="{id}" class="obj" {box(left, top, w, h)}>
  <svg class="glow" viewBox="0 0 160 170"><rect x="56" y="96" width="44" height="40" fill="#FFD23F"/></svg>
  <svg class="body" viewBox="0 0 160 170"><rect x="22" y="78" width="116" height="88" fill="#3DF2A6"/>
    <rect class="hl" x="22" y="78" width="34" height="34" fill="#9AF9D0"/><rect class="sh" x="104" y="78" width="34" height="88" fill="#22C98A"/>
    <polygon points="6,84 80,14 154,84" fill="#9B6BFF"/><polygon class="hl" points="22,80 80,26 80,44 42,80" fill="#BC9CFF"/>
    <polygon class="sh" points="80,14 154,84 128,84" fill="#7B4FE6"/>
    <rect x="60" y="100" width="36" height="32" rx="6" fill="#FFD23F"/></svg></div>'''


# ---------------------------------------------------------------- scene builder
JS_HELPERS = """
  const tl = gsap.timeline({ paused: true });
  function pop(s, t) {
    tl.fromTo(s, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.42, ease: "back.out(1.6)" }, t);
    tl.to(s, { scaleX: 1.08, scaleY: 0.92, duration: 0.08, ease: "power1.out" }, t + 0.42);
    tl.to(s, { scaleX: 1, scaleY: 1, duration: 0.16, ease: "back.out(2)" }, t + 0.5);
  }
  function leave(s, t) { tl.to(s, { scale: 0.6, opacity: 0, duration: 0.25, ease: "power2.in" }, t); }
  function breathe(s, t0, t1, p) {
    const n = Math.max(1, Math.ceil((t1 - t0) / (p / 2)) - 1);
    tl.fromTo(s, { scaleY: 1, scaleX: 1 }, { scaleY: 1.04, scaleX: 0.98, duration: p / 2, ease: "sine.inOut", yoyo: true, repeat: n }, t0);
  }
  function flicker(s, t0, t1, p) {
    const n = Math.max(1, Math.ceil((t1 - t0) / (p / 2)) - 1);
    tl.fromTo(s, { skewX: -3 }, { skewX: 3, duration: p / 2, ease: "sine.inOut", yoyo: true, repeat: n }, t0);
  }
  function blink(s, t) {
    tl.to(s, { scaleY: 0.1, duration: 0.07, ease: "power1.in" }, t);
    tl.to(s, { scaleY: 1, duration: 0.09, ease: "power1.out" }, t + 0.07);
  }
"""


class Scene:
    def __init__(self, id, start, dur, exit=True, first=False):
        self.id, self.start, self.dur, self.exit, self.first = id, start, dur, exit, first
        self.html, self.js = [], []
        self.origins = []

    def add(self, h):
        self.html.append(h)

    def j(self, s):
        self.js.append("  " + s)

    def cue(self, t, type, **kw):
        cues.append(dict(t=round(self.start + t, 3), type=type, **kw))

    def pop(self, sel, t, sound="pop", **kw):
        self.j(f'pop("{sel}", {t});')
        if sound:
            self.cue(t + (0.42 if sound == "thud" else 0.05), sound, **kw)

    def origin(self, sel, o):
        self.origins.append(f'gsap.set("{sel}", {{ transformOrigin: "{o}" }});')

    def write(self):
        sid = self.id
        cam = f"#{sid}-cam"
        drift = f"#{sid}-drift"
        D = self.dur
        cam_from = "scale: 1.08, y: 0, opacity: 1" if self.first else "scale: 0.9, y: 80, opacity: 0"
        head = [
            f'tl.fromTo("{cam}", {{ {cam_from} }}, {{ scale: 1, y: 0, opacity: 1, duration: 0.45, ease: "back.out(1.6)" }}, 0);',
            f'tl.fromTo("{drift}", {{ y: 0 }}, {{ y: -30, duration: {D}, ease: "sine.inOut" }}, 0);',
        ]
        if self.exit:
            head.append(f'tl.to("{cam}", {{ scale: 1.14, y: -40, opacity: 0, duration: 0.3, ease: "power2.in" }}, {round(D - 0.32, 2)});')
            self.cue(D - 0.4, "whoosh", dur=0.45, gain=0.45)
        js = "\n".join("  " + h for h in head) + "\n" + "\n".join(self.js)
        org = "\n".join("  " + o for o in self.origins)
        doc = f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}">
    <div id="{sid}-cam" class="cam"><div id="{sid}-drift" class="cam">
{chr(10).join(self.html)}
    </div></div>
  </div>
  <script>
  (function () {{
{JS_HELPERS}
{org}
{js}
  window.__timelines["{sid}"] = tl;
  }})();
  </script>
</template>
'''
        with open(os.path.join(ROOT, "compositions", f"{sid}.html"), "w") as f:
            f.write(doc)


def std_origins(sc, ids_body, ids_eyes, ids_pop):
    for i in ids_body:
        sc.origin(f"#{i}-b", "50% 100%")
    for i in ids_eyes:
        sc.origin(f"#{i}-eyes", "50% 50%")
    for i in ids_pop:
        sc.origin(f"#{i}", "50% 100%")


SCENES = []

# ---------------------------------------------------------------- scene 1  (0.0 - 5.5)
s = Scene("s1", 0.0, 5.5, first=True)
s.add(flame("s1-elder", 360, 600, 360, CYAN))
s.add(f'''<div id="s1-tag" class="obj" {box(110, 430, 190, 130)}><svg class="body" viewBox="0 0 190 130">
  <rect x="0" y="0" width="190" height="130" rx="22" fill="#FFFFFF"/><rect class="sh" x="120" y="0" width="70" height="130" rx="22" fill="#DCD6F5"/>
  <circle cx="34" cy="65" r="14" fill="#9B6BFF"/><rect x="62" y="40" width="96" height="16" rx="8" fill="#9B6BFF"/>
  <rect x="62" y="74" width="70" height="16" rx="8" fill="#C9B6FF"/></svg></div>''')
s.add(f'''<div id="s1-heart" class="obj" {box(445, 390, 190, 166)}><svg class="glow" viewBox="0 0 300 270"><path d="{HEART}" fill="#FFD23F"/></svg>
  <svg class="body" viewBox="0 0 300 270"><path d="{HEART}" fill="#FFD23F"/><path class="hl" d="{HEART_HL}" fill="#FFF0A0"/><path class="sh" d="{HEART_SH}" fill="#E8A912"/></svg></div>''')
s.add(house("s1-home", 790, 400, 170))
s.add(pip("s1-pip", 70, 1150, 250))
std_origins(s, ["s1-elder", "s1-pip"], ["s1-elder", "s1-pip"], ["s1-elder", "s1-pip", "s1-tag", "s1-home"])
s.origin("#s1-heart", "50% 50%")
s.cue(0.0, "swell", dur=2.2, gain=0.5)
s.j('breathe("#s1-elder-b", 0.0, 5.5, 2.0);')
s.j('flicker("#s1-elder-b", 0.0, 5.5, 0.9);')
s.j('tl.fromTo("#s1-elder-g", { opacity: 0.3 }, { opacity: 0.8, duration: 0.8, ease: "sine.inOut" }, 0.1);')
s.pop("#s1-pip", 0.9, sound="thud", gain=0.4)
s.j('breathe("#s1-pip-b", 1.4, 5.5, 1.6);')
s.pop("#s1-tag", 1.6, pitch=700, gain=0.35)
s.pop("#s1-home", 2.4, pitch=760, gain=0.35)
s.pop("#s1-heart", 3.2, pitch=820, gain=0.4)
s.j('blink("#s1-pip-eyes", 2.0);')
s.j('blink("#s1-elder-eyes", 2.9);')
s.j('tl.to("#s1-tag", { y: -160, opacity: 0, duration: 0.6, ease: "power2.in" }, 3.9);')
s.j('tl.to("#s1-home", { y: -160, opacity: 0, duration: 0.6, ease: "power2.in" }, 4.15);')
s.j('tl.to("#s1-heart", { y: -180, scale: 0.5, opacity: 0, duration: 0.6, ease: "power2.in" }, 4.4);')
s.cue(3.9, "whoosh", dur=1.0, gain=0.3)
s.j('tl.to("#s1-pip-eyes", { scaleY: 0.55, y: 10, duration: 0.3, ease: "power2.out" }, 4.4);')
s.j('tl.to("#s1-elder-g", { opacity: 0.25, duration: 0.6, ease: "sine.inOut" }, 4.4);')
SCENES.append(s)

# ---------------------------------------------------------------- scene 2  (5.5 - 10.5)
s = Scene("s2", 5.5, 5.0)
s.add(f'''<div id="s2-num" class="obj num" {box(0, 400, 1080, 360)}><div class="glow numtxt" data-layout-ignore>13</div><div class="numtxt">13</div></div>''')
s.add(flame("s2-elder", 450, 740, 180, CYAN))
for i, x in enumerate([70, 200, 330]):
    s.add(lantern(f"s2-l{i}", x, 1010 - (20 if i == 1 else 0)))
for i, x in enumerate([590, 720, 850]):
    s.add(house(f"s2-h{i}", x, 1020 - (20 if i == 1 else 0), 140))
s.add(f'''<div id="s2-arrow" class="obj" {box(440, 1050, 150, 90)}><svg class="body" viewBox="0 0 150 90">
  <path d="M0 30 L90 30 L90 4 L150 45 L90 86 L90 60 L0 60 Z" fill="#FF8A3D"/><path class="hl" d="M0 30 L90 30 L90 40 L0 40 Z" fill="#FFC08A"/></svg></div>''')
std_origins(s, ["s2-elder"], ["s2-elder"], ["s2-elder"] + [f"s2-l{i}" for i in range(3)] + [f"s2-h{i}" for i in range(3)])
s.origin("#s2-num", "50% 50%")
s.pop("#s2-num", 0.3, pitch=520, gain=0.65)
s.pop("#s2-elder", 1.4, pitch=600, gain=0.4)
s.j('breathe("#s2-elder-b", 1.9, 5.0, 1.8);')
s.j('flicker("#s2-elder-b", 1.9, 5.0, 0.9);')
s.j('tl.to("#s2-num", { y: -60, scale: 0.55, duration: 0.45, ease: "power2.inOut" }, 2.0);')
s.cue(2.0, "whoosh", dur=0.4, gain=0.3)
for i in range(3):
    s.pop(f"#s2-l{i}", 2.3 + i * 0.1, sound="pop" if i == 0 else None, pitch=480, gain=0.35)
for i in range(3):
    s.pop(f"#s2-h{i}", 2.65 + i * 0.1, sound="pop" if i == 0 else None, pitch=640, gain=0.35)
s.j('tl.to("#s2-elder-eyes", { x: -10, duration: 0.2, ease: "power2.out" }, 2.9);')
s.j('tl.to("#s2-elder-eyes", { x: 10, duration: 0.25, ease: "power2.inOut" }, 3.4);')
s.j('tl.fromTo("#s2-arrow", { x: -140, opacity: 0 }, { x: 0, opacity: 1, duration: 0.35, ease: "power3.in" }, 3.6);')
s.cue(3.6, "whoosh", dur=0.35, gain=0.4)
s.j('tl.fromTo(["#s2-h0", "#s2-h1", "#s2-h2"], { x: -8 }, { x: 8, duration: 0.06, yoyo: true, repeat: 5, ease: "sine.inOut" }, 3.95);')
s.j('tl.to(["#s2-h0", "#s2-h1", "#s2-h2"], { x: 0, duration: 0.06 }, 4.31);')
s.cue(3.95, "thud", gain=0.6)
s.j('tl.to("#s2-elder", { scaleX: 1.08, scaleY: 0.9, duration: 0.1, ease: "power1.out" }, 3.97);')
s.j('tl.to("#s2-elder", { scaleX: 1, scaleY: 1, duration: 0.2, ease: "back.out(2)" }, 4.07);')
SCENES.append(s)

# ---------------------------------------------------------------- scene 3  (10.5 - 15.5)
s = Scene("s3", 10.5, 5.0)
MOON = "M150 20 A130 130 0 1 0 280 170 A100 100 0 1 1 150 20 Z"
s.add(f'''<div id="s3-moon" class="obj" {box(780, 560, 220, 220)}><svg id="s3-moon-g" class="glow" viewBox="0 0 300 300"><path d="{MOON}" fill="#FFF4C2"/></svg>
  <svg class="body" viewBox="0 0 300 300"><path d="{MOON}" fill="#FFF4C2"/><path class="sh" d="M150 280 A130 130 0 0 0 280 170 A100 100 0 0 1 200 240 Z" fill="#F2DC8A"/></svg></div>''')
s.add(f'''<div id="s3-scroll" class="obj" {box(170, 500, 640, 250)}><svg class="body" viewBox="0 0 640 250">
  <rect x="30" y="20" width="580" height="210" fill="#FFF4D6"/><rect class="sh" x="30" y="180" width="580" height="50" fill="#EADBB4"/>
  <rect class="hl" x="30" y="20" width="580" height="24" fill="#FFFFFF"/>
  <rect x="80" y="70" width="300" height="18" rx="9" fill="#C9B6FF"/><rect x="80" y="110" width="250" height="18" rx="9" fill="#C9B6FF"/><rect x="80" y="150" width="280" height="18" rx="9" fill="#C9B6FF"/>
  <rect x="0" y="0" width="40" height="250" rx="20" fill="#5A3AB0"/><rect x="600" y="0" width="40" height="250" rx="20" fill="#5A3AB0"/></svg>
  <svg id="s3-seal" class="body" viewBox="0 0 640 250"><circle cx="500" cy="125" r="62" fill="#9B6BFF"/><circle class="hl" cx="482" cy="104" r="22" fill="#BC9CFF"/>
  <path d="M500 82 L540 125 L500 168 L460 125 Z" fill="#FFD23F"/></svg></div>''')
for i, x in enumerate([60, 250, 440, 630, 820]):
    s.add(lantern(f"s3-l{i}", x, 850 + (0 if i % 2 == 0 else 30)))
s.add(pip("s3-pip", 420, 1150, 240))
std_origins(s, ["s3-pip"], ["s3-pip"], ["s3-pip"] + [f"s3-l{i}" for i in range(5)])
s.origin("#s3-scroll", "50% 50%")
s.origin("#s3-seal", "78% 50%")
s.j('tl.fromTo("#s3-moon", { y: 140 }, { y: 0, duration: 2.0, ease: "sine.out" }, 0.1);')
for i in range(5):
    s.pop(f"#s3-l{i}", 0.3 + i * 0.08, sound="pop" if i == 0 else None, pitch=560, gain=0.35)
s.pop("#s3-pip", 0.6, sound=None)
s.j('breathe("#s3-pip-b", 1.1, 5.0, 1.6);')
s.j('tl.fromTo("#s3-scroll", { scaleX: 0, opacity: 0 }, { scaleX: 1, opacity: 1, duration: 0.45, ease: "back.out(1.6)" }, 0.9);')
s.cue(0.9, "whoosh", dur=0.4, gain=0.4)
s.j('tl.fromTo("#s3-seal", { scale: 2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.2, ease: "power3.in" }, 1.45);')
s.cue(1.65, "thud", gain=0.55)
s.j('tl.to("#s3-scroll", { scaleX: 0, opacity: 0, duration: 0.3, ease: "power2.in" }, 2.35);')
for i in range(5):
    t = 2.7 + i * 0.35
    s.j(f'tl.to("#s3-l{i}-off", {{ opacity: 0.85, duration: 0.25, ease: "power2.in" }}, {t:.2f});')
    s.j(f'tl.to("#s3-l{i}-g", {{ opacity: 0, duration: 0.25, ease: "power2.in" }}, {t:.2f});')
    s.j(f'tl.to("#s3-l{i}", {{ y: 12, duration: 0.25, ease: "power2.in" }}, {t:.2f});')
s.cue(2.7, "rumble", dur=1.9, gain=0.55)
s.j('tl.to("#s3-pip-eyes", { scaleY: 0.12, duration: 0.15, ease: "power2.in" }, 2.75);')
s.j('tl.fromTo("#s3-pip", { x: -4 }, { x: 4, duration: 0.07, yoyo: true, repeat: 17, ease: "sine.inOut" }, 2.9);')
s.j('tl.fromTo("#s3-moon-g", { opacity: 0.6 }, { opacity: 0.95, duration: 0.4, yoyo: true, repeat: 1, ease: "sine.inOut" }, 4.1);')
SCENES.append(s)

# ---------------------------------------------------------------- scene 4  (15.5 - 20.0)
s = Scene("s4", 15.5, 4.5)
for i, x in enumerate([90, 280, 470, 660, 850]):
    s.add(lantern(f"s4-l{i}", x, 410 + (0 if i % 2 == 0 else 24), 100, lit=False))
s.add(flame("s4-elder", 140, 680, 300, CYAN))
s.add(flame("s4-little", 560, 860, 200, YELLOW))
s.add(pip("s4-pip", 820, 1170, 210))
std_origins(s, ["s4-elder", "s4-little", "s4-pip"], ["s4-elder", "s4-little", "s4-pip"], ["s4-elder", "s4-little", "s4-pip"])
s.j('tl.fromTo("#s4-elder", { x: -420 }, { x: 0, duration: 0.5, ease: "power2.out" }, 0.1);')
s.cue(0.1, "whoosh", dur=0.5, gain=0.4)
s.j('breathe("#s4-elder-b", 0.7, 4.5, 2.0);')
s.j('flicker("#s4-elder-b", 0.7, 4.5, 0.9);')
s.pop("#s4-little", 1.3, sound="chime", pitch=880, gain=0.6)
s.cue(1.4, "sparkle", gain=0.4)
s.j('tl.fromTo("#s4-little-g", { opacity: 0.2 }, { opacity: 0.95, duration: 0.5, ease: "sine.inOut" }, 1.5);')
s.j('breathe("#s4-little-b", 1.9, 4.5, 1.4);')
s.j('flicker("#s4-little-b", 1.9, 4.5, 0.9);')
s.j('tl.to("#s4-elder", { rotation: 8, duration: 0.6, ease: "sine.inOut" }, 2.1);')
s.j('tl.to("#s4-elder-eyes", { x: 10, y: 6, duration: 0.3, ease: "power2.out" }, 2.1);')
s.pop("#s4-pip", 2.4, pitch=620, gain=0.3)
s.j('blink("#s4-little-eyes", 2.8);')
s.j('tl.fromTo("#s4-little-gl", { scale: 1 }, { scale: 1.9, duration: 0.2, yoyo: true, repeat: 1, ease: "sine.inOut", transformOrigin: "50% 50%" }, 3.1);')
s.cue(3.1, "tick", gain=0.3)
s.j('tl.to("#s4-pip-eyes", { scaleY: 0.6, duration: 0.25, ease: "power2.out" }, 3.3);')
SCENES.append(s)

# ---------------------------------------------------------------- scene 5  (20.0 - 24.5)
s = Scene("s5", 20.0, 4.5)
s.add(flame("s5-elder", 70, 700, 300, CYAN))
s.add(f'''<div id="s5-crack" class="obj" {box(430, 640, 120, 520)}><svg class="body" viewBox="0 0 120 520">
  <polyline id="s5-crack-l" points="60,0 30,90 86,170 24,270 92,350 40,440 70,520" fill="none" stroke="#FFFFFF" stroke-width="12" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="700" stroke-dashoffset="700"/></svg></div>''')
SPIKES = '<path id="s5-little-spk" d="M50 210 L80 110 L112 180 L150 40 L188 180 L220 110 L250 210 Z" fill="#FF8A3D" opacity="0"/>'
HOT = f'<path id="s5-little-hot" d="{FLAME}" fill="#FF8A3D" opacity="0"/>'
BROWS = '<g id="s5-little-brows" opacity="0"><rect x="92" y="226" width="46" height="12" rx="6" fill="#0B1E4A" transform="rotate(22 115 232)"/><rect x="162" y="226" width="46" height="12" rx="6" fill="#0B1E4A" transform="rotate(-22 185 232)"/></g>'
lit = flame("s5-little", 600, 780, 240, YELLOW, extras=HOT + BROWS)
lit = lit.replace('<svg id="s5-little-b" class="body" viewBox="0 0 300 420">', '<svg id="s5-little-b" class="body" viewBox="0 0 300 420">' + SPIKES)
s.add(lit)
s.add(f'''<div id="s5-meter" class="obj" {box(590, 1186, 380, 40, "border-radius:20px;background:#2A1E5A;overflow:hidden")}>
  <div id="s5-fill" style="position:absolute;inset:0;background:#3DF2A6;border-radius:20px"></div></div>''')
s.add(pip("s5-pip", 130, 1170, 220))
std_origins(s, ["s5-elder", "s5-little", "s5-pip"], ["s5-elder", "s5-little", "s5-pip"], ["s5-little", "s5-pip"])
s.origin("#s5-fill", "0% 50%")
s.origin("#s5-little-spk", "50% 100%")
s.j('breathe("#s5-elder-b", 0.3, 4.5, 2.0);')
s.j('flicker("#s5-elder-b", 0.3, 4.5, 0.9);')
s.j('breathe("#s5-little-b", 0.3, 2.2, 1.4);')
s.j('flicker("#s5-little-b", 0.3, 2.2, 0.9);')
s.pop("#s5-pip", 0.5, pitch=600, gain=0.3)
s.j('tl.to("#s5-elder-eyes", { x: -14, duration: 0.25, ease: "power2.out" }, 0.45);')
s.j('tl.to("#s5-elder", { x: -30, duration: 0.5, ease: "sine.inOut" }, 0.45);')
s.j('tl.to("#s5-crack-l", { strokeDashoffset: 0, duration: 0.25, ease: "power3.in" }, 0.85);')
s.cue(1.1, "thud", gain=0.6)
s.j('tl.to("#s5-pip-eyes", { scale: 1.2, duration: 0.2, ease: "back.out(2)", transformOrigin: "50% 50%" }, 1.15);')
s.j('tl.fromTo("#s5-pip", { rotation: -3 }, { rotation: 3, duration: 0.25, yoyo: true, repeat: 9, ease: "sine.inOut" }, 1.4);')
s.j('tl.to("#s5-little", { scale: 1.35, duration: 0.7, ease: "back.out(1.6)" }, 2.3);')
s.j('tl.to("#s5-little-hot", { opacity: 0.7, duration: 0.6, ease: "sine.inOut" }, 2.3);')
s.j('tl.fromTo("#s5-little-spk", { opacity: 0, scaleY: 0 }, { opacity: 1, scaleY: 1, duration: 0.45, ease: "back.out(1.6)" }, 2.4);')
s.j('tl.to("#s5-little-brows", { opacity: 1, duration: 0.2 }, 2.5);')
s.cue(2.3, "rumble", dur=1.2, gain=0.5)
s.j('tl.fromTo("#s5-fill", { scaleX: 0 }, { scaleX: 1, duration: 1.0, ease: "power2.out" }, 2.6);')
s.cue(3.4, "chime", pitch=990, gain=0.5)
SCENES.append(s)

# ---------------------------------------------------------------- scene 6  (24.5 - 29.0)
s = Scene("s6", 24.5, 4.5)
digits = "".join(f'<span id="s6-d{i}" class="digit" style="opacity:{1 if i == 1 else 0}">{i}</span>' for i in range(1, 9))
s.add(f'''<div id="s6-pill" class="obj pill" {box(290, 390, 500, 140)}><span class="pilltxt">YEAR</span><span class="digits" data-layout-allow-overlap>{digits}</span></div>''')
CLOAK = ('<path d="M150 70 C232 80 288 180 288 300 L288 418 L12 418 L12 300 C12 180 68 80 150 70 Z" fill="#4A2E9A"/>'
         '<path class="hl" d="M120 96 C70 130 44 200 40 290 C56 220 84 160 130 110 Z" fill="#6B4BC4"/>'
         '<path class="sh" d="M288 300 L288 418 L200 418 C240 380 262 330 268 230 C280 250 288 274 288 300 Z" fill="#35207A"/>'
         '<ellipse cx="150" cy="270" rx="86" ry="62" fill="#160F45"/>')
EYES_C = ('<g id="s6-elder-eyes"><ellipse cx="118" cy="270" rx="16" ry="20" fill="#35E0F2"/><ellipse cx="182" cy="270" rx="16" ry="20" fill="#35E0F2"/>'
          '<circle cx="123" cy="262" r="5" fill="#fff"/><circle cx="187" cy="262" r="5" fill="#fff"/></g>')
cl = flame("s6-elder", 150, 610, 340, CYAN, eyes=False, extras=CLOAK + EYES_C)
s.add(cl)
DOTS = [(470, 900), (530, 950), (585, 1000), (635, 1050), (680, 1095), (725, 1130)]
for i, (x, y) in enumerate(DOTS):
    s.add(f'<div id="s6-dot{i}" class="obj dot" {box(x - 11, y - 11, 22, 22)}></div>')
SHIELD = "M20 300 A190 190 0 0 1 400 300 Z"
s.add(f'''<div id="s6-shield" class="obj" {box(595, 990, 420, 330)}><svg id="s6-shield-g" class="glow" viewBox="0 0 420 330"><path d="{SHIELD}" fill="#3DF2A6"/></svg>
  <svg class="body" viewBox="0 0 420 330"><path d="{SHIELD}" fill="#3DF2A6" fill-opacity="0.22" stroke="#3DF2A6" stroke-width="14"/>
  <path class="hl" d="M70 200 A150 150 0 0 1 180 130" fill="none" stroke="#B9FFE0" stroke-width="10" stroke-linecap="round"/></svg></div>''')
for i, x in enumerate([620, 750, 870]):
    s.add(house(f"s6-h{i}", x, 1160 - (20 if i == 1 else 0), 130))
std_origins(s, ["s6-elder"], ["s6-elder"], ["s6-elder", "s6-shield"] + [f"s6-h{i}" for i in range(3)])
s.origin("#s6-pill", "50% 50%")
s.pop("#s6-pill", 0.15, pitch=500, gain=0.4)
for i in range(2, 9):
    t = 0.55 + (i - 1) * 0.2
    s.j(f'tl.set("#s6-d{i - 1}", {{ opacity: 0 }}, {t:.2f});')
    s.j(f'tl.fromTo("#s6-d{i}", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.18, ease: "back.out(2)" }}, {t:.2f});')
s.cue(0.55, "riser", dur=1.4, gain=0.4)
s.cue(1.95, "pop", pitch=880, gain=0.55)
s.j('tl.fromTo("#s6-elder", { x: -80, opacity: 0 }, { x: 0, opacity: 1, duration: 0.5, ease: "power2.out" }, 0.3);')
s.j('breathe("#s6-elder-b", 0.8, 4.5, 2.2);')
s.j('blink("#s6-elder-eyes", 1.2);')
for i in range(3):
    s.pop(f"#s6-h{i}", 1.6 + i * 0.1, sound="pop" if i == 0 else None, pitch=640, gain=0.35)
for i in range(len(DOTS)):
    s.j(f'tl.fromTo("#s6-dot{i}", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.2, ease: "back.out(2)" }}, {2.0 + i * 0.1:.2f});')
s.cue(2.0, "sparkle", dur=0.7, gain=0.3, pitch=1400)
s.j('tl.to("#s6-elder-eyes", { scaleY: 0.45, x: 10, duration: 0.25, ease: "power2.out" }, 2.9);')
s.pop("#s6-shield", 3.6, sound="chime", pitch=784, gain=0.55)
SCENES.append(s)

# ---------------------------------------------------------------- scene 7  (29.0 - 34.0)
s = Scene("s7", 29.0, 5.0)
DIM = f'<path id="s7-elder-dim" d="{FLAME}" fill="#1E2A6A" opacity="0"/>'
s.add(flame("s7-elder", 70, 640, 300, CYAN, extras=DIM))
s.add(flame("s7-little", 700, 640, 260, YELLOW))
s.add(f'''<div id="s7-beat" class="obj" {box(60, 1080, 960, 120)}><svg class="body" viewBox="0 0 960 120">
  <polyline id="s7-beat-l" points="0,60 300,60 340,10 380,110 420,60 600,60 630,28 660,92 690,60 960,60" fill="none" stroke="#3DF2A6" stroke-width="9" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="1300" stroke-dashoffset="1300"/></svg></div>''')
s.add(f'''<div id="s7-burst" class="obj" {box(400, 660, 280, 280)}><svg class="glow" viewBox="0 0 300 300"><path d="{STAR8}" fill="#FFD23F"/></svg>
  <svg class="body" viewBox="0 0 300 300"><path d="{STAR8}" fill="#FFD23F"/><path class="hl" d="M150 0 L176 104 L150 150 L124 104 Z" fill="#FFF0A0"/></svg></div>''')
s.add(f'''<div id="s7-spark" class="obj" {box(200, 760, 70, 70)}><svg class="glow" viewBox="0 0 300 300"><path d="{STAR8}" fill="#A6F7FF"/></svg>
  <svg class="body" viewBox="0 0 300 300"><path d="{STAR8}" fill="#FFFFFF"/></svg></div>''')
s.add(pip("s7-pip", 430, 1195, 205))
std_origins(s, ["s7-elder", "s7-little", "s7-pip"], ["s7-elder", "s7-little", "s7-pip"], ["s7-elder", "s7-little", "s7-pip"])
s.origin("#s7-burst", "50% 50%")
s.origin("#s7-spark", "50% 50%")
s.j('tl.set(["#s7-burst", "#s7-spark"], { opacity: 0 }, 0);')
s.j('breathe("#s7-little-b", 0.3, 5.0, 1.4);')
s.j('flicker("#s7-little-b", 0.3, 5.0, 0.9);')
s.j('tl.to("#s7-beat-l", { strokeDashoffset: 0, duration: 1.2, ease: "none" }, 0.2);')
s.cue(0.5, "pop", pitch=990, gain=0.3)
s.cue(0.95, "pop", pitch=990, gain=0.3)
s.j('tl.to("#s7-elder-dim", { opacity: 0.55, duration: 0.9, ease: "sine.inOut" }, 0.3);')
s.j('tl.to("#s7-elder-g", { opacity: 0.2, duration: 0.9, ease: "sine.inOut" }, 0.3);')
s.j('tl.fromTo("#s7-elder", { rotation: -3 }, { rotation: 3, duration: 0.3, yoyo: true, repeat: 3, ease: "sine.inOut" }, 0.3);')
s.j('tl.to("#s7-elder", { rotation: 0, duration: 0.15 }, 1.5);')
s.j('tl.to("#s7-beat", { opacity: 0.35, duration: 0.4 }, 1.5);')
s.pop("#s7-pip", 0.6, sound=None)
s.j('tl.to("#s7-elder", { x: 130, duration: 0.25, ease: "power3.in" }, 1.7);')
s.j('tl.to("#s7-little", { x: -150, duration: 0.25, ease: "power3.in" }, 1.7);')
s.cue(1.7, "whoosh", dur=0.3, gain=0.45)
s.j('tl.fromTo("#s7-burst", { scale: 0, opacity: 0, rotation: 0 }, { scale: 1, opacity: 1, rotation: 25, duration: 0.25, ease: "back.out(1.6)" }, 1.95);')
s.cue(1.95, "thud", gain=0.75)
s.j('tl.to("#s7-pip-eyes", { scale: 1.25, duration: 0.2, ease: "back.out(2)", transformOrigin: "50% 50%" }, 2.0);')
s.j('tl.to("#s7-elder", { x: 0, duration: 0.35, ease: "power2.out" }, 2.2);')
s.j('tl.to("#s7-little", { x: 0, duration: 0.35, ease: "power2.out" }, 2.2);')
s.j('tl.to("#s7-burst", { scale: 0.4, opacity: 0, duration: 0.25, ease: "power2.in" }, 2.4);')
s.j('tl.fromTo("#s7-spark", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(1.6)" }, 2.75);')
s.j('tl.to("#s7-spark", { x: 280, y: -180, rotation: 90, duration: 0.5, ease: "sine.out" }, 3.05);')
s.j('tl.to("#s7-spark", { x: 567, y: 82, rotation: 180, duration: 0.5, ease: "sine.in" }, 3.55);')
s.j('tl.to("#s7-spark", { scale: 0, duration: 0.15, ease: "power2.in" }, 4.05);')
s.cue(2.65, "riser", dur=1.4, gain=0.5)
s.j('tl.fromTo("#s7-little-gl", { scale: 1 }, { scale: 2.4, duration: 0.25, ease: "back.out(2)", transformOrigin: "50% 50%" }, 4.05);')
s.j('tl.fromTo("#s7-little-g", { opacity: 0.6 }, { opacity: 1, scale: 1.15, duration: 0.3, yoyo: true, repeat: 1, ease: "sine.inOut" }, 4.05);')
s.cue(4.05, "chime", pitch=1046, gain=0.7)
s.cue(4.1, "sparkle", gain=0.45)
SCENES.append(s)

# ---------------------------------------------------------------- scene 8  (34.0 - 40.0)
s = Scene("s8", 34.0, 6.0, exit=False)
DIM8 = f'<path id="s8-elder-dim" d="{FLAME}" fill="#1E2A6A" opacity="0.4"/>'
ARM = '<rect id="s8-elder-arm" x="250" y="250" width="200" height="30" rx="15" fill="#35E0F2"/>'
el = flame("s8-elder", 150, 640, 300, CYAN, extras=DIM8)
el = el.replace('<svg id="s8-elder-b" class="body" viewBox="0 0 300 420">', '<svg id="s8-elder-b" class="body" viewBox="0 0 300 420">' + ARM)
s.add(el)
s.add(flame("s8-little", 470, 770, 220, YELLOW))
s.add(f'<div id="s8-ring" class="obj ring" {box(540, 840, 100, 100)}></div>')
rng = random.Random(21)
PARTS = [(rng.randint(190, 400), rng.randint(720, 1000), rng.randint(-90, 90)) for _ in range(12)]
for i, (x, y, dx) in enumerate(PARTS):
    s.add(f'<div id="s8-p{i}" class="obj spark" {box(x, y, 26, 26)}></div>')
s.add(f'''<div id="s8-heart" class="obj" {box(390, 400, 300, 270)}><svg id="s8-heart-g" class="glow" viewBox="0 0 300 270"><path d="{HEART}" fill="#FFD23F"/></svg>
  <svg class="body" viewBox="0 0 300 270"><path d="{HEART}" fill="#FFD23F"/><path class="hl" d="{HEART_HL}" fill="#FFF0A0"/><path class="sh" d="{HEART_SH}" fill="#E8A912"/>
  <polyline id="s8-crack" points="150,52 128,110 168,150 136,200 150,250" fill="none" stroke="#FFFFFF" stroke-width="12" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="320" stroke-dashoffset="320"/></svg></div>''')
s.add(pip("s8-pip", 810, 1170, 210))
std_origins(s, ["s8-elder", "s8-little", "s8-pip"], ["s8-elder", "s8-little", "s8-pip"], ["s8-elder", "s8-little", "s8-pip"])
s.origin("#s8-heart", "50% 50%")
s.origin("#s8-ring", "50% 50%")
s.origin("#s8-elder-arm", "0% 50%")
s.j('tl.set(["#s8-ring"], { opacity: 0 }, 0);')
for i in range(len(PARTS)):
    s.j(f'tl.set("#s8-p{i}", {{ opacity: 0 }}, 0);')
s.j('tl.fromTo("#s8-elder-arm", { rotation: 60 }, { rotation: 60, duration: 0.01 }, 0);')
s.j('breathe("#s8-elder-b", 0.3, 2.2, 2.0);')
s.j('flicker("#s8-elder-b", 0.3, 2.2, 0.9);')
s.j('breathe("#s8-little-b", 0.3, 6.0, 1.4);')
s.j('flicker("#s8-little-b", 0.3, 6.0, 0.9);')
s.j('tl.to("#s8-elder-arm", { rotation: -6, duration: 0.45, ease: "back.out(1.6)" }, 0.9);')
s.j('tl.to("#s8-little", { scaleX: 1.06, scaleY: 0.92, duration: 0.08, ease: "power1.out" }, 1.35);')
s.j('tl.to("#s8-little", { scaleX: 1, scaleY: 1, duration: 0.18, ease: "back.out(2)" }, 1.43);')
s.j('tl.fromTo("#s8-ring", { scale: 0, opacity: 1 }, { scale: 2.4, opacity: 0, duration: 0.6, ease: "power2.out" }, 1.35);')
s.cue(1.35, "pop", pitch=660, gain=0.5)
s.cue(1.4, "chime", pitch=660, gain=0.4)
s.j('tl.to("#s8-little-eyes", { scale: 1.2, duration: 0.2, ease: "back.out(2)" }, 1.5);')
s.j('tl.to("#s8-elder-arm", { rotation: 60, duration: 0.4, ease: "sine.inOut" }, 1.9);')
s.j('tl.to("#s8-elder", { y: -70, opacity: 0, duration: 1.3, ease: "sine.inOut" }, 2.2);')
for i, (x, y, dx) in enumerate(PARTS):
    t = 2.2 + i * 0.07
    s.j(f'tl.fromTo("#s8-p{i}", {{ opacity: 0, x: 0, y: 0, scale: 0.4 }}, {{ opacity: 1, x: {dx}, y: {-220 - (i % 4) * 40}, scale: 1, duration: 1.1, ease: "sine.out" }}, {t:.2f});')
    s.j(f'tl.to("#s8-p{i}", {{ opacity: 0, duration: 0.4, ease: "power2.in" }}, {t + 1.1:.2f});')
s.cue(2.2, "sparkle", dur=1.0, gain=0.45)
s.cue(2.2, "swell", dur=2.6, gain=0.35, pitch=98)
s.j('tl.to("#s8-little", { x: 60, duration: 0.8, ease: "sine.inOut" }, 2.6);')
s.pop("#s8-pip", 2.6, pitch=600, gain=0.3)
s.j('breathe("#s8-pip-b", 3.1, 6.0, 1.6);')
s.pop("#s8-heart", 3.25, sound="chime", pitch=784, gain=0.65)
s.j('tl.to("#s8-pip-eyes", { scaleY: 0.6, duration: 0.25, ease: "power2.out" }, 3.6);')
s.j('blink("#s8-little-eyes", 4.0);')
s.j('tl.to("#s8-crack", { strokeDashoffset: 0, duration: 0.25, ease: "power3.in" }, 4.75);')
s.j('tl.to("#s8-heart", { scaleX: 1.08, scaleY: 0.92, duration: 0.08, ease: "power1.out" }, 5.0);')
s.j('tl.to("#s8-heart", { scaleX: 1, scaleY: 1, duration: 0.2, ease: "back.out(2)" }, 5.08);')
s.cue(5.0, "thud", gain=0.7)
s.j('tl.fromTo("#s8-heart-g", { opacity: 0.6 }, { opacity: 1, duration: 0.35, yoyo: true, repeat: 1, ease: "sine.inOut" }, 5.25);')
s.cue(5.3, "sparkle", gain=0.4, pitch=1500)
SCENES.append(s)

# ---------------------------------------------------------------- captions
CAPS = [
    (0.3, "IMAGINE GIVING UP"), (1.6, "YOUR *NAME,"), (2.4, "YOUR *HOME,"), (3.2, "YOUR BROTHER'S *LOVE"), (4.3, "TO KEEP HIM *ALIVE."),
    (5.8, "AT JUST *13,"), (6.9, "*ITACHI UCHIHA LEARNED"), (8.0, "HIS CLAN WAS PLANNING"), (8.9, "A *COUP"), (9.5, "AGAINST THEIR OWN VILLAGE."),
    (10.8, "TO STOP A *WAR,"), (11.9, "HE WAS *ORDERED"), (13.0, "TO WIPE OUT"), (13.8, "THE *ENTIRE CLAN"), (14.6, "IN ONE *NIGHT."),
    (15.8, "HE DID IT,"), (16.8, "BUT HE *SPARED"), (17.8, "*ONE BOY:"), (18.6, "HIS LITTLE BROTHER, *SASUKE."),
    (20.3, "THEN HE LET"), (21.1, "SASUKE *HATE HIM,"), (22.3, "SO THAT HATE"), (23.2, "WOULD MAKE HIM *STRONG."),
    (24.8, "FOR *EIGHT YEARS"), (25.9, "HE LIVED AS"), (26.6, "A *CRIMINAL,"), (27.4, "SECRETLY *SPYING"), (28.2, "TO *PROTECT THE VILLAGE."),
    (29.2, "SICK AND *DYING,"), (30.2, "HE STAGED"), (30.8, "ONE *FINAL FIGHT"), (31.8, "AND HID A"), (32.4, "PROTECTIVE *POWER"), (33.2, "IN SASUKE'S *EYE."),
    (34.2, "HE DIED AT *21"), (35.2, "WITH A GENTLE *TAP"), (36.1, "ON HIS BROTHER'S FOREHEAD."), (37.2, "SOMETIMES THE DEEPEST *LOVE"),
    (38.3, "LOOKS EXACTLY LIKE"), (39.0, "*BETRAYAL."),
]
SCENE_ENDS = [5.5, 10.5, 15.5, 20.0, 24.5, 29.0, 34.0, 40.0]
TICK_KEYS = {"13,", "NIGHT.", "21", "BETRAYAL."}


def write_captions():
    groups, js = [], []
    for n, (t, text) in enumerate(CAPS):
        nxt = CAPS[n + 1][0] if n + 1 < len(CAPS) else 40.0
        end = min(nxt, min(e for e in SCENE_ENDS if e > t))
        dur = round(end - t - 0.02, 2)
        spans = []
        for k, w in enumerate(text.split()):
            key = w.startswith("*")
            w = w.lstrip("*")
            spans.append(f'<span id="c{n}w{k}" class="w{" key" if key else ""}">{w}</span>')
            wt = round(t + k * 0.13, 2)
            js.append(f'  tl.fromTo("#c{n}w{k}", {{ opacity: 0, y: 30, scale: 0.5 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(1.6)" }}, {wt});')
            if key and w in TICK_KEYS:
                cues.append(dict(t=round(wt + 0.05, 3), type="tick", gain=0.3))
        groups.append(f'    <div id="cap{n}" class="clip capgroup" data-layout-allow-safe-zone data-start="{t}" data-duration="{dur}"><div id="cap{n}-in" class="capin">{" ".join(spans)}</div></div>')
        if end < 40.0:
            js.append(f'  tl.to("#cap{n}-in", {{ opacity: 0, y: -20, duration: 0.2, ease: "power2.in" }}, {round(end - 0.24, 2)});')
    doc = f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}">
{chr(10).join(groups)}
  </div>
  <script>
  (function () {{
  const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
  window.__timelines["captions"] = tl;
  }})();
  </script>
</template>
'''
    with open(os.path.join(ROOT, "compositions", "captions.html"), "w") as f:
        f.write(doc)


# ---------------------------------------------------------------- index / background
def stars_svg(id, n, seed, rmin, rmax, colors, h, twinkle=0):
    r = random.Random(seed)
    out = []
    for i in range(n):
        x, y = r.randint(0, W), r.randint(0, h)
        rad = round(r.uniform(rmin, rmax), 1)
        c = r.choice(colors)
        tid = f' id="{id}-t{i}"' if i < twinkle else ""
        out.append(f'<circle{tid} cx="{x}" cy="{y}" r="{rad}" fill="{c}"/>')
    return f'<svg id="{id}" class="layer" viewBox="0 0 {W} {h}" style="height:{h}px">{"".join(out)}</svg>'


def write_index():
    blocking = '\n    <link rel="stylesheet" href="assets/blocking.css" />' if BLOCKING else ""
    hosts = []
    for s in SCENES:
        hosts.append(f'''      <div id="{s.id}" data-composition-id="{s.id}" data-composition-src="compositions/{s.id}.html" data-start="{s.start}" data-duration="{s.dur}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:2"></div>''')
    audio = '\n      <audio id="sfx" src="assets/sfx.wav" class="clip" data-start="0" data-duration="40" data-track-index="5" data-volume="1"></audio>' if SOUND else ""
    tw = []
    for i in range(10):
        p = 1.2 + (i % 4) * 0.35
        n = int(40 / p) - 1
        tw.append(f'      tl.fromTo("#far-t{i}", {{ opacity: 1 }}, {{ opacity: 0.2, duration: {p:.2f}, yoyo: true, repeat: {n}, ease: "sine.inOut" }}, {i * 0.23:.2f});')
    doc = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <link rel="stylesheet" href="assets/style.css" />{blocking}
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #0B1E4A; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="40" data-width="{W}" data-height="{H}">
      <div id="sky" class="clip" data-start="0" data-duration="40" data-track-index="0" data-layout-ignore style="z-index:1">
        <div id="sky-grad"></div>
        <div id="horizon"></div>
        <div id="far-wrap" class="depth">{stars_svg("far", 90, 3, 1.2, 3.2, ["#FFFFFF", "#FFF4C2", "#A6F7FF"], 2000, twinkle=10)}</div>
        <div id="mid-wrap" class="depth">{stars_svg("mid", 26, 5, 4, 9, ["#9B6BFF", "#35E0F2", "#5B3FD6"], 2100)}</div>
      </div>
{chr(10).join(hosts)}
      <div id="near" class="clip depth" data-start="0" data-duration="40" data-track-index="2" data-layout-ignore style="z-index:3">{stars_svg("near-s", 12, 9, 6, 13, ["#A6F7FF", "#FFF4C2", "#BC9CFF"], 2500)}</div>
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="40" data-track-index="3" data-track-kind="captions" data-width="{W}" data-height="{H}" style="z-index:4"></div>{audio}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#far", {{ y: 0 }}, {{ y: -48, duration: 40, ease: "none" }}, 0);
      tl.fromTo("#mid", {{ y: 0 }}, {{ y: -112, duration: 40, ease: "none" }}, 0);
      tl.fromTo("#near-s", {{ y: 0 }}, {{ y: -480, duration: 40, ease: "none" }}, 0);
      tl.fromTo("#mid", {{ x: -10 }}, {{ x: 10, duration: 5, yoyo: true, repeat: 7, ease: "sine.inOut" }}, 0);
      tl.fromTo("#near-s", {{ x: 20 }}, {{ x: -20, duration: 4, yoyo: true, repeat: 9, ease: "sine.inOut" }}, 0);
{chr(10).join(tw)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(doc)


for sc in SCENES:
    sc.write()
write_captions()
write_index()
# keep the mix readable: drop the quietest small cues (<= 0.3 pops/ticks that sit within 0.6 s of a louder cue)
def crowded(c):
    if c["type"] not in ("pop", "tick") or c.get("gain", 0.5) > 0.3:
        return False
    return any(o is not c and abs(o["t"] - c["t"]) < 0.6 and o.get("gain", 0.5) > c.get("gain", 0.5) for o in cues)
cues[:] = [c for c in cues if not crowded(c)]
# secondary layers dropped so the 3-4 big moments stand out (skill: 20-35 cues per 40 s)
DROP = {(1.65, "pop"), (2.45, "pop"), (7.5, "whoosh"), (8.2, "pop"), (16.9, "sparkle"), (17.95, "pop"), (18.6, "tick"),
        (24.7, "pop"), (26.15, "pop"), (26.5, "sparkle"), (29.95, "pop"), (33.1, "sparkle"), (34.64, "tick"),
        (35.4, "chime"), (39.3, "sparkle")}
cues[:] = [c for c in cues if (round(c["t"], 2), c["type"]) not in DROP]
cues.sort(key=lambda c: c["t"])
with open(os.path.join(ROOT, "cues.json"), "w") as f:
    json.dump({"duration": 40.0, "bed": {"gain": 0.10, "note": 55}, "cues": cues}, f, indent=1)
print(f"wrote {len(SCENES)} scenes, {len(CAPS)} caption groups, {len(cues)} cues; blocking={BLOCKING} sound={SOUND}")
