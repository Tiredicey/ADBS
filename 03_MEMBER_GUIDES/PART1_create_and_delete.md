# Part 1: Create & Delete

**Status: COMPLETE.** Part 1 is the worked example. Copy its pattern for your own part.

**Commands:** `insertOne · insertMany · deleteOne · deleteMany`
**Soundbite (part opener):** "Documents in, documents out."
**Source:** 07 Handout p.2-4; 08 Handout p.1
**Optional crowd line:** "What haffen, collection?" after deleteMany({}). Parody of 'What haffen Vella?', a 2013 TV clip that resurfaced in 2025 (DZRH News, 2025-12-31).

## What you do

1. Open `02_BLUEPRINT_DECK/ADBS_MongoDB_Cloud_BLUEPRINT.pptx` and find the slides tagged `PART 1 · BLUEPRINT`.
2. Put your name in every `OWNER: ____` tag and on the part divider slide.
3. On each command slide, run the command (seed script below) and paste the **real** output, or a screenshot, into the orange box.
4. On table and text slides, fill every blank from the handout pages named in the slide footer.
5. Replace each `______` bullet with your own one-line explanation. The speaker notes say what to cover.
6. Rehearse at 30-45 seconds per slide, and say the soundbite out loud.
7. Save the file as `part1_<yourname>.pptx` and submit it (see `04_SUBMIT_YOUR_PART/README.md`).

## Slide-by-slide checklist

### 1. Same idea, new names
- Soundbite: "Tables are collections. Rows are documents."
- Cover: Lock the vocabulary first. The handout's Table 2 maps SQL to MongoDB: tables become collections, rows become documents, columns become fields. A collection does not force every document to have the same fields. Every document gets a unique _id. Say: Tables are collections. Rows are documents.
- Source: 07 Handout p.2-3, Table 2

### 2. insertOne: add one document
- Soundbite: "One document in. MongoDB hands it an _id."
- Command:
```js
db.movies.insertOne({"title" : "Stand by Me"})
```
- Cover: insertOne adds a single document. We gave no _id, so MongoDB created the ObjectId in the output. The collection did not exist before this line; MongoDB creates it on the first insert. Say: One document in. MongoDB hands it an _id.
- Source: 08 Handout p.1; 07 Handout p.3

### 3. insertMany: add several at once
- Soundbite: "Many documents, one trip."
- Command:
```js
db.movies.insertMany([
  {"title" : "Ghostbusters"},
  {"title" : "E.T."},
  {"title" : "Blade Runner"}
])
```
- Cover: insertMany takes an array. One call, three documents, three ids back, numbered 0, 1, 2 in array order. Say: Many documents, one trip.
- Source: 08 Handout p.1

### 4. Ordered vs unordered: what happens on an error
- Soundbite: "Ordered stops at the error. Unordered keeps going."
- Command:
```js
// unordered: duplicate _id 4 in the middle
db.movies.insertMany([
  {"_id" : 3, "title" : "Sixteen Candles"},
  {"_id" : 4, "title" : "The Terminator"},
  {"_id" : 4, "title" : "The Princess Bride"},
  {"_id" : 5, "title" : "Scarface"}
], {"ordered" : false})

// ordered (the default)
db.ordered.insertMany([{"_id":1}, {"_id":1}, {"_id":2}])
db.ordered.countDocuments()
```
- Cover: Quiz favorite. Same duplicate-key error, two outcomes. Unordered tries every document, so 3, 4 and 5 land and only the second 4 fails. Ordered is the default and stops at the first error, so the next document never goes in. Real server counts: 3 and 1. Say: Ordered stops at the error. Unordered keeps going.
- Source: 08 Handout p.1

### 5. deleteOne: remove the first match
- Soundbite: "deleteOne removes one. Even if many match."
- Command:
```js
// two documents match y: 1985
db.scratch2.insertMany([{_id:1, y:1985}, {_id:2, y:1985}])
db.scratch2.deleteOne({y : 1985})
db.scratch2.find()
```
- Cover: deleteOne deletes at most one document, the first match, even when more match. Two documents had y 1985; one is left. The safest filter is _id, which is unique, like the handout's deleteOne on _id 4. Say: deleteOne removes one. Even if many match.
- Source: 08 Handout p.1

### 6. deleteMany: remove every match
- Soundbite: "deleteMany clears every match."
- Command:
```js
db.movies.deleteMany({"year" : 1985})
```
- Cover: deleteMany removes every document that matches. Two movies had year 1985; deletedCount is 2. Always read deletedCount. Say: deleteMany clears every match.
- Source: 08 Handout p.1

### 7. Trap: an empty filter deletes everything
- Soundbite: "Empty filter, empty collection."
- Command:
```js
db.scratch.insertMany([{a:1}, {a:2}, {a:3}])
db.scratch.deleteMany({})

// 07 Handout uses the old method:
db.movies.remove({"_id" : 5})
```
- Cover: Two traps. deleteMany with an empty filter wipes the collection; deletedCount 3. And the 07 handout's remove still works, but mongosh prints a deprecation warning pointing to deleteOne or deleteMany. Optional crowd line: What haffen, collection? Say: Empty filter, empty collection.
- Source: 07 Handout p.4; mongosh 2.3.8 output

## Seed script: paste into mongosh to reproduce every output

Run the lines in order. Lines marked `expected error` or `premise test` are supposed to fail; the error message is the output you paste.

```js
use adbs_part1
db.movies.insertOne({"title" : "Stand by Me"})
db.movies.insertMany([{"title" : "Ghostbusters"}, {"title" : "E.T."}, {"title" : "Blade Runner"}])
db.movies.insertMany([{"_id" : 3, "title" : "Sixteen Candles"}, {"_id" : 4, "title" : "The Terminator"}, {"_id" : 4, "title" : "The Princess Bride"}, {"_id" : 5, "title" : "Scarface"}], {"ordered" : false})  // expected error
db.movies.countDocuments({"_id" : {"$in" : [3,4,5]}})
db.ordered.drop(); db.ordered.insertMany([{"_id" : 1}, {"_id" : 1}, {"_id" : 2}])  // expected error
db.ordered.countDocuments()
db.movies.deleteOne({"_id" : 4})
db.movies.updateOne({"_id":3},{"$set":{"year":1984}}); db.movies.insertMany([{"_id":0,"title":"Top Gun","year":1986},{"_id":1,"title":"Back to the Future","year":1985},{"_id":2,"title":"The Goonies","year":1985}])
db.movies.deleteMany({"year" : 1985})
db.movies.remove({"_id" : 5})  // deprecated
db.scratch.drop(); db.scratch.insertMany([{a:1},{a:2},{a:3}]); db.scratch.deleteMany({})  // trap
db.scratch2.drop(); db.scratch2.insertMany([{_id:1,y:1985},{_id:2,y:1985}]); db.scratch2.deleteOne({y:1985}); db.scratch2.find()
```

Reference outputs: `verification/results.json` (Verified live on MongoDB 8.0.4 + mongosh 2.3.8 (2026-10-30)). Yours should match, except ObjectId values, which differ on every run.

## Done when

- [ ] Every orange box shows real output (no typed guesses).
- [ ] No `____` blanks are left.
- [ ] Every slide still has its source footer.
- [ ] Speaker notes are rewritten in your own words.
- [ ] The file is submitted per `04_SUBMIT_YOUR_PART/README.md`.
