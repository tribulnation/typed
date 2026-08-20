"""Base endpoint classes for Alchemy's REST and enhanced JSON-RPC surfaces.

Every Alchemy surface this client implements authenticates by embedding the app API key
directly in the request URL itself, so there is no separate signed/unsigned request pair
the way an HMAC-signing venue needs: `RestClient`/`JsonRpcClient` below expose one
`request`/`rpc` pair rather than the generic template's `request`/`authed_request` split.

`RestClient` is the narrower interface (a plain REST verb-shaped call), implemented by
`core/transport/http.py`'s `ApiKeyPathHttpClient` -- kept as its own Protocol, rather than
folded into `JsonRpcClient`, since a future `api-key-path` REST-only surface (or a
distinct-auth surface, should one come back into scope) can implement it without also
implementing `rpc`. `JsonRpcClient` extends it with `rpc`, Alchemy's JSON-RPC call shape
for the `alchemy_*` "enhanced" methods (Token, Transfers, Utility, Simulation).
"""

from typing_extensions import Any, Mapping, Protocol, Self, TypeVar
from dataclasses import dataclass

from typed_core.validation import validator

T = TypeVar('T')


class RestClient(Protocol):
  """Structural interface for a plain REST request/reply transport."""

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


class JsonRpcClient(RestClient, Protocol):
  """`RestClient` plus a JSON-RPC call, for the chain-hosted `alchemy_*` methods."""

  async def rpc(
    self,
    method: str,
    params: Any | None = None,
    *,
    id: int = 1,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...


@dataclass(kw_only=True, frozen=True)
class RestEndpoint:
  """Base class for a plain REST endpoint group (Portfolio, Prices, NFT v3)."""

  client: RestClient

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
    json: Any | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.request(
      method, path, params=params, json=json, validator=validator, validate=validate
    )


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint(RestEndpoint):
  """Base class for an endpoint group that also calls Alchemy's `alchemy_*` JSON-RPC
  methods (Token, Transfers, Utility, Simulation).
  """

  client: JsonRpcClient

  async def rpc(
    self,
    method: str,
    params: Any | None = None,
    *,
    id: int = 1,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.rpc(
      method, params, id=id, validator=validator, validate=validate
    )
