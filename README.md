# ADBS: MongoDB Commands & Cloud Computing

IT2003 Advanced Database Systems group presentation, covering the 07, 08 and 09 handouts.

Every MongoDB command in the deck was run on a real server (MongoDB 8.0.4, mongosh 2.3.8), and the slides show the real output.

## Where everything is

| You are... | Open this |
|---|---|
| **Presenting, no time to prepare** | `01_FULL_DECK/ADBS_MongoDB_Cloud_FULL.pptx`: complete, all 8 parts |
| **A member building your part** | `03_MEMBER_GUIDES/PART<N>_*.md`, then `02_BLUEPRINT_DECK/ADBS_MongoDB_Cloud_BLUEPRINT.pptx` |
| **Handing in your finished part** | `04_SUBMIT_YOUR_PART/README.md` (browser upload, no Git needed) |
| **The owner assembling the final deck** | `05_FINAL_SUBMISSION/README.md` |
| **Playing the opener video** | `video/ADBS_freefall_1920x1080.mp4` (projector) or `video/ADBS_freefall_1080x1920.mp4` (phones) |
| **Checking that the outputs are real** | `verification/results.json`; rerun with `verification/run_commands.py` |

## The two decks

- **FULL** (49 slides): every part is finished, with real outputs, soundbites, speaker notes and sources.
- **BLUEPRINT** (49 slides): Part 1 is the finished example. Parts 2-8 keep the commands, titles, soundbites and sources, but their outputs, table cells and explanations are orange blanks for each owner to fill. The speaker notes say what to cover.

## Parts

| # | Topic | Commands |
|---|---|---|
| 1 | Create & Delete | insertOne, insertMany (ordered/unordered), deleteOne, deleteMany |
| 2 | Find, Replace & Update | findOne, replaceOne, updateOne ($set/$unset), updateMany |
| 3 | Query Selectors: Comparison | $lt, $lte, $gt, $gte |
| 4 | Query Selectors: $in, $or, null | $in, $or, null (there is no `$null` operator; the server rejects it) |
| 5 | Querying Arrays | array match, $push / $each, $all, $size |
| 6 | Arrays & Embedded Documents | $slice, dot notation, embedded documents |
| 7 | Cloud Computing & Implementation Types | public, private, hybrid; MongoDB Atlas example |
| 8 | Cloud Service Types & Benefits | SaaS, PaaS, IaaS; 10 benefits |

## Corrections found by running the commands

1. **`$null` is not a MongoDB operator.** `find({f: {$null: true}})` returns `MongoServerError: unknown operator: $null`. Use `{f: null}`, which matches null *and* missing fields, or `{f: {$type: "null"}}` for null only.
2. **`remove()` is deprecated** (the 07 Handout uses it). mongosh prints a warning and points to `deleteOne` / `deleteMany`.
3. **Inserting an element into an array** (`$push`) is not in the 08 Handout. It is sourced from the MongoDB Manual.

## Opener video

About 35 seconds at 30 fps, 140 BPM. The camera free-falls through a derelict, code-drawn orbital station, and each part's command appears on a bar line. A heartbeat kick plays on every beat until the fall exits over a planet horizon. The score is synthesized from scratch (no samples) and mastered to -14 LUFS / -1.5 dBTP. There are no strobes or flashes.

## Rebuild

```bash
pip install python-pptx numpy scipy soundfile pillow
python3 verification/run_commands.py   # needs a local mongod + mongosh on PATH
python3 src/build_deck.py              # both decks
python3 src/build_guides.py            # member guides
python3 video/score.py && python3 video/master.py
python3 video/render.py 1920 1080      # then mux with build/score_master.wav
```

## Sources

- STI IT2003 07, 08 and 09 Handouts.
- Chodorow, Brazil & Bradshaw (2019), *MongoDB: The Definitive Guide*, 3rd ed.
- MongoDB Manual: Query for Null or Missing Fields; `$push` (accessed 2026-10-30).
- Meme references, in speaker notes only: DZRH News, 2025-12-31, "LOL, Relate, Repeat: How these 15 viral memes defined the Philippines in 2025".
