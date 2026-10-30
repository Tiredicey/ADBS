# Part 5: Querying Arrays

**Commands:** `array match · $push · $all · $size`
**Soundbite (part opener):** "Arrays answer like single values."
**Source:** 08 Handout p.4; MongoDB Manual, $push
**Optional crowd line:** "$all: kumpleto ang barkada." (original line, no meme reference)

## What you do

1. Open `02_BLUEPRINT_DECK/ADBS_MongoDB_Cloud_BLUEPRINT.pptx` and find the slides tagged `PART 5 · BLUEPRINT`.
2. Put your name in every `OWNER: ____` tag and on the part divider slide.
3. On each command slide, run the command (seed script below) and paste the **real** output, or a screenshot, into the orange box.
4. On table and text slides, fill every blank from the handout pages named in the slide footer.
5. Replace each `______` bullet with your own one-line explanation. The speaker notes say what to cover.
6. Rehearse at 30-45 seconds per slide, and say the soundbite out loud.
7. Save the file as `part5_<yourname>.pptx` and submit it (see `04_SUBMIT_YOUR_PART/README.md`).

## Slide-by-slide checklist

### 1. Match one element: just ask for it
- Soundbite: "Ask for banana, get every basket with a banana."
- Command:
```js
db.food.find({"fruit" : "banana"})
```
- Cover: Querying an array looks like querying a single value. fruit banana matches every document whose array contains banana anywhere: 1 and 3. For a position, use key dot index, like fruit.2. Say: Ask for banana, get every basket with a banana.
- Source: 08 Handout p.4

### 2. Insert an element: $push
- Soundbite: "$push adds to the end."
- Command:
```js
db.food.updateOne({"_id" : 2},
  {"$push" : {"fruit" : "mango"}})

// several at once: $each
db.food.updateOne({"_id" : 3},
  {"$push" : {"fruit" : {"$each" : ["grape", "lime"]}}})
```
- Cover: To insert an element into an existing array, use $push in an update; it appends to the end. Pushing an array directly would nest it as one element, so use $each for several values. This comes from the MongoDB manual; the handout only inserts whole documents that contain arrays. Say: $push adds to the end.
- Source: MongoDB Manual, $push (read 2026-10-30)

### 3. $all: must contain every listed element
- Soundbite: "$all: has them all, any order."
- Command:
```js
db.food.find({"fruit" : {"$all" : ["apple", "banana"]}})
```
- Cover: $all needs every listed element, in any order. Documents 1 and 3 have both. Document 2 has apple but no banana. Say: $all, has them all, any order.
- Source: 08 Handout p.4

### 4. $size: match by array length
- Soundbite: "$size counts. Exactly."
- Command:
```js
db.food.find({"fruit" : {"$size" : 4}})
// after the $push of mango

// ranges are not allowed
db.food.find({"fruit" : {"$size" : {"$gt" : 3}}})
```
- Cover: $size matches arrays with exactly that many elements. After pushing mango, document 2 has four, so $size 4 finds it. Trap: $size takes a number only; $size with $gt fails to parse. Say: $size counts. Exactly.
- Source: 08 Handout p.4; mongosh 2.3.8 output

## Seed script: paste into mongosh to reproduce every output

Run the lines in order. Lines marked `expected error` or `premise test` are supposed to fail; the error message is the output you paste.

```js
use adbs_part5
db.food.drop(); db.food.insertOne({"_id" : 1, "fruit" : ["apple", "banana", "peach"]}); db.food.insertOne({"_id" : 2, "fruit" : ["apple", "kumquat", "orange"]}); db.food.insertOne({"_id" : 3, "fruit" : ["cherry", "banana", "apple"]})
db.food.find({"fruit" : "banana"})
db.food.find({"fruit" : {"$all" : ["apple", "banana"]}})
db.food.find({"fruit.2" : "peach"})
db.food.find({"fruit" : {"$size" : 3}}).count()
db.food.updateOne({"_id" : 2}, {"$push" : {"fruit" : "mango"}})
db.food.find({"fruit" : {"$size" : 4}})
db.food.find({"fruit" : {"$size" : {"$gt" : 3}}})  // expected error
db.food.updateOne({"_id" : 3}, {"$push" : {"fruit" : {"$each" : ["grape", "lime"]}}}); db.food.findOne({"_id" : 3})
```

Reference outputs: `verification/results.json` (Verified live on MongoDB 8.0.4 + mongosh 2.3.8 (2026-10-30)). Yours should match, except ObjectId values, which differ on every run.

## Done when

- [ ] Every orange box shows real output (no typed guesses).
- [ ] No `____` blanks are left.
- [ ] Every slide still has its source footer.
- [ ] Speaker notes are rewritten in your own words.
- [ ] The file is submitted per `04_SUBMIT_YOUR_PART/README.md`.
