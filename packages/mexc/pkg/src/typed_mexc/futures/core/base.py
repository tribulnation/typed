"""Futures' own resolved core (`codegen/config.toml` `[python.cores.futures]`, design §5c):
composes REST and the two Futures WebSocket connections, each holding its own
already-built transport forwarded from `core.base.FuturesClients`.
"""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from .client import FuturesHttpClient
from typed_mexc.futures.streams.core import FuturesStreamsClients


@dataclass(kw_only=True, frozen=True)
class FuturesClients:
  """Futures' own real transport clients: REST, and the (already-composed) pair of
  Futures WebSocket connections -- what `[python.cores.root].children`'s `futures`
  entry forwards down from `MexcBase`."""

  http_client: FuturesHttpClient
  streams_client: FuturesStreamsClients

  async def __aenter__(self) -> Self:
    await asyncio.gather(self.http_client.__aenter__(), self.streams_client.__aenter__())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.http_client.__aexit__(exc_type, exc_value, traceback),
      self.streams_client.__aexit__(exc_type, exc_value, traceback),
    )


@dataclass(kw_only=True, frozen=True)
class FuturesBase:
  """Base every generated Futures leaf/router class subclasses -- holds the
  already-built REST client and WS-connection pair `futures`'s own `http`/`streams`
  children forward."""

  http_client: FuturesHttpClient
  streams_client: FuturesStreamsClients

  @classmethod
  def new(cls, client: FuturesClients) -> Self:
    """Unpack Futures' own real transport clients (design §5a's `client`-first
    forwarding convention) into this base's named fields."""
    return cls(http_client=client.http_client, streams_client=client.streams_client)
