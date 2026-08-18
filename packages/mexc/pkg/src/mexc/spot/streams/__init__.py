from dataclasses import dataclass as _dataclass

from mexc.spot.core import MEXC_SPOT_API_BASE, AuthHttpClient
from .core import StreamsClient, UserStreamsClient, MEXC_SPOT_SOCKET_URL
from .market import MarketStreams
from .user import UserStreams

@_dataclass
class ListenKeys:
  auth_ws: UserStreamsClient

  async def create(self) -> str:
    """Create a spot user-stream listen key."""
    return await self.auth_ws.listen_key()

  async def list(self) -> list[str]:
    """List active spot user-stream listen keys."""
    return await self.auth_ws.list_keys()

  async def keepalive(self, key: str):
    """Keep a spot user-stream listen key alive."""
    return await self.auth_ws.refresh_key(key)

  async def close(self, key: str):
    """Close a spot user-stream listen key."""
    return await self.auth_ws.delete_key(key)


@_dataclass
class Streams:
  market: MarketStreams
  user: UserStreams
  listen_keys: ListenKeys
  ws: StreamsClient
  auth_ws: UserStreamsClient

  @classmethod
  def new(
    cls, api_key: str | None = None, api_secret: str | None = None, *,
    api_url: str = MEXC_SPOT_API_BASE,
    ws_url: str = MEXC_SPOT_SOCKET_URL,
  ):
    """Create a spot streams group from resolved credentials."""
    import os
    if api_key is None:
      api_key = os.environ['MEXC_ACCESS_KEY']
    if api_secret is None:
      api_secret = os.environ['MEXC_SECRET_KEY']
    auth_http = AuthHttpClient(api_key=api_key, api_secret=api_secret)
    return cls._build(auth_http=auth_http, api_url=api_url, ws_url=ws_url)

  @classmethod
  def _build(cls, *, auth_http: AuthHttpClient, api_url: str, ws_url: str):
    """Construct every child from one already-resolved `auth_http`.

    Shared by `new` and `Spot._build` -- the latter already has an `AuthHttpClient`
    (`public=True` for a credential-free client included) and must reuse that exact
    object, not `new`'s own key/secret resolution, which would build a second client
    and silently lose the `public` flag along the way.
    """
    ws = StreamsClient(url=ws_url)
    auth_ws = UserStreamsClient(auth_http=auth_http, api_url=api_url, ws_url=ws_url)
    return cls(
      market=MarketStreams(ws=ws),
      user=UserStreams(auth_ws),
      listen_keys=ListenKeys(auth_ws),
      ws=ws,
      auth_ws=auth_ws,
    )

  async def __aenter__(self):
    await self.ws.__aenter__()
    if not self.auth_ws.auth_http.public:
      await self.auth_ws.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    if self.ws.ctx_future.done():
      await self.ws.__aexit__(exc_type, exc_value, traceback)
    if self.auth_ws.ctx_future.done():
      await self.auth_ws.__aexit__(exc_type, exc_value, traceback)
