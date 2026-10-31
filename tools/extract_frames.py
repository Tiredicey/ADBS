import subprocess
import sys
from pathlib import Path
from PIL import Image

UP = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/home/user/uploaded_files")
SRC = {"bebop": "Cowboy_Bebop_-_Opening_-_Tank_HD_-_60_fps.mp4",
       "orbital": "The_Orbital_Children__Official_Trailer__Netflix_Anime.mp4"}
OUT = Path(__file__).resolve().parent.parent / "build" / "frames"
ASPECT = 3.2 / 6.55  # must match FRAME_W / FRAME_H in src/build_deck.py
# part: (video, seconds, crop centre x as a fraction, usable y range as fractions)
# Every pick has no burned-in subtitles or credits.
PICKS = {
    1: ("bebop", 33.22, 0.42, (0.0, 1.0)),
    2: ("bebop", 77.80, 0.55, (0.22, 1.0)),
    3: ("bebop", 62.55, 0.70, (0.0, 1.0)),
    4: ("bebop", 47.13, 0.55, (0.0, 1.0)),
    5: ("bebop", 54.74, 0.50, (0.0, 1.0)),
    6: ("bebop", 67.67, 0.30, (0.0, 1.0)),
    7: ("orbital", 53.00, 0.40, (0.11, 0.86)),
    8: ("orbital", 51.20, 0.36, (0.11, 0.86)),
}


def find(name):
    hits = sorted(UP.rglob(name.replace(".mp4", "*.mp4")))
    if not hits:
        raise SystemExit(f"video not found in {UP}: {name} (upload it, or pass the folder as the first argument)")
    return hits[0]


def crop(img, cx, yr):
    w, h = img.size
    y0, y1 = int(yr[0] * h), int(yr[1] * h)
    cw = min(w, int((y1 - y0) * ASPECT))
    x0 = max(0, min(w - cw, int(cx * w - cw / 2)))
    return img.crop((x0, y0, x0 + cw, y1))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for n, (video, t, cx, yr) in PICKS.items():
        raw = OUT / f"raw_{n}.png"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(find(SRC[video])),
                        "-frames:v", "1", str(raw)], check=True)
        im = crop(Image.open(raw).convert("RGB"), cx, yr)
        im.resize((640, int(640 / ASPECT)), Image.LANCZOS).save(OUT / f"part{n}.jpg", quality=88)
        raw.unlink()
    print("frames in", OUT)


if __name__ == "__main__":
    main()
