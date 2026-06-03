"""CSV + JSON persistence for the catalog (Day 1 Lab 2).

Copy into your `catalog/` package and fill the `# TODO`s. The other Lab 2 work
— `to_dict`/`from_dict` on Product and the query methods on ProductCatalog —
are *edits to your existing models.py*; see the lab README for those stubs.

Done-signal: `pytest tests/test_lab02.py -v` goes green.
"""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Iterable

from .models import Product, ProductCatalog

logger = logging.getLogger(__name__)

CSV_FIELDS = ["id", "name", "category", "price", "in_stock", "tags"]


def save_json(catalog: ProductCatalog, path: str | Path) -> None:
    # TODO: write [p.to_dict() for p in catalog.list_all()] as JSON, indent=2
    ...


def load_json(path: str | Path) -> ProductCatalog:
    # TODO: missing file -> log a warning, return an empty ProductCatalog.
    #       else read rows and rebuild with Product(**row). (tags stay a list in JSON)
    ...


def save_csv(catalog: ProductCatalog, path: str | Path) -> None:
    # TODO: csv.DictWriter over CSV_FIELDS; join tags with "|". Open with newline="".
    ...


def load_csv(path: str | Path) -> ProductCatalog:
    # TODO: missing file -> empty. Else csv.DictReader -> [Product.from_dict(row), ...]
    ...


def seed_products() -> Iterable[Product]:
    """The 5 demo products — moved here out of cli.py."""
    # TODO: return the 5 Products you seeded in Lab 1
    ...
