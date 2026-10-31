"""Measure reference videos the same way: cuts, motion, flashes, palette, loudness, tempo.

  python3 tools/teardown.py out.json video1.mp4 [video2.mp4 ...]
Low-resolution decodes keep memory under ~300 MB.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(f):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate", "-of", "json", str(f)])
    return json.loads(r.stdout)


def scene_cuts(f, thr=0.3):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-threads", "2", "-i", str(f), "-vf", f"scale=320:-2,select='gt(scene,{thr})',showinfo", "-an", "-f", "null", "-"])
    return [float(m) for m in re.findall(r"pts_time:([\d.]+)", r.stderr)]


def frames(f, fps, w, gray):
    fmt = "gray" if gray else "rgb24"
    vf = f"fps={fps},scale={w}:-2,format={fmt}"
    info = probe(f)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    h = int(round(v["height"] * w / v["width"] / 2) * 2)
    r = subprocess.run(["ffmpeg", "-v", "error", "-threads", "2", "-i", str(f), "-vf", vf, "-f", "rawvideo", "-"], capture_output=True)
    ch = 1 if gray else 3
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w, ch) if not gray else np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w)


def flashes(lum, fps):
    mean = lum.reshape(len(lum), -1).mean(1) / 255
    d = np.diff(mean)
    ev = np.where(np.abs(d) > 0.10)[0]
    worst = 0
    for i in range(len(mean)):
        worst = max(worst, len(ev[(ev >= i) & (ev < i + fps)]) // 2)
    return int(worst), float(np.abs(d).max())


def palette(rgb, k=6, seed=0):
    px = rgb.reshape(-1, 3).astype(np.float32)
    rng = np.random.default_rng(seed)
    px = px[rng.choice(len(px), min(len(px), 60000), replace=False)]
    c = px[rng.choice(len(px), k, replace=False)]
    for _ in range(25):
        lab = np.argmin(((px[:, None, :] - c[None]) ** 2).sum(2), 1)
        c = np.array([px[lab == j].mean(0) if np.any(lab == j) else c[j] for j in range(k)])
    share = np.bincount(lab, minlength=k) / len(lab)
    order = np.argsort(-share)
    return [{"hex": "%02X%02X%02X" % tuple(int(v) for v in c[j]), "share": round(float(share[j]), 3)} for j in order]


def loudness(f):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"])
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", tail)
    tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail)
    return (float(i.group(1)) if i else None, float(tp.group(1)) if tp else None)


def tempo(f):
    import librosa
    wav = Path("/tmp/_td.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-ac", "1", "-ar", "22050", str(wav)])
    y, sr = librosa.load(str(wav), sr=22050, mono=True)
    t, _ = librosa.beat.beat_track(y=y, sr=sr)
    wav.unlink(missing_ok=True)
    return round(float(np.atleast_1d(t)[0]), 1)


def main(out, files):
    rows = {}
    for f in files:
        f = Path(f)
        info = probe(f)
        dur = float(info["format"]["duration"])
        cuts = scene_cuts(f)
        lum = frames(f, 24, 160, True)
        motion = np.abs(np.diff(lum.astype(np.int16), axis=0)).reshape(len(lum) - 1, -1).mean(1)
        fl, jump = flashes(lum, 24)
        del lum
        rgb = frames(f, 2, 96, False)
        sat = rgb.max(3).astype(np.float32) - rgb.min(3)
        rows[f.name] = {
            "duration_s": round(dur, 2),
            "video": [{k: s.get(k) for k in ("codec_name", "width", "height", "r_frame_rate")} for s in info["streams"] if s["codec_type"] == "video"],
            "scene_cuts_gt_0.3": len(cuts),
            "cuts_per_min": round(len(cuts) / dur * 60, 1),
            "median_shot_s": round(float(np.median(np.diff([0.0] + cuts + [dur]))), 2),
            "near_still_share_24fps": round(float((motion < 1.0).mean()), 3),
            "mean_motion_luma": round(float(motion.mean()), 2),
            "max_flashes_in_any_1s": fl,
            "max_frame_luma_jump": round(jump, 3),
            "mean_saturation_0_255": round(float(sat.mean()), 1),
            "palette_k6": palette(rgb),
            "integrated_lufs_true_peak": loudness(f),
            "librosa_tempo_bpm": tempo(f),
        }
        del rgb
        print(f.name, json.dumps(rows[f.name]), flush=True)
    Path(out).write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
