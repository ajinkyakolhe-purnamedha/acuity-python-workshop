# Lab 5 — Build the `APIClient`

**Duration:** ~80 min · **Day:** 2 · **Module:** 2 (REST APIs with `requests`)

> **Concepts used:** `requests.Session`, the `APIClient`/`_request` funnel & `@retry` on transient failures → `codealong/module-5.ipynb` (the `@retry` decorator originates in Day-1 `codealong/module-3.ipynb`).
> This lab applies the module's `AccountClient` concepts to the course's `Product` domain — same patterns, different thing (the deliberate concept-vs-lab seam).

## Goal
Build a typed `APIClient` class that drives the FastAPI server from
Python — full CRUD, retry on transient failures, structured errors when
the server says no. Every method returns Pydantic `Product` objects; no
raw dicts leak out. This same class becomes the **toolbelt the agent uses
on Day 4**, so getting it clean matters.

## You start with
- Lab 4 end-state — Pydantic-typed FastAPI server.

## You'll end with
- `catalog/client.py` defining `APIClient` and `APIError`
- A working `APIClient().list_products()` that returns `list[Product]`
- The `@retry` decorator from Day 1 wrapping every HTTP call

## Starter files

`starter/client.py` gives you the class skeleton — `__init__`, the `@retry`-decorated `_request` signature, and every CRUD method signature. Fill the bodies marked `# TODO`. The funnel pattern is decided; the logic is yours.

```bash
cp ../labs/lab-05-api-client/starter/client.py catalog/   # run from my-catalog/
```

| File | You write |
|---|---|
| `starter/client.py` | `APIError.__init__`, the `_request` + `_extract_detail` bodies, and all six CRUD method bodies |

## Steps

1. **Start with the boilerplate.** `__init__` is already filled in `starter/client.py` — it wraps a `requests.Session` (`session or requests.Session()`). Why a session? Connection pooling + a single place to add auth headers later, and it's the seam tests inject a fake through on Day 3.

2. **One low-level `_request` method, decorated with `@retry`.**

   ```python
   @retry(times=3, delay=0.2,
          exceptions=(requests.ConnectionError, requests.Timeout))
   def _request(self, method: str, path: str, **kwargs) -> requests.Response:
       kwargs.setdefault("timeout", self.timeout)
       response = self._session.request(method, f"{self.base_url}{path}", **kwargs)
       if not response.ok:
           raise APIError(response.status_code, self._extract_detail(response))
       return response
   ```

   Only retry on **network** errors. Retrying a 400 is pointless and a 500 is questionable — let the caller decide.

3. **Define `APIError`** as a regular `Exception` with `status_code` and `detail` attributes (call `super().__init__` with a `"{status}: {detail}"` message, then stash both). Don't lean on `requests.HTTPError` — callers shouldn't have to import `requests` to catch errors from your client. Fill the `APIError.__init__` TODO in `starter/client.py`.

4. **Add typed CRUD methods.** Each method is the same move: call `_request`, then `Model.model_validate(...)` the JSON response (a list comprehension for `list_products`, a single validate for the rest; `delete_product` returns nothing). Do this for all six CRUD methods — fill the TODOs in `starter/client.py`.

5. **Drive it from an `if __name__ == "__main__":` block or a REPL.**

   ```python
   from catalog.client import APIClient
   from catalog.models import ProductCreate

   c = APIClient()
   print(c.health())
   c.create_product(ProductCreate(id=900, name="REPL test", category="Misc", price=10))
   for p in c.list_products():
       print(p.id, p.name)
   ```

## Expected output

```
>>> c.health()
{'status': 'ok', 'count': 5}

>>> c.list_products()
[Product(name='USB-C Cable', category='Electronics', price=499.0, in_stock=True, tags=['cable', 'usb-c'], id=1),
 Product(name='Mechanical Keyboard', category='Electronics', price=5499.0, ...)]

>>> c.create_product(ProductCreate(id=1, name="dup", category="x", price=1))
APIError: 409: Product id 1 already exists
```

## Make it pass

Your done-signal is the spec — the REPL output above is the warm-up. It **skips** until `client.py` exists, then goes red → green.

```bash
pytest tests/test_lab05.py -v
```

Target: all of `TestAPIClient` green — typed returns, `APIError` on non-2xx, and `@retry` recovering from a transient failure (an injected fake session stands in for the server).

## Common pitfalls
- Calling `requests.get(...)` instead of `self._session.request(...)` skips the session + the retry decorator. **Always** go through `_request`.
- Re-using one `APIClient` across threads — `requests.Session` is *mostly* thread-safe but don't push it. One client per thread.
- Forgetting to pass `timeout`. Without one, a hung server hangs your script forever.
- Letting the server raise `HTTPException(detail=...)` with non-string detail (e.g. Pydantic's list of errors) — `_extract_detail` should still handle it. Test that path.

## Stretch (optional)
- Add `auth_token: Optional[str] = None` to `__init__` and inject `Authorization: Bearer …` into every request.
- Add `list_products(category: Optional[str] = None)` that passes `?category=` as a query param (you'll need to add the filter to `server.py` too).
