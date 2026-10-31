# ADBS: MongoDB Commands & Cloud Computing

IT2003 Advanced Database Systems group presentation. Content follows the 07, 08 and 09 handouts only.

## Files

| File | What it is | Who gets it |
|---|---|---|
| `02_GROUP_DECK/ADBS_GROUP_DECK.pptx` | The shared deck. Part 1 is finished; Parts 2-8 have orange boxes and blanks for each member to fill. Slide 2 tells members exactly what to do. | Upload to OneDrive or Google Drive and share the edit link with the group |
| `01_FULL_DECK/ADBS_FULL_answer_key.pptx` | Every part finished. Use it to check members' work, or as a backup. | Group leader only |
| `video/ADBS_freefall_1920x1080.mp4` | 35-second opener for the projector | Optional |
| `video/ADBS_freefall_1080x1920.mp4` | Same opener, vertical, for phones | Optional |
| `verification/` | Script that ran every command on a real MongoDB 8.0.4 server, plus the raw results | Proof that the outputs are real |

## Rebuild

```bash
pip install python-pptx
python3 verification/run_commands.py   # needs a local mongod + mongosh on PATH
python3 src/build_deck.py              # builds both decks
```

## Sources

STI IT2003 07, 08 and 09 Handouts, and the references they cite.
