import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "verification"))
from run_commands import HANDOUT_MOVIES, SETUP  # noqa: E402

RESULTS = json.loads((ROOT / "verification" / "results.json").read_text())
_BY_ID = {s["id"]: s for s in RESULTS["steps"]}


def out(step_id):
    return _BY_ID[step_id]["output"]


def code(step_id):
    return _BY_ID[step_id]["code"]


def compact(step_id):
    flat = re.sub(r"\s*\n\s*", " ", out(step_id)).replace("{ ", "{").replace(" }", "}")
    return flat.replace(", matchedCount", ",\n matchedCount")


VERIFIED = "Outputs from a real run: " + RESULTS["server"] + " + " + RESULTS["shell"] + " (2026-10-30)"

PARTS = [
    {
        "n": 1,
        "title": "Create & Delete",
        "kicker": "insertOne · insertMany · deleteOne · deleteMany",
        "soundbite": "Documents in, documents out.",
        "source": "07 Handout p.2-3; 08 Handout p.1",
        "setup": SETUP[1] + "\n" + "// before the deleteMany slide:\n" + HANDOUT_MOVIES,
        "slides": [
            {
                "kind": "table",
                "title": "Tables are collections, rows are documents",
                "soundbite": "Tables are collections. Rows are documents.",
                "headers": ["SQL", "MongoDB"],
                "rows": [["Database", "Database"], ["Tables", "Collections"], ["Rows", "Documents"], ["Columns", "Fields"]],
                "points": [
                    "Collection: like a table with a dynamic schema.",
                    "Document: the basic unit of data. Every document has a unique \"_id\".",
                ],
                "notes": "The 07 Handout's Table 2 maps SQL words to MongoDB words: tables are called collections, rows are called documents, columns are called fields. A collection can be thought of as a table with a dynamic schema. A document is the basic unit of data, roughly a row but more expressive. Every document has a special key, _id, that is unique in its collection. Say: Tables are collections. Rows are documents.",
                "source": "07 Handout p.2-3, Table 2",
            },
            {
                "kind": "cmd",
                "title": "insertOne: add one document",
                "soundbite": "One document in. MongoDB adds the _id.",
                "code": code("p1_insertOne"),
                "output": out("p1_insertOne"),
                "points": [
                    "insertOne adds a single document.",
                    "No \"_id\" given, so MongoDB added one automatically.",
                ],
                "notes": "insertOne is the basic way to add one document. We did not give an _id, so insertOne added one automatically; it shows in the output as an ObjectId. Say: One document in. MongoDB adds the _id.",
                "source": "08 Handout p.1",
            },
            {
                "kind": "cmd",
                "title": "insertMany: add several at once",
                "soundbite": "Many documents, one command.",
                "code": code("p1_insertMany"),
                "output": out("p1_insertMany"),
                "points": [
                    "insertMany takes an array [ ] of documents.",
                    "The output lists one _id per document.",
                ],
                "notes": "To insert multiple documents, use insertMany and pass an array. Three movies went in with one command, and the output shows three new ids. Say: Many documents, one command.",
                "source": "08 Handout p.1",
            },
            {
                "kind": "cmd2",
                "title": "Ordered vs unordered insertMany",
                "soundbite": "Ordered stops at the error. Unordered keeps going.",
                "code": "// unordered: duplicate _id 4 in the middle\n" + code("p1_unordered") + "\n" + code("p1_unordered_find"),
                "output": out("p1_unordered").replace("MongoBulkWriteError: ", "MongoBulkWriteError:\n") + "\n\n" + out("p1_unordered_find") + "\n<- 3, 4 and 5 were all inserted",
                "code2": "// ordered (the default): same documents\n" + code("p1_ordered") + "\n" + code("p1_ordered_find"),
                "output2": out("p1_ordered").replace("MongoBulkWriteError: ", "MongoBulkWriteError:\n") + "\n\n" + out("p1_ordered_find") + "\n<- stopped at the error; Scarface never went in",
                "points": [],
                "notes": "From the 08 Handout: if a document halfway through insertMany causes an error, what happens depends on ordered or unordered. Ordered is the default: no documents after the error are inserted. Unordered, with ordered false: MongoDB tries to insert all documents, even if some fail. Same four movies, same duplicate _id 4. Unordered saved 3, 4 and 5. Ordered saved only 3 and 4. Say: Ordered stops at the error. Unordered keeps going.",
                "source": "08 Handout p.1",
            },
            {
                "kind": "cmd2",
                "title": "deleteOne: remove one document",
                "soundbite": "deleteOne removes one.",
                "code": code("p1_deleteOne"),
                "output": out("p1_deleteOne"),
                "code2": code("p1_deleteOne_find"),
                "output2": out("p1_deleteOne_find") + "\n<- _id 4 is gone",
                "points": [],
                "notes": "MongoDB provides deleteOne and deleteMany for removing documents. The handout deletes the document with _id 4 using deleteOne. The output says deletedCount 1, and checking again shows only 3 and 5 are left. Say: deleteOne removes one.",
                "source": "08 Handout p.1",
            },
            {
                "kind": "cmd2",
                "title": "deleteMany: remove every match",
                "soundbite": "deleteMany removes every match.",
                "code": "// before: the handout's movies\n" + code("p1_before_deleteMany"),
                "output": out("p1_before_deleteMany"),
                "code2": code("p1_deleteMany") + "\n" + code("p1_after_deleteMany"),
                "output2": out("p1_deleteMany") + "\n\n" + out("p1_after_deleteMany") + "\n<- only the 1984 movie is left",
                "points": [],
                "notes": "To delete all documents that match a filter, use deleteMany. The handout shows three movies: two from 1985 and one from 1984. deleteMany with year 1985 removes both 1985 movies, so deletedCount is 2 and only Sixteen Candles stays. Say: deleteMany removes every match.",
                "source": "08 Handout p.1",
            },
        ],
    },
    {
        "n": 2,
        "title": "Find, Replace & Update",
        "kicker": "findOne · replaceOne · updateOne · updateMany",
        "soundbite": "Find it first. Then change it.",
        "source": "08 Handout p.1-3",
        "setup": SETUP[2],
        "slides": [
            {
                "kind": "cmd",
                "title": "findOne: get one document",
                "soundbite": "findOne brings back one document.",
                "code": code("p2_findOne"),
                "output": out("p2_findOne"),
                "points": [
                    "findOne returns one document that matches the filter.",
                    "The handout uses it to load Joe before changing him.",
                ],
                "notes": "findOne returns a single matching document. In the handout, findOne loads Joe's document so it can be reshaped. Joe has friends 32 and enemies 2. Say: findOne brings back one document.",
                "source": "08 Handout p.1",
            },
            {
                "kind": "cmd",
                "title": "replaceOne: replace the whole document",
                "soundbite": "replaceOne swaps the whole document.",
                "code": code("p2_replaceOne"),
                "output": compact("p2_replaceOne") + "\n\n// db.users.findOne({\"username\" : \"Joe\"})\n" + out("p2_replaceOne_find"),
                "points": [
                    "replaceOne fully replaces a matching document with a new one.",
                    "Handout use: a big schema change (\"relationships\" subdocument).",
                ],
                "notes": "replaceOne fully replaces a matching document with a new one. The handout says this is useful for a dramatic schema migration. Friends and enemies move into a relationships subdocument, name becomes username, the old fields are deleted, then replaceOne saves it. Say: replaceOne swaps the whole document.",
                "source": "08 Handout p.1-2",
            },
            {
                "kind": "cmd2",
                "title": "updateOne with $set",
                "soundbite": "$set adds or changes a field.",
                "code": code("p2_set"),
                "output": compact("p2_set") + "\n\n// findOne({\"name\" : \"John\"})\n" + out("p2_set_find"),
                "code2": "// $set can even change the type\n" + code("p2_set_array"),
                "output2": compact("p2_set_array") + "\n\n// findOne({\"name\" : \"John\"})\n" + out("p2_set_array_find"),
                "points": [],
                "notes": "updateOne takes a filter first and a modifier second. The $set operator sets the value of a field; if the field does not exist yet, it is created. John gets a favorite book. The handout then shows $set can even change the type of the key: favorite book becomes an array of three books. Say: $set adds or changes a field.",
                "source": "08 Handout p.2",
            },
            {
                "kind": "cmd",
                "title": "updateOne with $unset",
                "soundbite": "$unset removes a field.",
                "code": code("p2_unset"),
                "output": compact("p2_unset") + "\n\n// findOne({\"name\" : \"John\"})\n" + out("p2_unset_find"),
                "points": [
                    "$unset removes the key altogether.",
                    "\"favorite book\" is gone; the rest of John stays.",
                ],
                "notes": "To remove the favorite book key altogether, the handout uses the $unset operator. After it runs, John's document no longer has a favorite book. Say: $unset removes a field.",
                "source": "08 Handout p.2",
            },
            {
                "kind": "cmd",
                "title": "$set inside an embedded document",
                "soundbite": "Use the dot to reach inside.",
                "code": code("p2_books_set"),
                "output": compact("p2_books_set") + "\n\n// db.books.findOne()\n" + out("p2_books_find"),
                "points": [
                    "\"author.name\" reaches inside the author subdocument.",
                    "Only the name changed; the email stayed.",
                ],
                "notes": "$set can also reach in and change embedded documents. The book's author is a subdocument with name and email. Using author.name in quotes changes only the name to Nicole Tagayon; the email stays. Say: Use the dot to reach inside.",
                "source": "08 Handout p.2",
            },
            {
                "kind": "cmd",
                "title": "updateMany: update every match",
                "soundbite": "One rule, every match.",
                "code": code("p2_updateMany"),
                "output": compact("p2_updateMany") + "\n\n// db.users.find({\"birthday\" : \"10/13/1978\"})\n" + out("p2_updateMany_find"),
                "points": [
                    "Same parameters as updateOne.",
                    "Difference: how many documents can change (3 here).",
                ],
                "notes": "updateMany follows the same semantics as updateOne and takes the same parameters. The key difference is how many documents might be changed. Three users share the birthday 10/13/1978, so all three get the gift Happy Birthday. matchedCount and modifiedCount are both 3. Say: One rule, every match.",
                "source": "08 Handout p.3",
            },
        ],
    },
    {
        "n": 3,
        "title": "Query Selectors: Comparison",
        "kicker": "$lt · $lte · $gt · $gte",
        "soundbite": "Less, less-or-equal, greater, greater-or-equal.",
        "source": "08 Handout p.3",
        "setup": SETUP[3],
        "slides": [
            {
                "kind": "table",
                "title": "Four comparison operators",
                "soundbite": "The e means equal is allowed.",
                "headers": ["Operator", "Means", "Symbol"],
                "rows": [["$lt", "less than", "<"], ["$lte", "less than or equal", "<="], ["$gt", "greater than", ">"], ["$gte", "greater than or equal", ">="]],
                "points": ["Practice ages (ours, not from the handout): Ana 17, Ben 18, Cara 24, Dan 30, Eli 31."],
                "notes": "The handout says $lt, $lte, $gt and $gte are comparison operators, corresponding to less than, less than or equal, greater than, and greater than or equal. The practice ages are our own data, used to show real results. Say: The e means equal is allowed.",
                "source": "08 Handout p.3",
            },
            {
                "kind": "cmd2",
                "title": "$lt and $lte",
                "soundbite": "18 is out with $lt, in with $lte.",
                "code": code("p3_lt"),
                "output": out("p3_lt"),
                "code2": code("p3_lte"),
                "output2": out("p3_lte"),
                "points": [],
                "notes": "$lt 18 means less than 18: only Ana, 17. $lte 18 means less than or equal: Ana and Ben, who is exactly 18. Say: 18 is out with lt, in with lte.",
                "source": "08 Handout p.3",
            },
            {
                "kind": "cmd2",
                "title": "$gt and $gte",
                "soundbite": "30 is out with $gt, in with $gte.",
                "code": code("p3_gt"),
                "output": out("p3_gt"),
                "code2": code("p3_gte"),
                "output2": out("p3_gte"),
                "points": [],
                "notes": "$gt 30 means greater than 30: only Eli, 31. $gte 30 means greater than or equal: Dan, exactly 30, and Eli. Say: 30 is out with gt, in with gte.",
                "source": "08 Handout p.3",
            },
            {
                "kind": "cmd",
                "title": "Combine them: ages 18 to 30",
                "soundbite": "Two operators, one field, one range.",
                "code": code("p3_range"),
                "output": out("p3_range"),
                "points": [
                    "The handout's example: users between 18 and 30.",
                    "Both conditions must be true.",
                ],
                "notes": "The handout looks for users between the ages of 18 and 30 by putting $gte 18 and $lte 30 on the same field. Both must be true: Ben, Cara and Dan. Say: Two operators, one field, one range.",
                "source": "08 Handout p.3",
            },
        ],
    },
    {
        "n": 4,
        "title": "Query Selectors: $in, $or, $not",
        "kicker": "$in · $or · $not",
        "soundbite": "One field, many values. Many fields, any match.",
        "source": "08 Handout p.3",
        "setup": SETUP[4],
        "slides": [
            {
                "kind": "cmd",
                "title": "$in: many values for one key",
                "soundbite": "$in is a guest list for one field.",
                "code": code("p4_in"),
                "output": out("p4_in"),
                "points": [
                    "$in queries a variety of values for a single key.",
                    "Handout raffle: winning tickets 725, 542 and 390.",
                ],
                "notes": "The handout gives two ways to do an OR query. $in is used to query a variety of values for a single key. The raffle's winning tickets are 725, 542 and 390, and one $in query finds all three. Say: $in is a guest list for one field.",
                "source": "08 Handout p.3",
            },
            {
                "kind": "cmd",
                "title": "$or: any condition, across keys",
                "soundbite": "$or: pass any one test.",
                "code": code("p4_or"),
                "output": out("p4_or"),
                "points": [
                    "$or is more general: conditions can use different keys.",
                    "Ticket 725, or any document where winner is true.",
                ],
                "notes": "$or is more general: it takes an array of possible criteria, and each can be on a different key. We want ticket 725 or any winner true. Ticket 725 matches the first; ticket 111 matches the second. Say: $or, pass any one test.",
                "source": "08 Handout p.3",
            },
            {
                "kind": "cmd",
                "title": "$not: everything that does NOT match",
                "soundbite": "$not flips the condition.",
                "code": code("p4_not"),
                "output": out("p4_not"),
                "points": [
                    "Handout: salary not greater than ₱10,000.",
                    "Mark (exactly ₱10,000) is included; Liza (₱15,000) is not.",
                ],
                "notes": "$not finds all documents that don't match a given pattern. The handout's example retrieves employees whose salary is not greater than 10,000 pesos. Rhea at 8,000 and Mark at exactly 10,000 come back; Liza at 15,000 does not. The salaries are our practice data. Say: $not flips the condition.",
                "source": "08 Handout p.3",
            },
        ],
    },
    {
        "n": 5,
        "title": "Querying Arrays",
        "kicker": "inserting arrays · array match · $all · $size",
        "soundbite": "Arrays answer like single values.",
        "source": "08 Handout p.4",
        "setup": SETUP[5],
        "slides": [
            {
                "kind": "cmd",
                "title": "Inserting arrays",
                "soundbite": "Square brackets make an array.",
                "code": code("p5_insert") + "\n" + code("p5_find_all"),
                "output": out("p5_find_all"),
                "points": [
                    "\"fruit\" holds a list of elements in [ ].",
                    "These three baskets are the handout's example.",
                ],
                "notes": "The handout inserts three documents whose fruit field is an array, written in square brackets. Basket 1 has apple, banana, peach. Basket 2 has apple, kumquat, orange. Basket 3 has cherry, banana, apple. Say: Square brackets make an array.",
                "source": "08 Handout p.4",
            },
            {
                "kind": "cmd",
                "title": "Query an array like a single value",
                "soundbite": "Ask for banana, get every basket with a banana.",
                "code": code("p5_scalar"),
                "output": out("p5_scalar"),
                "points": [
                    "Querying arrays behaves like querying scalars.",
                    "Matches if any element equals \"banana\".",
                ],
                "notes": "The handout says querying for elements of an array is designed to behave the way querying for scalars does. Asking for fruit banana matches baskets 1 and 3, because each has banana somewhere in the array. Say: Ask for banana, get every basket with a banana.",
                "source": "08 Handout p.4",
            },
            {
                "kind": "cmd",
                "title": "$all: must have every listed element",
                "soundbite": "$all: has them all, any order.",
                "code": code("p5_all"),
                "output": out("p5_all"),
                "points": [
                    "$all matches arrays by more than one element.",
                    "Basket 2 has apple but no banana, so it is out.",
                ],
                "notes": "If you need to match arrays by more than one element, use $all. Baskets with both apple and banana: 1 and 3. Basket 2 has no banana. Order does not matter: basket 3 has banana before apple. Say: $all, has them all, any order.",
                "source": "08 Handout p.4",
            },
            {
                "kind": "cmd",
                "title": "A specific position: key.index",
                "soundbite": "Count from zero.",
                "code": code("p5_index"),
                "output": out("p5_index"),
                "points": [
                    "\"fruit.2\" means the element at index 2.",
                    "Counting starts at 0, so index 2 is the third fruit.",
                ],
                "notes": "To query a specific element of an array, specify an index with the syntax key dot index. fruit.2 is the third element, because counting starts at zero. Only basket 1 has peach in that position. Say: Count from zero.",
                "source": "08 Handout p.4",
            },
            {
                "kind": "cmd",
                "title": "$size: match by number of elements",
                "soundbite": "$size counts the elements.",
                "code": code("p5_size"),
                "output": out("p5_size"),
                "points": [
                    "$size matches arrays with exactly that many elements.",
                    "All three baskets have 3 fruits.",
                ],
                "notes": "$size matches any array with the number of elements given. Every basket has exactly three fruits, so $size 3 returns all three. Say: $size counts the elements.",
                "source": "08 Handout p.4",
            },
        ],
    },
    {
        "n": 6,
        "title": "$slice & Embedded Documents",
        "kicker": "$slice · dot notation · embedded documents",
        "soundbite": "Trim what you see. Reach inside with a dot.",
        "source": "08 Handout p.4",
        "setup": SETUP[6],
        "slides": [
            {
                "kind": "cmd2",
                "title": "$slice: first 10 or last 10",
                "soundbite": "Positive from the front, negative from the back.",
                "code": "// blog post with 40 comments (our practice data)\n" + code("p6_slice_first"),
                "output": out("p6_slice_first"),
                "code2": code("p6_slice_last"),
                "output2": out("p6_slice_last"),
                "points": [],
                "notes": "$slice returns a subset of elements for an array key. The handout's blog post example returns the first 10 comments with 10, and the last 10 with minus 10. Our practice post has 40 comments, c1 to c40. Say: Positive from the front, negative from the back.",
                "source": "08 Handout p.4",
            },
            {
                "kind": "cmd",
                "title": "$slice [23, 10]: a page from the middle",
                "soundbite": "Skip 23, take 10.",
                "code": code("p6_slice_page"),
                "output": out("p6_slice_page"),
                "points": [
                    "Skips the first 23, returns the 24th through 33rd.",
                    "Fewer than 33? It returns as many as possible.",
                ],
                "notes": "$slice can return pages from the middle by taking an offset and a number of elements. [23, 10] skips the first 23 and returns the 24th through 33rd: c24 to c33. The handout notes that with fewer than 33 elements, it returns as many as possible. Say: Skip 23, take 10.",
                "source": "08 Handout p.4",
            },
            {
                "kind": "cmd",
                "title": "Querying embedded documents",
                "soundbite": "Use the dot to reach inside.",
                "code": code("p6_dot"),
                "output": out("p6_dot"),
                "points": [
                    "An embedded document is a document inside a document.",
                    "Reach its keys with dot notation: \"name.first\".",
                ],
                "notes": "Embedded or nested documents are documents that contain a document inside another document. John's name holds first and last. You query embedded keys using dot notation, in quotes: name.first and name.last. Say: Use the dot to reach inside.",
                "source": "08 Handout p.4",
            },
        ],
    },
    {
        "n": 7,
        "title": "Cloud Computing & Implementation Types",
        "kicker": "public · private · hybrid",
        "soundbite": "Cloud type = where it lives + who controls it.",
        "source": "09 Handout p.1",
        "setup": "",
        "slides": [
            {
                "kind": "text",
                "title": "What cloud computing is",
                "soundbite": "If it has the web, it has your data.",
                "body": [
                    "Cloud computing is the delivery of different services through the Internet: data storage, servers, databases, networking and software.",
                    "Instead of a hard drive or local storage, files are saved to a remote database.",
                    "As long as a device has access to the web, it has access to the data and the software to run it.",
                ],
                "notes": "Handout definition: cloud computing is the delivery of different services through the Internet, including data storage, servers, databases, networking and software. Rather than keeping files on a proprietary hard drive or local storage device, cloud storage saves them to a remote database. As long as a device has web access, it has access to the data and the programs to run it. Say: If it has the web, it has your data.",
                "source": "09 Handout p.1",
            },
            {
                "kind": "table",
                "title": "Three cloud implementation types",
                "soundbite": "Rent it, own it, or mix both.",
                "headers": ["Type", "Built by / for", "Handout example", "Key point"],
                "rows": [
                    ["Public", "A third party, to sell cloud services to the general public", "AWS, Google Application Engine, Microsoft Azure", "Reliable, low cost, scalable; not for strict sensitive-data rules"],
                    ["Private", "An organization, only for its own needs", "Large, geographically dispersed organizations", "Managed by internal IT staff or a third party"],
                    ["Hybrid", "A combination of private and public cloud", "Public for emails; private for financials and data recovery", "Flexibility plus control over critical assets"],
                ],
                "points": ["Type = where the infrastructure resides and who controls it."],
                "notes": "Implementation type is defined by where the infrastructure resides and who controls it. Public cloud: built by a third party to sell to the general public; the most common type; examples AWS, Google Application Engine and Microsoft Azure; high reliability, lower costs, zero maintenance, on-demand scalability, but not suitable for organizations with sensitive information under stringent security rules. Private cloud: built by an organization for its own needs, often large, geographically dispersed organizations; managed by internal IT staff or an external third party. Hybrid cloud: private plus public; for example, public cloud for high-volume apps like emails, private cloud for sensitive assets like financials and data recovery. Say: Rent it, own it, or mix both.",
                "source": "09 Handout p.1",
            },
        ],
    },
    {
        "n": 8,
        "title": "Cloud Service Types & Benefits",
        "kicker": "SaaS · PaaS · IaaS · 10 benefits",
        "soundbite": "Use it, build on it, or rent the machine.",
        "source": "09 Handout p.1-2",
        "setup": "",
        "slides": [
            {
                "kind": "table",
                "title": "Three types of cloud services",
                "soundbite": "SaaS: use it. PaaS: build on it. IaaS: rent the machine.",
                "headers": ["Type", "Provider offers", "The consumer", "Handout example"],
                "rows": [
                    ["SaaS", "Turnkey applications that run in the cloud", "Can customize some aspects, not the application itself", "MS Office 365, Google Docs, TurboTax Online, SCALA digital signage"],
                    ["PaaS", "Tools, languages and interfaces to build and deploy your own apps", "Builds and manages apps; does not manage the infrastructure", "Microsoft Azure platform with .NET and Java"],
                    ["IaaS", "Resources on demand: storage, servers, databases, processing, virtual desktop", "Adds or removes resources as needed", "AWS server with Linux and Apache, 16 GB RAM, 160 GB storage"],
                ],
                "points": ["Services follow an à la carte model and can build on top of each other."],
                "notes": "Cloud services follow an a la carte model and can build on top of each other. SaaS: the provider offers turnkey applications that run in the cloud, such as MS Office 365, Google Docs, Intuit's TurboTax Online and SCALA digital signage; consumers can customize certain aspects but cannot change the application itself. PaaS: the provider offers the capability to build and deploy consumer-created applications with its tools, languages and interfaces, such as the Microsoft Azure platform with .NET and Java; the consumer does not manage the underlying infrastructure. IaaS: consumers provision their own resources on demand, such as an AWS server running Linux and Apache with 16 GB RAM and 160 GB storage. Say: SaaS, use it. PaaS, build on it. IaaS, rent the machine.",
                "source": "09 Handout p.1",
            },
            {
                "kind": "benefits",
                "title": "10 benefits of cloud computing",
                "soundbite": "Scale up fast. Pay for what you use.",
                "items": [
                    ["Instant scalability", "scale capacity up or down to meet demand"],
                    ["Anywhere accessibility", "serve customers across the globe"],
                    ["Increased speed and operational agility", "add computing capacity with a click"],
                    ["Reduced expenditure", "no idle data centers; cost depends on use"],
                    ["Automatic updates/patches", "the provider takes care of them"],
                    ["Disaster recovery", "no costly on-premises setup needed"],
                    ["High security", "advanced security features reduce risk"],
                    ["Reduced carbon footprint", "resources as per demand, less e-waste"],
                    ["Flexibility", "any device, any location"],
                    ["Enterprise collaboration", "centralized, shared documents"],
                ],
                "notes": "The handout lists ten benefits, in this order: instant scalability; anywhere accessibility; increased speed and operational agility; reduced expenditure, since cloud costs depend on consumption, a variable expense; automatic updates and patches; disaster recovery; high security; reduced carbon footprint; flexibility; enterprise collaboration. Say: Scale up fast. Pay for what you use.",
                "source": "09 Handout p.1-2",
            },
        ],
    },
]

CHEATSHEET = [
    ("Create", 'insertOne({...})   insertMany([{...}, {...}], {"ordered" : false})'),
    ("Delete", 'deleteOne(filter)   deleteMany(filter)'),
    ("Read", 'find(filter)   findOne(filter)'),
    ("Change", 'replaceOne(filter, doc)   updateOne / updateMany(filter, {$set | $unset})'),
    ("Compare", '$lt <   $lte <=   $gt >   $gte >='),
    ("Choose", '$in [values]   $or [conditions]   $not {condition}'),
    ("Arrays", 'field: value   $all [...]   "fruit.2"   $size: n'),
    ("Slice / nest", '$slice: 10 | -10 | [23, 10]   "name.first"'),
    ("Cloud", 'Public · Private · Hybrid      SaaS · PaaS · IaaS'),
]

REFERENCES = [
    "STI IT2003 07 Handout 1: Introduction to NoSQL Database Management Systems.",
    "STI IT2003 08 Handout 1: Fundamentals of Document-Oriented Database.",
    "STI IT2003 09 Handout 1: Cloud Computing.",
    "Chodorow, K., Brazil, E., & Bradshaw, S. (2019). MongoDB: The definitive guide (3rd ed.). O'Reilly Media.",
    "Coronel, C., & Morris, S. (2018). Database systems: Design, implementation, & management (13th ed.). Cengage Learning.",
    "MongoDB (n.d.). Query and Update Operators. https://docs.mongodb.com/manual/reference/operator/",
]
