import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "verification"))
from content import PARTS, VERIFIED  # noqa: E402
from run_commands import STEPS  # noqa: E402


def seed_script(n):
    if n > 6:
        return ""
    lines = ["use adbs_part%d" % n]
    for sid, code, note in STEPS:
        if sid.startswith("p%d_" % n):
            lines.append(code + ("  // " + note if note else ""))
    return "\n".join(lines)


def guide(part):
    n = part["n"]
    out = [f"# Part {n}: {part['title']}", ""]
    if n == 1:
        out += ["**Status: COMPLETE.** Part 1 is the worked example. Copy its pattern for your own part.", ""]
    out += [
        f"**Commands:** `{part['kicker']}`",
        f"**Soundbite (part opener):** \"{part['soundbite']}\"",
        f"**Source:** {part['source']}",
        f"**Optional crowd line:** {part['meme']}",
        "",
        "## What you do",
        "",
        f"1. Open `02_BLUEPRINT_DECK/ADBS_MongoDB_Cloud_BLUEPRINT.pptx` and find the slides tagged `PART {n} · BLUEPRINT`.",
        "2. Put your name in every `OWNER: ____` tag and on the part divider slide.",
        "3. On each command slide, run the command (seed script below) and paste the **real** output, or a screenshot, into the orange box.",
        "4. On table and text slides, fill every blank from the handout pages named in the slide footer.",
        "5. Replace each `______` bullet with your own one-line explanation. The speaker notes say what to cover.",
        "6. Rehearse at 30-45 seconds per slide, and say the soundbite out loud.",
        f"7. Save the file as `part{n}_<yourname>.pptx` and submit it (see `04_SUBMIT_YOUR_PART/README.md`).",
        "",
        "## Slide-by-slide checklist",
        "",
    ]
    for i, sl in enumerate(part["slides"], 1):
        out.append(f"### {i}. {sl['title']}")
        out.append(f"- Soundbite: \"{sl['soundbite']}\"")
        if "code" in sl:
            code = sl["code"] + ("\n\n" + sl["code2"] if sl.get("code2") else "")
            out.append("- Command:")
            out.append("```js\n" + code + "\n```")
        out.append(f"- Cover: {sl['notes']}")
        out.append(f"- Source: {sl['source']}")
        out.append("")
    seed = seed_script(n)
    if seed:
        out += [
            "## Seed script: paste into mongosh to reproduce every output",
            "",
            "Run the lines in order. Lines marked `expected error` or `premise test` are supposed to fail; the error message is the output you paste.",
            "",
            "```js",
            seed,
            "```",
            "",
            f"Reference outputs: `verification/results.json` ({VERIFIED}). Yours should match, except ObjectId values, which differ on every run.",
            "",
        ]
    out += [
        "## Done when",
        "",
        "- [ ] Every orange box shows real output (no typed guesses).",
        "- [ ] No `____` blanks are left.",
        "- [ ] Every slide still has its source footer.",
        "- [ ] Speaker notes are rewritten in your own words.",
        "- [ ] The file is submitted per `04_SUBMIT_YOUR_PART/README.md`.",
        "",
    ]
    return "\n".join(out)


if __name__ == "__main__":
    d = ROOT / "03_MEMBER_GUIDES"
    d.mkdir(exist_ok=True)
    for p in PARTS:
        name = p["title"].lower().replace("&", "and")
        for ch in ",$:":
            name = name.replace(ch, "")
        (d / f"PART{p['n']}_{'_'.join(name.split())}.md").write_text(guide(p))
    print("guides", len(PARTS))
