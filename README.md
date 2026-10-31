# ADBS: MongoDB Commands & Cloud Computing

IT2003 Advanced Database Systems group presentation. Content follows the 07, 08 and 09 handouts only.

## Files

| File | What it is | Who gets it |
|---|---|---|
| `02_GROUP_DECK/ADBS_GROUP_DECK.pptx` | Shared deck. Part 1 finished; Parts 2-8 have orange paste boxes and blanks. Slide 2 (HELPER) tells members what to do. | Upload to OneDrive, share the edit link |
| `01_FULL_DECK/ADBS_FULL_answer_key.pptx` | Every part finished, with verbatim scripts in the speaker notes | Group leader only |
| `video/ADBS_opener_deck.mp4` | 35 s opener, 9.0 MB, ready to insert into PowerPoint | Optional |
| `video/ADBS_freefall_*.mp4` | Full-quality opener (landscape and vertical) | Optional |
| `verification/` | Runs every command on a real MongoDB 8.0.4 server; `results.json` holds the raw outputs | Proof the outputs are real |
| `tools/audit_deck.py` | Measures font sizes, words per slide and WCAG contrast | Checks |

## Design rules (checked by `tools/audit_deck.py`)

- Audience text at least 28 pt; code and output in Courier New 28 pt, 52 characters a line at most.
- Commands that change data are shown as 1 BEFORE, 2 COMMAND and REPLY, 3 AFTER, with added text highlighted and removed text struck through.
- Outputs are never cut. Line breaks may move; `src/reflow.py` checks that every character is kept.
- Every colour pair passes WCAG AA 4.5:1.
- Each part's script fits 3 minutes: the longest is 167 s at a slow 100 words per minute.
- Edits the user made to the shared deck on 2026-10-31 are built in (`SHOW_VIDEO`, `SHOW_REFERENCES`, `REMOVED_SLIDES` in `src/build_deck.py`). No name, presenter or date blanks anywhere.

## Rebuild

```bash
bash tools/setup_env.sh                                   # python-pptx + Arial/Courier font aliases
bash tools/setup_mongo.sh                                 # local MongoDB 8.0.4 + mongosh 2.3.8
PATH=$HOME/bin:$PATH python3 verification/run_commands.py # re-run every command
python3 src/build_deck.py                                 # build both decks
python3 tools/audit_deck.py 01_FULL_DECK/ADBS_FULL_answer_key.pptx
```

## Sources

STI IT2003 07, 08 and 09 Handouts, and the references they cite.
