---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 1 · Python Fundamentals + Catalog Foundation"
footer: "Acuity Training · Day 1 of 4"
---

<!-- _class: title -->

# Day 1
## Python Fundamentals
## **+ build the Catalog Foundation**

6 hours · 3 modules · 3 labs · one repo for the week

---

# What we build today

By 6 PM, a **local FastAPI server** running on your laptop, serving a `Product` catalog you wrote from scratch.

- Module 1 → Python core → Lab 1: `Product` foundation
- Module 2 → Data structures, files, modules → Lab 2: Persistent catalog
- Module 3 → OOP, decorators, FastAPI → Lab 3: Local API server

**Same repo carries through Day 2, 3, 4.** No throwaway demos.

---

# The week, in one picture

```
Day 1   Product class + FastAPI server
Day 2   + Pydantic + APIClient + CSV bulk-import
Day 3   + pytest suite + mocks + CI green
Day 4   + LLM-powered CatalogAgent + agent tests
```

Every day extends yesterday's project (your `my-catalog/`).
A catch-up baseline (`day-N-start/`) is provided each morning.

---

<!-- _class: title -->

# Module 1
## Python Core
*~40 min · then 80 min lab*

---

# Our story for today: bank accounts

Every example today is one **account**. In Python an account is just a `dict` — named fields, no class yet (classes come in Module 3).

```python
acct = {"id": 1, "owner": "Ada", "account_type": "savings",
        "balance": 1500.0, "is_active": True,
        "tags": ["primary", "online"]}
```

Same six fields all day. M2 stores many of these in files; M3 turns them into a class.

---

# Variables & Python's types — what is it?

A variable is just a name pointing at a value. You don't declare a type — Python figures it out from the value. The account fields cover the core types.

```python
acct["owner"]  # str  ·  acct["id"]   # int   ·  acct["balance"]  # float
acct["is_active"]  # bool  ·  acct["tags"]  # list  ·  acct        # dict
```

→ notebook: module-1 cell 2

---

# Truthiness — empty things are False

Python lets you test a value directly in `if`. "Empty" or "zero" values are **falsy**: `0`, `0.0`, `""`, `[]`, `{}`, `None`, `False`. Everything else is truthy.

```python
if not acct["tags"]:        # empty list is falsy → True here
    print("no tags yet")
```

→ notebook: module-1 cell 4

---

# Control flow — if / elif / else, for, while

`if/elif/else` chooses a branch; `for` walks a sequence; `while` repeats until a condition is false. Indentation (not braces) defines the block.

```python
for acct in accounts:
    if acct["is_active"]:
        print(acct["owner"])
```

→ notebook: module-1 cell 6

---

# Functions — args, defaults, return

`def` names reusable logic. Parameters can have **defaults**; callers pass args by position or by keyword (`name=value`); `return` hands a value back.

```python
def total_balance(accounts, only_active=True):
    return sum(a["balance"] for a in accounts if a["is_active"])
```

→ notebook: module-1 cell 8

---

# Exceptions — try / except / else / finally

When something goes wrong you `raise` an error; the caller `try`s the risky code and `except`s the failure. `else` runs on success, `finally` always runs.

```python
try:
    acct = find_account(accounts, 99)
except LookupError as err:
    print("not found:", err)
```

→ notebook: module-1 cell 10

---

<!-- _class: lab -->

# 🧪 Lab 1 — The `Product` Foundation

**80 min** · open `labs/lab-01-product-foundation/README.md` · scaffolds in `starter/`

You'll build:
- `catalog/models.py` — `Product` + `ProductCatalog`
- `catalog/cli.py` — `list`, `add` subcommands

End state: `python -m catalog.cli list` prints 5 seeded products.

---

<!-- _class: title -->

# Module 2
## Data Structures, Files & Modules
*~40 min · then 80 min lab*

---

# The four containers — what are they?

A bank has **many** accounts. Pick the container by the question you ask most: walk in order → **list**; look up by key → **dict**; a fixed record → **tuple**; unique membership → **set**.

```python
accounts = [ada, lin, sam]      # list: ordered bank
ada["balance"]                  # dict: account, lookup by key
tags = {"online", "vip"}        # set: unique tags
```

→ notebook: module-2 cell 2

---

# Dict — go deep

The dict is the workhorse: `.get` for safe lookup, an `{id: account}` index for O(1) finds, `|` to merge. The classic bug: **mutating a dict while iterating it** — iterate a copy of the keys.

```python
by_id = {a["id"]: a for a in accounts}   # index
by_id.get(99, None)                      # no KeyError
for k in list(by_id): ...                # safe to delete
```

→ notebook: module-2 cell 4

---

# Comprehensions — the Python idiom

A comprehension builds a new collection from an old one in one line — it says *what*, not *how*. Three flavors: list `[...]`, dict `{k: v}`, set `{...}`.

```python
active = [a["owner"] for a in accounts if a["is_active"]]
balances = {a["id"]: a["balance"] for a in accounts}
```

→ notebook: module-2 cell 6

---

# JSON — save & load accounts

`json.dump` writes a Python object to a file; `json.load` reads it back. JSON is the natural format for our dict-shaped accounts. Note: JSON has no tuple — a tuple **round-trips back as a list**.

```python
json.dump(accounts, fh, indent=2)   # save
accounts = json.load(fh)            # load
```

→ notebook: module-2 cell 8

---

# CSV — rows in, rows out

`csv.DictWriter`/`DictReader` move account dicts to and from rows. Always pass `newline=""`. The pain: everything reads back as a **string** — you coerce types by hand (Day-2 Pydantic fixes this).

```python
csv.DictWriter(fh, fieldnames=fields).writerows(accounts)
rows = list(csv.DictReader(fh))     # rows[0]["balance"] is "1500.0" (str!)
```

→ notebook: module-2 cell 10

---

# Modules & virtual environments — what are they?

A **module** is just a `.py` file you `import`. A **virtual environment** is a private per-project Python with its own packages, so projects never collide.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

→ notebook: module-2 cell 12

---

# Logging (not `print`)

`print` is for scripts; real code uses `logging`. Levels (`DEBUG<INFO<WARNING<ERROR`) dial verbosity without deleting lines. Loggers are *named* — pass `__name__` to tune per-module.

```python
logger = logging.getLogger("bank")
logger.info("withdraw owner=%s amount=%s", owner, amt)   # %s args, not f-string
```

→ notebook: module-2 cell 14

---

<!-- _class: lab -->

# 🧪 Lab 2 — Persistent Catalog

**80 min** · open `labs/lab-02-persistent-catalog/README.md` · scaffolds in `starter/`

You'll build:
- `catalog/storage.py` — CSV + JSON load/save
- Comprehension methods: `search_by_name`, `filter_by_price`, `group_by_category`
- `search` / `save` / `load` CLI subcommands

End state: catalog survives process restart.

---

<!-- _class: title -->

# Module 3
## OOP, Decorators, Type Hints, FastAPI
*~40 min · then 80 min lab*

---

# `class` / `self` / `__init__` — what is it?

A **class** is a blueprint; an **object** is one thing built from it.
`__init__` runs once when you build an object — it sets up that object's data.

```python
acct = BankAccount("Ada", 100)   # __init__ runs, returns the object
```

→ notebook: module-3 cell 2

---

# `self` — what is it?

A method's first parameter is the object it was called on.
Python passes it automatically — you write `self` by convention.

`acct.deposit(50)` → `BankAccount.deposit(acct, 50)`  *(Python fills in `self`)*

→ notebook: module-3 cell 4

---

# Methods vs attributes — what is it?

**Attributes** are the data on an object (`self.balance`).
**Methods** are functions defined in the class that act on that data.

```python
acct.balance        # attribute — just a value
acct.deposit(50)    # method   — call it, it changes state
```

→ notebook: module-3 cell 6

---

# Dunder methods — what is it?

"Dunder" = **d**ouble **under**score. Python calls them for you when you use
built-in syntax. `__repr__` controls how an account prints; `__eq__` controls `==` (by `id`).

```python
print(acct)         # Python calls acct.__repr__()
acct1 == acct2      # Python calls acct1.__eq__(acct2) — same id?
```

→ notebook: module-3 cell 8

---

# Type hints — what is it?

Annotations that say what type a value *should* be. Python does **not** enforce
them at runtime — they exist for readers, editors, and tools.

```python
def total_balance(accounts: list[dict]) -> float: ...
```

- Editors autocomplete · mypy/pyright catch bugs · FastAPI & Pydantic use them

→ notebook: module-3 cell 10

---

# `@dataclass` — boilerplate for free

A decorator that writes the boring class boilerplate for you.
List the fields with type hints; you get `__init__`, `__repr__`, `__eq__` free.

```python
@dataclass
class BankAccount:
    id: int
    owner: str
    balance: float = 0.0
    tags: list[str] = field(default_factory=list)
```

> Go deeper: Day 2 swaps `@dataclass` → Pydantic `BaseModel`, same fields, plus runtime validation.

→ notebook: module-3 cell 12

---

# What a decorator is — what is it?

A function that **takes a function and returns a (usually wrapped) function**.
`@log_calls` above a function is just `f = log_calls(f)`.

```python
@log_calls
def withdraw(acct, amount): ...   # withdraw = log_calls(withdraw)
```

→ notebook: module-3 cell 14

---

# `@retry(times=3)` — a decorator that takes arguments

A **parametrized** decorator: you call it with arguments, *then* it decorates.
One extra layer — the outer function captures the settings and returns the decorator.

```python
@retry(times=3)
def fetch_account(acct_id): ...   # flaky read, retried
```

→ notebook: module-3 cell 16

---

# FastAPI is decorators in action

A web route is just a function with a decorator on top. `@app.get("/accounts")`
*registers* that function to run when a request hits `/accounts`. Same shape you just built.

```python
@app.get("/accounts")
def list_accounts(): return ACCOUNTS
```

> Go deeper: Day 4's agent `@tool` reuses this exact register-a-function pattern.

→ notebook: module-3 cell 18

---

# What you'll run at the end of Lab 3

```bash
uvicorn catalog.server:app --reload

# Another terminal
curl http://localhost:8000/health
# {"status":"ok","count":5}

curl http://localhost:8000/products/2
# {"id":2,"name":"Mechanical Keyboard", ...}
```

Then visit **http://localhost:8000/docs** — that's your API, documented for free.

---

<!-- _class: lab -->

# 🧪 Lab 3 — Local API Server

**80 min** · open `labs/lab-03-local-api-server/README.md` · scaffolds in `starter/`

You'll build:
- `catalog/decorators.py` — `@retry` and `@log_calls`
- `catalog/server.py` — FastAPI app with full CRUD
- A running server on `localhost:8000` with `/docs`

End of Day 1 → your repo matches `checkpoints/day-2-start/`.

---

<!-- _class: title -->

# End of Day 1 ✅

Tomorrow: typed payloads (Pydantic), `requests`, and a Python client that drives this server end-to-end.

**Before you leave:** commit your work, push to your branch, take a screenshot of `/docs`.
