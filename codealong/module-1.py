"""Module 1 — Python Core · CODE-ALONG

Each concept TWICE: a SIMPLE way, then the ADVANCED/idiomatic way — same result,
fewer footguns. The jump between them is the lesson. Run it, or copy a block per slide:
    python3 codealong/module-1.py
§1-§4 = base slides 6-9 · §5-§6 = senior-track traps. Stdlib only.
"""

catalog = {1: "Cable", 2: "Keyboard"}      # id -> name

# §1  truthiness & None                                    (slide 7)
tags = []
print("§1 simple  :", "has" if len(tags) > 0 else "empty")   # measure the length
print("§1 advanced:", "has" if tags else "empty")            # [] is falsy — just test it
x = None
print("§1 None: use 'is', not '==' ->", x is None)

# §2  pass arguments to a function                         (slide 8)
def add_simple(catalog, id, name, category, price):          # simple: all positional — easy to mis-order
    catalog[id] = name
def add(catalog, name, *, category="Misc", price=0.0):       # advanced: keyword-only after * = clear calls
    new_id = max(catalog) + 1
    catalog[new_id] = name
    return new_id
add_simple(catalog, 3, "Mat", "Fitness", 1299)              # which arg was which?
new_id = add(catalog, "Speaker", category="Electronics", price=2499)   # reads like its meaning
print("§2 added id:", new_id, "->", catalog[new_id])

# §3  look up; handle the missing case                     (slide 9 / senior EAFP)
pid = 99
if pid in catalog:                          # simple: LBYL — look before you leap (double lookup, racy)
    name = catalog[pid]
else:
    name = "missing"
try:                                        # advanced: EAFP — ask forgiveness (one lookup, idiomatic)
    name2 = catalog[pid]
except KeyError:
    name2 = "missing"
print("§3 LBYL:", name, "== EAFP:", name2)

# §4  raise a meaningful error, keep the cause             (slide 9 / senior chaining)
class CatalogError(Exception):
    ...
def get_simple(pid):                        # simple: vague exception, original cause lost
    if pid not in catalog:
        raise Exception("not found")
def get(pid):                               # advanced: domain error + 'from' keeps the real cause
    try:
        return catalog[pid]
    except KeyError as exc:
        raise CatalogError(f"id {pid} not found") from exc
try:
    get(99)
except CatalogError as e:
    print("§4 raised:", e, "| cause kept:", type(e.__cause__).__name__)

# §5  a list as a default argument                         (senior trap)
def tag_simple(t, bucket=[]):               # simple: ONE list, shared across ALL calls — a bug
    bucket.append(t)
    return bucket
def tag(t, bucket=None):                    # advanced: None sentinel -> fresh list each call
    bucket = [] if bucket is None else bucket
    bucket.append(t)
    return bucket
tag_simple("a")
print("§5 buggy default:", tag_simple("b"), "| fixed:", tag("b"))   # buggy leaks 'a'

# §6  build functions in a loop                            (senior trap)
simple = [lambda: i for i in range(3)]      # late binding — every lambda sees the SAME i
advanced = [lambda i=i: i for i in range(3)]   # bind the value NOW via a default arg
print("§6 late-binding:", [f() for f in simple], "| fixed:", [f() for f in advanced])
