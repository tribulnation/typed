"""Spot's own further WebSocket split (design §5c, one level under `spot`): a public,
unauthenticated connection and a private, listen-key-authenticated one, forwarded as
two distinctly-based children of the generated `Streams` composite.
"""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from .client import SpotPublicStreamsClient
from .auth import SpotPrivateStreamsClient


@dataclass(kw_only=True, frozen=True)
class SpotStreamsClients:
  """Spot's own two physical WebSocket connections, already built -- what
  `[python.cores.spot].children`'s `streams` entry forwards down from `SpotClients`."""

  market_client: SpotPublicStreamsClient
  user_client: SpotPrivateStreamsClient

  async def __aenter__(self) -> Self:
    await asyncio.gather(self.market_client.__aenter__(), self.user_client.__aenter__())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.market_client.__aexit__(exc_type, exc_value, traceback),
      self.user_client.__aexit__(exc_type, exc_value, traceback),
    )


@dataclass(kw_only=True, frozen=True)
class SpotStreamsBase:
  """Base every generated/hand-written Spot WebSocket leaf/router class subclasses --
  holds the two already-built connections `streams`'s own `market`/`user` children
  forward (design §5c's `children` mapping, one level deeper than `spot` itself)."""

  market_client: SpotPublicStreamsClient
  user_client: SpotPrivateStreamsClient

  @classmethod
  def new(cls, client: SpotStreamsClients) -> Self:
    """Unpack Spot's own two connections (design §5a's `client`-first forwarding
    convention) into this base's named fields."""
    return cls(market_client=client.market_client, user_client=client.user_client)
