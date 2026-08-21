"""Base endpoint class for Moralis's HTTP RPC endpoints. Every Moralis endpoint --
across every product (EVM, Solana, Bitcoin, Auth, Cortex, Streams, ...) -- is a plain
api-key-header request/reply call, so one `RpcEndpoint`/`RpcClient` pair backs all of
them; only the transport's `base_url` differs per product (`core.transport.http`).
"""

from dataclasses import dataclass

import httpx
from typing_extensions import Any, Mapping, Protocol, Self


class RpcClient(Protocol):
  """Structural interface a transport implements to back an `RpcEndpoint`."""

  validate: bool
  """Client-level default for response validation."""

  async def request(
    self, method: str, path: str, /, *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
  ) -> httpx.Response:
    """Send a request relative to the transport's base URL.

    Args:
      params: Query parameters to send with the request.
      json: JSON request body, for a POST/PUT/PATCH endpoint that takes one.

    Raises:
      typed_core.exceptions.ApiError: The response was not a successful (200) response.
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


def clean_params(params: Mapping[str, Any]) -> dict[str, Any]:
  """Remove unset query parameters before sending a request."""
  return {key: value for key, value in params.items() if value is not None}


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for hand-written Moralis endpoint methods. Talks only to `client`,
  never to a concrete transport directly.
  """

  client: RpcClient

  async def __aenter__(self) -> Self:
    """Open the underlying transport."""
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the underlying transport."""
    await self.client.__aexit__(exc_type, exc_value, traceback)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Resolve a per-call validation override against the client-level default."""
    return self.client.validate if validate is None else validate

  async def request(
    self, method: str, path: str, /, *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
  ) -> httpx.Response:
    """Send a request through the underlying transport."""
    return await self.client.request(method, path, params=params, json=json)
