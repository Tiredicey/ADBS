import json
import shutil
import subprocess
from pathlib import Path

MONGOSH = shutil.which("mongosh") or str(Path.home() / "bin" / "mongosh")
OUT = Path(__file__).resolve().parent / "results.json"

SETUP = {
    1: 'use adbs_part1\ndb.dropDatabase()',
    2: 'use adbs_part2\ndb.dropDatabase()\n'
       'db.users.insertOne({"_id" : ObjectId("4b2b9f67a1f631733d917a7a"),\n'
       '  "name" : "Joe", "friends" : 32, "enemies" : 2})\n'
       'db.users.insertOne({"_id" : ObjectId("4b253b067525f35f94b60a31"),\n'
       '  "name" : "John", "age" : 24, "sex" : "male", "location" : "Taytay"})\n'
       'db.books.insertOne({"_id" : ObjectId("4b253b067525f35f94b60a31"),\n'
       '  "title" : "MongoDB-2019",\n'
       '  "author" : {"name" : "Nicole", "email" : "Nic@example.com"}})\n'
       'db.users.insertMany([{"_id" : 1, "birthday" : "10/13/1978"},\n'
       '  {"_id" : 2, "birthday" : "10/13/1978"},\n'
       '  {"_id" : 3, "birthday" : "10/13/1978"}])',
    3: 'use adbs_part3\ndb.dropDatabase()\n'
       'db.users.insertMany([{"_id" : 1, "name" : "Ana", "age" : 17},\n'
       '  {"_id" : 2, "name" : "Ben", "age" : 18},\n'
       '  {"_id" : 3, "name" : "Cara", "age" : 24},\n'
       '  {"_id" : 4, "name" : "Dan", "age" : 30},\n'
       '  {"_id" : 5, "name" : "Eli", "age" : 31}])',
    4: 'use adbs_part4\ndb.dropDatabase()\n'
       'db.raffle.insertMany([{"_id" : 1, "ticket_no" : 725, "winner" : false},\n'
       '  {"_id" : 2, "ticket_no" : 542, "winner" : false},\n'
       '  {"_id" : 3, "ticket_no" : 390, "winner" : false},\n'
       '  {"_id" : 4, "ticket_no" : 111, "winner" : true},\n'
       '  {"_id" : 5, "ticket_no" : 222, "winner" : false}])\n'
       'db.users.insertMany([{"_id" : 1, "name" : "Rhea", "salary" : 8000},\n'
       '  {"_id" : 2, "name" : "Mark", "salary" : 10000},\n'
       '  {"_id" : 3, "name" : "Liza", "salary" : 15000}])',
    5: 'use adbs_part5\ndb.dropDatabase()',
    6: 'use adbs_part6\ndb.dropDatabase()\n'
       'db.blog.posts.insertOne({"_id" : 1, "title" : "ADBS",\n'
       '  "comments" : Array.from({length : 40}, (_, i) => "c" + (i + 1))})\n'
       'db.people.insertOne({"_id" : 1,\n'
       '  "name" : {"first" : "John", "last" : "Escalona"}, "age" : 45})',
}

HANDOUT_MOVIES = ('db.movies.deleteMany({})\n'
                  'db.movies.insertMany([{"_id" : 0, "title" : "Top Gun", "year" : 1985},\n'
                  '  {"_id" : 1, "title" : "Back to the Future", "year" : 1985},\n'
                  '  {"_id" : 3, "title" : "Sixteen Candles", "year" : 1984}])')

DUP_DOCS = ('[\n  {"_id" : 3, "title" : "Sixteen Candles"},\n'
            '  {"_id" : 4, "title" : "The Terminator"},\n'
            '  {"_id" : 4, "title" : "The Princess Bride"},\n'
            '  {"_id" : 5, "title" : "Scarface"}]')

IDS_345 = 'db.movies.find({"_id" : {"$in" : [3, 4, 5]}})'
NO_ID = 'db.movies.find({}, {"_id" : 0})'
JOHN = 'db.users.findOne({"name" : "John"}, {"_id" : 0})'
BDAY = 'db.users.find({"birthday" : "10/13/1978"})'
FOOD = 'db.food.find()'

STEPS = [
    ("p1_insertOne_before", 1, "check", 'db.movies.find()'),
    ("p1_insertOne", 1, "cmd", 'db.movies.insertOne({"title" : "Stand by Me"})'),
    ("p1_insertOne_after", 1, "check", NO_ID),
    ("p1_insertMany_before", 1, "check", NO_ID),
    ("p1_insertMany", 1, "cmd", 'db.movies.insertMany([{"title" : "Ghostbusters"},\n  {"title" : "E.T."},\n  {"title" : "Blade Runner"}])'),
    ("p1_insertMany_after", 1, "check", NO_ID),
    ("p1_unordered_before", 1, "check", IDS_345),
    ("p1_unordered", 1, "error", 'db.movies.insertMany(' + DUP_DOCS + ',\n  {"ordered" : false})'),
    ("p1_unordered_after", 1, "check", IDS_345),
    ("p1_ordered_before", 1, "check", 'db.ordered.find()'),
    ("p1_ordered", 1, "error", 'db.ordered.insertMany(' + DUP_DOCS + ')'),
    ("p1_ordered_after", 1, "check", 'db.ordered.find()'),
    ("p1_deleteOne_before", 1, "check", IDS_345),
    ("p1_deleteOne", 1, "cmd", 'db.movies.deleteOne({"_id" : 4})'),
    ("p1_deleteOne_after", 1, "check", IDS_345),
    ("p1_handout_movies", 1, "seed", HANDOUT_MOVIES),
    ("p1_deleteMany_before", 1, "check", 'db.movies.find()'),
    ("p1_deleteMany", 1, "cmd", 'db.movies.deleteMany({"year" : 1985})'),
    ("p1_deleteMany_after", 1, "check", 'db.movies.find()'),

    ("p2_findOne", 2, "cmd", 'db.users.findOne({"name" : "Joe"})'),
    ("p2_replaceOne", 2, "cmd", 'var Joe = db.users.findOne({"name" : "Joe"});\n'
                                'Joe.relationships = {"friends" : Joe.friends,\n  "enemies" : Joe.enemies};\n'
                                'Joe.username = Joe.name;\n'
                                'delete Joe.friends; delete Joe.enemies;\ndelete Joe.name;\n'
                                'db.users.replaceOne({"name" : "Joe"}, Joe)'),
    ("p2_replaceOne_after", 2, "check", 'db.users.findOne({"username" : "Joe"})'),
    ("p2_set_before", 2, "check", JOHN),
    ("p2_set", 2, "cmd", 'db.users.updateOne({"name" : "John"},\n  {"$set" : {"favorite book" :\n    "Green Eggs and Ham"}})'),
    ("p2_set_after", 2, "check", JOHN),
    ("p2_set_array", 2, "cmd", 'db.users.updateOne({"name" : "John"},\n  {"$set" : {"favorite book" :\n  ["Cat\'s Cradle", "Foundation Trilogy",\n   "Ender\'s Game"]}})'),
    ("p2_set_array_after", 2, "check", JOHN),
    ("p2_unset", 2, "cmd", 'db.users.updateOne({"name" : "John"},\n  {"$unset" : {"favorite book" : 1}})'),
    ("p2_unset_after", 2, "check", JOHN),
    ("p2_books_before", 2, "check", 'db.books.findOne({}, {"_id" : 0})'),
    ("p2_books_set", 2, "cmd", 'db.books.updateOne({"author.name" : "Nicole"},\n  {"$set" : {"author.name" : "Nicole Tagayon"}})'),
    ("p2_books_after", 2, "check", 'db.books.findOne({}, {"_id" : 0})'),
    ("p2_updateMany_before", 2, "check", BDAY),
    ("p2_updateMany", 2, "cmd", 'db.users.updateMany({"birthday" : "10/13/1978"},\n  {"$set" : {"gift" : "Happy Birthday!"}})'),
    ("p2_updateMany_after", 2, "check", BDAY),

    ("p3_data", 3, "check", 'db.users.find()'),
    ("p3_lt", 3, "cmd", 'db.users.find({"age" : {"$lt" : 18}})'),
    ("p3_lte", 3, "cmd", 'db.users.find({"age" : {"$lte" : 18}})'),
    ("p3_gt", 3, "cmd", 'db.users.find({"age" : {"$gt" : 30}})'),
    ("p3_gte", 3, "cmd", 'db.users.find({"age" : {"$gte" : 30}})'),
    ("p3_range", 3, "cmd", 'db.users.find({"age" : {"$gte" : 18, "$lte" : 30}})'),

    ("p4_raffle_data", 4, "check", 'db.raffle.find()'),
    ("p4_in", 4, "cmd", 'db.raffle.find({"ticket_no" :\n  {"$in" : [725, 542, 390]}})'),
    ("p4_or", 4, "cmd", 'db.raffle.find({"$or" : [{"ticket_no" : 725},\n  {"winner" : true}]})'),
    ("p4_users_data", 4, "check", 'db.users.find()'),
    ("p4_not", 4, "cmd", 'db.users.find({salary:\n  {$not: {$gt: 10000}}}).pretty()'),

    ("p5_insert_before", 5, "check", FOOD),
    ("p5_insert", 5, "cmd", 'db.food.insertOne({"_id" : 1,\n  "fruit" : ["apple", "banana", "peach"]})\n'
                            'db.food.insertOne({"_id" : 2,\n  "fruit" : ["apple", "kumquat", "orange"]})\n'
                            'db.food.insertOne({"_id" : 3,\n  "fruit" : ["cherry", "banana", "apple"]})'),
    ("p5_insert_after", 5, "check", FOOD),
    ("p5_scalar", 5, "cmd", 'db.food.find({"fruit" : "banana"})'),
    ("p5_all", 5, "cmd", 'db.food.find({fruit : {$all : ["apple", "banana"]}})'),
    ("p5_index", 5, "cmd", 'db.food.find({"fruit.2" : "peach"})'),
    ("p5_size", 5, "cmd", 'db.food.find({"fruit" : {"$size" : 3}})'),

    ("p6_slice_first", 6, "cmd", 'db.blog.posts.findOne({"_id" : 1},\n  {"comments" : {"$slice" : 10}})'),
    ("p6_slice_last", 6, "cmd", 'db.blog.posts.findOne({"_id" : 1},\n  {"comments" : {"$slice" : -10}})'),
    ("p6_slice_page", 6, "cmd", 'db.blog.posts.findOne({"_id" : 1},\n  {"comments" : {"$slice" : [23, 10]}})'),
    ("p6_people_data", 6, "check", 'db.people.find()'),
    ("p6_dot", 6, "cmd", 'db.people.find({"name.first" : "John",\n  "name.last" : "Escalona"})'),
]


def eval_script(code):
    return "\n".join(line for line in code.split("\n") if not line.startswith("use "))


def run(part, code):
    return subprocess.run([MONGOSH, "--quiet", "adbs_part%d" % part, "--eval", eval_script(code)], capture_output=True, text=True, timeout=60)


def main():
    version = subprocess.run([MONGOSH, "--quiet", "--eval", "db.version()"], capture_output=True, text=True).stdout.strip()
    shell = subprocess.run([MONGOSH, "--version"], capture_output=True, text=True).stdout.strip()
    rows = []
    for part in sorted(SETUP):
        r = run(part, SETUP[part])
        rows.append({"id": "p%d_setup" % part, "part": part, "role": "setup", "code": SETUP[part], "output": (r.stdout + r.stderr).strip(), "exit": r.returncode})
        print(f"p{part}_setup              exit={r.returncode}")
        for sid, p, role, code in STEPS:
            if p != part:
                continue
            r = run(part, code)
            rows.append({"id": sid, "part": part, "role": role, "code": code, "output": (r.stdout + r.stderr).strip(), "exit": r.returncode})
            print(f"{sid:22s} exit={r.returncode}")
    OUT.write_text(json.dumps({"server": "MongoDB " + version, "shell": "mongosh " + shell, "steps": rows}, indent=1))
    bad = [x["id"] for x in rows if (x["exit"] != 0) != (x["role"] == "error")]
    print("unexpected:", bad or "none")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
