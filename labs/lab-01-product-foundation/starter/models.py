"""Catalog data model (Day 1 Lab 1).

Copy this file into your working folder's `catalog/` package, then fill in
every body marked `# TODO`. The signatures and docstrings are the contract —
the logic is yours. Done-signal: `pytest tests/test_lab01.py -v` goes green.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


class CatalogError(Exception):
    """Raised when a catalog operation fails (duplicate id, missing id, ...)."""


@dataclass
class Product:
    # TODO: declare fields — id:int, name:str, category:str, price:float,
    #       in_stock:bool=True, tags:list[str]=field(default_factory=list)
    ...


class ProductCatalog:
    """In-memory catalog keyed by product id."""

    def __init__(self, products: Optional[list[Product]] = None) -> None:
        self._items: dict[int, Product] = {}
        for p in products or []:
            self.add(p)

    def add(self, product: Product) -> Product:
        # TODO: raise CatalogError on duplicate id and on negative price,
        #       then store, logger.info(...), and return the product
        ...

    def get(self, product_id: int) -> Product:
        # TODO: raise CatalogError if missing, else return it
        ...

    def delete(self, product_id: int) -> Product:
        # TODO: raise CatalogError if missing, else pop + log + return removed
        ...

    def list_all(self) -> list[Product]:
        # TODO: return a list copy of the values
        ...

    def __len__(self) -> int:
        # TODO: how many products are stored?
        ...
