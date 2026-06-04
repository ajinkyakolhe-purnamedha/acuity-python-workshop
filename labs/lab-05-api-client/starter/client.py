"""Typed HTTP client for the catalog API — Day 2 Lab 5.

Drives the FastAPI server from Python. Every method returns a Pydantic
`Product` (or a list of them) — no raw dicts leak out. One private
`_request` funnel wears the Day-1 `@retry` so a network blip doesn't kill a
bulk-import run. On Day 4, the agent's tools will literally *be* these methods.

Fill every `# TODO`. The `__init__`, the `@retry` decorator, and the method
signatures are given — you write the bodies.

Done-signal: `APIClient().list_products()` returns `list[Product]`, and a
duplicate POST raises `APIError` (README → Expected output).
Concepts: codealong/module-5.ipynb (requests.Session, the _request funnel,
@retry, typed returns).  `@retry` itself: codealong/module-3.ipynb.
"""

from __future__ import annotations

import logging
from typing import Optional

import requests

from .decorators import retry
from .models import Product, ProductCreate, ProductUpdate

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 5.0
DEFAULT_BASE_URL = "http://localhost:8000"


class APIError(Exception):
    """Raised when the catalog API returns a non-2xx response.

    A plain Exception on purpose: callers catch APIError without importing
    `requests` (module-5, §"Wrap it in AccountClient").
    """

    def __init__(self, status_code: int, detail: str) -> None:
        # TODO: super().__init__(f"{status_code}: {detail}") and store
        #       self.status_code / self.detail so callers can branch on them.
        ...


class APIClient:
    """CRUD client for the catalog API."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        # session is injected for tests (Day 3) — defaults to a real pooled Session.
        self._session = session or requests.Session()

    # ---- low-level: every call funnels through here ----

    @retry(times=3, delay=0.2, exceptions=(requests.ConnectionError, requests.Timeout))
    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        # TODO (module-5, §"requests — one good pattern"):
        #   1. default the timeout:        kwargs.setdefault("timeout", self.timeout)
        #   2. send it via the SESSION:    resp = self._session.request(method, f"{self.base_url}{path}", **kwargs)
        #   3. on a non-2xx, raise APIError(resp.status_code, self._extract_detail(resp))
        #   4. otherwise return resp
        # NOTE: always go through self._session (NOT requests.get) so the retry
        #       + session headers apply. Only retry network errors, never 4xx.
        ...

    @staticmethod
    def _extract_detail(response: requests.Response) -> str:
        # TODO: return the server's JSON "detail" if present, else the raw text.
        #   try: return response.json().get("detail", response.text)
        #   except ValueError: return response.text or response.reason
        ...

    # ---- typed CRUD: each is two lines (call _request, validate into a model) ----

    def health(self) -> dict:
        # hint: return self._request("GET", "/health").json()
        ...

    def list_products(self) -> list[Product]:
        # hint: data = self._request("GET", "/products").json()
        #       return [Product.model_validate(row) for row in data]
        ...

    def get_product(self, product_id: int) -> Product:
        # hint: self._request("GET", f"/products/{product_id}").json() → Product.model_validate(...)
        ...

    def create_product(self, payload: ProductCreate) -> Product:
        # hint: self._request("POST", "/products", json=payload.model_dump()).json()
        ...

    def update_product(self, product_id: int, patch: ProductUpdate) -> Product:
        # hint: PATCH with json=patch.model_dump(exclude_unset=True)
        ...

    def delete_product(self, product_id: int) -> None:
        # hint: self._request("DELETE", f"/products/{product_id}")  (no return)
        ...
