"""Base class for Etherscan's request/reply endpoints."""

from typing_extensions import Protocol, Self, TypeVar, Mapping, Any
from dataclasses import dataclass

from typed_core.validation import validator

T = TypeVar('T')


class RpcClient(Protocol):
  """Structural contract every generated endpoint method calls through.

  `data` carries a form-urlencoded body (`application/x-www-form-urlencoded`), the shape
  the contract-verification endpoints take -- distinct from a JSON body because Etherscan
  never takes one of those.
  """

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    data: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    data: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for an Etherscan endpoint, sharing one transport client."""

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
    data: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.request(
      method, path, params=params, data=data, validator=validator, validate=validate,
    )

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    data: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.authed_request(
      method, path, params=params, data=data, validator=validator, validate=validate,
    )
