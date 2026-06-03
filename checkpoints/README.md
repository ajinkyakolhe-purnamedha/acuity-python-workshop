# Catch-up baselines

Each `day-N-start/` is the **start** state for Day N. If you fell behind the
previous day, copy one of these over your working folder and rejoin:

```bash
cd path/to/your/working-folder
rm -rf catalog tests data .github   # whatever you had
cp -r ../workshop/checkpoints/day-N-start/. .
pip install -e ".[dev]"
```

| Folder | Contents |
|---|---|
| `day-1-start/` | Day-1 starting point — `pyproject.toml`, `.gitignore`, empty `catalog/` package, **+ `tests/` spec suite** (the Day-1 labs' done-signal; `pytest` skips each test until you build the module it covers, then red→green) |
| `day-2-start/` | End of Day 1 — `Product`, `ProductCatalog`, storage, decorators, FastAPI server |
| `day-3-start/` | End of Day 2 — adds Pydantic models, `APIClient`, CSV bulk-import |
| `day-4-start/` | End of Day 3 — adds the full pytest suite, coverage, and GitHub Actions |

The final state (Day 4 end) is the `product-catalog/` folder one level up.

## Standalone lab baseline

| Folder | Contents |
|---|---|
| `lab-3-start/` | **Lab 3 on its own** (no Labs 1–2 needed). `models.py` + `storage.py` are provided **complete**; `decorators.py` + `server.py` are **scaffolds** with `# TODO`s. You build only the decorators + FastAPI server. Done-signal: `pytest tests/test_lab03.py`. |

```bash
cp -r checkpoints/lab-3-start my-lab3 && cd my-lab3
pip install -e ".[dev]"
pytest tests/test_lab03.py          # RED — now fill the TODOs in decorators.py + server.py → GREEN
```
