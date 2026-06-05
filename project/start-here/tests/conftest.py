"""Shared fixtures for the Day-1 lab specs (Labs 1–2).

The import is lazy inside the fixture so this conftest stays importable even
before `catalog/models.py` exists. The Lab 1–2 specs target the **Day-1
dataclass** `Product`; once you migrate it to Pydantic in Lab 4 they skip
(see the module-level guard in test_lab01/02).
"""

from __future__ import annotations

import dataclasses

import pytest


@pytest.fixture
def seeded_catalog():
    """A 3-product catalog: ids 10/20/30, two Electronics + one Fitness."""
    pytest.importorskip("catalog.models")
    from catalog.models import Product, ProductCatalog

    if not dataclasses.is_dataclass(Product):
        pytest.skip("Lab 1–2 specs target the Day-1 dataclass Product (now Pydantic)")

    # keyword args work for both the dataclass (Day 1) and Pydantic (Day 2+)
    return ProductCatalog(
        [
            Product(id=10, name="Cable", category="Electronics",
                    price=499.0, in_stock=True, tags=["usb"]),
            Product(id=20, name="Keyboard", category="Electronics",
                    price=5499.0, in_stock=True, tags=["mech"]),
            Product(id=30, name="Yoga Mat", category="Fitness",
                    price=1299.0, in_stock=False, tags=["yoga"]),
        ]
    )
