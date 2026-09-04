"""Futures' own further WebSocket split (design §5c, one level under `futures`): a
public, unauthenticated connection and a private, login-gated one, forwarded as two
distinctly-based children of the generated `Streams` composite.
"""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from .client import FuturesPublicStreamsClient
from .auth import FuturesPrivateStreamsClient


@dataclass(kw_only=True, frozen=True)
class FuturesStreamsClients:
  """Futures' own two physical WebSocket connections, already built -- what
  `[python.cores.futures].children`'s `streams` entry forwards down from
  `FuturesClients`."""

  market_client: FuturesPublicStreamsClient
  user_client: FuturesPrivateStreamsClient

  async def __aenter__(self) -> Self:
    await asyncio.gather(self.market_client.__aenter__(), self.user_client.__aenter__())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.market_client.__aexit__(exc_type, exc_value, traceback),
      self.user_client.__aexit__(exc_type, exc_value, traceback),
    )


@dataclass(kw_only=True, frozen=True)
class FuturesStreamsBase:
  """Base every generated/hand-written Futures WebSocket leaf/router class
  subclasses -- holds the two already-built connections `streams`'s own
  `market`/`user` children forward."""

  market_client: FuturesPublicStreamsClient
  user_client: FuturesPrivateStreamsClient

  @classmethod
  def new(cls, client: FuturesStreamsClients) -> Self:
    """Unpack Futures' own two connections (design §5a's `client`-first forwarding
    convention) into this base's named fields."""
    return cls(market_client=client.market_client, user_client=client.user_client)
