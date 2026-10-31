import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from timeline import BAR, DURATION, EXIT_BAR, FPS, LEAD_FRAMES, SECTIONS, kick_times  # noqa: E402

W = int(sys.argv[1]) if len(sys.argv) > 1 else 1920
H = int(sys.argv[2]) if len(sys.argv) > 2 else 1080
OUT = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).resolve().parent / "build" / f"video_{W}x{H}.mp4"
ONLY = [int(a) for a in sys.argv[4:]]
FRAMES = int(round(DURATION * FPS))
T_EXIT = EXIT_BAR * BAR
FOCAL = 0.62 * min(W, H)
CX, CY = W / 2, H * (0.46 if W > H else 0.40)
S = min(W, H) / 1080

INK = np.array([20, 32, 46], np.float32)
INK_T = (20, 32, 46)
SIGNAL = (217, 72, 15)
MINT = (159, 224, 201)
AMBER = (242, 178, 122)
TEAL = (11, 110, 97)
STEEL = (150, 170, 190)

FD = Path("/usr/share/fonts/truetype/liberation")
F_HERO = ImageFont.truetype(str(FD / "LiberationSans-Bold.ttf"), int((104 if W > H else 92) * S))
F_MONO = ImageFont.truetype(str(FD / "LiberationMono-Bold.ttf"), int((92 if W > H else 78) * S))
F_SUB = ImageFont.truetype(str(FD / "LiberationSans-Regular.ttf"), int(44 * S))
F_KICK = ImageFont.truetype(str(FD / "LiberationSans-Bold.ttf"), int(28 * S))

RNG = np.random.default_rng(1404)
SEG_GAP, SIDES, RADIUS, N_SEG = 4.0, 8, 3.0, 400
SEG_MISSING = RNG.random((N_SEG, SIDES)) < 0.27
SEG_LIGHT = RNG.random(N_SEG) < 0.22
SEG_LIGHT_V = RNG.integers(0, SIDES, N_SEG)
SEG_STRUT = RNG.random((N_SEG, SIDES)) < 0.35
DEB = np.stack([RNG.uniform(-2.6, 2.6, 260), RNG.uniform(-2.6, 2.6, 260), RNG.uniform(0, 64, 260)], 1)
STARS = np.stack([RNG.uniform(0, W, 900), RNG.uniform(0, H, 900), RNG.uniform(0.15, 1.0, 900)], 1)

_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_rr = np.sqrt(((_xx - CX) / (0.75 * max(W, H))) ** 2 + ((_yy - CY) / (0.75 * max(W, H))) ** 2)
VIGNETTE = np.clip(1.15 - _rr ** 1.6, 0.18, 1.0)[..., None].astype(np.float32)
del _yy, _xx, _rr
GRAIN = [np.random.default_rng(9000 + i).normal(0, 3.0, (H, W, 1)).astype(np.float32) for i in range(4)]
KICKS_VISUAL = np.array(kick_times()) - LEAD_FRAMES / FPS


def z_cam(t):
    return 6.0 * t + 5.0 * t * t / T_EXIT


Z_END = z_cam(T_EXIT) + 2.0


def pulse(t):
    past = KICKS_VISUAL[KICKS_VISUAL <= t]
    return 0.0 if len(past) == 0 else math.exp(-(t - past[-1]) / 0.09)


JIT = [0.0, 0.0]


def jitter(t, p):
    fade = max(0.0, 1.0 - max(0.0, t - T_EXIT) / 0.6)
    jx = 0.0042 * W * (math.sin(2 * math.pi * 0.37 * t) + 0.6 * math.sin(2 * math.pi * 0.83 * t + 1.0))
    jy = -0.0085 * H * p + 0.0025 * H * math.sin(2 * math.pi * 0.51 * t + 2.0)
    return jx * fade, jy * fade


def project(x, y, dz, zoom):
    k = FOCAL * zoom / dz
    return CX + JIT[0] + x * k, CY + JIT[1] + y * k


def fog(dz):
    return max(0.0, min(1.0, 1.0 - dz / 52.0)) ** 1.3


def mix(c, a):
    return tuple(int(INK_T[i] + (c[i] - INK_T[i]) * a) for i in range(3))


def draw_space(d, t):
    reveal = min(1.0, 0.25 + max(0.0, t - T_EXIT + 1.2))
    for x, y, b in STARS:
        d.point(((x + t * 4 * b) % W, y), fill=mix((230, 238, 246), b * reveal))
    if t > T_EXIT - 1.5:
        a = min(1.0, (t - (T_EXIT - 1.5)) / 1.8)
        r = 1.35 * max(W, H)
        ex, ey = CX, H + r * 0.82 - a * 0.12 * H
        for col, grow, k in ((MINT, 1.012, 0.35), (TEAL, 1.0, 0.9)):
            rr = r * grow
            d.ellipse((ex - rr, ey - rr, ex + rr, ey + rr), fill=mix(col, a * k))


def draw_station(d, t, zoom, p):
    zc = z_cam(t)
    first = int(zc // SEG_GAP) + 1
    roll = 0.16 * t
    segs = []
    for i in range(first, first + 15):
        z = i * SEG_GAP
        if z > Z_END:
            break
        dz = z - zc
        if dz < 0.35:
            continue
        a0 = roll + i * 0.035
        pts = [project(RADIUS * math.cos(a0 + 2 * math.pi * k / SIDES), RADIUS * math.sin(a0 + 2 * math.pi * k / SIDES), dz, zoom) for k in range(SIDES)]
        segs.append((i, dz, pts))
    for idx in range(len(segs) - 1, -1, -1):
        i, dz, pts = segs[idx]
        a = fog(dz)
        wdt = max(1, int(7 * S * 2.2 / dz))
        if idx + 1 < len(segs):
            nxt = segs[idx + 1][2]
            for k in range(SIDES):
                if SEG_STRUT[i % N_SEG, k]:
                    d.line((pts[k], nxt[k]), fill=mix(STEEL, a * 0.45), width=max(1, wdt // 2))
        col = mix(STEEL, a * 0.95)
        for k in range(SIDES):
            if not SEG_MISSING[i % N_SEG, k]:
                d.line((pts[k], pts[(k + 1) % SIDES]), fill=col, width=wdt)
        if SEG_LIGHT[i % N_SEG]:
            lx, ly = pts[SEG_LIGHT_V[i % N_SEG]]
            rad = max(2, 26 * S / dz) * (1 + 0.35 * p)
            d.ellipse((lx - rad, ly - rad, lx + rad, ly + rad), fill=mix(SIGNAL, a * (0.55 + 0.45 * p)))


def draw_debris(d, t, zoom):
    if t > T_EXIT + 0.4:
        return
    zc, zp = z_cam(t), z_cam(max(0.0, t - 1.0 / 45))
    for x, y, z0 in DEB:
        z = z0 + (zc // 64) * 64
        if z < zc + 0.4:
            z += 64
        dz, dzp = z - zc, z - zp
        p1 = project(x, y, dz, zoom)
        p0 = project(x, y, max(dzp, dz + 0.01), zoom)
        d.line((p0, p1), fill=mix((205, 215, 226), fog(dz) * 0.9), width=max(1, int(3 * S * 2 / dz)))


def text_layer(img, t):
    cur = None
    for s in SECTIONS:
        if t >= s["bar"] * BAR - LEAD_FRAMES / FPS:
            cur = s
    if cur is None:
        return
    t0 = cur["bar"] * BAR - LEAD_FRAMES / FPS
    a = min(1.0, (t - t0) * FPS / 5.0)
    if cur["bar"] < EXIT_BAR:
        a *= min(1.0, max(0.0, (t0 + 2 * BAR - 0.05 - t) * FPS / 4.0))
    if a <= 0:
        return
    hero_font = F_MONO if ("$" in cur["hero"] or cur["hero"][0].islower()) else F_HERO
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    x = int(0.07 * W)
    y0 = int(H * (0.62 if W > H else 0.66))
    kicker = cur["kicker"] + ("  ·  " + cur["meme"] if cur.get("meme") else "")
    kb = od.textbbox((0, 0), kicker, font=F_KICK)
    hb = od.textbbox((0, 0), cur["hero"], font=hero_font)
    sb = od.textbbox((0, 0), cur["sub"], font=F_SUB)
    limit = W - 2 * x
    if hb[2] > limit:
        hero_font = ImageFont.truetype(hero_font.path, int(hero_font.size * limit / hb[2]))
        hb = od.textbbox((0, 0), cur["hero"], font=hero_font)
    sub_font = F_SUB
    if sb[2] > limit:
        sub_font = ImageFont.truetype(F_SUB.path, int(F_SUB.size * limit / sb[2]))
        sb = od.textbbox((0, 0), cur["sub"], font=sub_font)
    gap1, gap2 = int(22 * S), int(26 * S)
    total = (kb[3] - kb[1]) + gap1 + (hb[3] - hb[1]) + gap2 + (sb[3] - sb[1])
    width = max(kb[2], hb[2], sb[2]) + int(56 * S)
    pad = int(28 * S)
    od.rectangle((x - pad, y0 - pad, x - pad + width, y0 + total + pad), fill=(10, 16, 24, int(205 * a)))
    od.rectangle((x - pad, y0 - pad, x - pad + int(8 * S), y0 + total + pad), fill=SIGNAL + (int(255 * a),))
    dx = int((1 - a) * 24 * S)
    od.text((x + dx, y0 - kb[1]), kicker, font=F_KICK, fill=AMBER + (int(255 * a),))
    yh = y0 + (kb[3] - kb[1]) + gap1
    od.text((x + dx, yh - hb[1]), cur["hero"], font=hero_font, fill=(246, 248, 250, int(255 * a)))
    ys = yh + (hb[3] - hb[1]) + gap2
    od.text((x + dx, ys - sb[1]), cur["sub"], font=sub_font, fill=MINT + (int(255 * a),))
    img.alpha_composite(ov)


def frame(n):
    t = n / FPS
    p = pulse(t) if t < T_EXIT else 0.0
    zoom = 1.0 + 0.025 * p
    JIT[0], JIT[1] = jitter(t, pulse(t))
    img = Image.new("RGB", (W, H), INK_T)
    d = ImageDraw.Draw(img)
    draw_space(d, t)
    draw_station(d, t, zoom, p)
    draw_debris(d, t, zoom)
    rgba = img.convert("RGBA")
    text_layer(rgba, t)
    arr = np.asarray(rgba.convert("RGB"), dtype=np.float32)
    arr = arr * np.minimum(1.0, VIGNETTE * (1.0 + 0.05 * p)) + GRAIN[n % len(GRAIN)]
    arr = INK + (arr - INK) * min(1.0, t / 0.6)
    return np.clip(arr, 0, 255).astype(np.uint8)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if ONLY:
        for n in ONLY:
            Image.fromarray(frame(n)).save(OUT.parent / f"still_{W}x{H}_{n:04d}.png")
        print("stills", ONLY)
        return
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-threads", "2", "-x264-params", "rc-lookahead=10",
           "-crf", "21", "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(FRAMES):
        proc.stdin.write(frame(n).tobytes())
        if n % 60 == 0:
            print("frame", n, "/", FRAMES, flush=True)
    proc.stdin.close()
    rc = proc.wait()
    print("done" if rc == 0 else f"ffmpeg exit {rc}", OUT, flush=True)
    sys.exit(rc)


if __name__ == "__main__":
    main()
