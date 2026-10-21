"""HTTP transport: one `RpcClient` for every HTTP surface, owning the connection pool, the
signer, the network code and response validation.
"""

from typing_extensions import Any, Self, TypeVar
from dataclasses import dataclass, field
import json

import rfc8785

from typed_core.exceptions import AuthError, BadRequest
from typed_core.http import HttpClient
from typed_core.validation import validator

from ..auth import Credentials, sign_action
from ..endpoint.rpc import Auth, Method, RpcClient
from ..endpoint.wire import query_values
from ..envelope import unwrap
from ..networks import NetworkProfile

T = TypeVar('T')


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """HTTP client for every Margin Trade route, signing the calls that need it."""

  network: NetworkProfile
  """Host and network code: always taken together."""
  http: HttpClient = field(default_factory=HttpClient)
  """Connection pool."""
  credentials: Credentials | None = None
  """Signer; `None` means only unsigned calls can be made."""
  validate: bool = True
  """Validate responses by default."""

  async def __aenter__(self) -> Self:
    """Take ownership of the connection pool without connecting (it opens lazily)."""
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the connection pool, if it was opened. Only the root client calls this."""
    await self.http.__aexit__(exc_type, exc_value, traceback)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  def signer(self, auth: Auth) -> Credentials:
    """The credentials a signed call needs.

    Raises:
      AuthError: The client has no wallet, or the call needs the master key and the wallet
        is an agent.
    """
    if self.credentials is None:
      raise AuthError('This call is signed: build the client with a `wallet`.')
    elif auth == 'master' and not self.credentials.is_master:
      raise AuthError('This call must be signed by the master key, not an agent.')
    else:
      return self.credentials

  async def request(
    self,
    method: Method,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
    auth: Auth = 'none',
    testnet_only: bool = False,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request to the network's host, unwrap the envelope, then validate.

    A signed call's `body` is the action: it is signed into `{a, n, u, ts, s, v}` just before
    sending, so `ts` is as fresh as possible (the venue allows 60 s of skew), and the
    envelope is sent as RFC 8785 canonical JSON, so the action goes out byte-identical to
    what was signed.

    Raises:
      AuthError: The call is signed and the client has no (suitable) wallet, or the venue
        refused the signature.
      BadRequest: The call is testnet-only and this client is on mainnet, or the venue
        refused the request.
    """
    if testnet_only and self.network.code == 'm':
      raise BadRequest(f'{body and body.get("type")} exists on testnet only.')
    if auth != 'none':
      envelope = sign_action(body or {}, self.signer(auth), network=self.network.code)
      # The venue checks the signature against the action exactly as sent (a float `5.0`
      # fails where `5` passes), so the envelope goes out canonical: byte-identical to what
      # `s` signs, RFC 8785 being compositional.
      signed: dict[str, Any] = dict(envelope)
      content = rfc8785.dumps(signed)
    else:
      content = None if body is None else json.dumps(body, separators=(',', ':'))
    response = await self.http.request(
      method,
      self.network.api_url + path,
      params=query_values(params) if params else None,
      content=content,
      headers=None if content is None else {'Content-Type': 'application/json'},
    )
    payload = unwrap(response)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    else:
      return payload
