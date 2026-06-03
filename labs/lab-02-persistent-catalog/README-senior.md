# Lab 2+ — Persistent Catalog (Senior Track)

**Duration:** ~80 min · **Day:** 1 · **Module:** 2 · **Replaces:** Lab 2 base + stretch

## Who this is for
Persistence done the way you'd ship it: **atomic** writes (no half-written files after a crash), **streamed** reads (constant memory regardless of file size), and stdlib-driven queries. Same `storage.py` surface as the base lab, hardened internals.

## You'll end with
- `catalog/storage.py` — `save_json`/`load_json`/`save_csv`/`load_csv`/`seed_products`, all on `pathlib.Path`, JSON save is atomic, CSV load is a generator
- `ProductCatalog` queries via `defaultdict`/`Counter`
- A `catalog.json` that is never left half-written

## Steps

1. **`atomic_write` context manager** (top of `storage.py`):
   ```python
   from contextlib import contextmanager
   import os, pathlib

   @contextmanager
   def atomic_write(path: pathlib.Path):
       tmp = path.with_suffix(path.suffix + ".tmp")
       fh = tmp.open("w", newline="", encoding="utf-8")
       try:
           yield fh
           fh.flush(); os.fsync(fh.fileno()); fh.close()
           os.replace(tmp, path)            # atomic rename
       except BaseException:
           fh.close(); tmp.unlink(missing_ok=True)
           raise
   ```
   `save_json` and `save_csv` both write through this. Kill the process mid-save (Ctrl-C in a `time.sleep` you insert) and confirm `catalog.json` is either old-and-intact or new-and-complete — never garbage.

2. **`pathlib` everywhere.** Signatures take `path: pathlib.Path`. No `open(str)`, no `os.path.join`. `DEFAULT_PATH = pathlib.Path("catalog.json")`.

3. **Streamed CSV load — a generator, not a list.**
   ```python
   def iter_csv_rows(path: pathlib.Path) -> Iterator[Product]:
       with path.open(newline="", encoding="utf-8") as fh:
           for row in csv.DictReader(fh):
               yield Product.from_dict(row)

   def load_csv(path) -> ProductCatalog:
       return ProductCatalog(list(iter_csv_rows(path)))   # list() only here
   ```
   The point: `iter_csv_rows` holds one row at a time. Day 2's bulk-import reuses exactly this to stream a large CSV into the API without loading it all.

4. **`load_json` is missing-file safe** — log a warning, return empty `ProductCatalog`. Use `Path.exists()`, not a `try/except FileNotFoundError` around the whole rebuild (be precise about what you're guarding).

5. **Queries via stdlib:**
   ```python
   from collections import defaultdict, Counter

   def group_by_category(self) -> dict[str, list[Product]]:
       groups: dict[str, list[Product]] = defaultdict(list)
       for p in self._items.values():
           groups[p.category].append(p)
       return dict(groups)

   def count_by_category(self) -> dict[str, int]:
       return dict(Counter(p.category for p in self._items.values()))
   ```
   `count_by_category` is the exact tool the Day-4 agent will expose. Build it now.

6. **CLI** — `save`/`load` subcommands, only persist after a mutation (`add`/`delete`), and add `counts` calling `count_by_category`.

## Expected output
```
$ python -m catalog.cli counts
Electronics  3
Home         1
Fitness      1

$ python -m catalog.cli add 10 Notebook Stationery 199
INFO: saved 6 products to catalog.json   (atomic: catalog.json.tmp → catalog.json)
```

## Common pitfalls
- Forgetting `os.replace` is atomic but `shutil.move` across filesystems is **not** — keep the tmp file beside the target (same dir, same FS).
- Returning a generator from `load_csv` and wondering why the catalog is empty on second iteration — generators exhaust. `list()` at the boundary, stream internally.
- `newline=""` must be set on the *file you write to* (here, inside `atomic_write`) or Windows doubles line endings.
- `os.fsync` matters for true durability but is slow — fine for a catalog save, don't fsync per-row in a loop.

## Stretch
- Add a `--format csv|json` flag dispatched with `functools.singledispatch` or a dict of handlers (no `if/elif` ladder).
- Make `save_json` write deterministically (`sort_keys=True`) so two saves of the same data are byte-identical — useful for diffing in git on Day 3.

## You should now match `checkpoints/day-3-start/` shape
Your `storage.py` is hardened beyond the reference, but the public functions match. To rejoin the exact Day-2 starting baseline, copy `checkpoints/day-2-start/`. The `count_by_category` and streaming generator you wrote here both resurface — Day 2 (bulk import) and Day 4 (agent tool).
