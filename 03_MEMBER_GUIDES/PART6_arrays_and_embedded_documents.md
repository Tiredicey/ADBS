# Part 6: Arrays & Embedded Documents

**Commands:** `$slice · dot notation · embedded documents`
**Soundbite (part opener):** "Trim what you see. Reach inside with a dot."
**Source:** 08 Handout p.2, p.4
**Optional crowd line:** "Sierra Madre baddie: shields the whole document." Riff on the 2025 'Sierra Madre Baddie' meme (DZRH News, 2025-12-31).

## What you do

1. Open `02_BLUEPRINT_DECK/ADBS_MongoDB_Cloud_BLUEPRINT.pptx` and find the slides tagged `PART 6 · BLUEPRINT`.
2. Put your name in every `OWNER: ____` tag and on the part divider slide.
3. On each command slide, run the command (seed script below) and paste the **real** output, or a screenshot, into the orange box.
4. On table and text slides, fill every blank from the handout pages named in the slide footer.
5. Replace each `______` bullet with your own one-line explanation. The speaker notes say what to cover.
6. Rehearse at 30-45 seconds per slide, and say the soundbite out loud.
7. Save the file as `part6_<yourname>.pptx` and submit it (see `04_SUBMIT_YOUR_PART/README.md`).

## Slide-by-slide checklist

### 1. $slice: first N or last N elements
- Soundbite: "Positive from the front, negative from the back."
- Command:
```js
// a post with 40 comments: c1 ... c40
db.posts.findOne({"_id" : 1}, {"comments" : {"$slice" : 3}})

db.posts.findOne({"_id" : 1}, {"comments" : {"$slice" : -3}})
```
- Cover: $slice returns part of an array, from the projection. 3 gives the first three comments; minus 3 the last three. The document still stores all 40. Say: Positive from the front, negative from the back.
- Source: 08 Handout p.4

### 2. $slice with [skip, limit]: a page
- Soundbite: "Skip 23, take 10."
- Command:
```js
db.posts.findOne({"_id" : 1},
  {"comments" : {"$slice" : [23, 10]}})
```
- Cover: Two numbers mean skip then limit. Skip 23, take 10: c24 through c33, exactly as the handout says. A shorter array just returns what exists. That is how you page through comments. Say: Skip 23, take 10.
- Source: 08 Handout p.4

### 3. Embedded documents: query with dot notation
- Soundbite: "Use the dot to reach inside."
- Command:
```js
db.people.find({"name.first" : "John",
                "name.last" : "Escalona"}, {"_id" : 0})

// update inside a subdocument
db.people.updateOne({"name.first" : "John"},
  {"$set" : {"name.last" : "Tagayon"}})
```
- Cover: An embedded document is a document inside a document. Reach its fields with quoted dot notation: name.first, name.last. The same dot works in $set, like the handout's author.name update. Say: Use the dot to reach inside.
- Source: 08 Handout p.2, p.4

### 4. Trap: whole-document match is exact and ordered
- Soundbite: "Same fields, wrong order, zero results."
- Command:
```js
// stored as {first: "John", last: "Escalona"}
db.people.find({"name" : {"first" : "John",
                          "last" : "Escalona"}}).count()

db.people.find({"name" : {"last" : "Escalona",
                          "first" : "John"}}).count()
```
- Cover: Matching the whole embedded document compares it exactly, field order included. Swap first and last and you get zero. Dot notation ignores order, which is why we prefer it. Say: Same fields, wrong order, zero results.
- Source: mongosh 2.3.8 output

## Seed script: paste into mongosh to reproduce every output

Run the lines in order. Lines marked `expected error` or `premise test` are supposed to fail; the error message is the output you paste.

```js
use adbs_part6
db.posts.drop(); db.posts.insertOne({"_id" : 1, "title" : "ADBS", "comments" : Array.from({length : 40}, (_, i) => "c" + (i + 1))})
db.posts.findOne({"_id" : 1}, {"comments" : {"$slice" : 3}})
db.posts.findOne({"_id" : 1}, {"comments" : {"$slice" : -3}})
db.posts.findOne({"_id" : 1}, {"comments" : {"$slice" : [23, 10]}})
db.people.drop(); db.people.insertOne({"name" : {"first" : "John", "last" : "Escalona"}, "age" : 45})
db.people.find({"name.first" : "John", "name.last" : "Escalona"}, {"_id" : 0})
db.people.find({"name" : {"first" : "John", "last" : "Escalona"}}).count()
db.people.find({"name" : {"last" : "Escalona", "first" : "John"}}).count()  // trap
db.people.updateOne({"name.first" : "John"}, {"$set" : {"name.last" : "Tagayon"}})
```

Reference outputs: `verification/results.json` (Verified live on MongoDB 8.0.4 + mongosh 2.3.8 (2026-10-30)). Yours should match, except ObjectId values, which differ on every run.

## Done when

- [ ] Every orange box shows real output (no typed guesses).
- [ ] No `____` blanks are left.
- [ ] Every slide still has its source footer.
- [ ] Speaker notes are rewritten in your own words.
- [ ] The file is submitted per `04_SUBMIT_YOUR_PART/README.md`.
