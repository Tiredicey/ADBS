"""Builds both decks from content.py and the real MongoDB results (verification/results.json).

Design rules, checked by tools/audit_deck.py:
  * Audience text >= 28 pt (FLOOR). Code and output: Courier New 28 pt, at most 52 characters a line.
  * One idea per slide. Same layout every time: title, panels, takeaway band, footer.
  * Commands that change data: 1 BEFORE -> 2 COMMAND -> 3 AFTER. Split across slides only when needed.
  * Outputs are never cut. Line breaks may move; reflow.check() proves every character is kept.
  * Colours pass WCAG AA 4.5:1.
Shapes named EXEMPT_* are helper or reference text (footer, progress, paste-box instructions).
"""
import json
import math
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from content import CHEATSHEET, PARTS, REFERENCES, STEP, VERIFIED, part_words  # noqa: E402
from reflow import reflow  # noqa: E402

PAL = {
    "INK": "14202E", "PAPER": "F4F6F8", "WHITE": "FFFFFF", "ROW_ALT": "EEF1F4", "RULE": "C9D1DA",
    "PANEL": "16212E", "PANEL_TXT": "E6ECF2", "OUT": "9FE0C9", "ERR": "FFB4A8", "COMMENT": "8FA3B8",
    "AMBER": "F2B27A", "NEW": "FFD27F", "SIGNAL": "C2410C", "TEAL": "0B6E61", "MUTED": "4A5868",
    "BLANK": "FFF4E5",
}
C = {k: RGBColor.from_string(v) for k, v in PAL.items()}
# (text, background, where it is used). The audit checks every pair against 4.5:1.
CONTRAST_PAIRS = [
    ("INK", "PAPER", "titles, body"), ("INK", "WHITE", "tables, cards"), ("INK", "ROW_ALT", "table rows"),
    ("INK", "BLANK", "blanks"), ("MUTED", "PAPER", "footer, list notes"), ("MUTED", "WHITE", "card notes"),
    ("SIGNAL", "PAPER", "numbers"), ("SIGNAL", "WHITE", "card labels"), ("SIGNAL", "BLANK", "paste boxes"),
    ("TEAL", "PAPER", "verified tag"), ("WHITE", "TEAL", "takeaway band"), ("WHITE", "INK", "table header, dividers"),
    ("PANEL_TXT", "PANEL", "code"), ("OUT", "PANEL", "output"), ("ERR", "PANEL", "errors, removed"),
    ("COMMENT", "PANEL", "comments"), ("AMBER", "PANEL", "panel labels"), ("NEW", "PANEL", "added"),
    ("AMBER", "INK", "divider number"), ("OUT", "INK", "divider kicker"), ("COMMENT", "INK", "divider timing"),
    ("PANEL_TXT", "INK", "divider text"),
]

SANS, MONO = "Arial", "Courier New"
FLOOR = 28          # pt, smallest audience text (see README for the viewing-distance maths)
MONO_PT = 28
WIDTH = 52          # characters per code/output line at 28 pt inside a panel
LINE_PT = 32        # exact line pitch for code/output; fixed in points so PowerPoint and LibreOffice agree
LINE = LINE_PT / 72
SW, SH = 13.333, 7.5
M = 0.45            # side margin: keeps content inside the TV's safe area
CW = SW - 2 * M
TOP, BOTTOM = 1.2, 6.85
BAND, GAP, PAD = 0.62, 0.12, 0.2
GROUP_PARTS = range(2, 9)
VIDEO = ROOT / "video" / "ADBS_opener_deck.mp4"
POSTER = ROOT / "video" / "ADBS_opener_poster.png"
EMPTY = "// no output: the collection is empty"
# The user's own edits to the shared deck (2026-10-31), kept so a rebuild never undoes them.
SHOW_VIDEO = False          # user deleted the opener slide; set True to put it back
SHOW_REFERENCES = False     # user deleted the References slide
REMOVED_SLIDES = {"Tables are collections. Rows are documents."}   # user deleted this Part 1 slide
NO_BLANKS_FOR = ("Presenter", "Group:", "Section:", "Date:")       # no name/date fill-ins anywhere
FLOW_MAX = 8        # output lines in a BEFORE/AFTER panel: label + check + 8 + band fit 5.65 in
KIND_COLOR = {"code": "PANEL_TXT", "out": "OUT", "error": "ERR", "comment": "COMMENT"}


def I(x):
    return Inches(x)


class Deck:
    def __init__(self, group):
        self.group = group
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = I(SW), I(SH)
        self.layout = self.prs.slide_layouts[6]
        self.count = 0
        self.found = set()
        self.wanted = set()

    def new(self, bg="PAPER"):
        s = self.prs.slides.add_slide(self.layout)
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = C[bg]
        self.count += 1
        return s


def rect(slide, x, y, w, h, fill=None, line=None, name=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, I(x), I(y), I(w), I(h))
    if fill:
        shp.fill.solid()
        shp.fill.fore_color.rgb = C[fill]
    else:
        shp.fill.background()
    if line:
        shp.line.color.rgb = C[line]
        shp.line.width = Pt(2)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    if name:
        shp.name = name
    return shp


def text(slide, x, y, w, h, paras, size=FLOOR, color="INK", font=SANS, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=1.0, pad=0.0, name=None, target=None, wrap=True):
    tb = target or slide.shapes.add_textbox(I(x), I(y), I(w), I(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, I(pad))
    if isinstance(paras, str):
        paras = [paras]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align
        para.line_spacing = spacing
        for seg in ([{"t": p}] if isinstance(p, str) else p):
            r = para.add_run()
            r.text = seg["t"]
            f = r.font
            f.name = seg.get("font", font)
            f.size = Pt(seg.get("size", size))
            f.bold = seg.get("bold", bold)
            f.color.rgb = C[seg.get("color", color)]
            if seg.get("underline"):
                f.underline = True
            if seg.get("strike"):
                r._r.get_or_add_rPr().set("strike", "sngStrike")
    return tb


# ---------- outputs ----------

def shape_output(step_id, max_lines=10, reply=False):
    s = STEP[step_id]
    o = s["output"]
    if not o:
        return [EMPTY], "comment"
    if s["role"] == "error":
        return reflow(o, WIDTH).split("\n"), "error"
    r = reflow(o, WIDTH, compact=reply)
    if len(r.split("\n")) > max_lines and not reply:
        r = reflow(o, WIDTH, compact=True)
    return r.split("\n"), "out"


def sentences(t):
    return [s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s]


def split_before(t):
    ss = sentences(t)
    idx = next((i for i, s in enumerate(ss) if s.startswith("Before") or "start from" in s), 0)
    return " ".join(ss[:idx + 1]), " ".join(ss[idx + 1:])


def split_even(t, k):
    ss = sentences(t)
    if k <= 1:
        return [t]
    size = math.ceil(len(ss) / k)
    return [" ".join(ss[i * size:(i + 1) * size]) for i in range(k)]


# ---------- panels ----------

def inline_check(p):
    c = p.get("check")
    return bool(c) and "\n" not in c and len(p["label"]) * 0.28 + 0.5 + len(c) * MONO_PT * 0.6 / 72 <= CW - 0.4


def panel_lines(p):
    if p.get("paste"):
        return max(p["paste"]["n"], 2) + 1
    return len(p["lines"]) + 1 + (1 if p.get("check") and not inline_check(p) else 0)


def panel_h(p):
    return PAD + panel_lines(p) * LINE


def stack_h(panels, band):
    h = sum(panel_h(p) for p in panels) + GAP * max(len(panels) - 1, 0)
    return h + (GAP + BAND if band else 0)


def _splits(n):
    """Every way to cut n panels into contiguous groups, fewest groups first."""
    from itertools import combinations
    for k in range(1, n + 1):
        for cuts in combinations(range(1, n), k - 1):
            b = (0,) + cuts + (n,)
            yield [(b[i], b[i + 1]) for i in range(k)]


def pack(panels):
    """Fewest slides; among those, the most even fill (no near-empty slide next to a full one)."""
    avail = BOTTOM - TOP
    best, best_k = None, None
    for split in _splits(len(panels)):
        if best_k is not None and len(split) > best_k:
            break
        groups = [panels[a:b] for a, b in split]
        hs = [stack_h(g, i == len(groups) - 1) for i, g in enumerate(groups)]
        if max(hs) > avail + 1e-6:
            continue
        score = (max(hs) - min(hs), -min(hs))
        if best is None or score < best[0]:
            best, best_k = (score, groups), len(split)
    if best is None:
        tall = max(panels, key=lambda p: stack_h([p], True))
        raise SystemExit(f"panel too tall: {tall['label']} needs {stack_h([tall], True):.2f} in, has {avail:.2f}")
    return best[1]


def styled(t, kind, marks, deck):
    base = KIND_COLOR[kind]
    spans = []
    if kind in ("out", "error"):
        for style in ("new", "gone"):
            for m in marks.get(style, []):
                start = 0
                while True:
                    i = t.find(m, start)
                    if i < 0:
                        break
                    spans.append((i, i + len(m), style))
                    deck.found.add((style, m))
                    start = i + len(m)
    spans.sort()
    segs, pos = [], 0
    for a, b, st in spans:
        if a < pos:
            continue
        if a > pos:
            segs.append({"t": t[pos:a], "color": base})
        seg = {"t": t[a:b]}
        seg.update({"color": "NEW", "bold": True, "underline": True} if st == "new" else {"color": "ERR", "strike": True})
        segs.append(seg)
        pos = b
    if pos < len(t) or not segs:
        segs.append({"t": t[pos:] or " ", "color": base})
    return segs


def draw_panel(slide, y, p, deck):
    h = panel_h(p)
    if p.get("paste"):
        box = rect(slide, M, y, CW, h, fill="BLANK", line="SIGNAL", name="EXEMPT_PASTE")
        paste = p["paste"]
        paras = [[{"t": p["label"] + "  ·  PASTE YOUR SCREENSHOT HERE", "bold": True, "color": "SIGNAL", "size": 22}]]
        if paste.get("run"):
            paras.append([{"t": "Run:  ", "bold": True, "size": 18}, {"t": paste["run"].replace("\n", " "), "font": MONO, "size": 18}])
        paras.append([{"t": "Screenshot " + paste["what"] + " (Win + Shift + S). Click this box's edge, press Delete, then Ctrl + V.", "size": 18}])
        text(slide, 0, 0, 0, 0, paras, pad=0.15, target=box)
        return h
    rect(slide, M, y, CW, h, fill="PANEL")
    head = [{"t": p["label"], "bold": True, "color": "AMBER", "font": SANS}]
    if p.get("check") and inline_check(p):
        head.append({"t": "   " + p["check"], "color": "COMMENT"})
    paras = [head]
    if p.get("check") and not inline_check(p):
        paras.append([{"t": p["check"], "color": "COMMENT"}])
    for t, kind in p["lines"]:
        if len(t) > WIDTH:
            raise SystemExit(f"line too long ({len(t)}): {t}")
        paras.append(styled(t, kind, p.get("marks", {}), deck))
    text(slide, M + 0.16, y + 0.1, CW - 0.24, h - 0.12, paras, size=MONO_PT, font=MONO, wrap=False, spacing=Pt(LINE_PT))
    return h


def paste_of(p, what="the result"):
    return {"label": p["label"], "paste": {"n": len(p["lines"]), "run": p.get("check"), "what": what}, "say": p["say"]}


def flow_panels(sl, deck):
    b_lines, b_kind = shape_output(sl["before"], max_lines=FLOW_MAX)
    a_lines, a_kind = shape_output(sl["after"], max_lines=FLOW_MAX)
    r_lines, r_kind = shape_output(sl["cmd"], reply=True)
    code = STEP[sl["cmd"]]["code"].split("\n")
    pre, mid = split_before(sl["say"][0])
    note_b = [(sl["before_note"], "comment")] if sl.get("before_note") else []
    note_r = [(sl["reply_note"], "comment")] if sl.get("reply_note") else []
    before = {"label": "1  BEFORE", "check": STEP[sl["before"]]["code"], "lines": note_b + [(x, b_kind) for x in b_lines],
              "marks": {"gone": sl.get("gone", [])}, "say": pre}
    command = {"label": "2  COMMAND → REPLY", "lines": [(x, "code") for x in code] + note_r + [(x, r_kind) for x in r_lines], "say": mid}
    after = {"label": "3  AFTER", "check": STEP[sl["after"]]["code"], "lines": [(x, a_kind) for x in a_lines],
             "marks": {"new": sl.get("new", [])}, "say": sl["say"][1]}
    if not deck.group:
        deck.wanted |= {("gone", m) for m in sl.get("gone", [])} | {("new", m) for m in sl.get("new", [])}
        return [before, command, after]
    return [paste_of(before),
            {"label": "2  COMMAND", "lines": [(x, "code") for x in code], "say": mid},
            {"label": "2  REPLY", "paste": {"n": len(r_lines), "run": None, "what": "the shell's reply to the command above"}, "say": ""},
            paste_of(after)]


def find_panels(sl, deck, data=False):
    ids = [sl["data"]] if data else sl["finds"]
    says = split_even(sl["say"][0], len(ids))
    out = []
    for j, fid in enumerate(ids):
        code = STEP[fid]["code"].split("\n")
        note = [(sl["note"], "comment")] if sl.get("note") and j == 0 else []
        room = 10 - 1 - len(code) - len(note)
        o_lines, kind = shape_output(fid, max_lines=room)
        if deck.group:
            out += [{"label": "COMMAND", "lines": note + [(x, "code") for x in code], "say": says[j]},
                    {"label": "RESULT", "paste": {"n": len(o_lines), "run": None, "what": "the result of the command above"}, "say": ""}]
        else:
            out.append({"label": "COMMAND → RESULT", "lines": note + [(x, "code") for x in code] + [(x, kind) for x in o_lines], "say": says[j]})
    return out


# ---------- slide chrome ----------

def footer(s, ctx, source, verified):
    y = 6.98
    if source:
        text(s, M, y, 5.6, 0.4, "Source: " + source, size=14, color="MUTED", name="EXEMPT_FOOTER")
    if verified:
        text(s, 6.1, y, 3.1, 0.4, VERIFIED, size=14, color="TEAL", align=PP_ALIGN.CENTER, name="EXEMPT_FOOTER")
    if ctx:
        text(s, 9.3, y - 0.06, SW - M - 9.3, 0.45, ctx, size=22, bold=True, color="MUTED", align=PP_ALIGN.RIGHT, name="EXEMPT_PROGRESS")


def band(s, msg):
    shp = rect(s, M, BOTTOM - BAND, CW, BAND, fill="TEAL")
    text(s, 0, 0, 0, 0, [[{"t": msg}]], size=FLOOR, bold=True, color="WHITE", anchor=MSO_ANCHOR.MIDDLE, pad=0.18, target=shp)


def notes(s, body):
    s.notes_slide.notes_text_frame.text = body


def say_notes(ctx, script, source, todo=False):
    script = script.strip() or "(No new words. Let the class read this slide, then click.)"
    head = "TO DO: run the commands, paste screenshots into the orange boxes, fill the blanks.\nSuggested script:\n" if todo else ""
    return f"{head}SAY ({ctx}):\n{script}\n\nSource: {source}"


def base_slide(deck, title, bg="PAPER"):
    s = deck.new(bg)
    rect(s, 0, 0, 0.14, SH, fill="SIGNAL")
    text(s, M, 0.3, CW, 0.8, title, size=36, bold=True)
    return s


def helper_tag(s):
    text(s, 8.6, 0.05, SW - 8.6 - M, 0.3, "HELPER · delete before presenting", size=14, bold=True, color="SIGNAL", align=PP_ALIGN.RIGHT, name="EXEMPT_HELPER")


# ---------- slide kinds ----------

def plan(deck, part, sl):
    """Returns a list of slide specs (dict) for one content item."""
    bp = deck.group and part["n"] in GROUP_PARTS
    if sl["title"] in REMOVED_SLIDES:
        return []
    if sl["kind"] in ("flow", "find", "data"):
        if sl["kind"] == "flow":
            panels = flow_panels(sl, deck) if not bp else flow_panels(sl, _GroupView(deck))
        else:
            panels = find_panels(sl, deck if not bp else _GroupView(deck), data=sl["kind"] == "data")
        groups = pack(panels)
        return [{"kind": "panels", "panels": g, "band": sl["takeaway"] if i == len(groups) - 1 else None,
                 "next": groups[i + 1][0]["label"].strip() if i + 1 < len(groups) else None,
                 "say": " ".join(p["say"] for p in g if p.get("say")), "sl": sl, "bp": bp} for i, g in enumerate(groups)]
    return [{"kind": sl["kind"], "sl": sl, "band": sl["takeaway"], "say": " ".join(sl["say"]), "bp": bp}]


class _GroupView:
    """Deck proxy that makes panel builders produce paste boxes (group deck, Parts 2-8)."""
    group = True

    def __init__(self, deck):
        self._d = deck

    def __getattr__(self, k):
        return getattr(self._d, k)


def render(deck, part, spec, ctx):
    sl, bp = spec["sl"], spec["bp"]
    s = base_slide(deck, sl["title"])
    kind = spec["kind"]
    if kind == "panels":
        y = TOP
        for p in spec["panels"]:
            y += draw_panel(s, y, p, deck) + GAP
    elif kind == "table":
        draw_table(s, sl, bp)
    elif kind == "text":
        items = ["____________________________" for _ in sl["body"]] if bp else sl["body"]
        text(s, M, TOP + 0.15, CW, BOTTOM - BAND - TOP - 0.3,
             [[{"t": "▸  ", "color": "SIGNAL", "bold": True}, {"t": it}] for it in items], size=32, spacing=1.1)
    elif kind == "card":
        draw_card(s, sl, bp)
    elif kind == "list":
        draw_list(s, sl, bp)
    if spec["band"]:
        band(s, spec["band"])
    elif spec.get("next") and kind == "panels" and stack_h(spec["panels"], True) <= BOTTOM - TOP + 1e-6:
        text(s, M, BOTTOM - BAND, CW, BAND, "Next: " + spec["next"] + "  →", size=FLOOR, color="MUTED",
             anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.RIGHT, pad=0.18)
    footer(s, ctx, sl["source"], verified=kind == "panels" and not bp)
    notes(s, say_notes(ctx, spec["say"], sl["source"], todo=bp))


def draw_table(s, sl, bp):
    rows, cols = len(sl["rows"]) + 1, len(sl["headers"])
    widths = {2: [3.6, CW - 3.6], 3: [3.0, CW - 6.0, 3.0]}[cols]
    rh = min(1.0, (BOTTOM - BAND - GAP - TOP - 0.15) / rows)   # fill the space above the band
    tbl = s.shapes.add_table(rows, cols, I(M), I(TOP + 0.15), I(CW), I(rh * rows)).table
    for c, wd in enumerate(widths):
        tbl.columns[c].width = I(wd)
    for r_i in range(rows):
        tbl.rows[r_i].height = I(rh)
    for c, hd in enumerate(sl["headers"]):
        cell = tbl.cell(0, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C["INK"]
        text(None, 0, 0, 0, 0, [[{"t": hd, "bold": True, "color": "WHITE"}]], size=FLOOR, anchor=MSO_ANCHOR.MIDDLE, pad=0.12, target=_CellBox(cell))
    for r_i, row in enumerate(sl["rows"], start=1):
        for c, val in enumerate(row):
            cell = tbl.cell(r_i, c)
            blank = bp and c > 0
            cell.fill.solid()
            cell.fill.fore_color.rgb = C["BLANK" if blank else ("WHITE" if r_i % 2 else "ROW_ALT")]
            v = blank_for(widths[c] - 0.34, 30) if blank else val
            seg = {"t": v, "bold": c == 0, "font": MONO if (c == 0 and v.startswith("$")) else SANS}
            text(None, 0, 0, 0, 0, [[seg]], size=30, anchor=MSO_ANCHOR.MIDDLE, pad=0.12, target=_CellBox(cell))


class _CellBox:
    """Lets text() fill a table cell like a text box."""

    def __init__(self, cell):
        self.text_frame = cell.text_frame
        self.text_frame.clear()

    @property
    def name(self):
        return ""

    @name.setter
    def name(self, v):
        pass


_FONTS = {}


def _font(bold):
    """Liberation Sans has the same advance widths as Arial (metric-compatible), so it measures Arial text."""
    if bold not in _FONTS:
        from PIL import ImageFont
        import subprocess
        path = subprocess.run(["fc-match", "-f", "%{file}", "Liberation Sans:bold" if bold else "Liberation Sans"],
                              capture_output=True, text=True).stdout.strip()
        _FONTS[bold] = ImageFont.truetype(path, 1000)
    return _FONTS[bold]


def text_w(t, pt, bold=False):
    return _font(bold).getlength(t) / 1000 * pt / 72


def blank_for(width_in, pt):
    """An underline blank that fits on one line of the given width."""
    return "_" * max(4, int(width_in / text_w("_", pt)))


def no_name_blanks(deck):
    for i, s in enumerate(deck.prs.slides, 1):
        for shp in s.shapes:
            frames = [shp.text_frame] if shp.has_text_frame else []
            if getattr(shp, "has_table", False) and shp.has_table:
                frames += [c.text_frame for r in shp.table.rows for c in r.cells]
            for tf in frames:
                if any(k in tf.text for k in NO_BLANKS_FOR):
                    raise SystemExit(f"name/date blank left on slide {i}: {tf.text[:60]}")


def wrapped_lines(t, width_in, pt, bold=False):
    lines, cur = 1, ""
    for word in t.split():
        trial = (cur + " " + word).strip()
        if cur and text_w(trial, pt, bold) > width_in - 0.05:
            lines += 1
            cur = word
        else:
            cur = trial
    return lines


def draw_card(s, sl, bp):
    y = TOP + 0.1
    lw = max(text_w(label, FLOOR, True) for label, _ in sl["rows"]) + 0.35
    vw = CW - lw - 0.3
    for label, value in sl["rows"]:
        v = blank_for(min(vw, 6.0), FLOOR) if bp else value
        h = 0.22 + wrapped_lines(v, vw, FLOOR) * 0.47
        rect(s, M, y, CW, h, fill="BLANK" if bp else "WHITE", line="RULE")
        text(s, M + 0.15, y + 0.1, lw, h - 0.15, label, size=FLOOR, bold=True, color="SIGNAL")
        text(s, M + 0.15 + lw, y + 0.1, vw, h - 0.15, v, size=FLOOR)
        y += h + 0.1
    if y > BOTTOM - BAND - GAP + 0.05:
        raise SystemExit(f"card too tall: {sl['title']} ends at {y:.2f}")


def draw_list(s, sl, bp):
    y = TOP + 0.05
    for i, (name, desc) in enumerate(sl["items"]):
        n = sl["start"] + i
        text(s, M, y, 1.0, 0.9, str(n), size=40, bold=True, color="SIGNAL")
        body = [[{"t": "________________", "bold": True, "size": 32}], [{"t": "one line from the 09 Handout", "size": FLOOR, "color": "MUTED"}]] if bp else \
               [[{"t": name, "bold": True, "size": 32}], [{"t": desc, "size": FLOOR, "color": "MUTED"}]]
        text(s, M + 1.1, y, CW - 1.1, 0.95, body)
        y += 0.98
    if y > BOTTOM - BAND - GAP + 0.05:
        raise SystemExit(f"list too tall: {sl['title']}")


# ---------- fixed slides ----------

def slide_video(deck):
    s = deck.new("INK")
    mv = s.shapes.add_movie(str(VIDEO), 0, 0, I(SW), I(SH), poster_frame_image=str(POSTER), mime_type="video/mp4")
    mv.name = "OPENER_VIDEO"
    notes(s, "Opener video, 35 seconds. Click the video once to play it (or press Alt + P). When it ends, press the right arrow key for the title slide.")


def slide_title(deck):
    s = deck.new("INK")
    rect(s, 0, 5.75, SW, 0.1, fill="AMBER")
    text(s, M, 0.9, CW, 0.6, "IT2003 · ADVANCED DATABASE SYSTEMS", size=FLOOR, bold=True, color="AMBER")
    text(s, M, 1.6, CW, 2.4, [[{"t": "MongoDB Commands"}], [{"t": "& Cloud Computing"}]], size=60, bold=True, color="WHITE", spacing=0.95)
    sub = "Shared group deck · Part 1 is done · Parts 2-8: fill the orange boxes" if deck.group else "07, 08 and 09 Handouts"
    text(s, M, 3.9, CW, 1.4, sub, size=FLOOR, color="PANEL_TXT")
    notes(s, "SAY: Good day. We are [group name]. Our topic is MongoDB commands and cloud computing, from the 07, 08 and 09 handouts. Each of us has 3 minutes.")


def slide_howto(deck):
    s = base_slide(deck, "How to do your part (read this first)")
    helper_tag(s)
    steps = [
        ("Find your part", "The 'Eight parts' slide lists them. Your part has a big number divider."),
        ("Look at Part 1", "Part 1 is finished. Make yours look like it."),
        ("Open the MongoDB shell", "MongoDB Compass → Connect → click  >_ Open MongoDB shell."),
        ("Run your SETUP slide", "Copy all its lines, paste in the shell, press Enter."),
        ("Go box by box, top to bottom", "Each orange box says what to run. Order: 1 BEFORE, 2 COMMAND, 3 AFTER."),
        ("Paste a screenshot", "Win + Shift + S. Click the box's edge, press Delete, then Ctrl + V."),
        ("Fill the blanks", "Replace every ______ using the handout page in the footer."),
        ("Practice the script", "View → Notes. Read it aloud with a timer. Stay under 3 minutes."),
    ]
    for i, (head, body) in enumerate(steps):
        cx = M + 6.3 * (i // 4)
        cy = 1.3 + 1.33 * (i % 4)
        rect(s, cx, cy, 6.1, 1.2, fill="WHITE", line="RULE", name="EXEMPT_HOWTO")
        text(s, cx + 0.12, cy, 0.8, 1.2, str(i + 1), size=40, bold=True, color="SIGNAL", anchor=MSO_ANCHOR.MIDDLE, name="EXEMPT_HOWTO")
        text(s, cx + 0.9, cy + 0.1, 5.1, 1.05, [[{"t": head, "bold": True, "size": 20}], [{"t": body, "size": 16, "color": "MUTED"}]], name="EXEMPT_HOWTO")
    text(s, M, 6.65, CW, 0.4, "Only edit YOUR part. Delete every slide marked HELPER before presenting.", size=18, bold=True, color="SIGNAL", name="EXEMPT_HOWTO")
    notes(s, "Instructions for group members. Delete this slide before presenting.")


def slide_agenda(deck):
    s = base_slide(deck, "Eight parts · 3 minutes each")
    for i, p in enumerate(PARTS):
        cx = M + 6.3 * (i // 4)
        cy = TOP + 1.38 * (i % 4)
        rect(s, cx, cy, 6.1, 1.25, fill="WHITE", line="RULE")
        text(s, cx + 0.15, cy, 0.9, 1.25, str(p["n"]), size=40, bold=True, color="SIGNAL", anchor=MSO_ANCHOR.MIDDLE)
        text(s, cx + 1.05, cy, 4.95, 1.25, p["title"], size=FLOOR, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    notes(s, "SAY: We have eight parts. Parts 1 to 6 are MongoDB commands. Parts 7 and 8 are cloud computing.")


def slide_divider(deck, part, nslides, seconds):
    s = deck.new("INK")
    text(s, M, 1.0, 3.6, 3.0, str(part["n"]), size=180, bold=True, color="AMBER")
    text(s, 4.2, 0.6, 8.6, 2.3, part["title"], size=44, bold=True, color="WHITE", anchor=MSO_ANCHOR.BOTTOM)
    text(s, 4.2, 3.0, 8.6, 1.0, part["kicker"], size=FLOOR, color="OUT")
    text(s, 4.2, 4.15, 8.6, 1.1, "“" + part["takeaway"] + "”", size=32, color="AMBER")
    text(s, 4.2, 5.55, 8.6, 0.5, f"{nslides} slides · about {seconds // 60} min {seconds % 60:02d} s", size=22, color="COMMENT", name="EXEMPT_PROGRESS")
    timing = f"\n\n(Whole part: {part_words(part, REMOVED_SLIDES)} words, about {seconds // 60} min {seconds % 60:02d} s at a calm 130 words a minute. Limit: 3 minutes.)"
    notes(s, "SAY:\n" + part["intro"] + timing)


def slide_setup(deck, part):
    s = base_slide(deck, f"Part {part['n']} SETUP: run this first")
    helper_tag(s)
    body = part["setup"].split("\n")
    rect(s, M, TOP, CW, 4.9, fill="PANEL", name="EXEMPT_SETUP")
    pt = min(20, (CW - 0.3) * 72 / (0.6 * max(len(x) for x in body)), 4.6 * 72 / (1.15 * len(body)))
    text(s, M + 0.15, TOP + 0.12, CW - 0.3, 4.7, [[{"t": x or " ", "color": "COMMENT" if x.startswith("//") else "PANEL_TXT"}] for x in body],
         size=round(pt, 1), font=MONO, wrap=False, name="EXEMPT_SETUP")
    text(s, M, 6.25, CW, 0.5, "Copy all of it into the MongoDB shell and press Enter. Run it again any time to start over.", size=18, color="MUTED", name="EXEMPT_SETUP")
    notes(s, "Setup only. Delete this slide before presenting.")


def slide_cheatsheet(deck):
    s = base_slide(deck, "All commands on one slide")
    rows = CHEATSHEET
    for i, (k, v) in enumerate(rows):
        y = TOP + 0.56 * i
        rect(s, M, y, CW, 0.52, fill="WHITE" if i % 2 == 0 else "ROW_ALT")
        text(s, M + 0.15, y, 2.6, 0.52, k, size=FLOOR, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, M + 2.9, y, CW - 3.0, 0.52, v, size=FLOOR, font=SANS if k == "Cloud" else MONO, anchor=MSO_ANCHOR.MIDDLE, wrap=False)
    notes(s, "Leave this up during questions.")


def slide_refs(deck):
    s = base_slide(deck, "References")
    text(s, M, TOP, CW, 5.4, [[{"t": r}] for r in REFERENCES], size=20, spacing=1.25, name="EXEMPT_REF")
    notes(s, "Sources: the three handouts and the references they cite.")


# ---------- build ----------

def build(group, out):
    d = Deck(group)
    report = {"deck": out.name, "parts": []}
    if SHOW_VIDEO:
        slide_video(d)
    slide_title(d)
    if group:
        slide_howto(d)
    slide_agenda(d)
    for part in PARTS:
        specs = [sp for sl in part["slides"] for sp in plan(d, part, sl)]
        n = len(specs) + 1
        w = part_words(part, REMOVED_SLIDES)
        sec = round(w / 130 * 60)
        slide_divider(d, part, n, sec)
        if group and part["n"] in GROUP_PARTS and part.get("setup"):
            slide_setup(d, part)
        for i, sp in enumerate(specs, start=2):
            render(d, part, sp, f"Part {part['n']} · {i} of {n}")
        report["parts"].append({"part": part["n"], "slides": n, "words": w,
                                "seconds_at_100_130_150_wpm": [round(w / r * 60) for r in (100, 130, 150)]})
    slide_cheatsheet(d)
    if SHOW_REFERENCES:
        slide_refs(d)
    no_name_blanks(d)
    missing = d.wanted - d.found
    if missing:
        raise SystemExit("highlight not found: " + repr(sorted(missing)))
    out.parent.mkdir(parents=True, exist_ok=True)
    d.prs.save(out)
    report["slides"] = d.count
    report["size_mb"] = round(out.stat().st_size / 1e6, 1)
    return report


if __name__ == "__main__":
    reports = [build(False, ROOT / "01_FULL_DECK" / "ADBS_FULL_answer_key.pptx"),
               build(True, ROOT / "02_GROUP_DECK" / "ADBS_GROUP_DECK.pptx")]
    (ROOT / "verification" / "deck_report.json").write_text(json.dumps(reports, indent=1))
    for r in reports:
        print(r["deck"], r["slides"], "slides", r["size_mb"], "MB")
    for p in reports[0]["parts"]:
        print(f"  Part {p['part']}: {p['slides']} slides, {p['words']} words, {p['seconds_at_100_130_150_wpm']} s at 100/130/150 wpm")
