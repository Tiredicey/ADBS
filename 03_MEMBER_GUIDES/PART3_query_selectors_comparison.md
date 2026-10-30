# Part 3: Query Selectors: Comparison

**Commands:** `$lt · $lte · $gt · $gte`
**Soundbite (part opener):** "Less, less-or-equal, greater, greater-or-equal."
**Source:** 08 Handout p.3
**Optional crowd line:** "Sobrang strict ng $gt." Riff on the 2025 'Sobrang Latina' catchphrase (DZRH News, 2025-12-31).

## What you do

1. Open `02_BLUEPRINT_DECK/ADBS_MongoDB_Cloud_BLUEPRINT.pptx` and find the slides tagged `PART 3 · BLUEPRINT`.
2. Put your name in every `OWNER: ____` tag and on the part divider slide.
3. On each command slide, run the command (seed script below) and paste the **real** output, or a screenshot, into the orange box.
4. On table and text slides, fill every blank from the handout pages named in the slide footer.
5. Replace each `______` bullet with your own one-line explanation. The speaker notes say what to cover.
6. Rehearse at 30-45 seconds per slide, and say the soundbite out loud.
7. Save the file as `part3_<yourname>.pptx` and submit it (see `04_SUBMIT_YOUR_PART/README.md`).

## Slide-by-slide checklist

### 1. Four operators, four symbols
- Soundbite: "The e means equal is allowed."
- Cover: Four comparison operators. lt and gt are strict; add an e and equality counts. The right column shows ages 17, 18 and 24 against 18. Say: The e means equal is allowed.
- Source: 08 Handout p.3

### 2. $lt and $lte
- Soundbite: "18 is out with $lt, in with $lte."
- Command:
```js
db.students.find({"age" : {"$lt" : 18}}, {"_id" : 0})

db.students.find({"age" : {"$lte" : 18}}, {"_id" : 0})
```
- Cover: One letter apart. $lt 18 returns only Ana, 17. $lte 18 adds Ben, exactly 18. Say: 18 is out with lt, in with lte.
- Source: 08 Handout p.3

### 3. $gt and $gte
- Soundbite: "30 is out with $gt, in with $gte."
- Command:
```js
db.students.find({"age" : {"$gt" : 30}}, {"_id" : 0})

db.students.find({"age" : {"$gte" : 30}}, {"_id" : 0})
```
- Cover: Mirror image. $gt 30 returns only Eli, 31. $gte 30 adds Dan, exactly 30. Say: 30 is out with gt, in with gte.
- Source: 08 Handout p.3

### 4. Combine them: a range
- Soundbite: "Two operators, one field, one range."
- Command:
```js
db.students.find({"age" : {"$gte" : 18, "$lte" : 30}},
                 {"_id" : 0})
```
- Cover: Two operators in the same field document must both be true. The handout's between 18 and 30 query returns Ben, Cara and Dan. Both ends count because of gte and lte. Say: Two operators, one field, one range.
- Source: 08 Handout p.3

### 5. Trap: a number stored as text
- Soundbite: ""20" is text, not twenty."
- Command:
```js
// Fay's age was typed as a string
db.students.insertOne({"name" : "Fay", "age" : "20"})
db.students.find({"age" : {"$gte" : 18}},
                 {"_id" : 0, "name" : 1})
```
- Cover: Fay's age is the string 20. $gte 18 compares numbers to numbers, so Fay never appears. No error, just a missing row: the dangerous kind of bug. Say: Quote-20 is text, not twenty.
- Source: mongosh 2.3.8 output

## Seed script: paste into mongosh to reproduce every output

Run the lines in order. Lines marked `expected error` or `premise test` are supposed to fail; the error message is the output you paste.

```js
use adbs_part3
db.students.drop(); db.students.insertMany([{"name":"Ana","age":17},{"name":"Ben","age":18},{"name":"Cara","age":24},{"name":"Dan","age":30},{"name":"Eli","age":31}])
db.students.find({"age" : {"$lt" : 18}}, {"_id" : 0})
db.students.find({"age" : {"$lte" : 18}}, {"_id" : 0})
db.students.find({"age" : {"$gt" : 30}}, {"_id" : 0})
db.students.find({"age" : {"$gte" : 30}}, {"_id" : 0})
db.students.find({"age" : {"$gte" : 18, "$lte" : 30}}, {"_id" : 0})
db.students.insertOne({"name":"Fay","age":"20"}); db.students.find({"age" : {"$gte" : 18}}, {"_id" : 0, "name" : 1})  // trap
```

Reference outputs: `verification/results.json` (Verified live on MongoDB 8.0.4 + mongosh 2.3.8 (2026-10-30)). Yours should match, except ObjectId values, which differ on every run.

## Done when

- [ ] Every orange box shows real output (no typed guesses).
- [ ] No `____` blanks are left.
- [ ] Every slide still has its source footer.
- [ ] Speaker notes are rewritten in your own words.
- [ ] The file is submitted per `04_SUBMIT_YOUR_PART/README.md`.
