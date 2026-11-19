"""HTTP transport: one `RpcClient` per EVEDEX REST service."""

from typing_extensions import Any, Mapping, TypeVar
from dataclasses import dataclass, field

from typed_core.http import HttpClient
from typed_core.validation import validator

from ..auth import Credentials, Session
from ..endpoint.rpc import AuthMode, RpcClient
from ..exc import AuthError
from ..signing import Action, sign_action
from ..wire import dumps, unwrap

T = TypeVar('T')


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """REST client of one EVEDEX service, owning authentication, signing and validation.

  Authenticates with the API key when it has one and the service takes it, else with the
  wallet's JWT session; a `401` on a session token refreshes it and retries once. The
  `HttpClient` and `Session` are shared by every service of one client, and owned by the
  root: this transport neither opens nor closes them.
  """

  base_url: str
  http: HttpClient = field(default_factory=HttpClient)
  credentials: Credentials | None = None
  """`None` means unauthenticated: only `public`/`optional` requests can be sent."""
  session: Session | None = None
  """The wallet's JWT session; `None` without a wallet key."""
  chain_id: int
  """Chain id of the EIP-712 domain."""
  accepts_api_key: bool = True
  """Whether this service authorizes `X-API-Key` (Exchange does; Auth does not)."""
  validate: bool = True

  async def __aenter__(self):
    """Nothing to open: the shared `HttpClient` is the root's to open."""
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Nothing to close: the shared `HttpClient` is the root's to close."""

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  def api_key(self) -> str | None:
    """The API key to send, if this service takes one and the client has one."""
    if self.accepts_api_key and self.credentials is not None:
      return self.credentials.api_key

  async def send(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None,
    json: Any | None,
    auth: AuthMode,
  ) -> Any:
    """Send one request, authenticated as `auth` says, and return the bare payload.

    Raises:
      AuthError: A `private` request on a client with no usable credential for this
        service, or the venue rejected the credential.
    """
    headers = {'Accept': 'application/json'}
    content = None
    if json is not None:
      content = dumps(json)
      headers['Content-Type'] = 'application/json'
    url = self.base_url + path
    token = None
    if auth != 'public':
      if (api_key := self.api_key()) is not None:
        headers['X-API-Key'] = api_key
      elif self.session is not None:
        token = await self.session.access_token()
        headers['Authorization'] = f'Bearer {token}'
      elif auth == 'private':
        raise AuthError(
          'No credentials for this call: it needs a wallet key'
          + (' or an API key.' if self.accepts_api_key else '.')
        )
    response = await self.http.request(
      method, url, params=params, content=content, headers=headers
    )
    if response.status_code == 401 and token is not None and self.session is not None:
      token = await self.session.rejected(token)
      headers['Authorization'] = f'Bearer {token}'
      response = await self.http.request(
        method, url, params=params, content=content, headers=headers
      )
    return unwrap(response)

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    auth: AuthMode = 'public',
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request to `base_url + path` and validate its bare payload."""
    payload = await self.send(method, path, params=params, json=json, auth=auth)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload

  def sign(self, action: Action, body: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize and EIP-712-sign one body as `action` (`signing.sign_action`).

    Raises:
      AuthError: The client has no wallet key.
    """
    if self.credentials is None or self.credentials.account is None:
      raise AuthError(
        'Signed calls need the wallet private key; an API key cannot sign.'
      )
    return sign_action(self.credentials.account, action, body, chain_id=self.chain_id)

  async def signed_request(
    self,
    method: str,
    path: str,
    *,
    action: Action,
    json: Mapping[str, Any],
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Sign `json` as `action`, then send it `private`.

    Raises:
      AuthError: The client has no wallet key.
    """
    return await self.request(
      method,
      path,
      json=self.sign(action, json),
      auth='private',
      validator=validator,
      validate=validate,
    )
