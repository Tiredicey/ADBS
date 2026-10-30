import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from timeline import BAR, BARS, DURATION, EXIT_BAR, SR, chord_for_bar, cue_sheet, kick_times  # noqa: E402

RNG = np.random.default_rng(140)
N = int(DURATION * SR)
T = np.arange(N) / SR


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def adsr(n, a, d, s, r):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    hold = max(n - a - d - r, 0)
    return np.concatenate([np.linspace(0, 1, a, False), np.linspace(1, s, d, False), np.full(hold, s), np.linspace(s, 0, r)])[:n]


def filt(x, kind, hz):
    return sosfilt(butter(2, hz, kind, fs=SR, output="sos"), x)


def add(buf, sig, start):
    i = int(round(start * SR))
    j = min(len(buf), i + len(sig))
    if i < j:
        buf[i:j] += sig[: j - i]


def thump(f0, f1, length, decay):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 38)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * decay) * (1 - np.exp(-t * 900))


def heartbeat():
    out = np.zeros(int(0.5 * SR))
    lub = thump(150, 48, 0.32, 13)
    n_click = int(0.006 * SR)
    lub[:n_click] += filt(RNG.standard_normal(n_click), "high", 2500) * np.linspace(1, 0, n_click) * 0.12
    dub = thump(120, 55, 0.24, 17) * 0.55
    out[: len(lub)] += lub
    off = int(0.135 * SR)
    out[off: off + len(dub)] += dub
    return out


def pad(notes, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for m in notes:
        for cents in (-7, 0, 7):
            f = mtof(m) * 2 ** (cents / 1200)
            sig += 2 * ((t * f + RNG.random()) % 1.0) - 1
    return filt(sig / (len(notes) * 3), "low", 1400) * adsr(n, 0.35, 0.3, 0.8, 0.4)


def comb_reverb(x, mix):
    wet = np.zeros_like(x)
    for d in (0.0297, 0.0371, 0.0411, 0.0437):
        k = int(d * SR)
        y = x.copy()
        for _ in range(6):
            y = np.concatenate([np.zeros(k), y[:-k]]) * 0.78 + x
        wet += y
    return x * (1 - mix) + filt(wet / 4, "low", 5000) * mix * 0.35


def build():
    kick, pads, sub, hits = (np.zeros(N) for _ in range(4))
    hb = heartbeat()
    for t0 in kick_times():
        add(kick, hb * (0.55 if t0 < 2 * BAR else 0.85), t0)
    for b in range(BARS):
        notes = chord_for_bar(b)[1]
        length = BAR + (1.0 if b == BARS - 1 else 0.5)
        add(pads, pad(notes, length) * (0.5 if b < 2 else 0.7), b * BAR)
        n = int(length * SR)
        add(sub, np.sin(2 * np.pi * mtof(notes[0] - 24) * np.arange(n) / SR) * adsr(n, 0.05, 0.2, 0.85, 0.4) * 0.35, b * BAR)
    noise = RNG.standard_normal(N)
    sweep = 0.5 + 0.5 * np.sin(2 * np.pi * T / (4 * BAR) - np.pi / 2)
    air = filt(filt(noise, "high", 300), "low", 1200) * (0.10 + 0.06 * sweep) + filt(filt(noise, "high", 1500), "low", 7000) * (0.03 + 0.05 * sweep)
    air = filt(air * np.clip(T / 1.5, 0, 1), "low", 7500)
    end = EXIT_BAR * BAR
    rest = DURATION - end
    tt = np.arange(int(rest * SR)) / SR
    shimmer = sum(np.sin(2 * np.pi * mtof(m + 12) * tt) for m in (62, 65, 69)) / 3 * np.exp(-tt * 0.9) * 0.18
    add(hits, thump(90, 36, rest, 2.2) * 1.2 + shimmer, end)
    rn = int(BAR * SR)
    add(hits, filt(RNG.standard_normal(rn), "high", 900) * np.linspace(0, 1, rn) ** 2 * 0.12, end - BAR)
    duck = np.ones(N)
    k = int(0.22 * SR)
    curve = 1 - 0.45 * np.exp(-np.arange(k) / SR * 14)
    for t0 in kick_times():
        s = int(t0 * SR)
        seg = duck[s: s + k]
        duck[s: s + k] = np.minimum(seg, curve[: len(seg)])
    pads = comb_reverb(pads * duck, 0.3)
    sub *= duck
    lag = int(0.011 * SR)
    left = kick + sub + pads * 0.9 + air + hits
    right = kick + sub + pads + np.concatenate([np.zeros(lag), air[:-lag]]) + hits
    st = np.stack([left, right], axis=1)
    fl = int(0.6 * SR)
    st[-fl:] *= np.linspace(1, 0, fl)[:, None]
    return st / (np.max(np.abs(st)) * 1.12)


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    out = here / "build" / "score_raw.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out, build(), SR, subtype="PCM_24")
    (here / "cue_sheet.json").write_text(json.dumps(cue_sheet(), indent=1))
    print("wrote", out, round(DURATION, 3), "s")
