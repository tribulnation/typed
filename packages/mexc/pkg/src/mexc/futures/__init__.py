from dataclasses import dataclass
import asyncio
import os

from mexc.futures.core import MEXC_FUTURES_API_BASE, AuthHttpClient
from .streams import Streams
from .streams.core import MEXC_FUTURES_SOCKET_URL
from .account import Account
from .market import Market
from .position import Position
from .trade import Trade

@dataclass
class Futures:
  account: Account
  market: Market
  position: Position
  trade: Trade
  streams: Streams
  auth_http: AuthHttpClient

  @classmethod
  def new(
    cls, api_key: str | None = None, api_secret: str | None = None, *,
    base_url: str = MEXC_FUTURES_API_BASE,
    ws_url: str = MEXC_FUTURES_SOCKET_URL,
    default_validate: bool = True,
  ):
    """Create a futures API group with signed endpoint support."""
    if api_key is None:
      api_key = os.environ['MEXC_ACCESS_KEY']
    if api_secret is None:
      api_secret = os.environ['MEXC_SECRET_KEY']
    auth_http = AuthHttpClient(api_key=api_key, api_secret=api_secret)
    return cls._build(api_url=base_url, ws_url=ws_url, auth_http=auth_http, default_validate=default_validate)

  @classmethod
  def public(
    cls, *,
    base_url: str = MEXC_FUTURES_API_BASE,
    ws_url: str = MEXC_FUTURES_SOCKET_URL,
    default_validate: bool = True,
  ):
    """Create a public-only futures API group."""
    auth_http = AuthHttpClient(api_key='', api_secret='', public=True)
    return cls._build(api_url=base_url, ws_url=ws_url, auth_http=auth_http, default_validate=default_validate)

  @classmethod
  def _build(
    cls, *, api_url: str, ws_url: str, auth_http: AuthHttpClient, default_validate: bool,
  ):
    """Construct every child from one resolved `auth_http`, shared by `new`/`public`."""
    streams = (
      Streams.public(url=ws_url, default_validate=default_validate)
      if auth_http.public
      else Streams.new(
        auth_http.api_key, auth_http.api_secret,
        url=ws_url,
        default_validate=default_validate,
      )
    )
    return cls(
      account=Account(
        base_url=api_url,
        auth_http=auth_http,
        default_validate=default_validate,
      ),
      market=Market(
        base_url=api_url,
        http=auth_http,
        default_validate=default_validate,
      ),
      position=Position(
        base_url=api_url,
        auth_http=auth_http,
        default_validate=default_validate,
      ),
      trade=Trade(
        base_url=api_url,
        auth_http=auth_http,
        default_validate=default_validate,
      ),
      streams=streams,
      auth_http=auth_http,
    )

  async def __aenter__(self):
    """Open the underlying futures transports."""
    await asyncio.gather(
      self.auth_http.__aenter__(),
      self.streams.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the underlying futures transports."""
    await asyncio.gather(
      self.auth_http.__aexit__(exc_type, exc_value, traceback),
      self.streams.__aexit__(exc_type, exc_value, traceback),
    )
