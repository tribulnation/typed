"""Base endpoint class for Kraken Spot's HTTP RPC endpoints: public (unsigned) GET,
private (signed) POST -- Spot never mixes the two within one endpoint, so `request`/
`authed_request` fix the HTTP method rather than taking one as a parameter.
"""

from typing_extensions import Protocol, Self, TypeVar, Mapping, Any
from dataclasses import dataclass

from typed_core.validation import validator

T = TypeVar('T')


class RpcClient(Protocol):
  """Structural interface a transport implements to back an `RpcEndpoint`."""

  async def request(
    self,
    path: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unsigned GET request to a public endpoint."""
    ...

  async def authed_request(
    self,
    path: str,
    data: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send a POST request to a private endpoint.

    Raises:
      AuthError: This transport was built with no credentials (`public=True` upstream).
    """
    ...

  async def authed_json_request(
    self,
    path: str,
    data: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send a POST request with a JSON body, for the two endpoints Kraken
    rejects a form-urlencoded body on (`AddOrderBatch`, `CancelOrderBatch`).

    Raises:
      AuthError: This transport was built with no credentials (`public=True` upstream).
    """
    ...

  async def authed_raw_request(
    self,
    path: str,
    data: Mapping[str, Any] | None = None,
  ) -> bytes:
    """Sign and send a POST request to a private endpoint whose response is not the
    standard `{error, result}` JSON envelope (`RetrieveExport`'s binary export file).

    Raises:
      AuthError: This transport was built with no credentials (`public=True` upstream).
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for Kraken Spot HTTP endpoints."""

  client: RpcClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    path: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.request(
      path, params, validator=validator, validate=validate
    )

  async def authed_request(
    self,
    path: str,
    data: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.authed_request(
      path, data, validator=validator, validate=validate
    )

  async def authed_json_request(
    self,
    path: str,
    data: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.authed_json_request(
      path, data, validator=validator, validate=validate
    )

  async def authed_raw_request(
    self,
    path: str,
    data: Mapping[str, Any] | None = None,
  ) -> bytes:
    return await self.client.authed_raw_request(path, data)
