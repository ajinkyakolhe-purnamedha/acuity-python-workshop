# Lab 1+ — `Product` Foundation (Senior Track)

**Duration:** ~80 min · **Day:** 1 · **Module:** 1 · **Replaces:** Lab 1 base + stretch

## Who this is for
You've written Python for years. Build the *same* `Product` + `ProductCatalog`, but make `Product` immutable, hashable, and sortable — and make `ProductCatalog` lean on the stdlib instead of hand-rolled loops. Lands on the identical Day-2 baseline; just a sharper route.

## You'll end with
- `catalog/models.py` — `Product` as `@dataclass(frozen=True, slots=True, order=True)`, `CatalogError`, a `ProductCatalog` with EAFP lookups
- `catalog/cli.py` — `list`, `add`, `search`, plus a `summary` subcommand
- `python -m catalog.cli summary` prints counts via `Counter`

## Steps

1. **Immutable, hashable, orderable `Product`.**
   ```python
   @dataclass(frozen=True, slots=True, order=True)
   class Product:
       id: int
       name: str
       category: str
       price: float
       in_stock: bool = True
       tags: tuple[str, ...] = ()      # tuple, not list — frozen must be hashable
   ```
   - `order=True` sorts by field order (id first). Decide if that's the order you want — reorder fields or set `sort_index` via `field(compare=...)` if not.
   - `tags` is a `tuple` because `frozen` instances must be hashable; a `list` field breaks `__hash__`. Note the friction — Day 2's Pydantic removes it.

2. **EAFP lookups in `ProductCatalog`.** No `if id in self._items` pre-checks:
   ```python
   def get(self, product_id: int) -> Product:
       try:
           return self._items[product_id]
       except KeyError:
           raise CatalogError(f"id {product_id} not found") from None
   ```
   Use `from None` deliberately — the bare `KeyError` is noise here.

3. **`add` rejects duplicates without a double lookup.** Use `dict.setdefault` or catch the collision; don't `if id in ...: raise` then assign.

4. **`summary()` via `Counter`.**
   ```python
   from collections import Counter
   def summary(self) -> dict:
       cats = Counter(p.category for p in self._items.values())
       return {
           "count": len(self),
           "total_value": sum(p.price for p in self._items.values()),
           "categories": dict(cats),
       }
   ```

5. **Sorting for free.** Because `Product` is `order=True`, `sorted(catalog.list_all())` just works. Add `--sort price|name` to the `list` subcommand using `key=attrgetter(...)`.

6. **`summary` subcommand** in `cli.py`. Run it.

## Expected output
```
$ python -m catalog.cli summary
count=5  total_value=₹10695.00
  Electronics  3
  Home         1
  Fitness      1

$ python -m catalog.cli list --sort price
    1  USB-C Cable          ₹  499.00
    3  Steel Water Bottle   ₹  899.00
    ...
```

## Common pitfalls
- `list` field on a `frozen` dataclass — `__hash__` raises at use. Use `tuple`.
- `order=True` without thinking about field order → sorts by `id` when you meant `price`. Set `compare=False` on fields that shouldn't participate.
- `frozen=True` means `product.price = 9` raises `FrozenInstanceError`. To "edit", build a new one: `replace(product, price=9)` (`from dataclasses import replace`).
- `slots=True` + a `@cached_property` collide — slots forbid the backing dict. Know the tradeoff.

## Stretch
- Add `__post_init__` that rejects negative price by raising `CatalogError` — the dataclass mirror of a Pydantic validator. Note where it fires (construction, not `add`) and what that changes.
- Make `ProductCatalog` itself iterable (`__iter__`, `__contains__`) so `for p in catalog` and `99 in catalog` work.

## You should now match `checkpoints/day-2-start/`
The reference baseline uses a plain (non-frozen) dataclass. Your frozen/slots version is **behaviorally compatible** — if you want to rejoin the exact baseline for Day 2, copy `checkpoints/day-2-start/` over your folder. Nothing you built here is wasted: the dunder/`Counter` instincts carry into every later day.
