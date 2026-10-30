import json
import subprocess
from pathlib import Path

B = Path(__file__).resolve().parent / "build"


def loudnorm_json(stderr):
    return json.loads(stderr[stderr.rfind("{"): stderr.rfind("}") + 1])


def main():
    target = "I=-14:TP=-1.5:LRA=11"
    r1 = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(B / "score_raw.wav"), "-af", f"loudnorm={target}:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    p = loudnorm_json(r1.stderr)
    af = (f"loudnorm={target}:measured_I={p['input_i']}:measured_TP={p['input_tp']}:measured_LRA={p['input_lra']}:"
          f"measured_thresh={p['input_thresh']}:offset={p['target_offset']}:linear=true:print_format=json")
    r2 = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-y", "-i", str(B / "score_raw.wav"), "-af", af, "-ar", "48000", "-c:a", "pcm_s24le", str(B / "score_master.wav")], capture_output=True, text=True)
    q = loudnorm_json(r2.stderr)
    print("pass1 input I", p["input_i"], "TP", p["input_tp"], "| pass2", q["normalization_type"], "I", q["output_i"], "TP", q["output_tp"])


if __name__ == "__main__":
    main()
