# Lab 3+ — Local API Server (Senior Track)

**Duration:** ~80 min · **Day:** 1 · **Module:** 3 · **Replaces:** Lab 3 base + stretch

## Who this is for
Same FastAPI server, built so Day 3 testing is painless: a **dependency-injected** catalog (no global to monkeypatch), an **exponential-backoff** `@retry`, a `@property` computed field, and typed responses. This is the "I've shipped FastAPI" version of Lab 3.

## You'll end with
- `catalog/decorators.py` — `@log_calls` + `@retry(times, delay, backoff, exceptions)` with exponential backoff
- `catalog/server.py` — catalog injected via `Depends`, `CatalogError` mapped to HTTP codes
- A `@property` on `Product` (or catalog) computing a derived field
- Running server at `localhost:8000` with `/docs`

## Steps

1. **`@retry` with exponential backoff.** Extend the base signature:
   ```python
   def retry(times=3, delay=0.1, backoff=2.0,
             exceptions=(Exception,)):
       def decorator(func):
           @functools.wraps(func)
           def wrapper(*args, **kwargs):
               wait, last = delay, None
               for attempt in range(1, times + 1):
                   try:
                       return func(*args, **kwargs)
                   except exceptions as exc:
                       last = exc
                       logger.warning("%s %d/%d failed: %s",
                                      func.__name__, attempt, times, exc)
                       if attempt < times:
                           time.sleep(wait); wait *= backoff
               raise last
           return wrapper
       return decorator
   ```
   Keep `functools.wraps` — Day 3 fixtures introspect the wrapped function. Verify backoff with a flaky function and `delay=0.01`.

2. **Inject the catalog with `Depends`** — no module global the tests must reach around:
   ```python
   from fastapi import Depends

   app = FastAPI(title="Product Catalog", version="0.1.0")
   app.state.catalog = ProductCatalog(list(seed_products()))

   def get_catalog() -> ProductCatalog:
       return app.state.catalog

   @app.get("/products")
   def list_products(cat: ProductCatalog = Depends(get_catalog)) -> list[dict]:
       return [p.to_dict() for p in cat.list_all()]
   ```
   On Day 3 you'll override this with `app.dependency_overrides[get_catalog] = lambda: fresh` — clean, no monkeypatch.

3. **A `@property` computed field.** Add a derived value that isn't stored:
   ```python
   @property
   def display_price(self) -> str:
       return f"₹{self.price:,.2f}"
   ```
   (On a `frozen` dataclass from Lab 1+, `@property` is fine — it doesn't store state. `@cached_property` would clash with `slots=True`; know why.)

4. **Map `CatalogError` → HTTP precisely.** Missing → 404, duplicate → 409, bad payload → 400. One `try/except CatalogError` per mutating route; let unexpected errors 500 honestly (don't blanket-catch `Exception`).

5. **Typed route signatures.** Even pre-Pydantic, annotate return types (`-> list[dict]`, `-> dict`) so `/docs` and the Day-2 Pydantic swap are a diff, not a rewrite.

6. **Run + verify** (`uvicorn catalog.server:app --reload`), then hit the curl block from the base Lab 3 and visit `/docs`.

## Expected output
```
$ curl http://localhost:8000/health
{"status":"ok","count":5}

$ curl -o /dev/null -w '%{http_code}\n' http://localhost:8000/products/999
404
$ curl -o /dev/null -w '%{http_code}\n' -X POST .../products -d '{...dup id...}'
409
```
`@retry` self-test (third attempt succeeds):
```
WARNING flaky attempt 1/3 failed: boom
WARNING flaky attempt 2/3 failed: boom
INFO    return flaky -> 'ok'      (waited 0.01s, 0.02s — exponential)
```

## Common pitfalls
- `Depends(get_catalog())` — calling it. Pass the **function** `Depends(get_catalog)`, not its result.
- Putting `app.state.catalog = ...` inside a route — it must be set at startup (module level or a `@app.on_event("startup")`).
- Exponential backoff with a high `backoff` and `times` → multi-second test hangs. Use tiny `delay` in tests.
- Blanket `except Exception` on a route hides real 500s as 400s. Catch `CatalogError` specifically.
- Returning a `frozen` dataclass directly — FastAPI still can't serialize it; `.to_dict()` until Pydantic on Day 2.

## Stretch
- Add `PATCH /products/{id}/price` injected via `Depends`, returning the updated product.
- Stack decorators: `@log_calls` on a route *and* `@retry` on the `APIClient` you'll write Day 2 — observe order (`@log_calls` outermost logs the retries).
- Write a tiny `Protocol` (`SupportsToDict`) and type `list_products`' return against it.

---

**End of Day 1 — Senior Track.** Your server is DI-clean and your decorators are production-shaped. To start Day 2 from the canonical baseline, copy `checkpoints/day-2-start/` — but keep your `Depends` pattern in mind: it's exactly what makes Day 3's test fixtures trivial.
