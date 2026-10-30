# Part 2: Find, Replace & Update

**Commands:** `findOne · replaceOne · updateOne · updateMany`
**Soundbite (part opener):** "Find it first. Then change it."
**Source:** 08 Handout p.1-3
**Optional crowd line:** "Kuya, natanggal!" for $unset. Parody of the 2025 'Kuya natanggal' meme (DZRH News, 2025-12-31).

## What you do

1. Open `02_BLUEPRINT_DECK/ADBS_MongoDB_Cloud_BLUEPRINT.pptx` and find the slides tagged `PART 2 · BLUEPRINT`.
2. Put your name in every `OWNER: ____` tag and on the part divider slide.
3. On each command slide, run the command (seed script below) and paste the **real** output, or a screenshot, into the orange box.
4. On table and text slides, fill every blank from the handout pages named in the slide footer.
5. Replace each `______` bullet with your own one-line explanation. The speaker notes say what to cover.
6. Rehearse at 30-45 seconds per slide, and say the soundbite out loud.
7. Save the file as `part2_<yourname>.pptx` and submit it (see `04_SUBMIT_YOUR_PART/README.md`).

## Slide-by-slide checklist

### 1. findOne: one document, or null
- Soundbite: "findOne gives one document. No match gives null."
- Command:
```js
db.users.findOne({"name" : "Joe"}, {"_id" : 0})

db.users.findOne({"name" : "Nobody"})
```
- Cover: findOne returns the first matching document, or null when nothing matches. Never a list. The second argument is a projection; _id 0 hides the _id. find, by contrast, returns every match. Say: findOne gives one document. No match gives null.
- Source: 08 Handout p.1-3

### 2. replaceOne: swap the whole document
- Soundbite: "replaceOne swaps the body. The _id stays."
- Command:
```js
var joe = db.users.findOne({"name" : "Joe"})
joe.relationships = {"friends" : joe.friends,
                     "enemies" : joe.enemies}
joe.username = joe.name
delete joe.friends; delete joe.enemies; delete joe.name
db.users.replaceOne({"name" : "Joe"}, joe)
```
- Cover: replaceOne replaces the whole matched document. The handout uses it for a schema migration: friends and enemies move into a relationships subdocument and name becomes username. Fields you leave out disappear. The _id is kept. Say: replaceOne swaps the body. The _id stays.
- Source: 08 Handout p.1-2

### 3. updateOne: change one field with $set / $unset
- Soundbite: "$set adds or changes. $unset removes."
- Command:
```js
db.users.updateOne({"name" : "John"},
  {"$set" : {"favorite book" : "Green Eggs and Ham"}})

db.users.updateOne({"name" : "John"},
  {"$unset" : {"favorite book" : 1}})
```
- Cover: updateOne takes a filter and a modifier. $set changes a field or creates it. $unset removes it. Only the first match changes. Read matchedCount and modifiedCount. Optional crowd line for $unset: Kuya, natanggal! Say: $set adds or changes. $unset removes.
- Source: 08 Handout p.2

### 4. updateMany: same change, every match
- Soundbite: "One rule, every match."
- Command:
```js
db.bday.updateMany({"birthday" : "10/13/1978"},
  {"$set" : {"gift" : "Happy Birthday!"}})
```
- Cover: updateMany has the same parameters as updateOne; only the number of changed documents differs. Three share the birthday, so matched and modified are 3. Say: One rule, every match.
- Source: 08 Handout p.3

### 5. Trap: updateOne without an operator
- Soundbite: "No $, no update."
- Command:
```js
db.users.updateOne({"name" : "John"}, {"age" : 25})
```
- Cover: Forget the dollar operator and updateOne refuses: Update document requires atomic operators. That protects you from replacing a whole document by accident. If replacing is the goal, use replaceOne. Say: No dollar, no update.
- Source: mongosh 2.3.8 output

## Seed script: paste into mongosh to reproduce every output

Run the lines in order. Lines marked `expected error` or `premise test` are supposed to fail; the error message is the output you paste.

```js
use adbs_part2
db.users.drop(); db.users.insertOne({"name" : "Joe", "friends" : 32, "enemies" : 2})
db.users.findOne({"name" : "Joe"}, {"_id" : 0})
db.users.findOne({"name" : "Nobody"})
var joe = db.users.findOne({"name" : "Joe"}); joe.relationships = {"friends" : joe.friends, "enemies" : joe.enemies}; joe.username = joe.name; delete joe.friends; delete joe.enemies; delete joe.name; db.users.replaceOne({"name" : "Joe"}, joe)
db.users.findOne({"username" : "Joe"}, {"_id" : 0})
db.users.insertOne({"name" : "John", "age" : 24, "location" : "Taytay"})
db.users.updateOne({"name" : "John"}, {"$set" : {"favorite book" : "Green Eggs and Ham"}})
db.users.updateOne({"name" : "John"}, {"$unset" : {"favorite book" : 1}})
db.bday.drop(); db.bday.insertMany([{"_id":1,"birthday":"10/13/1978"},{"_id":2,"birthday":"10/13/1978"},{"_id":3,"birthday":"10/13/1978"}])
db.bday.updateMany({"birthday" : "10/13/1978"}, {"$set" : {"gift" : "Happy Birthday!"}})
db.users.updateOne({"name" : "John"}, {"age" : 25})  // expected error
```

Reference outputs: `verification/results.json` (Verified live on MongoDB 8.0.4 + mongosh 2.3.8 (2026-10-30)). Yours should match, except ObjectId values, which differ on every run.

## Done when

- [ ] Every orange box shows real output (no typed guesses).
- [ ] No `____` blanks are left.
- [ ] Every slide still has its source footer.
- [ ] Speaker notes are rewritten in your own words.
- [ ] The file is submitted per `04_SUBMIT_YOUR_PART/README.md`.
