"""dYdX Indexer WebSocket transport (design §2/§5/§6/§8, 2026-08-31 codegen mechanization).

`IndexerWsClient` is the shared transport every Indexer WebSocket leaf's resolved core
(`StreamsMixin`) forwards through. Every stream's push envelope is the identical
`{type, channel, ..., contents: X}` shape (`envelope.payload` is uniformly `'contents'`
across all 7 streams) -- a fixed core convention, not a per-call `meta` fact, so `streams`
declares no `[cores.streams].meta` schema at all.
"""

from typing_extensions import AsyncIterable, Literal, Any, NotRequired, Self, TypedDict, TypeVar, cast
from types import UnionType
from dataclasses import dataclass, field
import asyncio
import json
import logging
import re

import orjson
import pydantic

from typed_core import LogicError, BadRequest
from typed_core.util import Stream, StreamManager
from typed_core.validation import validator
from typed_core.ws.streams import Streams, Subscription

logger = logging.getLogger('dydx.indexer.streams')

INDEXER_WS_URL = 'wss://indexer.dydx.trade/v4/ws'
INDEXER_TESTNET_WS_URL = 'wss://indexer.v4testnet.dydx.exchange/v4/ws'

CHANNEL_PLACEHOLDER = re.compile(r'\{([^{}]+)\}')
"""A `{placeholder}` name in a channel template -- the same shape `docs/spec/
authoring.md` rule 8's own channel templates use everywhere else."""

T = TypeVar('T')


class BaseMessage(TypedDict):
  """BaseMessage payload."""
  connection_id: str
  message_id: int


class Connected(BaseMessage):
  """Connected payload."""
  type: Literal['connected']


class Channel(TypedDict):
  """Channel payload."""
  channel: str
  id: NotRequired[str]


class Subscribed(BaseMessage, Channel):
  """Subscribed payload."""
  type: Literal['subscribed']
  contents: Any


class Unsubscribed(BaseMessage, Channel):
  """Unsubscribed payload."""
  type: Literal['unsubscribed']


class Error(BaseMessage):
  """Error payload."""
  type: Literal['error']


class Notification(BaseMessage, Channel):
  """Stream notification payload."""
  type: Literal['channel_data', 'channel_batch_data']
  version: str
  contents: Any


Msg = Connected | Subscribed | Unsubscribed | Error | Notification
MsgT: type[Msg] = Msg  # type: ignore

msg_adapter = pydantic.TypeAdapter(MsgT)


class Params(TypedDict, total=False):
  """Params payload."""
  batched: bool


def parse_channel_id(channel_id: str) -> tuple[str, str | None]:
  """Split a stream channel id into channel and subscription id.

  Args:
    channel_id: Stream channel id.

  Returns:
    The parsed value.
  """
  if ':' in channel_id:
    channel, id = channel_id.split(':')
    return channel, id
  else:
    return channel_id, None


def channel_id(msg: Channel) -> str:
  """Build the local stream channel key for an indexer message.

  Args:
    msg: WebSocket message.

  Returns:
    The parsed value.
  """
  out = msg['channel']
  if (id := msg.get('id')) is not None and id != msg['channel']:  # yes that happens, it's a dydx bug
    out += f':{id}'
  return out


@dataclass
class IndexerWsClient(Streams[Notification, Params, Subscribed, Unsubscribed]):
  """Typed-core WebSocket transport for dYdX indexer streams."""
  url: str = INDEXER_WS_URL
  validate: bool = True
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  replies: asyncio.Queue[Error | Subscribed | Unsubscribed] = field(default_factory=asyncio.Queue)

  def parse_msg(self, msg: str | bytes) -> Subscription | None:
    """Parse an indexer WebSocket message.

    Args:
      msg: WebSocket message.

    Returns:
      The parsed value.
    """
    obj = msg_adapter.validate_json(msg)
    match obj['type']:
      case 'subscribed' | 'unsubscribed' | 'error':
        self.replies.put_nowait(obj)
      case 'channel_data' | 'channel_batch_data':
        channel = channel_id(obj)
        return {'channel': channel, 'notification': obj}

  async def send(self, msg: object):
    """Send a WebSocket message to the indexer.

    Args:
      msg: WebSocket message.
    """
    ws = await self.ws
    await ws.send(orjson.dumps(msg), text=True)

  async def request(self, msg: object) -> Error | Subscribed | Unsubscribed:
    """Send a serialized WebSocket request and wait for its reply.

    Args:
      msg: WebSocket message.

    Returns:
      The subscription, unsubscription, or error reply.
    """
    async with self.lock:
      await self.send(msg)
      return await self.replies.get()

  async def request_subscription(self, channel: str, params: Params | None = None) -> Subscribed:
    """Request an indexer WebSocket subscription.

    Args:
      channel: Stream channel name.
      params: Query parameters.

    Returns:
      The parsed value.
    """
    channel, id = parse_channel_id(channel)
    msg: dict = {
      'type': 'subscribe',
      'channel': channel,
    }
    if (params or {}).get('batched', False):
      msg['batched'] = True
    if id is not None:
      msg['id'] = id
    reply = await self.request(msg)
    if reply['type'] == 'error':
      raise BadRequest(reply)
    elif reply['type'] != 'subscribed':
      raise LogicError(f'Unexpected response type: {reply}')
    return reply

  async def request_unsubscription(self, channel: str, params: Params | None = None) -> Unsubscribed:
    """Request an indexer WebSocket unsubscription.

    Args:
      channel: Stream channel name.
      params: Query parameters.

    Returns:
      The parsed value.
    """
    channel, id = parse_channel_id(channel)
    msg = {
      'type': 'unsubscribe',
      'channel': channel,
    }
    if id is not None:
      msg['id'] = id
    reply = await self.request(msg)
    if reply['type'] == 'error':
      raise BadRequest(reply)
    if reply['type'] != 'unsubscribed':
      raise LogicError(f'Unexpected response type: {reply}')
    return reply


@dataclass(kw_only=True)
class StreamsMixin:
  """Base for every generated Indexer WebSocket endpoint module -- the resolved `core`
  for the `indexer/streams/` subtree (`codegen/config.toml`)."""

  client: IndexerWsClient = field(default_factory=IndexerWsClient)

  async def __aenter__(self) -> Self:
    """Enter the indexer client context."""
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Exit the indexer client context."""
    await self.client.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    channel: str,
    request: Any = None,
    *,
    meta: dict[str, Any] | None = None,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> StreamManager[T, Any, Unsubscribed]:
    """Subscribe to one Indexer WebSocket channel (design §2/§8): substitute every
    `{placeholder}` `channel`'s own template declares against `request`'s matching
    field, in the order they're declared, then join the substituted pieces back
    together at the position they occupied in `id` -- the wire's own subscribe frame
    has exactly one `id` slot (`IndexerWsClient.request_subscription`/
    `parse_channel_id`), so a multi-field channel like `'v4_candles:{market}/
    {resolution}'` composes its own real fields into that one slot, never sends them
    separately. Also defaults `batched` to `True` when the caller omits it, and --
    once subscribed -- extracts each push's `contents` (batched or not), each
    validated through `response_type`'s validator.

    Generalized from a hardcoded single `{id}` placeholder (this method's own
    previous shape) once `raw_candles`/`raw_subaccounts`/`raw_parent_subaccounts`
    stopped needing a hand-written `market`/`resolution`-splitting wrapper on top --
    every `{placeholder}` still resolves the identical way `{id}` alone used to,
    just generalized to any field name `channel`'s own template names, matching
    design §7's "core, not codegen, resolves any `{placeholder}`" rule exactly.

    Args:
      channel: Wire channel template, e.g. `'v4_candles:{market}/{resolution}'` --
        `core`, not codegen, resolves any `{placeholder}` against `request`'s own
        fields (design §7/§8).
      request: The generated `Parameters` value (a `TypedDict` instance, or `None` for a
        parameterless subscription).
      meta: Unused -- `streams` declares no `meta` schema (every push's envelope is the
        same fixed shape); kept for signature parity with `IndexerMixin.request`.
      validate: Per-call override of pushed-payload validation.
      request_type: The generated parameters type, used to serialize `request`.
      response_type: The generated payload type, used to validate each extracted `contents`.
    """
    values: dict[str, Any] = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else {}
    )
    resolved_channel = channel
    for placeholder in CHANNEL_PLACEHOLDER.findall(channel):
      if placeholder in values:
        resolved_channel = resolved_channel.replace(
          f'{{{placeholder}}}', str(values.pop(placeholder)),
        )
    batched = values.pop('batched', True)
    if batched is None:
      batched = True
    params: Params = {'batched': batched}

    async def impl() -> Stream[T, Any, Unsubscribed]:
      """Open the subscription and build the parsed, unsubscribable stream."""
      subscription = await self.client.subscribe(resolved_channel, params)

      async def parsed_stream() -> AsyncIterable[Any]:
        """Yield each pushed message's own `contents`, one item at a time."""
        async for msg in subscription:
          data = msg['contents']
          items = data if batched else [data]
          for item in items:
            should_validate = self.client.validate if validate is None else validate
            yield (
              validator(cast(type, response_type)).python(item)
              if should_validate and response_type is not None
              else item
            )

      reply_contents = subscription.reply['contents']
      should_validate = self.client.validate if validate is None else validate
      reply: Any = (
        validator(cast(type, response_type)).python(reply_contents)
        if should_validate and response_type is not None
        else reply_contents
      )
      return Stream(reply, parsed_stream(), subscription.unsubscribe)

    return StreamManager(impl)

  @classmethod
  def new(cls, url: str = INDEXER_WS_URL, *, validate: bool = True) -> Self:
    """Create a mainnet indexer streams client.

    Args:
      url: Indexer WebSocket URL.
      validate: Default response validation setting.

    Returns:
      The configured indexer streams client.
    """
    return cls(client=IndexerWsClient(url=url, validate=validate))
