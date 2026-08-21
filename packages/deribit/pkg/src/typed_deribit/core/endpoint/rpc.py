"""Base endpoint class for Deribit's JSON-RPC method surface.

Deribit is JSON-RPC (`method` + `params`), not REST-shaped (verb + path) — `RpcClient`
takes just those two, unlike a REST venue's `request(method, path, ...)`.
"""

from typing_extensions import Any, Mapping, Protocol, Self, TypeVar
from dataclasses import dataclass

from typed_core.validation import validator

T = TypeVar('T')


class RpcClient(Protocol):
  """Structural interface a transport implements to back an `RpcEndpoint`: one JSON-RPC
  method call, unauthenticated or authenticated."""

  async def request(
    self,
    method: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def authed_request(
    self,
    method: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for Deribit JSON-RPC endpoint groups."""

  client: RpcClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    method: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.request(
      method, params=params, validator=validator, validate=validate
    )

  async def authed_request(
    self,
    method: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.authed_request(
      method, params=params, validator=validator, validate=validate
    )
