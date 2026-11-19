#!/usr/bin/env python3
"""Make a sound-effects track for an explainer animation. Standard library only.

  python3 sfx.py cues.json assets/sfx.wav

cues.json:
  {"duration": 40.0,
   "bed": {"gain": 0.10, "note": 55},            # optional soft space drone under everything
   "cues": [{"t": 0.40, "type": "whoosh", "dur": 0.5, "gain": 0.6},
            {"t": 1.20, "type": "pop", "pitch": 660},
            {"t": 6.00, "type": "riser", "dur": 1.5}]}

Types: whoosh, pop, tick, chime, thud, rumble, riser, sparkle, swell.
Every cue sits on a visible action: t is the frame where the action lands
(for whoosh / riser / swell, t is where it STARTS; a riser ends on the action).
The same cues.json always gives the same file (seeded noise).
"""
import json
import math
import random
import struct
import sys
import wave

SR = 44100
TAU = 2 * math.pi


def env(i, n, attack, release):
    """0..1 envelope: linear attack, exponential-ish release, both in samples."""
    if i < attack:
        return i / max(1, attack)
    left = n - i
    if left < release:
        return (left / max(1, release)) ** 1.6
    return 1.0


def noise_sweep(rng, n, f0, f1, q=0.25):
    """White noise through a one-pole low-pass whose cutoff glides f0 -> f1, minus its own
    slow part (a rough band-pass): reads as air moving."""
    out, lp, slow = [], 0.0, 0.0
    for i in range(n):
        k = i / max(1, n - 1)
        f = f0 * (f1 / f0) ** k
        a = 1 - math.exp(-TAU * f / SR)
        b = 1 - math.exp(-TAU * f * q / SR)
        x = rng.uniform(-1, 1)
        lp += a * (x - lp)
        slow += b * (lp - slow)
        out.append(lp - slow)
    return out


def whoosh(rng, c):
    n = int(SR * c.get("dur", 0.45))
    up = c.get("up", True)
    f0, f1 = (300, 3200) if up else (3200, 300)
    s = noise_sweep(rng, n, f0, f1)
    return [2.2 * v * math.sin(math.pi * i / n) ** 1.5 for i, v in enumerate(s)]


def pop(rng, c):
    n = int(SR * c.get("dur", 0.12))
    p = c.get("pitch", 520)
    out, ph = [], 0.0
    for i in range(n):
        k = i / n
        ph += TAU * p * (1.6 - 0.9 * k) / SR
        out.append(math.sin(ph) * env(i, n, 30, n * 0.8) * (1 - k) ** 1.2)
    return out


def tick(rng, c):
    n = int(SR * 0.035)
    p = c.get("pitch", 2400)
    return [0.7 * (math.sin(TAU * p * i / SR) + 0.3 * rng.uniform(-1, 1)) * (1 - i / n) ** 3 for i in range(n)]


def chime(rng, c):
    n = int(SR * c.get("dur", 1.1))
    p = c.get("pitch", 880)
    parts = [(1.0, 1.0, 4.0), (2.01, 0.45, 6.0), (3.02, 0.22, 9.0), (4.2, 0.10, 12.0)]
    out = []
    for i in range(n):
        t = i / SR
        v = sum(a * math.sin(TAU * p * r * t) * math.exp(-d * t) for r, a, d in parts)
        out.append(0.55 * v * min(1.0, i / 60))
    return out


def thud(rng, c):
    n = int(SR * c.get("dur", 0.35))
    p = c.get("pitch", 70)
    out, ph = [], 0.0
    for i in range(n):
        t = i / SR
        ph += TAU * (p + 90 * math.exp(-40 * t)) / SR
        click = rng.uniform(-1, 1) * math.exp(-400 * t) * 0.25
        out.append((math.sin(ph) * math.exp(-11 * t) + click) * min(1.0, i / 40))
    return out


def rumble(rng, c):
    n = int(SR * c.get("dur", 1.6))
    s = noise_sweep(rng, n, 90, 60, q=0.4)
    return [6.0 * v * env(i, n, n * 0.25, n * 0.5) for i, v in enumerate(s)]


def riser(rng, c):
    n = int(SR * c.get("dur", 1.4))
    s = noise_sweep(rng, n, 400, 6000)
    out, ph = [], 0.0
    for i, v in enumerate(s):
        k = i / n
        ph += TAU * (180 * 2 ** (2.0 * k)) / SR
        out.append((1.8 * v + 0.25 * math.sin(ph)) * k ** 2 * (1.0 if k < 0.985 else (1 - k) / 0.015))
    return out


def sparkle(rng, c):
    n = int(SR * c.get("dur", 0.7))
    out = [0.0] * n
    for j in range(7):
        st = int(n * 0.6 * j / 7)
        p = c.get("pitch", 1800) * rng.choice([1, 1.25, 1.5, 2, 2.5])
        m = min(n - st, int(SR * 0.22))
        for i in range(m):
            t = i / SR
            out[st + i] += 0.3 * math.sin(TAU * p * t) * math.exp(-18 * t) * min(1.0, i / 30)
    return out


def swell(rng, c):
    n = int(SR * c.get("dur", 2.0))
    p = c.get("pitch", 110)
    out = []
    for i in range(n):
        t = i / SR
        v = sum(math.sin(TAU * p * r * t + r) / (j + 1) for j, r in enumerate((1, 1.5, 2, 3)))
        out.append(0.3 * v * math.sin(math.pi * i / n) ** 2)
    return out


MAKERS = dict(whoosh=whoosh, pop=pop, tick=tick, chime=chime, thud=thud, rumble=rumble,
              riser=riser, sparkle=sparkle, swell=swell)


def bed(n, note, gain):
    """A slow two-note space drone, fading in and out."""
    out = []
    for i in range(n):
        t = i / SR
        lfo = 0.75 + 0.25 * math.sin(TAU * 0.09 * t)
        v = (math.sin(TAU * note * t) + 0.5 * math.sin(TAU * note * 1.498 * t + 1.0)
             + 0.3 * math.sin(TAU * note * 2.003 * t + 2.0))
        fade = min(1.0, t / 1.5, (n - i) / (SR * 1.5))
        out.append(gain * 0.5 * v * lfo * fade)
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    spec = json.load(open(sys.argv[1]))
    total = int(SR * float(spec["duration"]))
    b = spec.get("bed")
    mix = bed(total, b.get("note", 55), b.get("gain", 0.1)) if b else [0.0] * total
    rng = random.Random(7)
    for c in spec.get("cues", []):
        make = MAKERS.get(c["type"])
        if not make:
            sys.exit("unknown cue type: %s (use %s)" % (c["type"], ", ".join(sorted(MAKERS))))
        s = make(rng, c)
        g = c.get("gain", 0.5)
        st = int(SR * c["t"])
        for i, v in enumerate(s):
            if 0 <= st + i < total:
                mix[st + i] += g * v
    peak = max(1e-9, max(abs(v) for v in mix))
    k = min(1.0, 0.89 / peak)  # never clip; never boost
    with wave.open(sys.argv[2], "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for v in mix:
            x = int(max(-1.0, min(1.0, v * k)) * 32767)
            frames += struct.pack("<hh", x, x)
        w.writeframes(bytes(frames))
    print("wrote %s  %.1f s  %d cues  peak %.2f" % (sys.argv[2], total / SR, len(spec.get("cues", [])), peak * k))


if __name__ == "__main__":
    main()
