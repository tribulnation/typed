"""Base endpoint class for Kraken's WebSocket RPC methods: trading (`add_order`,
`cancel_order`, etc.), always sent over the private connection. Kraken's WS trading
methods have no public counterpart, so -- unlike `endpoint/rpc.py`'s HTTP split --
there is only one call shape here (`method` + `params`), not a public/private pair.
"""

from typing_extensions import Protocol, Self, TypeVar, Mapping, Any
from dataclasses import dataclass

from typed_core.validation import validator

T = TypeVar('T')


class WsRpcClient(Protocol):
  """Structural interface a socket transport implements to back a `WsRpcEndpoint`."""

  async def request(
    self,
    method: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Call a WebSocket RPC method and await its `req_id`-correlated reply, returning
    the reply's `result` field.
    """
    ...

  async def raw_request(
    self,
    method: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Call a WebSocket RPC method and await its `req_id`-correlated reply, returning
    the whole reply frame -- for the methods whose reply does not nest its payload
    under `result` (`ping`, `batch_cancel` -- see `spec/status.md`).
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class WsRpcEndpoint:
  """Base class for Kraken's WebSocket trading-method endpoints."""

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
    return await self.client.request(
      method, params, validator=validator, validate=validate
    )

  async def raw_request(
    self,
    method: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.raw_request(
      method, params, validator=validator, validate=validate
    )
