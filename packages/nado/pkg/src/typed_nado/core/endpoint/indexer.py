"""Base endpoint class for the archive (indexer) and rewards APIs: one `POST` of
`{<query>: {...}}` per call, answered with the bare payload."""

from typing_extensions import (
  Any,
  Literal,
  NotRequired,
  Protocol,
  Self,
  TypedDict,
  TypeVar,
)
from dataclasses import dataclass
from types import UnionType

from typed_core.validation import validator

from .wire import SubaccountField, dump_request

T = TypeVar('T')


class IndexerMeta(TypedDict):
  """Per-endpoint quirks of an archive or rewards call."""

  sign: NotRequired[Literal['leaderboard']]
  """`leaderboard` for a rewards call carrying a signed `update_registration`
  (`LeaderboardAuthentication`); absent for every unsigned call."""
  default_subaccount: NotRequired[SubaccountField]
  """Fill this request field (`subaccount` or `sender`) with the client's own subaccount
  when the caller leaves it out."""


class IndexerClient(Protocol):
  """Structural interface the indexer transport implements to back an `IndexerEndpoint`."""

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
    """Send one query, map errors, then validate.

    Args:
      name: The query name (`candlesticks`, `leaderboard_contests`).
      values: The query's wire values.
      sign: Fill and sign `values` this way first.
      default_subaccount: Default this field of `values` to the client's subaccount.
      validator: Response validator.
      validate: Per-call override of response validation.
    """
    ...


@dataclass(kw_only=True, frozen=True)
class IndexerEndpoint:
  """Base class for archive and rewards endpoints."""

  client: IndexerClient
  """The archive or rewards transport."""

  async def __aenter__(self) -> Self:
    """Return this surface. Nothing opens: transports connect lazily, on first use."""
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Do nothing: only the root client (`core.base.ClientBase`) closes transports."""

  async def request(
    self,
    request: Any = None,
    *,
    method: str | None = None,
    path: str,
    meta: IndexerMeta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Perform one archive or rewards query.

    Args:
      request: The endpoint's `Request` value, or `None` for a parameterless call.
      method: Ignored: every query is a JSON `POST`.
      path: The query name.
      meta: This call's signing quirks.
      validate: Per-call override of response validation.
      request_type: The endpoint's request type, used to serialize `request`.
      response_type: The endpoint's response type, used to validate the reply.
    """
    values = dump_request(request, request_type)
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return await self.client.call(
      path,
      values,
      sign=meta.get('sign'),
      default_subaccount=meta.get('default_subaccount'),
      validator=response_validator,
      validate=validate,
    )
