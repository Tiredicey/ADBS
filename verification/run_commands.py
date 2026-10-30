import json
import shutil
import subprocess
from pathlib import Path

MONGOSH = shutil.which("mongosh") or str(Path.home() / "bin" / "mongosh")
OUT = Path(__file__).resolve().parent / "results.json"

STEPS = [
    ("p0_reset", 'db.dropDatabase()', ""),
    ("p1_insertOne", 'db.movies.insertOne({"title" : "Stand by Me"})', ""),
    ("p1_insertMany", 'db.movies.insertMany([{"title" : "Ghostbusters"}, {"title" : "E.T."}, {"title" : "Blade Runner"}])', ""),
    ("p1_unordered", 'db.movies.insertMany([{"_id" : 3, "title" : "Sixteen Candles"}, {"_id" : 4, "title" : "The Terminator"}, {"_id" : 4, "title" : "The Princess Bride"}, {"_id" : 5, "title" : "Scarface"}], {"ordered" : false})', "expected error"),
    ("p1_count_after_unordered", 'db.movies.countDocuments({"_id" : {"$in" : [3,4,5]}})', ""),
    ("p1_ordered_reset", 'db.ordered.drop(); db.ordered.insertMany([{"_id" : 1}, {"_id" : 1}, {"_id" : 2}])', "expected error"),
    ("p1_ordered_count", 'db.ordered.countDocuments()', ""),
    ("p1_deleteOne", 'db.movies.deleteOne({"_id" : 4})', ""),
    ("p1_seed_years", 'db.movies.updateOne({"_id":3},{"$set":{"year":1984}}); db.movies.insertMany([{"_id":0,"title":"Top Gun","year":1986},{"_id":1,"title":"Back to the Future","year":1985},{"_id":2,"title":"The Goonies","year":1985}])', ""),
    ("p1_deleteMany", 'db.movies.deleteMany({"year" : 1985})', ""),
    ("p1_remove_deprecated", 'db.movies.remove({"_id" : 5})', "deprecated"),
    ("p1_deleteMany_all", 'db.scratch.drop(); db.scratch.insertMany([{a:1},{a:2},{a:3}]); db.scratch.deleteMany({})', "trap"),
    ("p1_deleteOne_first", 'db.scratch2.drop(); db.scratch2.insertMany([{_id:1,y:1985},{_id:2,y:1985}]); db.scratch2.deleteOne({y:1985}); db.scratch2.find()', ""),
    ("p2_seed", 'db.users.drop(); db.users.insertOne({"name" : "Joe", "friends" : 32, "enemies" : 2})', ""),
    ("p2_findOne", 'db.users.findOne({"name" : "Joe"}, {"_id" : 0})', ""),
    ("p2_findOne_none", 'db.users.findOne({"name" : "Nobody"})', ""),
    ("p2_replaceOne", 'var joe = db.users.findOne({"name" : "Joe"}); joe.relationships = {"friends" : joe.friends, "enemies" : joe.enemies}; joe.username = joe.name; delete joe.friends; delete joe.enemies; delete joe.name; db.users.replaceOne({"name" : "Joe"}, joe)', ""),
    ("p2_after_replace", 'db.users.findOne({"username" : "Joe"}, {"_id" : 0})', ""),
    ("p2_seed2", 'db.users.insertOne({"name" : "John", "age" : 24, "location" : "Taytay"})', ""),
    ("p2_updateOne_set", 'db.users.updateOne({"name" : "John"}, {"$set" : {"favorite book" : "Green Eggs and Ham"}})', ""),
    ("p2_updateOne_unset", 'db.users.updateOne({"name" : "John"}, {"$unset" : {"favorite book" : 1}})', ""),
    ("p2_updateMany_seed", 'db.bday.drop(); db.bday.insertMany([{"_id":1,"birthday":"10/13/1978"},{"_id":2,"birthday":"10/13/1978"},{"_id":3,"birthday":"10/13/1978"}])', ""),
    ("p2_updateMany", 'db.bday.updateMany({"birthday" : "10/13/1978"}, {"$set" : {"gift" : "Happy Birthday!"}})', ""),
    ("p2_updateOne_operatorless", 'db.users.updateOne({"name" : "John"}, {"age" : 25})', "expected error"),
    ("p3_seed", 'db.students.drop(); db.students.insertMany([{"name":"Ana","age":17},{"name":"Ben","age":18},{"name":"Cara","age":24},{"name":"Dan","age":30},{"name":"Eli","age":31}])', ""),
    ("p3_lt", 'db.students.find({"age" : {"$lt" : 18}}, {"_id" : 0})', ""),
    ("p3_lte", 'db.students.find({"age" : {"$lte" : 18}}, {"_id" : 0})', ""),
    ("p3_gt", 'db.students.find({"age" : {"$gt" : 30}}, {"_id" : 0})', ""),
    ("p3_gte", 'db.students.find({"age" : {"$gte" : 30}}, {"_id" : 0})', ""),
    ("p3_range", 'db.students.find({"age" : {"$gte" : 18, "$lte" : 30}}, {"_id" : 0})', ""),
    ("p3_string_trap", 'db.students.insertOne({"name":"Fay","age":"20"}); db.students.find({"age" : {"$gte" : 18}}, {"_id" : 0, "name" : 1})', "trap"),
    ("p4_seed", 'db.raffle.drop(); db.raffle.insertMany([{"ticket_no":725,"winner":false},{"ticket_no":542,"winner":false},{"ticket_no":390,"winner":false},{"ticket_no":111,"winner":true},{"ticket_no":222,"winner":false,"claimed_by":null},{"ticket_no":333,"winner":false,"claimed_by":"Lia"}])', ""),
    ("p4_in", 'db.raffle.find({"ticket_no" : {"$in" : [725, 542, 390]}}, {"_id" : 0})', ""),
    ("p4_or", 'db.raffle.find({"$or" : [{"ticket_no" : 725}, {"winner" : true}]}, {"_id" : 0})', ""),
    ("p4_null", 'db.raffle.find({"claimed_by" : null}, {"_id" : 0, "ticket_no" : 1})', ""),
    ("p4_null_strict", 'db.raffle.find({"claimed_by" : {"$type" : "null"}}, {"_id" : 0, "ticket_no" : 1})', ""),
    ("p4_dollar_null", 'db.raffle.find({"claimed_by" : {"$null" : true}})', "premise test"),
    ("p5_seed", 'db.food.drop(); db.food.insertOne({"_id" : 1, "fruit" : ["apple", "banana", "peach"]}); db.food.insertOne({"_id" : 2, "fruit" : ["apple", "kumquat", "orange"]}); db.food.insertOne({"_id" : 3, "fruit" : ["cherry", "banana", "apple"]})', ""),
    ("p5_scalar", 'db.food.find({"fruit" : "banana"})', ""),
    ("p5_all", 'db.food.find({"fruit" : {"$all" : ["apple", "banana"]}})', ""),
    ("p5_index", 'db.food.find({"fruit.2" : "peach"})', ""),
    ("p5_size", 'db.food.find({"fruit" : {"$size" : 3}}).count()', ""),
    ("p5_push", 'db.food.updateOne({"_id" : 2}, {"$push" : {"fruit" : "mango"}})', ""),
    ("p5_size_after_push", 'db.food.find({"fruit" : {"$size" : 4}})', ""),
    ("p5_size_range_trap", 'db.food.find({"fruit" : {"$size" : {"$gt" : 3}}})', "expected error"),
    ("p5_push_each", 'db.food.updateOne({"_id" : 3}, {"$push" : {"fruit" : {"$each" : ["grape", "lime"]}}}); db.food.findOne({"_id" : 3})', ""),
    ("p6_seed", 'db.posts.drop(); db.posts.insertOne({"_id" : 1, "title" : "ADBS", "comments" : Array.from({length : 40}, (_, i) => "c" + (i + 1))})', ""),
    ("p6_slice_first", 'db.posts.findOne({"_id" : 1}, {"comments" : {"$slice" : 3}})', ""),
    ("p6_slice_last", 'db.posts.findOne({"_id" : 1}, {"comments" : {"$slice" : -3}})', ""),
    ("p6_slice_page", 'db.posts.findOne({"_id" : 1}, {"comments" : {"$slice" : [23, 10]}})', ""),
    ("p6_people_seed", 'db.people.drop(); db.people.insertOne({"name" : {"first" : "John", "last" : "Escalona"}, "age" : 45})', ""),
    ("p6_dot", 'db.people.find({"name.first" : "John", "name.last" : "Escalona"}, {"_id" : 0})', ""),
    ("p6_exact_ok", 'db.people.find({"name" : {"first" : "John", "last" : "Escalona"}}).count()', ""),
    ("p6_exact_order_trap", 'db.people.find({"name" : {"last" : "Escalona", "first" : "John"}}).count()', "trap"),
    ("p6_set_embedded", 'db.people.updateOne({"name.first" : "John"}, {"$set" : {"name.last" : "Tagayon"}})', ""),
]


def main():
    version = subprocess.run([MONGOSH, "--quiet", "--eval", "db.version()"], capture_output=True, text=True).stdout.strip()
    shell = subprocess.run([MONGOSH, "--version"], capture_output=True, text=True).stdout.strip()
    rows = []
    for sid, code, note in STEPS:
        r = subprocess.run([MONGOSH, "--quiet", "adbs", "--eval", code], capture_output=True, text=True, timeout=60)
        rows.append({"id": sid, "code": code, "note": note, "output": (r.stdout + r.stderr).strip(), "exit": r.returncode})
        print(f"{sid:28s} exit={r.returncode}")
    OUT.write_text(json.dumps({"server": "MongoDB " + version, "shell": "mongosh " + shell, "steps": rows}, indent=1))
    bad = [x["id"] for x in rows if (x["exit"] != 0) != (x["note"] in ("expected error", "premise test"))]
    print("unexpected:", bad or "none")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
