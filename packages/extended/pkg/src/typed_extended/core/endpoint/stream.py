"""Base endpoint class for the WebSocket streams: one `subscribe()` call per stream method.

Extended's v1 streams take no client frames: the URL path picks the stream (and the
market), the query string its options, and the server starts pushing as soon as the
connection opens. So every subscription is its own connection, and unsubscribing closes it.
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

from typed_core.util import StreamManager
from typed_core.validation import validator

from .wire import dump_request, fill_path

T = TypeVar('T', default=Any)


class StreamMeta(TypedDict):
  """Per-stream quirks of a WebSocket subscription."""

  auth: NotRequired[Literal['api_key']]
  """`api_key` when the stream needs the `X-Api-Key` header on its upgrade (the account
  stream); absent when public."""


class StreamClient(Protocol):
  """Structural interface the WebSocket transport implements to back a `StreamEndpoint`."""

  def subscribe(
    self,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    authed: bool = False,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, None, None]':
    """Open the stream at `path` (below the v1 stream base), with `params` as its query
    string, sending the API key on the upgrade when `authed`."""
    ...


@dataclass(frozen=True, kw_only=True)
class StreamEndpoint:
  """Base class for WebSocket stream endpoints."""

  client: StreamClient
  """The WebSocket transport."""

  async def __aenter__(self) -> Self:
    """Return this surface; each stream opens its own connection when subscribed."""
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Do nothing: only the root client closes the stream transport."""

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
    """Open one stream: fill `channel`'s `{placeholders}` from `parameters` (an absent
    optional one drops its segment: every market), send the rest as the query string.

    Args:
      channel: Stream path template, e.g. `/orderbooks/{market}`.
      parameters: The stream's `Parameters` value, or `None` for a fixed stream.
      meta: This stream's quirks: whether it needs the API key.
      validate: Per-call override of pushed-message validation.
      request_type: The stream's parameters type, used to serialize `parameters`.
      response_type: The stream's message type, used to validate each push.
    """
    values = dump_request(parameters, request_type)
    path = fill_path(channel, values)
    message_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return self.client.subscribe(
      path,
      params=values or None,
      authed=meta.get('auth') == 'api_key',
      validator=message_validator,
      validate=validate,
    )
