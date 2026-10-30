BPM = 140
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 20
TAIL = 1.0
DURATION = BARS * BAR + TAIL
FPS = 30
SR = 48000
LEAD_FRAMES = 3
EXIT_BAR = 18

SECTIONS = [
    {"bar": 0, "kicker": "IT2003 · ADVANCED DATABASE SYSTEMS", "hero": "FREE FALL", "sub": "into MongoDB & the Cloud"},
    {"bar": 2, "kicker": "PART 1", "hero": "insertOne · deleteMany", "sub": "Documents in, documents out."},
    {"bar": 4, "kicker": "PART 2", "hero": "findOne · updateMany", "sub": "Find it first. Then change it."},
    {"bar": 6, "kicker": "PART 3", "hero": "$lt  $lte  $gt  $gte", "sub": "The e means equal is allowed."},
    {"bar": 8, "kicker": "PART 4", "hero": "$in · $or · $not", "sub": "One field, many values. Many fields, any match."},
    {"bar": 10, "kicker": "PART 5", "hero": "$all · $size · fruit.2", "sub": "Arrays answer like single values."},
    {"bar": 12, "kicker": "PART 6", "hero": "$slice · name.first", "sub": "Trim what you see. Reach inside with a dot."},
    {"bar": 14, "kicker": "PART 7", "hero": "Public · Private · Hybrid", "sub": "Rent it, own it, or mix both."},
    {"bar": 16, "kicker": "PART 8", "hero": "SaaS · PaaS · IaaS", "sub": "Use it, build on it, or rent the machine."},
    {"bar": 18, "kicker": "EVERY COMMAND RUN ON A REAL SERVER", "hero": "ADBS", "sub": "github.com/Tiredicey/ADBS"},
]

CHORDS = [("Dm", [62, 65, 69]), ("Bb", [58, 62, 65]), ("Gm", [55, 58, 62]), ("A", [57, 61, 64])]


def chord_for_bar(bar):
    return CHORDS[0] if bar >= EXIT_BAR else CHORDS[(bar // 2) % 4]


def kick_times():
    return [i * BEAT for i in range(EXIT_BAR * 4)]


def cue_sheet():
    rows = []
    for b in range(BARS):
        rows.append({"time_s": round(b * BAR, 4), "bar": b, "event": "bar", "detail": "chord " + chord_for_bar(b)[0]})
    for s in SECTIONS:
        rows.append({"time_s": round(max(0.0, s["bar"] * BAR - LEAD_FRAMES / FPS), 4), "bar": s["bar"], "event": "hero_text_in", "detail": s["hero"]})
    for i, t in enumerate(kick_times()):
        rows.append({"time_s": round(t, 4), "bar": i // 4, "event": "heartbeat_kick", "detail": "beat " + str(i % 4 + 1)})
    rows.append({"time_s": round(EXIT_BAR * BAR, 4), "bar": EXIT_BAR, "event": "final_hit", "detail": "exit station, Dm resolve"})
    rows.sort(key=lambda r: (r["time_s"], r["event"]))
    return rows
