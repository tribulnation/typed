"""Base endpoint class for KuCoin RPC (REST) endpoints.

Every Classic product — Account, Spot, Margin, Earn, VIP Lending, Futures,
Copy Trading, Broker — mixes its generated methods onto a subclass of `RpcEndpoint`; see
`spec/core.md` §Surfaces. `RpcEndpoint` itself never touches a base URL, credentials or
an `httpx` response directly — that's `transport.http.HttpRpcClient`'s job, reached only
through the `RpcClient` protocol below.
"""

from typing_extensions import Any, Mapping, Protocol, Self, TypeVar
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
    headers: Mapping[str, str] | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unsigned request, returning the unwrapped, optionally-validated result."""
    ...

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    headers: Mapping[str, str] | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send one request, returning the unwrapped, optionally-validated result.

    Raises:
      AuthError: This transport was built with no credentials.
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for KuCoin REST endpoint classes/mixins."""

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
    headers: Mapping[str, str] | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.request(
      method,
      path,
      params=params,
      json=json,
      headers=headers,
      validator=validator,
      validate=validate,
    )

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    headers: Mapping[str, str] | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.authed_request(
      method,
      path,
      params=params,
      json=json,
      headers=headers,
      validator=validator,
      validate=validate,
    )
