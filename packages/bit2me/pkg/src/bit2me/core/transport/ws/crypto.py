"""The `crypto_ws` surface: account notifications. No subscribe/unsubscribe protocol
— one `authenticate` frame, then every notification type the account is entitled to
arrives unprompted on the same firehose. See `spec/core.md`'s Surfaces/WebSocket
sections.

`BIT2ME_CRYPTO_WS_URL` isn't stated directly in Bit2Me's docs (they give only an
unresolved `wss://${host}:${port}/` template), but is confirmed via Bit2Me's own
official sample repo (`github.com/bit2me-dev/bit2me-api-node-tool`) and independently
by a live connection: authenticating with a JWT token stays open cleanly. Use the
token form of `authenticate` — the documented `apikey`-array alternative reproducibly
gets an abrupt close (code `1006`) instead, isolated by an A/B test that changed only
the auth payload on the same connection/host.
"""

import asyncio
from dataclasses import dataclass, field
from typing_extensions import Any, AsyncIterator, Self
import orjson

from typed_core.ws import Socket

BIT2ME_CRYPTO_WS_URL = 'wss://ws.bit2me.com/'


@dataclass
class CryptoWsConnection(Socket):
  """One connection. `on_msg` only queues frames — there's no reply/push split to
  route, unlike `trading_ws`, since nothing here is request/reply shaped."""

  url: str = BIT2ME_CRYPTO_WS_URL
  queue: 'asyncio.Queue[dict[str, Any]]' = field(
    default_factory=asyncio.Queue, init=False, repr=False
  )

  def on_msg(self, msg: str | bytes):
    self.queue.put_nowait(orjson.loads(msg))

  async def authenticate(self, *, token: str | None = None, api_key: str | None = None):
    """Send the first frame after connect. Exactly one of `token`/`api_key` should be
    given, per Bit2Me's documented `{type: 'authenticate', payload: {token}}` /
    `{type: 'authenticate', payload: {apikey: [key]}}` shapes.

    Prefer `token` — confirmed working live (mint one with `auth.mint_ws_token`, the
    same flow `trading_ws` uses). `api_key` is kept because Bit2Me documents it, but a
    direct A/B test against the same connection found it reproducibly closes the
    socket with code `1006` instead of authenticating; that path is currently known
    broken, not just unverified.

    Bit2Me sends no success acknowledgement — silence means it worked. Docs describe
    an immediate close with code `4000` on failure; the next `notifications()` read
    then surfaces that as a `NetworkError` from the underlying listener, not a more
    specific `AuthError` — distinguishing the close code is a follow-up, not core to
    this PoC. (The `1006` seen from the `api_key` path doesn't match `4000` either,
    so even the failure-signal shape isn't fully confirmed yet.)
    """
    payload = {'token': token} if token is not None else {'apikey': [api_key]}
    ws = await self.ws
    await ws.send(orjson.dumps({'type': 'authenticate', 'payload': payload}))

  async def notifications(self) -> AsyncIterator[dict]:
    """Every notification frame received after authenticating, as a permissive dict —
    matching the spec's own deliberate `additionalProperties: true, no title` choice
    for all 34 notification types, since Bit2Me documents only a payload sketch per
    type, not a full schema."""
    while True:
      yield await self.wait(self.queue.get())


@dataclass(kw_only=True)
class CryptoWsClient:
  """Thin wrapper resolving `url` at `.new()` time, same shape as the other `ws/`
  clients even though `crypto_ws` needs no credential-driven auth split."""

  conn: CryptoWsConnection = field(default_factory=CryptoWsConnection)

  @classmethod
  def new(cls, *, url: str = BIT2ME_CRYPTO_WS_URL) -> Self:
    return cls(conn=CryptoWsConnection(url=url))

  async def __aenter__(self) -> Self:
    await self.conn.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.conn.__aexit__(exc_type, exc_value, traceback)

  async def authenticate(self, *, token: str | None = None, api_key: str | None = None):
    await self.conn.authenticate(token=token, api_key=api_key)

  def notifications(self) -> AsyncIterator[dict]:
    return self.conn.notifications()
