"""WS API transport: Binance's request/response trading API (`{id, method, params}` ->
`{id, status, result|error, rateLimits}`) over one persistent connection — built on
`typed_core.ws.StreamsRpc` rather than plain `Rpc`, since the same connection can also be
upgraded to push this account's order/balance events once subscribed (see
`request_subscription` below), not just answer requests.

Only Spot is wired. `session.logon` (stateful session auth) isn't implemented: Binance
only supports it with an Ed25519 key, and every credential this client has is HMAC — see
`spec/core.md`'s Authentication section. `userDataStream.subscribe.signature` covers the
same practical need (push events over this connection) with a plain per-request HMAC
signature instead, confirmed live.
"""

from typing_extensions import Any, Mapping, TypeVar, cast
from dataclasses import dataclass, field
from datetime import timedelta
import json

from typed_core.exceptions import AuthError
from typed_core.util import StreamManager
from typed_core.validation import validator
from typed_core.ws import StreamsRpc
from typed_core.ws.streams_rpc import Message

from ...auth import Credentials, signed_params
from ...endpoint.ws_rpc import WsRpcClient
from ...envelope import raise_error

T = TypeVar('T')

BINANCE_WS_API_URL = 'wss://ws-api.binance.com:443/ws-api/v3'

USER_DATA_CHANNEL = 'userData'
"""Binance's WS API has exactly one thing a connection can subscribe to — this account's
own push events, keyed by an opaque server-assigned `subscriptionId` rather than a
channel name — so this is a fixed local identifier, not a venue concept.
"""


@dataclass
class SocketRpc(StreamsRpc[dict, dict, dict, None, dict, dict]):
  """Raw WS API connection: id-correlated request/response, plus (once subscribed)
  un-id'd `{"subscriptionId", "event"}` pushes — confirmed live, not assumed from docs.
  """

  url: str = BINANCE_WS_API_URL
  credentials: Credentials | None = None
  recv_window: int | None = None

  async def rpc_send(self, id: int, req: dict):
    ws = await self.ws
    await ws.send(json.dumps({**req, 'id': id}))

  def parse_msg(self, msg: str | bytes) -> Message[dict, dict] | None:
    obj = json.loads(msg)
    if 'id' in obj:
      return {'kind': 'response', 'id': obj['id'], 'response': obj}
    return {'kind': 'subscription', 'channel': USER_DATA_CHANNEL, 'notification': obj}

  async def authed_rpc_request(
    self, method: str, params: Mapping[str, Any] | None = None
  ) -> dict:
    """Sign and send one WS API request. Unlike REST, `apiKey` is part of the signed
    JSON `params` object here — there are no per-message headers over a WebSocket.
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    query = dict(params or {})
    query['apiKey'] = self.credentials.api_key
    signed = signed_params(query, self.credentials, recv_window=self.recv_window)
    return await self.rpc_request({'method': method, 'params': signed})

  async def keyed_rpc_request(
    self, method: str, params: Mapping[str, Any] | None = None
  ) -> dict:
    """Send one WS API request carrying `apiKey` in `params` but no signature —
    `MARKET_DATA`/`USER_STREAM`-tier methods (the listenKey trio), which the venue
    documents as needing only the key, not `timestamp`/`signature`.
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    query = dict(params or {})
    query['apiKey'] = self.credentials.api_key
    return await self.rpc_request({'method': method, 'params': query})

  async def request_subscription(self, channel: str, params: None = None) -> dict:
    reply = await self.authed_rpc_request('userDataStream.subscribe.signature')
    if reply['status'] != 200:
      raise_error(reply['status'], reply.get('error'))
    return reply

  async def request_unsubscription(self, channel: str, params: None = None) -> dict:
    """`userDataStream.unsubscribe` takes no params and needs no signature when used
    this way — it just ends *this* connection's subscription, confirmed live.
    """
    reply = await self.rpc_request(
      {'method': 'userDataStream.unsubscribe', 'params': {}}
    )
    if reply['status'] != 200:
      raise_error(reply['status'], reply.get('error'))
    return reply


@dataclass(kw_only=True)
class SocketRpcClient(WsRpcClient):
  """WS API client, owning the connection and validation."""

  conn: SocketRpc = field(default_factory=SocketRpc)
  validate: bool = True

  @classmethod
  def new(
    cls,
    url: str = BINANCE_WS_API_URL,
    *,
    credentials: Credentials | None = None,
    recv_window: int | None = None,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
  ):
    """Build one subtree. Thin: no environment lookup — the root's `.new()` owns
    resolving credentials, see `main.py`.
    """
    conn = SocketRpc(
      url=url, credentials=credentials, recv_window=recv_window, timeout=timeout
    )
    return cls(conn=conn, validate=validate)

  def should_validate(self, validate: bool | None = None) -> bool:
    return self.validate if validate is None else validate

  async def __aenter__(self):
    await self.conn.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.conn.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    method: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    reply = await self.conn.rpc_request(
      {'method': method, 'params': dict(params) if params else {}}
    )
    return self.result(reply, validator=validator, validate=validate)

  async def authed_request(
    self,
    method: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    reply = await self.conn.authed_rpc_request(method, params)
    return self.result(reply, validator=validator, validate=validate)

  async def keyed_request(
    self,
    method: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    reply = await self.conn.keyed_rpc_request(method, params)
    return self.result(reply, validator=validator, validate=validate)

  def result(
    self,
    reply: dict,
    validator: validator[T] | None = None,
    *,
    validate: bool | None = None,
  ) -> T:
    if reply['status'] != 200:
      raise_error(reply['status'], reply.get('error'))
    result = reply['result']
    if validator is not None and self.should_validate(validate):
      return validator.python(result)
    return result

  def subscribe_user_data(
    self,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    manager = self.conn.subscribe(USER_DATA_CHANNEL)
    if validator is None or not self.should_validate(validate):
      return cast(StreamManager[T, Any, Any], manager)
    return manager.map(validator)
