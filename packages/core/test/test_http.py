"""
Pin `HttpClient`'s lazy connection contract.

Mirrors `test_socket.py`'s reasoning for the HTTP transport: `docs/production_guidelines.md`'s
"Core And Instantiation" promises that entering a client opens nothing, first use opens the
transport, and exiting closes exactly what was opened. `HttpClient.__aenter__` used to call
`await self.client` unconditionally; `__aexit__` already no-oped when `_client is None`, so
only `__aenter__` needed to change.

`httpx.AsyncClient` is replaced with a call-recorder via `monkeypatch` so these tests never
open a real HTTP connection.
"""
from dataclasses import dataclass, field
from typing_extensions import Any
import pytest
import httpx

import typed_core.http as http_module
from typed_core.http import HttpClient

@dataclass
class FakeHttpxClient:
  """Stand-in for `httpx.AsyncClient`: records construction and lifecycle calls instead of opening a socket."""
  entered: bool = field(default=False, init=False)
  exit_calls: list[tuple] = field(default_factory=list, init=False)
  request_calls: list[tuple] = field(default_factory=list, init=False)

  def __post_init__(self):
    FakeHttpxClient.instances.append(self)

  async def __aenter__(self):
    self.entered = True
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    self.exit_calls.append((exc_type, exc_value, traceback))

  async def request(self, method: str, url: str, **kwargs: Any):
    self.request_calls.append((method, url))
    return httpx.Response(200, request=httpx.Request(method, url))

FakeHttpxClient.instances = []
"""Every `FakeHttpxClient` constructed by the current test, class-level so the fixture can reset it."""

@pytest.fixture(autouse=True)
def fake_httpx_client(monkeypatch: pytest.MonkeyPatch):
  """Replace `httpx.AsyncClient` inside `typed_core.http` with the call-recorder above."""
  FakeHttpxClient.instances = []
  monkeypatch.setattr(http_module.httpx, 'AsyncClient', lambda **kwargs: FakeHttpxClient())
  yield

@pytest.mark.asyncio
async def test_aenter_opens_nothing():
  """Entering an `HttpClient` must not construct a transport."""
  client = HttpClient()
  async with client as opened:
    assert opened is client
    assert client._client is None
    assert not FakeHttpxClient.instances

@pytest.mark.asyncio
async def test_use_opens_the_client():
  """A request opens the underlying transport exactly once."""
  client = HttpClient()
  async with client:
    await client.request('GET', 'http://example.invalid')
  assert len(FakeHttpxClient.instances) == 1
  assert FakeHttpxClient.instances[0].entered is True

@pytest.mark.asyncio
async def test_two_requests_open_once():
  """Two requests within one `async with` open the transport once, not twice."""
  client = HttpClient()
  async with client:
    await client.request('GET', 'http://example.invalid/a')
    await client.request('GET', 'http://example.invalid/b')
  assert len(FakeHttpxClient.instances) == 1

@pytest.mark.asyncio
async def test_aexit_without_use_connects_nothing():
  """Exiting a client that was never used must not construct a transport just to close it."""
  async with HttpClient():
    pass
  assert not FakeHttpxClient.instances

@pytest.mark.asyncio
async def test_aexit_closes_what_was_opened():
  """Exiting after use closes exactly the transport that was opened."""
  client = HttpClient()
  async with client:
    await client.request('GET', 'http://example.invalid')
  assert len(FakeHttpxClient.instances[0].exit_calls) == 1

@pytest.mark.asyncio
async def test_exception_in_body_still_closes_what_was_opened():
  """An exception raised inside the `async with` body must not skip closing an opened transport."""
  client = HttpClient()
  with pytest.raises(RuntimeError, match='boom'):
    async with client:
      await client.request('GET', 'http://example.invalid')
      raise RuntimeError('boom')
  assert len(FakeHttpxClient.instances[0].exit_calls) == 1

@pytest.mark.asyncio
async def test_reentering_after_exit_gets_a_working_connection():
  """A client entered, used, exited and re-entered opens a fresh transport, not a stale reference."""
  client = HttpClient()
  async with client:
    await client.request('GET', 'http://example.invalid')
  first = FakeHttpxClient.instances[0]
  async with client:
    await client.request('GET', 'http://example.invalid')
    assert client._client is not None
  assert len(FakeHttpxClient.instances) == 2
  assert first.exit_calls
  assert FakeHttpxClient.instances[1].entered is True
