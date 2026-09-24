"""Base endpoint class for the Aster Chain JSON-RPC (`tapi`): read-only `aster_*` methods,
all public, with positional `params` laid out in the order each endpoint declares in
`meta['params']`."""

from typing_extensions import Any, Mapping, Protocol, Self, Sequence, TypedDict, TypeVar
from dataclasses import dataclass
from types import UnionType

from typed_core.validation import validator

from .wire import dump_request

T = TypeVar('T')


class Meta(TypedDict):
  """The per-endpoint facts the JSON-RPC core needs to lay out one call."""

  params: list[str]
  """Wire names of the request fields, in the venue's documented positional order, e.g.
  `["address", "symbol", "from", "to", "blockTag"]`."""


class JsonRpcClient(Protocol):
  """Structural interface a transport implements to back a `JsonRpcEndpoint`."""

  async def call(
    self,
    method: str,
    params: Sequence[Any],
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class JsonRpcEndpoint:
  """Base class for Aster Chain JSON-RPC endpoints."""

  client: JsonRpcClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    request: Any = None,
    *,
    path: str,
    meta: Meta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Call one JSON-RPC method. Parameters are positional: each field of `request` fills
    its slot of `params`, in the order `meta['params']` lists; an omitted interior field
    is sent as `null` and omitted trailing fields are dropped.

    Args:
      request: The generated `Request` value, or `None` for a parameterless method.
      path: The JSON-RPC method name, e.g. `aster_getBalance`.
      meta: The endpoint's positional layout.
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the `result`.
    """
    values = dump_request(request, request_type) or {}
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return await self.client.call(
      path,
      positional(values, meta['params']),
      validator=response_validator,
      validate=validate,
    )


def positional(values: Mapping[str, Any], order: Sequence[str]) -> list[Any]:
  """Lay `values` out in `order`. An omitted field before a sent one is sent as `null`,
  so later values keep their slots; omitted trailing fields are dropped.

  Raises:
    ValueError: A key of `values` is not listed in `order`.
  """
  if unlisted := [key for key in values if key not in order]:
    raise ValueError(
      f'request fields {unlisted} have no positional slot in {list(order)}'
    )
  slots = list(order)
  while slots and slots[-1] not in values:
    slots.pop()
  return [values.get(key) for key in slots]
