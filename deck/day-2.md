---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 2 · JSON & API Automation"
footer: "Acuity Training · Day 2 of 4"
---

<!-- _class: title -->

# Day 2
## JSON & API Automation
## **against your Day-1 API**

6 hours · 3 modules · 3 labs · same repo as yesterday

---

# Where we left off

A FastAPI server on `localhost:8000` exposing your `ProductCatalog`.
Today: **drive that server from Python**, with typed payloads.

```
Day 1     Day 2 (today)
─────     ─────────────
server  →  typed server (Pydantic)
            + APIClient
            + CSV bulk-import → import_report.json
```

If you're behind: `cp -r ../checkpoints/day-2-start/. .`

---

# Today's arc

| Module | ~40 min | 80 min lab |
|---|---|---|
| 1 | JSON deep + Pydantic | Lab 4: Pydantic on the API |
| 2 | REST with `requests` | Lab 5: Build the `APIClient` |
| 3 | Data-driven patterns | Lab 6: CSV → API bulk import |

Same `product-catalog/` repo, three new files: `models.py` (upgraded), `client.py`, `import_csv.py`.

---

<!-- _class: title -->

# Module 1
## JSON Deep + Pydantic Validation
*~40 min · then 80 min lab*

---

# JSON — the parts that bite

Yesterday's `@dataclass BankAccount` has to leave Python eventually — as JSON over the wire. JSON is **stricter and poorer** than Python: a few of its rules will bite you.

- No trailing commas, no comments; `true`/`false`/`null` are lowercase. No `NaN`/`Infinity`.
- Keys are always strings. JSON has **no tuples, no sets, no dates**.
- Map: object↔dict, array↔list. A Python **tuple round-trips back as a list**.

→ notebook: module-4 cell 2

---

# stdlib `json` — the 4 functions

Two pairs. The **`s` means "string"**: `loads`/`dumps` work on strings, `load`/`dump` work on open files. That single letter is the whole API.

```python
text = json.dumps(account_dict, indent=2)   # dict → str
back = json.loads(text)                      # str  → dict
```

→ notebook: module-4 cell 4

---

# JSON pitfalls — what raw `json` can't serialise

`json.dumps` raises on a `Decimal` or a `datetime`, and **silently** emits invalid `NaN`. The escape hatch `default=str` stringifies anything — but loses the type. Pydantic handles these for real.

```python
json.dumps({"created": datetime.now()})  # TypeError
json.dumps({"bal": float("nan")})        # 'NaN' — invalid JSON!
```

→ notebook: module-4 cell 6

---

# Why Pydantic, not raw dicts

A raw account `dict` with `id="one", balance=-50` is **wrong forever** — nothing checks it until something downstream crashes. Pydantic validates at the **boundary** and gives field-level errors.

```python
BankAccount.model_validate({"id": "one", "balance": -50})
# ValidationError: id → valid integer; balance → >= 0
```

→ notebook: module-4 cell 8

---

# Migrate `BankAccount`: `@dataclass` → `BaseModel`

The headline change. Same six fields, same type hints — but `BaseModel` **validates on construction**. `Field(ge=...)` adds constraints; `default_factory=list` gives each account its own `tags`.

```python
class BankAccount(BaseModel):
    id: int = Field(ge=1)
    balance: float = Field(default=0.0, ge=0)
    tags: list[str] = Field(default_factory=list)
```

→ notebook: module-4 cell 10

---

# Multiple models, one resource

One class can't do create + update + read. **Create** needs `id`; **update** is all-optional (PATCH) and `extra="forbid"` rejects typos; **read** is what storage returns.

```python
class AccountBase(BaseModel): owner: str; balance: float = Field(ge=0)
class AccountCreate(AccountBase): id: int = Field(ge=1)
class AccountUpdate(BaseModel):
    balance: float | None = None
    model_config = ConfigDict(extra="forbid")
```

→ notebook: module-4 cell 12

---

# Coercion vs validation

Pydantic v2 is **lax by default**: `"1500.0"`→float, `"true"`→bool, `"1"`→int. This is exactly what makes a CSV (all strings) feed an API without manual parsing. Need it exact? `strict=True`.

```python
AccountCreate.model_validate({"id": "1", "balance": "1500.0"})  # coerced ✓
```

→ notebook: module-4 cell 14

---

# `@field_validator` for custom logic

CSV will hand us `tags="primary|online"` — one string, not a list. A `mode="before"` validator splits it **before** type-checking, and passes a real list through untouched.

```python
@field_validator("tags", mode="before")
@classmethod
def _split(cls, v):
    return v.split("|") if isinstance(v, str) else v
```

→ notebook: module-4 cell 16

---

# FastAPI + Pydantic: free /docs

One type hint on the route gives you a validated body (422 with field errors), a serialised response, and an auto-generated `/docs` — no extra code.

```python
@app.post("/accounts", response_model=BankAccount)
def create(payload: AccountCreate): ...
```

→ notebook: module-4 cell 18

---

<!-- _class: lab -->

# 🧪 Lab 4 — Pydantic Models for the Catalog

**80 min** · open `labs/lab-04-pydantic-models/README.md`

You'll add:
- `Product`, `ProductCreate`, `ProductUpdate` in `models.py`
- `response_model=Product` on every route
- New `PATCH /products/{id}` using `ProductUpdate`
- Bad POST → **422** with structured field errors

---

<!-- _class: title -->

# Module 2
## REST APIs with `requests`
*~40 min · then 80 min lab*

---

# The HTTP verbs you actually use

Every call to the account server is one verb + one URL. The verb is a **promise about what the call does** — and two properties of that promise decide whether a retry is safe.

- **Safe** = read-only, changes nothing (`GET`). **Idempotent** = same request, same end state however many times you send it.
- Idempotent matters because a retry re-sends the *same* request: safe for `GET`/`PUT`/`DELETE`, dangerous for a non-idempotent `POST`.

→ notebook: module-5 cell 4

---

# Status codes — whose fault is it?

The first digit tells you who broke and what to do. The whole retry policy falls out of it: a 4xx is **you** (don't retry — the next try fails identically); a 5xx or a dropped connection is **transient** (retry may recover).

- **2xx** ok · **3xx** redirect · **4xx** YOUR fault · **5xx** SERVER's fault.
- Rule: **retry 5xx + network errors; never retry 4xx**.

→ notebook: module-5 cell 6

---

# `requests` — one good pattern

A `Session` pools TCP connections and carries default headers across calls. The shape is always the same four moves — and `timeout` is **not optional**: without it a stalled server hangs your code forever.

```python
session = requests.Session()
session.headers.update({"X-Trace-Id": "abc"})
resp = session.post(url, json=payload, timeout=5.0)  # json= serialises + sets header
resp.raise_for_status()                              # 4xx/5xx → HTTPError
```

→ notebook: module-5 cell 8

---

# Auth: tokens & headers

Auth is just a header you attach to the session once — every later call carries it. The cardinal sin is leaking the secret: an API key in the **query string** lands in server logs and browser history; keep it in a header, and keep the value in an env var, never in source.

```python
session.headers["Authorization"] = f"Bearer {os.environ['TOKEN']}"
```

→ notebook: module-5 cell 10

---

# Wrap it in `AccountClient`

A class with a CRUD method per verb invites copy-paste drift. Instead, **one private `_request` funnel** owns the URL-joining, the timeout, and the error check; every public method calls it. A non-2xx response becomes a small `APIError(status, detail)` you can catch.

```python
def _request(self, method, path, **kwargs):
    resp = self._session.request(method, self.base_url + path, **kwargs)
    if not resp.ok:
        raise APIError(resp.status_code, ...)
    return resp
```

→ notebook: module-5 cell 12

---

# Typed returns, not dicts

The wire speaks dicts; your code should not. Each method validates the JSON back into the **Pydantic models from Module 4**, so callers stay in `BankAccount`-land — and a malformed server response fails loudly at the boundary, not three functions later.

```python
def list_accounts(self) -> list[BankAccount]:
    data = self._request("GET", "/accounts").json()
    return [BankAccount.model_validate(r) for r in data]
```

→ notebook: module-5 cell 14

---

# When to retry — and when not

Reuse Day-1's `@retry` on the `_request` funnel, but scope it to **transient** failures only: connection drops and timeouts. The exception tuple *is* the policy — a 4xx never raises those types, so it can never be retried.

```python
@retry(times=3, delay=0.2,
       exceptions=(ConnectionError, Timeout))   # never 400/401/403/409/422
def _request(self, ...): ...
```

→ notebook: module-5 cell 16

---

<!-- _class: lab -->

# 🧪 Lab 5 — Build the `APIClient`

**80 min** · open `labs/lab-05-api-client/README.md`

You'll build:
- `catalog/client.py` — `APIClient` + `APIError`
- Full typed CRUD via Pydantic models
- `@retry` on every HTTP call

End state: `APIClient().list_products()` returns `list[Product]`.

---

<!-- _class: title -->

# Module 3
## Data-Driven Automation Patterns
*~40 min · then 80 min lab*

---

# Chaining: output of A → input of B

We have an `AccountClient`. Real automation isn't one call — it's small clients **composed into a workflow**, where the output of step A is the input of step B: `create` returns an account whose `id` feeds the `update`, which feeds the `list`.

- The composition is the program; each step stays tiny and testable.
- Day 3 will **mock each step independently** — chaining is only safe because the seams are clean.

→ notebook: module-6 cell 4

---

# Data-driven: CSV → API

A CSV is a list of intentions. Walk it with `csv.DictReader`, validate each row through `AccountCreate.model_validate(row)`, then send the survivors. Pydantic coercion turns CSV **strings** into typed values (`"1500.0"` → `float`).

- Keep **three buckets** separate: **validation errors** (row never reached the API), **API errors** (server rejected: 409/422/500), **successes**.
- Collapsing them lies to the operator — they can't tell a bad row from a flaky server.

→ notebook: module-6 cell 6

---

# Environment & secrets

The base URL and token are **config, not code** — read them from the environment so the same script runs against staging or prod untouched. Workshops: a `.env` file + `python-dotenv`. Production: a secret manager injecting env vars.

```python
TOKEN = os.environ["CATALOG_TOKEN"]            # required → fail loud if missing
BASE  = os.environ.get("CATALOG_BASE_URL", "http://localhost:8000")
```

- **Never** `print(token)` — it lands in CI logs forever.

→ notebook: module-6 cell 8

---

# Pagination

A server won't hand you 10,000 accounts in one response — it pages them. Two shapes you'll meet: **cursor** (`{"items": [...], "next": "/accounts?page=2"}`) and **offset** (`?offset=20&limit=10`). Follow `next` until it's `None`.

- **Cursor is safer**: offset double-reads / skips rows when items shift mid-scan.
- Your loop is the same either way — accumulate items, advance the pointer, stop when it's empty.

→ notebook: module-6 cell 10

---

# Rate limits & backoff

```
HTTP/1.1 429 Too Many Requests
Retry-After: 30
```

A `429` means *slow down* — and the server tells you how long via `Retry-After`. **Respect that header** instead of hammering; blind retries make it worse.

- Wait `Retry-After` seconds, then retry the same request once.
- Production: exponential backoff **+ jitter** so a fleet doesn't retry in lockstep.

→ notebook: module-6 cell 12

---

# The report is the product

```json
{ "summary": {"rows_read": 5, "created": 2,
              "validation_errors": 2, "api_errors": 1},
  "validation_errors": [{"row": 3, "input": {...}, "errors": [...]}] }
```

The CSV is input; the **report is the artifact** you hand back. It's what lets an operator fix row 3 and re-run — and what Day 3's tests assert against.

- Three buckets in, three buckets out: `created`, `validation_errors`, `api_errors`.

→ notebook: module-6 cell 14

---

<!-- _class: lab -->

# 🧪 Lab 6 — Bulk-Import Workflow

**80 min** · open `labs/lab-06-bulk-import/README.md`

You'll build:
- `data/products.csv` with intentionally bad rows
- `catalog/import_csv.py` runnable as `python -m catalog.import_csv`
- `import_report.json` with `created`, `validation_errors`, `api_errors`

End of Day 2 → your repo matches `checkpoints/day-3-start/`.

---

<!-- _class: title -->

# End of Day 2 ✅

Tomorrow: lock everything we just built under a real test suite — pytest, mocks, parametrize, HTML reports, GitHub Actions CI.

**Before you leave:** commit, push, take a screenshot of `import_report.json`.
