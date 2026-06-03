# Lab 8 — Test the `APIClient` (Mocked + Integration)

**Duration:** ~80 min · **Day:** 3 · **Module:** 2 (Parametrize + Mocking)

## Goal
Lock the Day-2 `APIClient` under tests **without** depending on a real
server for every run. Mock `requests.Session`. Parametrize across status
codes. Then add a separate **integration** class that *does* spin up a real
uvicorn server for end-to-end confidence. The same mocking pattern is
exactly what Day 4 will use to mock the LLM — so don't skip it.

## You start with
- Lab 7 end-state — `tests/conftest.py`, `test_models.py`, `test_catalog.py` green.

## You'll end with
- `tests/test_client.py` with three classes: success, error mapping, integration
- A `live_server` session-scoped fixture in `conftest.py`
- `pytest -m "not integration"` runs in <1s; `pytest -m integration` boots a real server

## Steps

1. **Add a session-scoped `live_server` fixture to `conftest.py`.** It picks a free port, spawns `python -m uvicorn`, waits for `/health` to respond, then `yield`s the base URL. Tear it down with `proc.terminate()`.

   ```python
   @pytest.fixture(scope="session")
   def live_server():
       port = _free_port()
       proc = subprocess.Popen(
           [sys.executable, "-m", "uvicorn",
            "catalog.server:app", "--port", str(port), "--log-level", "warning"],
           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
       )
       base_url = f"http://127.0.0.1:{port}"
       _wait_for(f"{base_url}/health")
       yield base_url
       proc.terminate(); proc.wait(timeout=5)
   ```

   Session scope = one server for the whole test run. Don't re-boot per test.

2. **Build a mock-response helper.** Tests need a tiny "fake `requests.Response`" all over the place:

   ```python
   def _mock_response(status, payload):
       resp = MagicMock(spec=requests.Response)
       resp.ok = 200 <= status < 300
       resp.status_code = status
       resp.json.return_value = payload
       resp.text = str(payload)
       return resp
   ```

3. **Inject a mock session.** Your `APIClient` already accepts `session=` in its constructor (Lab 5). That's the seam:

   ```python
   @pytest.fixture
   def client_with_mock_session():
       session = MagicMock(spec=requests.Session)
       client = APIClient(base_url="http://test.local", session=session)
       return client, session
   ```

4. **Write success-path tests.** Assert the returned object is a real Pydantic `Product`, and that the right HTTP verb + path + body went out.

   ```python
   def test_create_product_sends_json_body(self, client_with_mock_session):
       client, session = client_with_mock_session
       session.request.return_value = _mock_response(201, {...})
       client.create_product(ProductCreate(id=5, name="Y", category="c", price=9.5))
       call = session.request.call_args
       assert call.args[0] == "POST"
       assert call.kwargs["json"]["id"] == 5
   ```

5. **Parametrize error mapping.** One test method, five status codes:

   ```python
   @pytest.mark.parametrize("status", [400, 404, 409, 422, 500])
   def test_non_2xx_raises_api_error(self, client_with_mock_session, status):
       client, session = client_with_mock_session
       session.request.return_value = _mock_response(status, {"detail": "boom"})
       with pytest.raises(APIError) as exc:
           client.list_products()
       assert exc.value.status_code == status
   ```

6. **Test the retry logic.** Use `side_effect = [ConnectionError, ConnectionError, success_response]`:

   ```python
   def test_retries_then_succeeds(self, client_with_mock_session):
       client, session = client_with_mock_session
       session.request.side_effect = [
           requests.ConnectionError("blip"),
           requests.ConnectionError("blip"),
           _mock_response(200, []),
       ]
       assert client.list_products() == []
       assert session.request.call_count == 3
   ```

   Then add `test_does_not_retry_on_4xx` — a 409 should be called exactly once.

7. **Add an `@pytest.mark.integration` class.** No mocks — talk to the real `live_server`:

   ```python
   @pytest.mark.integration
   class TestLiveServer:
       def test_full_crud_roundtrip(self, live_server):
           client = APIClient(base_url=live_server)
           created = client.create_product(ProductCreate(id=9001, ...))
           assert created.id == 9001
           ...
   ```

   Register the marker in `pyproject.toml`:
   ```toml
   [tool.pytest.ini_options]
   markers = ["integration: tests that hit a live FastAPI server (slow)"]
   ```

8. **Run both flavours.**
   ```bash
   pytest -m "not integration" -q   # fast, no network
   pytest -m integration         -q   # boots uvicorn
   pytest                         -q   # both
   ```

## Expected output

```
$ pytest -m "not integration" -q
...........................                                              [100%]
27 passed in 0.5s

$ pytest -m integration -q
..                                                                       [100%]
2 passed in 1.2s
```

## Common pitfalls
- Mocking `requests.get` at module level — your `APIClient` uses `self._session.request`, not `requests.get`. Patch *where it's looked up*.
- Using `MagicMock()` without `spec=requests.Session` — typos like `session.requst(...)` won't fail. Always pass `spec=`.
- Forgetting `wait_for(/health)` — the test starts before uvicorn is ready and you get random `ConnectionRefused` flakes.
- Boots uvicorn but never kills it — your CI runner accumulates zombie servers. Always teardown in the fixture.
- Asserting `session.request.call_count == 3` *without* `assert result == ...` — your retry might be silently returning `None`.

## Stretch (optional)
- Replace the `MagicMock` session with the [`responses`](https://github.com/getsentry/responses) library — declarative HTTP mocking, easier to read.
- Add `@pytest.mark.parametrize` over `client.list_products / get_product / delete_product` to assert each one retries on `ConnectionError` once.
