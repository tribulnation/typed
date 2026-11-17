"""REST transport: one `RpcClient` for every REST call, owning the connection pool, JWT
authentication, signing, the envelope and validation.
"""

from typing_extensions import Any, Literal, Mapping, Self, TypeVar
from dataclasses import dataclass, field

from typed_core.http import HttpClient
from typed_core.validation import validator

from ..auth import Session, Tokens
from ..endpoint.rpc import Method, RpcClient
from ..endpoint.wire import query_values
from ..envelope import NONCE_REVERTS, unwrap
from ..exc import ApiError, AuthError
from ..networks import NetworkProfile
from ..signing import SignKind, Signing

T = TypeVar('T')

validate_tokens = validator(Tokens)


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """REST client: connection pool, JWT session, signing, envelope and validation."""

  network: NetworkProfile
  """Deployment: REST base URL."""
  signing: Signing
  """Credentials and signing state, shared with the WebSocket transport."""
  http: HttpClient = field(default_factory=HttpClient)
  """Connection pool."""
  session: Session = field(default_factory=Session)
  """JWT session, opened on the first call that needs one."""
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

  async def call(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    headers: Mapping[str, str] | None = None,
  ) -> Any:
    """Send one request as-is and return its unwrapped `data`, unvalidated.

    Raises:
      NetworkError: The request could not be sent.
      ApiError: The response carried an error (`core.envelope`).
    """
    response = await self.http.request(
      method,
      self.network.api_url + path,
      params=query_values(params) if params else None,
      json=json,
      headers={'Accept': 'application/json', **(headers or {})},
    )
    return unwrap(response)

  async def login(self) -> Tokens:
    """Log in with an EIP-712 signature, returning fresh tokens."""
    body = await self.signing.attach(self, 'login', {})
    return validate_tokens.python(await self.call('POST', '/v1/auth/login', json=body))

  async def refresh(self, refresh_token: str) -> Tokens:
    """Exchange a refresh token for fresh tokens (the refresh token rotates)."""
    payload = await self.call(
      'POST', '/v1/auth/refresh', json={'refresh_token': refresh_token}
    )
    return validate_tokens.python(payload)

  async def token(self) -> str:
    """A live JWT access token, logging in or refreshing first if needed."""
    return await self.session.token(self.login, self.refresh)

  async def request(
    self,
    method: Method,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Mapping[str, Any] | None = None,
    auth: Literal['jwt'] | None = None,
    sign: SignKind | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request to the REST base URL plus `path`, unwrap the envelope, then validate.

    Args:
      method: HTTP verb.
      path: URL path.
      params: Query parameters.
      json: JSON body fields.
      auth: Authenticate with a JWT.
      sign: Complete and sign `json` for this action first (`core.signing`).
      validator: Response validator.
      validate: Per-call override of response validation.

    Raises:
      AuthError: The call needs keys the client lacks, or the venue rejected them.
      ApiError: The venue returned an error (`core.envelope`).
    """
    headers: dict[str, str] = {}
    if auth == 'jwt':
      headers['Authorization'] = f'Bearer {await self.token()}'
    body: Any = dict(json) if json is not None else None
    if sign is not None:
      body = await self.signing.attach(self, sign, body or {})
    try:
      payload = await self.call(method, path, params=params, json=body, headers=headers)
    except AuthError:
      if auth == 'jwt':
        self.session.invalidate()
      raise
    except ApiError as e:
      if sign is not None and any(reason in str(e) for reason in NONCE_REVERTS):
        self.signing.nonces.reset()
      raise
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload
