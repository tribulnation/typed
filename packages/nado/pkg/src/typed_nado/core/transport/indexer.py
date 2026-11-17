"""Archive (indexer) and rewards transport: `POST {<query>: {...}}` to one URL, answered
with the bare payload."""

from typing_extensions import Any, Literal, TypeVar
from dataclasses import dataclass

from typed_core.http import HttpClient
from typed_core.validation import validator

from ..endpoint.indexer import IndexerClient
from ..envelope import unwrap_bare
from ..exc import AuthError, LogicError
from ..endpoint.wire import SubaccountField
from ..signing import Signer, with_default_subaccount, prepare
from .http import post_json

T = TypeVar('T')


async def no_tx_nonce() -> str:
  """Never awaited: no archive or rewards payload takes a sequential nonce.

  Raises:
    LogicError: Always; reaching it is a bug in this client.
  """
  raise LogicError('This payload takes no sequential nonce')


@dataclass(kw_only=True)
class IndexerTransport(IndexerClient):
  """The archive v1 or rewards v1 service."""

  http: HttpClient
  """The client's shared HTTP connection pool."""
  url: str
  """The service URL every query is posted to."""
  signer: Signer | None = None
  """Signs rewards registrations; `None` for a public client."""
  validate: bool = True
  """Validate responses by default."""
  timeout: float | None = None
  """Per-request timeout in seconds; the shared HTTP client's default when `None`. The
  archive's heavier queries take over 10 s (measured on testnet), so it gets a longer one."""

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def call(
    self,
    name: str,
    values: dict[str, Any],
    *,
    sign: Literal['leaderboard'] | None = None,
    default_subaccount: SubaccountField | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one query; see `IndexerClient.call`.

    Raises:
      AuthError: The call is signed, or omits a subaccount it would default to the
        client's own, on a public client.
      BadRequest: The venue refused the request.
      RateLimited: The venue throttled the request.
      ApiError: Any other venue error.
    """
    values = with_default_subaccount(name, values, default_subaccount, self.signer)
    if sign is not None:
      if self.signer is None:
        raise AuthError(
          f'{name} needs a signing key; this client was built with `public=True`.'
        )
      values = await prepare(sign, values, self.signer, no_tx_nonce)
    result = unwrap_bare(
      await post_json(self.http, self.url, {name: values}, timeout=self.timeout)
    )
    if validator is not None and self.should_validate(validate):
      return validator.python(result)
    return result
