from dataclasses import dataclass
import asyncio

from typed_mexc.core.auth import resolve_credentials
from .core import StreamsClient, AuthedStreamsClient, MEXC_FUTURES_SOCKET_URL
from .user import UserStreams
from .market import MarketStreams

@dataclass
class Streams:
  market: MarketStreams
  user: UserStreams
  auth_ws: AuthedStreamsClient | None
  ws: StreamsClient

  @classmethod
  def new(
    cls, api_key: str | None = None, api_secret: str | None = None, *,
    public: bool = False,
    url: str = MEXC_FUTURES_SOCKET_URL,
    default_validate: bool = True,
  ):
    """Create a futures streams group.

    Args:
      api_key: MEXC access key; read from `MEXC_ACCESS_KEY` when omitted.
      api_secret: MEXC secret key; read from `MEXC_SECRET_KEY` when omitted.
      public: Build a public-only group with no credentials.
      url: WebSocket URL, overridable for tests.
      default_validate: Validate responses by default.
    """
    ws = StreamsClient(url=url)
    creds = resolve_credentials(api_key, api_secret, public=public)
    if creds is None:
      return cls(
        market=MarketStreams(ws, default_validate=default_validate),
        user=UserStreams(None, default_validate=default_validate),
        auth_ws=None,
        ws=ws,
      )
    auth_ws = AuthedStreamsClient(api_key=creds.api_key, api_secret=creds.api_secret, url=url)
    return cls(
      market=MarketStreams(ws, default_validate=default_validate),
      user=UserStreams(auth_ws, default_validate=default_validate),
      auth_ws=auth_ws,
      ws=ws,
    )

  async def __aenter__(self):
    if self.auth_ws is not None:
      await self.auth_ws.__aenter__()
    await self.ws.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    tasks = []
    if self.auth_ws is not None and self.auth_ws.ctx_future.done():
      tasks.append(self.auth_ws.__aexit__(exc_type, exc_value, traceback))
    if self.ws.ctx_future.done():
      tasks.append(self.ws.__aexit__(exc_type, exc_value, traceback))
    if tasks:
      await asyncio.gather(*tasks)
  
