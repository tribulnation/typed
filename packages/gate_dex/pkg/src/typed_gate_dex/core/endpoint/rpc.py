"""Base class for Gate DEX actions, and the client protocol it talks to."""

from typing_extensions import Any, Literal, Mapping, Protocol, Self, TypedDict, TypeVar
from dataclasses import dataclass
from types import UnionType

T = TypeVar('T')


class Meta(TypedDict, total=False):
  """Per-action quirks the core needs; `{}` for every action but one."""

  keep_envelope: bool
  """Return the whole `{code, msg, data, page}` envelope instead of `data`.
  `market.pair.liquidity.list` sets it: its only page total sits beside `data`."""


class RpcClient(Protocol):
  """Sends one signed Gate DEX action and returns its validated result."""

  async def request(
    self,
    request: Mapping[str, Any] | None = None,
    *,
    method: Literal['POST'] = 'POST',
    path: str,
    meta: Meta | None = None,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Sign and send one action, then return its result.

    Args:
      request: The action's `params`; `None` sends `{}`.
      method: HTTP verb; the venue only accepts `POST`.
      path: The action name (`trade.swap.quote`), which plays the role of the path.
      meta: Per-action quirks.
      validate: Override response validation for this call.
      request_type: Type `request` is serialized through; may be a union.
      response_type: Type the result is validated against; may be a union.
    """
    ...

  async def __aenter__(self) -> Self:
    """Take ownership of the transport for an `async with` block."""
    ...

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Release the transport, closing any open connection."""
    ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for Gate DEX endpoints: every method forwards one action to `client`."""

  client: RpcClient
  """Signed transport this endpoint's actions are sent through."""

  async def __aenter__(self) -> Self:
    """Own `client` for an `async with` block, so a section can be used on its own."""
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Release `client`, closing any open connection."""
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    request: Mapping[str, Any] | None = None,
    *,
    method: Literal['POST'] = 'POST',
    path: str,
    meta: Meta | None = None,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Send one action and return its result.

    Args:
      request: The action's `params`; `None` sends `{}`.
      method: HTTP verb; the venue only accepts `POST`.
      path: The action name (`trade.swap.quote`), which plays the role of the path.
      meta: Per-action quirks.
      validate: Override response validation for this call.
      request_type: Type `request` is serialized through; may be a union
        (`trade.swap.submit`'s two request shapes).
      response_type: Type the result is validated against; may be a union
        (`trade.swap.gasprice`'s per-chain-family shapes).
    """
    return await self.client.request(
      request,
      method=method,
      path=path,
      meta=meta,
      validate=validate,
      request_type=request_type,
      response_type=response_type,
    )
