"""Spot's own resolved core (`codegen/config.toml` `[python.cores.spot]`, design §5c):
composes REST and the two Spot WebSocket connections, each holding its own
already-built transport forwarded from `core.base.SpotClients`.
"""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from .client import SpotHttpClient
from typed_mexc.spot.streams.core import SpotStreamsClients


@dataclass(kw_only=True, frozen=True)
class SpotClients:
  """Spot's own real transport clients: REST, and the (already-composed) pair of
  Spot WebSocket connections -- what `[python.cores.root].children`'s `spot` entry
  forwards down from `MexcBase`."""

  http_client: SpotHttpClient
  streams_client: SpotStreamsClients

  async def __aenter__(self) -> Self:
    await asyncio.gather(self.http_client.__aenter__(), self.streams_client.__aenter__())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.http_client.__aexit__(exc_type, exc_value, traceback),
      self.streams_client.__aexit__(exc_type, exc_value, traceback),
    )


@dataclass(kw_only=True, frozen=True)
class SpotBase:
  """Base every generated Spot leaf/router class subclasses -- holds the already-built
  REST client and WS-connection pair `spot`'s own `http`/`streams` children forward."""

  http_client: SpotHttpClient
  streams_client: SpotStreamsClients

  @classmethod
  def new(cls, client: SpotClients) -> Self:
    """Unpack Spot's own real transport clients (design §5a's `client`-first
    forwarding convention) into this base's named fields."""
    return cls(http_client=client.http_client, streams_client=client.streams_client)
