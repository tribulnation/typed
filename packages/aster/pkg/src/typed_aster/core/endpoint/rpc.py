"""Base endpoint class for the Binance-style REST surfaces: futures (`fapi`), spot
(`sapi`), prediction (`papi`) and Aster Chain REST (`chainapi`).

Every call goes through `RpcEndpoint.request`, which dispatches on the endpoint's
`meta['sign']`: `none` is sent as is, every other mode is signed by the transport.
"""

from typing_extensions import (
  Any,
  Literal,
  Mapping,
  NotRequired,
  Protocol,
  Self,
  TypedDict,
  TypeVar,
)
from dataclasses import dataclass
from types import UnionType

from typed_core.validation import validator

from ..auth import Wallet
from .wire import dump_request

T = TypeVar('T')

SignMode = Literal['none', 'agent', 'main', 'typed', 'withdraw']
"""How a call is authorised:

- `none`: public, unsigned.
- `agent` (the default): `user`, `signer` and `nonce` appended, and the agent signs
  `Message{msg}` over the query string.
- `main`: `user` and `nonce` added (and `signer`/`childSignature` when `Meta.order`
  lists them), and the main wallet signs `Message{msg}`.
- `typed`: `asterChain`, `user` and `nonce` appended, and the main wallet signs the
  action struct `Meta.action`.
- `withdraw`: signed as `agent`, after the main wallet signs the withdraw `Action` into
  `userNonce`/`userSignature`.
"""


class Meta(TypedDict):
  """The per-endpoint facts the transport needs to authorise one call. `{}` means an
  ordinary agent-signed call."""

  sign: NotRequired[SignMode]
  """Signing mode; `agent` when omitted."""
  action: NotRequired[str]
  """`typed` only: the EIP-712 primary type, e.g. `ApproveAgent`. Named `action`, not
  `type`, so it never collides with a wire parameter (orders take a `type`)."""
  order: NotRequired[list[str]]
  """`main` only: the documented field order of the signed message, e.g.
  `["subSourceAddr", "nonce", "user", "signer", "subAccountName", "status"]`. Listing
  `signer` sends the agent address; listing `childSignature` makes a sub-account
  co-sign (the `child` wallet)."""


class RpcClient(Protocol):
  """Structural interface a transport implements to back an `RpcEndpoint`."""

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    meta: Meta,
    params: Mapping[str, Any] | None = None,
    child: Wallet | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for REST endpoints. The same class serves every Binance-style surface:
  only the transport's `base_url` differs."""

  client: RpcClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    request: Any = None,
    *,
    method: str,
    path: str,
    meta: Meta,
    child: Wallet | None = None,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Perform one REST call.

    Args:
      request: The generated `Request` value, or `None` for a parameterless call.
      method: HTTP verb.
      path: Path relative to the surface's base URL, e.g. `balance`.
      meta: How the call is authorised.
      child: The sub-account wallet, for the calls it co-signs (`childSignature` in `meta['order']`).
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
    """
    params = dump_request(request, request_type)
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    if meta.get('sign', 'agent') == 'none':
      return await self.client.request(
        method, path, params=params, validator=response_validator, validate=validate
      )
    return await self.client.authed_request(
      method,
      path,
      meta=meta,
      params=params,
      child=child,
      validator=response_validator,
      validate=validate,
    )
