"""Base endpoint class for the subscriptions WebSocket: one `subscribe()` call per stream
method."""

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

from typed_core.util import StreamManager
from typed_core.validation import validator

from .wire import SubaccountField, dump_request

T = TypeVar('T', default=Any)


class StreamMeta(TypedDict):
  """Per-stream quirks of a subscription."""

  authenticate: NotRequired[Literal[True]]
  """The stream needs an authenticated connection (`order_update`, the only one)."""
  default_subaccount: NotRequired[SubaccountField]
  """The stream is scoped to a subaccount: fill this scope field with the client's own when
  the caller leaves it out (`order_update`, `fill`, `position_change`)."""


class StreamClient(Protocol):
  """Structural interface the subscriptions transport implements to back a
  `StreamEndpoint`."""

  def subscribe(
    self,
    stream: Mapping[str, Any],
    *,
    authenticate: bool = False,
    default_subaccount: SubaccountField | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, None, None]':
    """Subscribe to one stream (`{"type": ..., <scope>}`), validating each event.

    Args:
      stream: The stream object: its `type` plus its scope (`product_id`, `subaccount`,
        `granularity`).
      authenticate: Authenticate the connection first.
      default_subaccount: Default this scope field to the client's subaccount.
      validator: Event validator.
      validate: Per-call override of event validation.
    """
    ...


@dataclass(frozen=True, kw_only=True)
class StreamEndpoint:
  """Base class for subscription stream endpoints."""

  client: StreamClient
  """The subscriptions transport."""

  async def __aenter__(self) -> Self:
    """Return this surface. Nothing opens: the socket connects on the first subscription."""
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Do nothing: only the root client (`core.base.ClientBase`) closes the socket."""

  def subscribe(
    self,
    channel: str,
    parameters: Any = None,
    *,
    meta: StreamMeta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> 'StreamManager[T, None, None]':
    """Subscribe to one stream. An omitted optional `product_id` subscribes to every
    product, where the stream allows it.

    Args:
      channel: The stream `type` (`trade`, `best_bid_offer`).
      parameters: The stream's scope (`Parameters`), or `None` for an unscoped stream.
      meta: This stream's quirks: authentication and subaccount scope.
      validate: Per-call override of event validation.
      request_type: The stream's parameters type, used to serialize `parameters`.
      response_type: The stream's event type, used to validate each event.
    """
    values = dump_request(parameters, request_type)
    event_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return self.client.subscribe(
      {'type': channel, **values},
      authenticate=meta.get('authenticate', False),
      default_subaccount=meta.get('default_subaccount'),
      validator=event_validator,
      validate=validate,
    )
