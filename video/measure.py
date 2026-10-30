import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from timeline import FPS, LEAD_FRAMES, kick_times  # noqa: E402

HERE = Path(__file__).resolve().parent


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(f):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size,bit_rate:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels", "-of", "json", str(f)])
    return json.loads(r.stdout)


def loudness(f):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"])
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", tail).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail).group(1))
    return i, tp


def scene_cuts(f, thr=0.3):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-vf", f"select='gt(scene,{thr})',showinfo", "-an", "-f", "null", "-"])
    return [float(m) for m in re.findall(r"pts_time:([\d.]+)", r.stderr)]


def luma_series(f):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-vf", "scale=160:-2,format=gray", "-f", "rawvideo", "-"], capture_output=True)
    info = probe(f)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    w = 160
    h = int(round(v["height"] * 160 / v["width"] / 2) * 2)
    frames = np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w).astype(np.float32)
    return frames


def flash_check(frames):
    mean = frames.reshape(len(frames), -1).mean(1)
    d = np.diff(mean)
    big = np.abs(d) > 0.10 * 255
    events = np.where(big)[0]
    worst = 0
    for i in range(len(frames)):
        win = events[(events >= i) & (events < i + FPS)]
        worst = max(worst, len(win) // 2)
    return int(worst), float(np.abs(d).max() / 255)


def near_still_share(frames, thr=1.0):
    diff = np.abs(np.diff(frames, axis=0)).reshape(len(frames) - 1, -1).mean(1)
    return float((diff < thr).mean())


def visual_pulse_offset(frames):
    mean = frames.reshape(len(frames), -1).mean(1)
    kicks = np.array(kick_times())
    offs = []
    for k in kicks:
        c = int(round(k * FPS))
        lo, hi = max(0, c - 6), min(len(mean) - 1, c + 4)
        if hi - lo < 3:
            continue
        seg = np.diff(mean[lo:hi + 1])
        peak = lo + int(np.argmax(seg)) + 1
        offs.append((peak - c) / FPS)
    return float(np.median(offs)), float(np.std(offs)), len(offs)


def audio_onsets(f):
    import librosa
    y, sr = librosa.load(str(f), sr=22050, mono=True)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    on = librosa.onset.onset_detect(y=y, sr=sr, units="time", backtrack=False)
    kicks = np.array(kick_times())
    errs = [float(np.min(np.abs(on - k))) for k in kicks if len(on)]
    return float(np.atleast_1d(tempo)[0]), float(np.median(errs)), float(np.percentile(errs, 95)), len(on)


def main():
    rows = {}
    for f in sorted(HERE.glob("ADBS_freefall_*.mp4")):
        info = probe(f)
        dur = float(info["format"]["duration"])
        i, tp = loudness(f)
        cuts = scene_cuts(f)
        frames = luma_series(f)
        flashes, max_jump = flash_check(frames)
        still = near_still_share(frames)
        pv_med, pv_sd, pv_n = visual_pulse_offset(frames)
        tempo, on_med, on_p95, n_on = audio_onsets(f)
        rows[f.name] = {
            "duration_s": round(dur, 3),
            "size_mb": round(int(info["format"]["size"]) / 1e6, 2),
            "streams": [{k: s.get(k) for k in ("codec_name", "width", "height", "r_frame_rate", "sample_rate", "channels") if s.get(k)} for s in info["streams"]],
            "integrated_lufs": i,
            "true_peak_dbfs": tp,
            "scene_cuts_gt_0.3": len(cuts),
            "cuts_per_min": round(len(cuts) / dur * 60, 2),
            "near_still_frame_share": round(still, 3),
            "max_flashes_in_any_1s": flashes,
            "max_frame_luma_jump": round(max_jump, 4),
            "visual_pulse_offset_median_s": round(pv_med, 4),
            "visual_pulse_offset_sd_s": round(pv_sd, 4),
            "visual_pulse_n": pv_n,
            "design_visual_lead_s": round(-LEAD_FRAMES / FPS, 4),
            "librosa_tempo_bpm": round(tempo, 2),
            "kick_onset_err_median_ms": round(on_med * 1000, 1),
            "kick_onset_err_p95_ms": round(on_p95 * 1000, 1),
            "audio_onsets_detected": n_on,
        }
        print(f.name, json.dumps(rows[f.name], indent=1))
    (HERE / "measurements.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
