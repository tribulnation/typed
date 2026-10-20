"""Base endpoint for GRVT's edge host: plain REST (referral, deposit, bridge, vault listing)."""

from dataclasses import dataclass
from types import UnionType

from typing_extensions import Any, Protocol, Self, TypedDict, TypeVar

T = TypeVar('T')


class EdgeMeta(TypedDict, total=False):
  """Per-endpoint facts the edge transport needs: whether the endpoint is public."""

  public: bool
  """The endpoint needs no session (`investment/strategies`, `bridge/rhino-chain-id`)."""


class EdgeClient(Protocol):
  """Structural interface of the edge transport (`transport.edge.EdgeTransport`)."""

  async def request(
    self,
    request: Any = None,
    *,
    method: str,
    path: str,
    meta: EdgeMeta | None = None,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Call one edge endpoint and return its validated body; see `EdgeEndpoint.request`."""
    ...

  async def __aenter__(self) -> Self:
    """Take one (shared) ownership of the transport's connections."""
    ...

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Release that ownership; the last owner's exit closes the connections."""
    ...


@dataclass(kw_only=True, frozen=True)
class EdgeEndpoint:
  """Base of every edge endpoint, and of the routers composing them."""

  client: EdgeClient

  async def __aenter__(self) -> Self:
    """Take one (shared) ownership of the underlying connections; each opens lazily on
    first use."""
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Release that ownership; the connections close when their last owner leaves, so a
    block nested in another (or in `async with client`) closes nothing the outer one
    holds."""
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    request: Any = None,
    *,
    method: str,
    path: str,
    meta: EdgeMeta | None = None,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Call one edge endpoint.

    Args:
      request: The request value (a `TypedDict`), or `None`. Sent as the query string for
        `GET`, as the JSON body otherwise; `{name}` placeholders in `path` are filled from it.
      method: HTTP method.
      path: HTTP path, e.g. `/api/v1/deposit/addresses`.
      meta: Per-endpoint facts: whether a session is needed.
      validate: Per-call override of response validation.
      request_type: Type of `request`, used to serialize it.
      response_type: Type of the returned body, used to validate it.
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
