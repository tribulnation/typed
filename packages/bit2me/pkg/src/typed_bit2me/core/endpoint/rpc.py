"""Transport-agnostic base for Bit2Me's request/reply-style endpoints (`http`'s REST
calls, and `trading_ws`'s six one-shot commands)."""

from dataclasses import dataclass
from typing_extensions import Any, Mapping, Protocol, Self, TypeVar

from typed_core.validation import validator

T = TypeVar('T')


class RpcClient(Protocol):
  """What an endpoint needs from its transport: request/reply, public or authenticated."""

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T: ...
  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T: ...
  async def __aenter__(self) -> Self: ...
  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base for every hand-written or generated `http`/`trading_ws`-command endpoint
  method. Frozen: nothing about an endpoint changes after construction, so a
  subsection composing further children exposes each as a `functools.cached_property`
  returning `Child(client=self.client)`.
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
    validator: 'validator[T] | None' = None,
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
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.authed_request(
      method, path, params=params, json=json, validator=validator, validate=validate
    )
