# ADBS: MongoDB Commands & Cloud Computing

IT2003 Advanced Database Systems group presentation. Content follows the 07, 08 and 09 handouts only.

## Files

| File | What it is | Who gets it |
|---|---|---|
| `02_GROUP_DECK/ADBS_GROUP_DECK.pptx` | Shared deck. Part 1 finished; Parts 2-8 have orange paste boxes and blanks. Slide 2 (HELPER) tells members what to do. | Upload to OneDrive, share the edit link |
| `01_FULL_DECK/ADBS_FULL_answer_key.pptx` | Every part finished, with verbatim scripts in the speaker notes | Group leader only |
| `verification/` | Runs every command on a real MongoDB 8.0.4 server; `results.json` holds the raw outputs | Proof the outputs are real |
| `tools/audit_deck.py` | Measures font sizes, words per slide and WCAG contrast | Checks |

## Design rules (checked by `tools/audit_deck.py`)

- Audience text at least 28 pt; code and output in Courier New 28 pt, 52 characters a line at most.
- Commands that change data are shown as 1 BEFORE, 2 COMMAND and REPLY, 3 AFTER, with added text highlighted and removed text struck through.
- Outputs are never cut. Line breaks may move; `src/reflow.py` checks that every character is kept.
- Every colour pair passes WCAG AA 4.5:1.
- Each part's script fits 3 minutes: the longest is 167 s at a slow 100 words per minute.
- Edits the user made to the shared deck on 2026-10-31 are built in (`SHOW_VIDEO`, `SHOW_REFERENCES`, `REMOVED_SLIDES` in `src/build_deck.py`). No name, presenter or date blanks anywhere.

## Opener video

Scratched on 2026-10-31 at the group's request. The last version (render scripts, score, measurements) is in git history at commit `b1e4eb7`.

## Frames on the part dividers (private copies only)

Added on 2026-10-31 at the user's request. Each of the 8 part dividers can show one still on its right edge (3.2 x 6.55 in), with a credit line under it. Content slides stay plain.

- Parts 1 to 6: stills from the Cowboy Bebop opening "Tank!" (© 1998 Sunrise Inc.) at 33.22, 77.80, 62.55, 47.13, 54.74 and 67.67 s.
- Parts 7 and 8: character stills from The Orbital Children trailer (Netflix) at 53.00 and 51.20 s.
- Every still was chosen to have no burned-in subtitles or credits.
- The stills are copyrighted. `build/frames/` and `03_WITH_FRAMES/` are gitignored, so they never reach this public repo. The decks in `01_FULL_DECK/` and `02_GROUP_DECK/` contain no pictures.

To make the frame decks (this needs the two uploaded videos):

```bash
python3 tools/extract_frames.py [folder-with-videos]   # writes build/frames/part1..8.jpg
python3 src/build_deck.py --frames                     # also writes 03_WITH_FRAMES/*_FRAMES.pptx
```

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
