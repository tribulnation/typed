"""Base endpoint class for REST-shaped RPC endpoints."""

from typing_extensions import Protocol, Self, TypeVar, Mapping, Any
from dataclasses import dataclass

from typed_core.validation import validator

T = TypeVar('T')


class RpcClient(Protocol):
  """Structural interface a transport implements to back an `RpcEndpoint`. No `json:`
  parameter: Binance never sends JSON bodies, only form-encoded `params` (see
  `spec/core.md`'s Authentication section).
  """

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def keyed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for REST-shaped RPC endpoints. Every Binance REST surface (Spot, USD-M/
  COIN-M Futures, Options, Portfolio Margin) shares this shape — only `client.base_url`
  and which methods a subclass adds differ.
  """

  client: RpcClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unsigned request — `NONE`-security endpoints only."""
    return await self.client.request(
      method, path, params=params, validator=validator, validate=validate
    )

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send one request — `TRADE`/`USER_DATA`/`MARGIN`-tier endpoints."""
    return await self.client.authed_request(
      method, path, params=params, validator=validator, validate=validate
    )

  async def keyed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send a request carrying the API key but no signature — `MARKET_DATA`/
    `USER_STREAM`-tier endpoints (and the rare unsigned `USER_DATA` outlier — see
    `spec/core.md`'s Authentication section).
    """
    return await self.client.keyed_request(
      method, path, params=params, validator=validator, validate=validate
    )
