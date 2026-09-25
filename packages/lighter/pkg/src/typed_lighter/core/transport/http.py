"""REST transport for the main API: one `RpcClient` for every `client.api` call, plus the raw
`sendTx`/`sendTxBatch` submission `client.tx` uses over HTTP."""

from typing_extensions import Any, Mapping, Self, TypeVar
from dataclasses import dataclass, field

from typed_core.http import HttpClient
from typed_core.validation import validator
import httpx

from ..auth import TokenProvider
from ..endpoint.rpc import Auth, Method, RpcClient
from ..endpoint.wire import form_values, query_values
from ..envelope import unwrap
from ..exc import AuthError

T = TypeVar('T')


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """REST client for the main API, owning connection, auth-token attachment and validation."""

  base_url: str
  """Main REST API base URL (paths start with `/api/v1/`)."""
  http: HttpClient = field(default_factory=HttpClient)
  """Connection pool."""
  tokens: TokenProvider | None = None
  """Auth token source; `None` means only public calls can be made."""
  validate: bool = True
  """Validate responses by default."""

  async def __aenter__(self) -> Self:
    """Take ownership of the connection pool without connecting (it opens lazily)."""
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the connection pool, if it was opened. Only the root client (`core.client.ClientBase`) calls this."""
    await self.http.__aexit__(exc_type, exc_value, traceback)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  def auth_headers(self, auth: Auth) -> dict[str, str]:
    """The `Authorization` header (the bare token, no `Bearer` prefix) a call needs.

    Raises:
      AuthError: The call needs a token this client cannot provide.
    """
    if auth == 'none':
      return {}
    if self.tokens is None:
      if auth == 'optional':
        return {}
      raise AuthError(
        'This call needs an auth token: build the client with credentials.'
      )
    if auth == 'write' and self.tokens.scope != 'write':
      raise AuthError(
        'This call needs a token derived from an API key, not a read-only token.'
      )
    return {'Authorization': self.tokens.token()}

  async def request(
    self,
    method: Method,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    form: Mapping[str, Any] | None = None,
    auth: Auth = 'none',
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request to `base_url + path`, unwrap the envelope, then validate.

    Args:
      method: HTTP verb.
      path: URL path.
      params: Query parameters.
      form: Form-encoded body fields.
      auth: Token requirement.
      validator: Response validator.
      validate: Per-call override of response validation.
    """
    response = await self.http.request(
      method,
      self.base_url + path,
      params=query_values(params) if params else None,
      data=form_values(form) if form is not None else None,
      headers=self.auth_headers(auth),
    )
    return self.result(response, validator=validator, validate=validate)

  def result(
    self,
    response: httpx.Response,
    validator: validator[T] | None = None,
    *,
    validate: bool | None = None,
  ) -> T:
    """Unwrap the envelope and map errors, then validate."""
    payload = unwrap(response)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload
