"""Tiny argparse CLI for the catalog (Day 1 Lab 1).

The argparse plumbing is given (boilerplate, not the lesson). Fill the command
bodies marked `# TODO`. `search` / `save` / `load` arrive in Lab 2, once the
catalog has queries and persistence to back them.

Run:  python -m catalog.cli list
"""

from __future__ import annotations

import argparse
import logging
import sys

from .models import CatalogError, Product, ProductCatalog

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

SEED = [
    Product(1, "USB-C Cable", "Electronics", 499.0, True, ["cable", "usb-c"]),
    Product(2, "Mechanical Keyboard", "Electronics", 5499.0, True, ["keyboard", "mech"]),
    Product(3, "Steel Water Bottle", "Home", 899.0, True, ["bottle", "steel"]),
    Product(4, "Yoga Mat", "Fitness", 1299.0, False, ["mat", "yoga"]),
    Product(5, "Bluetooth Speaker", "Electronics", 2499.0, True, ["speaker", "bt"]),
]


def cmd_list(args: argparse.Namespace) -> int:
    catalog = ProductCatalog(list(SEED))
    # TODO: print each product as one row, then a "<n> products" footer
    ...
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    catalog = ProductCatalog(list(SEED))
    # TODO: build a Product from args, catalog.add(...);
    #       on CatalogError print "ERROR: ..." to stderr and return 1
    ...
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="catalog")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list").set_defaults(fn=cmd_list)

    p_add = sub.add_parser("add")
    p_add.add_argument("id", type=int)
    p_add.add_argument("name")
    p_add.add_argument("category")
    p_add.add_argument("price", type=float)
    p_add.set_defaults(fn=cmd_add)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
