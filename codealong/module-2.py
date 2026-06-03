"""Module 2 — Data Structures, Files & Modules · CODE-ALONG

Each concept TWICE: a SIMPLE way, then the ADVANCED/idiomatic way — same result,
less code. The jump between them is the lesson. Run it, or copy a block per slide:
    python3 codealong/module-2.py
Stdlib only.
"""
import csv, io, json, logging, os
from collections import Counter, defaultdict
from contextlib import contextmanager
from pathlib import Path

products = [
    {"id": 1, "name": "Cable",    "category": "Electronics", "price": 499},
    {"id": 2, "name": "Keyboard", "category": "Electronics", "price": 5499},
    {"id": 3, "name": "Yoga Mat", "category": "Fitness",     "price": 1299},
]

# §1  look up a product by id                              (slides 13-14)
simple = None
for p in products:                          # simple: scan the list, O(n)
    if p["id"] == 2:
        simple = p["name"]
by_id = {p["id"]: p for p in products}      # advanced: dict, O(1) lookup
print("§1 lookup:", simple, "==", by_id[2]["name"])

# §2  keep the cheap product names                         (slide 15)
simple = []
for p in products:                          # simple: loop + append
    if p["price"] < 1500:
        simple.append(p["name"])
advanced = [p["name"] for p in products if p["price"] < 1500]   # comprehension
print("§2 filter:", simple, "==", advanced)

# §3  write CSV                                            (slide 16)
simple = "id,name\n" + "\n".join(f'{p["id"]},{p["name"]}' for p in products)  # hand-rolled (breaks on commas/quotes)
buf = io.StringIO()
w = csv.DictWriter(buf, fieldnames=["id", "name"]); w.writeheader()
for p in products:                          # advanced: csv module quotes/escapes for you
    w.writerow({"id": p["id"], "name": p["name"]})
print("§3 rows -> simple:", simple.count("\n"), "csv:", buf.getvalue().strip().count("\n"))
print("§3 json round-trip:", json.loads(json.dumps(products[0]))["name"])   # JSON ⇄ dict in one call each

# §4  group + count by category                           (slide 17 / senior)
simple = {}
for p in products:                          # simple: manual dict-of-lists
    simple.setdefault(p["category"], []).append(p["name"])
groups = defaultdict(list)
for p in products:                          # advanced: defaultdict — no setdefault
    groups[p["category"]].append(p["name"])
print("§4 group:", dict(groups), "| count:", Counter(p["category"] for p in products))   # Counter = count in one line

# §5  total price of all products                         (senior)
total_list = sum([p["price"] for p in products])   # simple: builds the whole list first
total_gen  = sum(p["price"] for p in products)      # advanced: generator — () not [], one pass
print("§5 sum:", total_list, "==", total_gen)

# §6  report an event                                     (slide 18)
print("§6 print: added id=1")                       # simple: print — no level/source, always on
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logging.info("added id=%s", 1)                      # advanced: logging — levels + %s lazy formatting

# §7  guaranteed cleanup                                  (senior)
print(" open")                              # simple: try/finally by hand
try:
    print(" ...writing...")
finally:
    print(" close")
@contextmanager
def saving(name):                           # advanced: a context manager hides the try/finally
    print(" open", name)
    try:
        yield
    finally:
        print(" close", name)
with saving("catalog.json"):                # real use: atomic_write (write tmp, then os.replace)
    print(" ...writing...")

# §8  build a file path                                   (senior)
simple = os.path.join("data", "products.csv")     # simple: string join
advanced = Path("data") / "products.csv"           # advanced: pathlib, compose with /
print("§8 path:", simple, "==", str(advanced), "| suffix:", advanced.suffix)
