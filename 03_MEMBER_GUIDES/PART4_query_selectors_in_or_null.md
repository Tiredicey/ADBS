# Part 4: Query Selectors: $in, $or, null

**Commands:** `$in · $or · null`
**Soundbite (part opener):** "One field, many values. Many fields, any match."
**Source:** 08 Handout p.3; MongoDB Manual, Query for Null or Missing Fields
**Optional crowd line:** "Tayo ay nasa $null... wala pala." Riff on the 2025 'Tayo ay nasa fine dining restaurant' meme (DZRH News, 2025-12-31).

## What you do

1. Open `02_BLUEPRINT_DECK/ADBS_MongoDB_Cloud_BLUEPRINT.pptx` and find the slides tagged `PART 4 · BLUEPRINT`.
2. Put your name in every `OWNER: ____` tag and on the part divider slide.
3. On each command slide, run the command (seed script below) and paste the **real** output, or a screenshot, into the orange box.
4. On table and text slides, fill every blank from the handout pages named in the slide footer.
5. Replace each `______` bullet with your own one-line explanation. The speaker notes say what to cover.
6. Rehearse at 30-45 seconds per slide, and say the soundbite out loud.
7. Save the file as `part4_<yourname>.pptx` and submit it (see `04_SUBMIT_YOUR_PART/README.md`).

## Slide-by-slide checklist

### 1. $in: any of these values, one field
- Soundbite: "$in is a guest list for one field."
- Command:
```js
db.raffle.find({"ticket_no" : {"$in" : [725, 542, 390]}},
               {"_id" : 0})
```
- Cover: $in matches one field against a list. The raffle's winning tickets 725, 542 and 390 come back in one query. Say: $in is a guest list for one field.
- Source: 08 Handout p.3

### 2. $or: any of these conditions, any fields
- Soundbite: "$or: pass any one test."
- Command:
```js
db.raffle.find({"$or" : [{"ticket_no" : 725},
                         {"winner" : true}]},
               {"_id" : 0})
```
- Cover: $or takes an array of whole conditions, each on any field. Ticket 725 passes the first; ticket 111 passes the second because winner is true. One field, use $in; several fields, use $or. Say: $or, pass any one test.
- Source: 08 Handout p.3

### 3. Premise check: "$null" is not an operator
- Soundbite: "There is no $null. Write null."
- Command:
```js
db.raffle.find({"claimed_by" : {"$null" : true}})
```
- Cover: Our topic list said dollar-null. We tested it instead of assuming: the server answers unknown operator: $null. There is no such operator. You query with the plain value null. Say: There is no dollar-null. Write null.
- Source: mongosh 2.3.8 output; MongoDB Manual, Query for Null or Missing Fields

### 4. null matches null AND missing
- Soundbite: "null means 'null or not there'."
- Command:
```js
db.raffle.find({"claimed_by" : null},
               {"_id" : 0, "ticket_no" : 1})

// only documents where the value is really null
db.raffle.find({"claimed_by" : {"$type" : "null"}},
               {"_id" : 0, "ticket_no" : 1})
```
- Cover: {field: null} matches documents where the field is null and documents where it does not exist. Five tickets return; only 222 stores null. For real nulls only, use $type null. Ticket 333, claimed by Lia, never matches. Say: null means null or not there.
- Source: MongoDB Manual, Query for Null or Missing Fields (read 2026-10-30)

## Seed script: paste into mongosh to reproduce every output

Run the lines in order. Lines marked `expected error` or `premise test` are supposed to fail; the error message is the output you paste.

```js
use adbs_part4
db.raffle.drop(); db.raffle.insertMany([{"ticket_no":725,"winner":false},{"ticket_no":542,"winner":false},{"ticket_no":390,"winner":false},{"ticket_no":111,"winner":true},{"ticket_no":222,"winner":false,"claimed_by":null},{"ticket_no":333,"winner":false,"claimed_by":"Lia"}])
db.raffle.find({"ticket_no" : {"$in" : [725, 542, 390]}}, {"_id" : 0})
db.raffle.find({"$or" : [{"ticket_no" : 725}, {"winner" : true}]}, {"_id" : 0})
db.raffle.find({"claimed_by" : null}, {"_id" : 0, "ticket_no" : 1})
db.raffle.find({"claimed_by" : {"$type" : "null"}}, {"_id" : 0, "ticket_no" : 1})
db.raffle.find({"claimed_by" : {"$null" : true}})  // premise test
```

Reference outputs: `verification/results.json` (Verified live on MongoDB 8.0.4 + mongosh 2.3.8 (2026-10-30)). Yours should match, except ObjectId values, which differ on every run.

## Done when

- [ ] Every orange box shows real output (no typed guesses).
- [ ] No `____` blanks are left.
- [ ] Every slide still has its source footer.
- [ ] Speaker notes are rewritten in your own words.
- [ ] The file is submitted per `04_SUBMIT_YOUR_PART/README.md`.
