"""Base endpoint class for WS-API-shaped RPC endpoints — `{method, params}` requests, with
no separate HTTP-verb/path pair the way `endpoint/rpc.py`'s REST shape has.

Also carries `subscribe_user_data`: Binance's WS API connection can be upgraded, via a
signed `userDataStream.subscribe.signature` call, to also push this account's
order/balance events on the same connection — the one place a Binance WS surface is
genuinely both RPC- and stream-shaped at once (see `spec/core.md`'s WebSocket section).
"""

from typing_extensions import Any, Mapping, Protocol, Self, TypeVar
from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T', default=Any)


class WsRpcClient(Protocol):
  """Structural interface a transport implements to back a `WsRpcEndpoint`."""

  async def request(
    self,
    method: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def authed_request(
    self,
    method: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  def subscribe_user_data(
    self,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]': ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class WsRpcEndpoint:
  """Base class for WS-API-shaped RPC endpoints (Binance's Spot/USD-M/COIN-M WS API)."""

  client: WsRpcClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    method: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unsigned request."""
    return await self.client.request(
      method, params, validator=validator, validate=validate
    )

  async def authed_request(
    self,
    method: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send one request."""
    return await self.client.authed_request(
      method, params, validator=validator, validate=validate
    )

  def subscribe_user_data(
    self,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe this connection to account/order push events. Signed."""
    return self.client.subscribe_user_data(validator=validator, validate=validate)
