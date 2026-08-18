"""Base endpoint class for RPC (REST) endpoints."""

from typing_extensions import Protocol, Self, TypeVar, Mapping, Any
from dataclasses import dataclass

from typed_core.validation import validator

T = TypeVar('T')


class RpcClient(Protocol):
  """Structural interface a transport implements to back an `RpcEndpoint`."""

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

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send one request.

    Raises:
      AuthError: This client was built with no credentials (`public=True` upstream).
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for RPC endpoints. A subsection composing further children exposes each one
  as a `functools.cached_property` returning `Child(client=self.client)`.
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
    json: Any | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.request(
      method, path, params=params, json=json, validator=validator, validate=validate
    )

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.authed_request(
      method, path, params=params, json=json, validator=validator, validate=validate
    )
